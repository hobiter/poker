from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # room_id -> client_id -> WebSocket
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, room_id: str, client_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        conns = self.active_connections.setdefault(room_id, {})
        conns[client_id] = websocket

    def disconnect(self, room_id: str, client_id: str) -> None:
        conns = self.active_connections.get(room_id, {})
        if client_id in conns:
            del conns[client_id]

    async def send_personal(self, room_id: str, client_id: str, message: Dict) -> None:
        conns = self.active_connections.get(room_id, {})
        ws = conns.get(client_id)
        if ws:
            await ws.send_json(message)

    async def broadcast(self, room_id: str, message: Dict) -> None:
        conns = list(self.active_connections.get(room_id, {}).values())
        for conn in conns:
            try:
                await conn.send_json(message)
            except Exception:
                # swallow; disconnect will be cleaned up elsewhere
                pass
