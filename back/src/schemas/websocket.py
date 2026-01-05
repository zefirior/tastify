from typing import Any, Literal
from pydantic import BaseModel


class WSMessage(BaseModel):
    event: str
    data: dict[str, Any]


class WSEventType:
    ROOM_UPDATED = "room_updated"
    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    GAME_STARTED = "game_started"
    ROUND_STARTED = "round_started"
    ROUND_FINISHED = "round_finished"
    GAME_FINISHED = "game_finished"
    GUESS_SUBMITTED = "guess_submitted"
    ROOM_CLOSED = "room_closed"
    ERROR = "error"

