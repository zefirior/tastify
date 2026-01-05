"""Base classes for game implementations."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, TYPE_CHECKING

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from src.models import Room, GameRound


class GameAction(BaseModel):
    """Base schema for game actions. Each game defines its own action types."""

    action: str  # Action type identifier


class ActionResult(BaseModel):
    """Result of executing a game action."""

    success: bool
    message: str | None = None
    data: dict[str, Any] | None = None
    broadcast_event: str | None = None  # WebSocket event to broadcast
    broadcast_data: dict[str, Any] | None = None  # Data to broadcast


class RoundResult(BaseModel):
    """Result of finishing a round."""

    round_number: int
    target_number: int | None = None  # Game-specific, may not apply to all games
    results: list[dict[str, Any]]  # Player results


class BaseGame(ABC):
    """
    Abstract base class for all games.
    
    Each game implementation must:
    1. Define a unique game_type identifier
    2. Provide display_name for UI
    3. Implement game-specific action handling
    4. Implement round creation and finishing logic
    """

    @property
    @abstractmethod
    def game_type(self) -> str:
        """Unique identifier for this game type (e.g., 'guess_number')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name for the game."""
        pass

    @property
    @abstractmethod
    def action_schema(self) -> type[GameAction]:
        """Pydantic schema class for validating game actions."""
        pass

    @abstractmethod
    def get_available_actions(self) -> list[dict[str, Any]]:
        """
        Return list of available actions for Swagger documentation.
        Each action should include: name, description, required fields.
        """
        pass

    @abstractmethod
    async def create_round(
        self,
        room: "Room",
        session: AsyncSession,
        settings: dict[str, Any] | None = None,
    ) -> "GameRound":
        """
        Create a new game round.
        
        Args:
            room: The room to create a round for
            session: Database session
            settings: Game-specific settings from config
            
        Returns:
            The created GameRound
        """
        pass

    @abstractmethod
    async def execute_action(
        self,
        room: "Room",
        player_id: int,
        action: GameAction,
        session: AsyncSession,
    ) -> ActionResult:
        """
        Execute a game-specific action.
        
        Args:
            room: The room where the action is executed
            player_id: ID of the player executing the action
            action: The action to execute (validated against action_schema)
            session: Database session
            
        Returns:
            ActionResult with success status and optional data to broadcast
        """
        pass

    @abstractmethod
    async def finish_round(
        self,
        room: "Room",
        session: AsyncSession,
    ) -> RoundResult:
        """
        Finish the current round and calculate results.
        
        Args:
            room: The room to finish the round for
            session: Database session
            
        Returns:
            RoundResult with scores and player results
        """
        pass

    async def on_player_join(
        self,
        room: "Room",
        player_id: int,
        session: AsyncSession,
    ) -> None:
        """
        Called when a player joins the room.
        Override for game-specific join logic.
        """
        pass

    async def on_player_leave(
        self,
        room: "Room",
        player_id: int,
        session: AsyncSession,
    ) -> None:
        """
        Called when a player leaves the room.
        Override for game-specific leave logic.
        """
        pass

    def can_start_game(self, room: "Room") -> tuple[bool, str | None]:
        """
        Check if the game can be started.
        
        Returns:
            Tuple of (can_start, error_message)
        """
        if len(room.players) < 2:
            return False, "At least 2 players required to start"
        return True, None

