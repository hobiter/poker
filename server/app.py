from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uuid

from .models import RoomCreate, JoinRequest
from .storage import InMemoryStore
from .ws_manager import ConnectionManager

from engine.deck import Deck
from engine.session import Session

app = FastAPI(title="Poker - Phase 2 Scaffold")

# Allow cross-origin requests from local frontend dev servers (Phase 3)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = InMemoryStore()
manager = ConnectionManager()


@app.post("/rooms")
def create_room(rc: RoomCreate):
    room_id = store.create_room(rc)
    return JSONResponse({"roomId": room_id})


@app.get("/rooms/{room_id}")
def get_room(room_id: str):
    room = store.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@app.post("/rooms/{room_id}/join")
def join_room(room_id: str, jr: JoinRequest):
    player_id = store.join_room(room_id, jr.display_name)
    if not player_id:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"playerId": player_id}


@app.post("/rooms/{room_id}/start_hand")
async def start_hand(room_id: str, seed: Optional[int] = None):
    room = store.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    players = room.get("players", [])
    if len(players) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 players to start")
    # create a session from current players (preserve join order)
    players_list = [(p["id"], p.get("stack", room["config"].get("starting_stack", 2000))) for p in players]
    session = Session(players_list,
                      dealer_index=0,
                      small_blind=room["config"].get("blinds", {}).get("small", 5),
                      big_blind=room["config"].get("blinds", {}).get("big", 10))
    session.start_hand(seed)
    store.set_session(room_id, session)

    # map hole cards to players by session order
    mapping = {p.id: p.hole_cards for p in session.players}
    board = session.community
    hand_id = session.hand_id

    # maintain lightweight current_hand for compatibility
    hand_data = {"handId": hand_id, "seed": seed, "holeCards": mapping, "board": board}
    store.set_current_hand(room_id, hand_data)

    # broadcast hand start (public) and send personalized hole cards
    await manager.broadcast(room_id, {"type": "hand:start", "handId": hand_id, "playerCount": session.player_count})
    for pid, cards in mapping.items():
        await manager.send_personal(room_id, pid, {"type": "deal:hole", "handId": hand_id, "cards": cards})

    return {"handId": hand_id}


@app.get("/rooms/{room_id}/session/{player_id}/legal_actions")
def get_legal_actions(room_id: str, player_id: str):
    """Return the legal actions for a given player in the active session.

    This is a simple dev/testing endpoint used by the frontend to render
    allowed action buttons for the current player.
    """
    session = store.get_session(room_id)
    if not session:
        raise HTTPException(status_code=404, detail="No active session")
    idx = next((i for i, p in enumerate(session.players) if p.id == player_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Player not in session")
    return {"actions": session.legal_actions(idx)}


@app.websocket("/ws/{room_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, client_id: str):
    await manager.connect(room_id, client_id, websocket)
    try:
        # On connect, send a state_sync (public + personal placeholders)
        room = store.get_room(room_id)
        await websocket.send_json({
            "type": "state_sync",
            "publicView": {"roomId": room_id, "playerCount": len(room["players"]) if room else 0},
            "personalView": {"clientId": client_id},
        })

        while True:
            data = await websocket.receive_json()
            # handle client messages by type
            msg_type = data.get("type")
            if msg_type == "action:post":
                payload = data.get("payload", {})
                action_type = payload.get("actionType") or payload.get("action")

                # if a session exists, validate the action against legal actions
                session = store.get_session(room_id)
                if session:
                    idx = next((i for i, p in enumerate(session.players) if p.id == client_id), None)
                    if idx is None:
                        await websocket.send_json({"type": "error", "code": "unknown_player", "message": "Player not in session"})
                        continue
                    allowed = [a.get("action") for a in session.legal_actions(idx)]
                    if action_type not in allowed:
                        await websocket.send_json({"type": "error", "code": "illegal_action", "message": "Action not allowed", "allowed": allowed})
                        continue

                    # apply action (amount optional)
                    amount = payload.get("amount")
                    session.apply_action(idx, action_type, amount)
                    store.set_session(room_id, session)

                    # broadcast action
                    msg = {"type": "action:posted", "from": client_id, "payload": payload}
                    await manager.broadcast(room_id, msg)

                    # if betting round completes, deal next community and broadcast
                    if session.is_betting_round_complete():
                        session.deal_next_community()
                        store.set_session(room_id, session)
                        await manager.broadcast(room_id, {"type": "community:update", "community": session.community, "street": session.street})
                        # announce next to act after dealing
                        if session.current_player_idx is not None:
                            next_pid = session.players[session.current_player_idx].id
                            # start turn timer for next player
                            session.start_turn_timer()
                            store.set_session(room_id, session)
                            await manager.broadcast(room_id, {"type": "turn:change", "next": next_pid})
                    else:
                        # advance to next player who still needs to act this round
                        session.advance_to_next_to_act()
                        store.set_session(room_id, session)
                        if session.current_player_idx is not None:
                            next_pid = session.players[session.current_player_idx].id
                            session.start_turn_timer()
                            store.set_session(room_id, session)
                            await manager.broadcast(room_id, {"type": "turn:change", "next": next_pid})
                else:
                    # legacy behavior: no session present, broadcast unvalidated action
                    msg = {"type": "action:posted", "from": client_id, "payload": payload}
                    await manager.broadcast(room_id, msg)
            else:
                # unknown messages echoed as warnings
                await websocket.send_json({"type": "warning", "message": "unknown message type"})

    except WebSocketDisconnect:
        manager.disconnect(room_id, client_id)
    except Exception:
        manager.disconnect(room_id, client_id)


@app.post("/rooms/{room_id}/force_timeout")
async def force_timeout(room_id: str):
    """Test-only endpoint to force the current player's timeout (auto-fold).

    This exists to allow tests to simulate a timeout without waiting real time.
    """
    session = store.get_session(room_id)
    if not session:
        raise HTTPException(status_code=404, detail="No active session")
    folded_id = session.force_timeout()
    store.set_session(room_id, session)
    if folded_id:
        # await broadcast so TestClient-connected websockets receive messages
        await manager.broadcast(room_id, {"type": "action:posted", "from": folded_id, "payload": {"action": "fold", "auto": True}})
        if session.current_player_idx is not None:
            next_pid = session.players[session.current_player_idx].id
            await manager.broadcast(room_id, {"type": "turn:change", "next": next_pid})
        return {"folded": folded_id}
    return {"folded": None}
