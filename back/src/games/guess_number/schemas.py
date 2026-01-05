"""Schemas for Guess the Number game actions."""

from enum import Enum
from typing import Literal

from pydantic import Field

from src.games.base import GameAction


class ActionType(str, Enum):
    """Available actions for Guess the Number game."""

    START_GAME = "start_game"
    SUBMIT_GUESS = "submit_guess"


class GuessNumberAction(GameAction):
    """
    Action schema for Guess the Number game.
    
    Actions:
    - start_game: Start the game (host only)
    - submit_guess: Submit a guess for the current round
    """

    action: ActionType
    guess: int | None = Field(
        default=None,
        ge=1,
        le=100,
        description="The guess value (required for submit_guess action)",
    )

