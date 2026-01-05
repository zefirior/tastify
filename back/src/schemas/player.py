from datetime import datetime
from pydantic import BaseModel


class PlayerResponse(BaseModel):
    id: int
    name: str
    score: int
    current_guess: int | None
    is_host: bool
    connected_at: datetime

    model_config = {"from_attributes": True}


class GuessRequest(BaseModel):
    player_id: int
    guess: int

