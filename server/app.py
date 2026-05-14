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
from fastapi.staticfiles import StaticFiles
from pathlib import Path

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


def _session_public_view(session: Session) -> dict:
    pots = session.compute_pots()
    return {
        "handId": session.hand_id,
        "street": session.street,
        "community": session.community,
        "pot": sum(pot["amount"] for pot in pots),
        "pots": pots,
        "currentTurn": session.players[session.current_player_idx].id if session.current_player_idx is not None else None,
        "players": [
            {
                "id": player.id,
                "seat": player.seat,
                "stack": player.stack,
                "contribution": player.contribution,
                "roundContribution": player.round_contribution,
                "status": player.status,
                "hasHoleCards": bool(player.hole_cards),
            }
            for player in session.players
        ],
        "timeRemaining": session.time_remaining(),
    }


def _room_public_view(room_id: str, room: dict) -> dict:
    session = room.get("session")
    return {
        "roomId": room_id,
        "name": room.get("name"),
        "seatCount": room.get("seat_count"),
        "playerCount": len(room.get("players", [])),
        "players": room.get("players", []),
        "config": room.get("config", {}),
        "session": _session_public_view(session) if session else None,
    }


def _personal_view(session: Optional[Session], client_id: str) -> dict:
    if not session:
        return {"clientId": client_id}
    player = next((p for p in session.players if p.id == client_id), None)
    return {
        "clientId": client_id,
        "holeCards": player.hole_cards if player else None,
    }


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.post("/rooms")
def create_room(rc: RoomCreate):
    room_id = store.create_room(rc)
    return JSONResponse({"roomId": room_id})


@app.get("/rooms/{room_id}")
def get_room(room_id: str):
    room = store.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return _room_public_view(room_id, room)


@app.get("/rooms/{room_id}/state")
def get_room_state(room_id: str, client_id: Optional[str] = None):
    room = store.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    session = store.get_session(room_id)
    return {
        "type": "state_sync",
        "publicView": _room_public_view(room_id, room),
        "personalView": _personal_view(session, client_id) if client_id else None,
    }


@app.post("/rooms/{room_id}/join")
def join_room(room_id: str, jr: JoinRequest):
    room = store.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if len(room.get("players", [])) >= room.get("seat_count", 0):
        raise HTTPException(status_code=400, detail="Room is full")
    player_id = store.join_room(room_id, jr.display_name)
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
    await manager.broadcast(room_id, {"type": "state:update", "publicView": _room_public_view(room_id, room)})

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
        room = store.get_room(room_id)
        session = store.get_session(room_id)
        await websocket.send_json({
            "type": "state_sync",
            "publicView": _room_public_view(room_id, room) if room else {"roomId": room_id, "playerCount": 0},
            "personalView": _personal_view(session, client_id),
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
                    try:
                        session.apply_action(idx, action_type, amount)
                    except ValueError as exc:
                        await websocket.send_json({
                            "type": "error",
                            "code": "invalid_action",
                            "message": str(exc),
                            "allowed": session.legal_actions(idx),
                        })
                        continue
                    store.set_session(room_id, session)

                    # broadcast action
                    msg = {"type": "action:posted", "from": client_id, "payload": payload}
                    await manager.broadcast(room_id, msg)
                    room = store.get_room(room_id)
                    if room:
                        await manager.broadcast(room_id, {"type": "state:update", "publicView": _room_public_view(room_id, room)})

                    # if betting round completes, deal next community and broadcast
                    if session.is_betting_round_complete():
                        finished = session.settle_if_hand_over()
                        if not finished:
                            session.deal_next_community()
                            finished = session.settle_if_hand_over()
                        room = store.get_room(room_id)
                        store.set_session(room_id, session)
                        if finished:
                            await manager.broadcast(room_id, finished)
                        else:
                            await manager.broadcast(room_id, {"type": "community:update", "community": session.community, "street": session.street})
                            # announce next to act after dealing
                            if session.current_player_idx is not None:
                                next_pid = session.players[session.current_player_idx].id
                                # start turn timer for next player
                                session.start_turn_timer()
                                store.set_session(room_id, session)
                                await manager.broadcast(room_id, {"type": "turn:change", "next": next_pid})
                        room = store.get_room(room_id)
                        if room:
                            await manager.broadcast(room_id, {"type": "state:update", "publicView": _room_public_view(room_id, room)})
                    else:
                        # advance to next player who still needs to act this round
                        session.advance_to_next_to_act()
                        store.set_session(room_id, session)
                        room = store.get_room(room_id)
                        if room:
                            await manager.broadcast(room_id, {"type": "state:update", "publicView": _room_public_view(room_id, room)})
                        if session.current_player_idx is not None:
                            next_pid = session.players[session.current_player_idx].id
                            session.start_turn_timer()
                            store.set_session(room_id, session)
                            await manager.broadcast(room_id, {"type": "turn:change", "next": next_pid})
                            room = store.get_room(room_id)
                            if room:
                                await manager.broadcast(room_id, {"type": "state:update", "publicView": _room_public_view(room_id, room)})
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
    finished = session.settle_if_hand_over()
    store.set_session(room_id, session)
    if folded_id:
        # await broadcast so TestClient-connected websockets receive messages
        await manager.broadcast(room_id, {"type": "action:posted", "from": folded_id, "payload": {"action": "fold", "auto": True}})
        if finished:
            await manager.broadcast(room_id, finished)
        room = store.get_room(room_id)
        if room:
            await manager.broadcast(room_id, {"type": "state:update", "publicView": _room_public_view(room_id, room)})
        if not finished and session.current_player_idx is not None:
            next_pid = session.players[session.current_player_idx].id
            await manager.broadcast(room_id, {"type": "turn:change", "next": next_pid})
        return {"folded": folded_id}
    return {"folded": None}


# If a built frontend exists at `frontend/dist`, serve it as static files
# after API and WebSocket routes have been registered.
dist_path = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if dist_path.exists():
    app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="frontend")
