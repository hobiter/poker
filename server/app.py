from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import uuid

from .models import RoomCreate, JoinRequest
from .storage import InMemoryStore
from .ws_manager import ConnectionManager

from engine.deck import Deck

app = FastAPI(title="Poker - Phase 2 Scaffold")

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

    deck = Deck()
    deck.shuffle(seed)
    hole_cards = deck.deal_hole_cards(len(players), 2)
    board = deck.draw(3) + deck.draw(1) + deck.draw(1)
    hand_id = str(uuid.uuid4())
    # map hole cards to players by join order
    mapping = {p["id"]: hole_cards[i] for i, p in enumerate(players)}
    hand_data = {"handId": hand_id, "seed": seed, "holeCards": mapping, "board": board}
    store.set_current_hand(room_id, hand_data)

    # broadcast hand start (public) and send personalized hole cards
    await manager.broadcast(room_id, {"type": "hand:start", "handId": hand_id, "playerCount": len(players)})
    for pid, cards in mapping.items():
        await manager.send_personal(room_id, pid, {"type": "deal:hole", "handId": hand_id, "cards": cards})

    return {"handId": hand_id}


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
                # Validate and broadcast action posted
                msg = {"type": "action:posted", "from": client_id, "payload": data.get("payload")}
                await manager.broadcast(room_id, msg)
            else:
                # unknown messages echoed as warnings
                await websocket.send_json({"type": "warning", "message": "unknown message type"})

    except WebSocketDisconnect:
        manager.disconnect(room_id, client_id)
    except Exception:
        manager.disconnect(room_id, client_id)
