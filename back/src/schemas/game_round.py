from datetime import datetime
from pydantic import BaseModel

from src.models.game_round import RoundStatus


class GameRoundResponse(BaseModel):
    id: int
    round_number: int
    target_number: int | None = None  # Only shown after round ends
    status: RoundStatus
    started_at: datetime
    finished_at: datetime | None

    model_config = {"from_attributes": True}


class RoundResultPlayer(BaseModel):
    player_id: int
    player_name: str
    guess: int | None
    distance: int | None
    points_earned: int


class RoundResultResponse(BaseModel):
    round_number: int
    target_number: int
    results: list[RoundResultPlayer]

