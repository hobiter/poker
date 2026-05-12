import uuid
from typing import Dict, List, Optional

from .models import RoomCreate


class InMemoryStore:
    """Simple in-memory store for rooms and players (Phase 2 scaffold).

    Not persistent — suitable for dev, tests, and early integration.
    """
    def __init__(self):
        self.rooms: Dict[str, Dict] = {}

    def create_room(self, rc: RoomCreate) -> str:
        room_id = str(uuid.uuid4())
        room = {
            "id": room_id,
            "name": rc.name or "Room",
            "seat_count": rc.seat_count,
            "config": rc.dict(),
            "players": [],
        }
        self.rooms[room_id] = room
        return room_id

    def get_room(self, room_id: str) -> Optional[Dict]:
        return self.rooms.get(room_id)

    def join_room(self, room_id: str, display_name: str) -> Optional[str]:
        room = self.rooms.get(room_id)
        if not room:
            return None
        seat_number = len(room["players"]) + 1
        player_id = str(uuid.uuid4())
        player = {
            "id": player_id,
            "display_name": display_name,
            "seat_number": seat_number,
            "stack": room["config"].get("starting_stack", 2000),
        }
        room["players"].append(player)
        return player_id

    def set_current_hand(self, room_id: str, hand_data: dict) -> None:
        room = self.rooms.get(room_id)
        if not room:
            return
        room["current_hand"] = hand_data

    def get_current_hand(self, room_id: str) -> Optional[dict]:
        room = self.rooms.get(room_id)
        if not room:
            return None
        return room.get("current_hand")

    def set_session(self, room_id: str, session) -> None:
        room = self.rooms.get(room_id)
        if not room:
            return
        room["session"] = session

    def get_session(self, room_id: str):
        room = self.rooms.get(room_id)
        if not room:
            return None
        return room.get("session")
