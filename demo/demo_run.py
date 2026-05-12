#!/usr/bin/env python3
"""Demo harness that exercises server flows using FastAPI TestClient.

Creates a room, joins two players, opens WebSocket connections, starts a hand,
posts an action, forces a timeout, and prints observed events.

Run:
    .venv/Scripts/python.exe demo/demo_run.py
"""
import os
import sys
# Ensure project root is on sys.path so `server` package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from fastapi.testclient import TestClient

from server.app import app


def pretty(m):
    return json.dumps(m, indent=2, sort_keys=True)


def main():
    client = TestClient(app)

    payload = {
        "seat_count": 6,
        "game_type": "no-limit",
        "blinds": {"small": 5, "big": 10},
        "starting_stack": 2000,
        "name": "Demo Room",
    }
    r = client.post("/rooms", json=payload)
    room_id = r.json().get("roomId")
    print("Created room:", room_id)

    r1 = client.post(f"/rooms/{room_id}/join", json={"display_name": "Alice"})
    p1 = r1.json().get("playerId")
    r2 = client.post(f"/rooms/{room_id}/join", json={"display_name": "Bob"})
    p2 = r2.json().get("playerId")
    print("Joined players:", p1, p2)

    with client.websocket_connect(f"/ws/{room_id}/{p1}") as ws1:
        msg = ws1.receive_json()
        print("ws1 initial:", pretty(msg))
        with client.websocket_connect(f"/ws/{room_id}/{p2}") as ws2:
            msg2 = ws2.receive_json()
            print("ws2 initial:", pretty(msg2))

            print("Starting hand...")
            rsh = client.post(f"/rooms/{room_id}/start_hand")
            print("start_hand response:", rsh.json())

            # each socket should receive a public hand:start and a personal deal:hole
            msgs1 = [ws1.receive_json(), ws1.receive_json()]
            msgs2 = [ws2.receive_json(), ws2.receive_json()]
            print("ws1 messages:")
            for m in msgs1:
                print(pretty(m))
            print("ws2 messages:")
            for m in msgs2:
                print(pretty(m))

            # Have second player post an action
            print("Player 2 posting action: call")
            ws2.send_json({"type": "action:post", "payload": {"actionType": "call"}})
            # read action broadcasts
            a1 = ws1.receive_json()
            a2 = ws2.receive_json()
            print("Observed broadcasts:")
            print(pretty(a1))
            print(pretty(a2))

            # Force a timeout (auto-fold) via test-only endpoint
            print("Forcing timeout (auto-fold) via API...")
            rft = client.post(f"/rooms/{room_id}/force_timeout")
            print("force_timeout response:", rft.json())

            # try to read follow-up events (up to 3)
            for i in range(3):
                try:
                    ev = ws1.receive_json()
                except Exception:
                    break
                print("Event:", pretty(ev))

    print("Demo complete.")


if __name__ == "__main__":
    main()
