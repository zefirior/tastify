from datetime import datetime
from pydantic import BaseModel, Field

from src.models.room import RoomStatus
from src.schemas.player import PlayerResponse
from src.schemas.game_round import GameRoundResponse


class CreateRoomRequest(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50)


class JoinRoomRequest(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50)


class RoomResponse(BaseModel):
    id: int
    code: str
    status: RoomStatus
    host_id: int | None
    current_round_number: int
    created_at: datetime
    updated_at: datetime
    players: list[PlayerResponse] = []
    current_round: GameRoundResponse | None = None

    model_config = {"from_attributes": True}


class CreateRoomResponse(BaseModel):
    room: RoomResponse
    player_id: int


class JoinRoomResponse(BaseModel):
    room: RoomResponse
    player_id: int

