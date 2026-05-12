from pydantic import BaseModel
from typing import Optional


class Blinds(BaseModel):
    small: int
    big: int
    ante: Optional[int] = 0


class RoomCreate(BaseModel):
    name: Optional[str] = None
    seat_count: int
    game_type: str
    blinds: Blinds
    starting_stack: int


class JoinRequest(BaseModel):
    display_name: str
