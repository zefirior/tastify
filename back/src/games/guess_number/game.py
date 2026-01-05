"""Guess the Number game implementation."""

import random
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.games.base import BaseGame, GameAction, ActionResult, RoundResult
from src.games.guess_number.schemas import GuessNumberAction, ActionType
from src.models import Room, GameRound, RoomStatus, RoundStatus


class GuessNumberGame(BaseGame):
    """
    Guess the Number game.
    
    Players guess a randomly generated number (1-100).
    The player with the closest guess wins the round.
    Points are awarded based on ranking.
    """

    @property
    def game_type(self) -> str:
        return "guess_number"

    @property
    def display_name(self) -> str:
        return "Guess the Number"

    @property
    def action_schema(self) -> type[GameAction]:
        return GuessNumberAction

    def get_available_actions(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "start_game",
                "description": "Start the game (host only, requires at least 2 players)",
                "fields": [],
            },
            {
                "name": "submit_guess",
                "description": "Submit a guess for the current round",
                "fields": [
                    {
                        "name": "guess",
                        "type": "integer",
                        "required": True,
                        "min": 1,
                        "max": 100,
                        "description": "Your guess (1-100)",
                    }
                ],
            },
        ]

    async def create_round(
        self,
        room: Room,
        session: AsyncSession,
        settings: dict[str, Any] | None = None,
    ) -> GameRound:
        """Create a new round with a random target number."""
        settings = settings or {}
        min_target = settings.get("min_target", 1)
        max_target = settings.get("max_target", 100)

        target = random.randint(min_target, max_target)

        game_round = GameRound(
            round_number=room.current_round_number,
            target_number=target,
            status=RoundStatus.ACTIVE,
        )
        room.rounds.append(game_round)
        await session.flush()

        # Reset all player guesses for the new round
        for player in room.players:
            player.current_guess = None

        return game_round

    async def execute_action(
        self,
        room: Room,
        player_id: int,
        action: GameAction,
        session: AsyncSession,
    ) -> ActionResult:
        """Execute a game action."""
        if not isinstance(action, GuessNumberAction):
            return ActionResult(success=False, message="Invalid action schema")

        if action.action == ActionType.START_GAME:
            return await self._handle_start_game(room, player_id, session)
        elif action.action == ActionType.SUBMIT_GUESS:
            return await self._handle_submit_guess(room, player_id, action.guess, session)
        else:
            return ActionResult(success=False, message=f"Unknown action: {action.action}")

    async def _handle_start_game(
        self,
        room: Room,
        player_id: int,
        session: AsyncSession,
    ) -> ActionResult:
        """Handle start_game action."""
        # Check if player is host
        if room.host_id != player_id:
            return ActionResult(success=False, message="Only the host can start the game")

        # Check if game can be started
        can_start, error = self.can_start_game(room)
        if not can_start:
            return ActionResult(success=False, message=error)

        if room.status != RoomStatus.WAITING:
            return ActionResult(success=False, message="Game has already started")

        # Start the game
        room.status = RoomStatus.PLAYING
        room.current_round_number = 1

        # Create the first round
        # Get settings from registry (will be passed by router)
        game_round = await self.create_round(room, session)

        return ActionResult(
            success=True,
            message="Game started",
            data={"round_number": game_round.round_number},
            broadcast_event="game_started",
            broadcast_data=None,  # Room state will be broadcast separately
        )

    async def _handle_submit_guess(
        self,
        room: Room,
        player_id: int,
        guess: int | None,
        session: AsyncSession,
    ) -> ActionResult:
        """Handle submit_guess action."""
        if guess is None:
            return ActionResult(success=False, message="Guess is required")

        if room.status != RoomStatus.PLAYING:
            return ActionResult(success=False, message="Game is not in progress")

        # Find the player
        player = next((p for p in room.players if p.id == player_id), None)
        if player is None:
            return ActionResult(success=False, message="Player not found in room")

        # Check if there's an active round
        current_round = self._get_current_round(room)
        if current_round is None or current_round.status != RoundStatus.ACTIVE:
            return ActionResult(success=False, message="No active round")

        # Submit the guess
        player.current_guess = guess

        return ActionResult(
            success=True,
            message="Guess submitted",
            data={"guess": guess},
            broadcast_event="guess_submitted",
            broadcast_data={"player_id": player_id},
        )

    def _get_current_round(self, room: Room) -> GameRound | None:
        """Get the current active round for the room."""
        for r in room.rounds:
            if r.round_number == room.current_round_number and r.status == RoundStatus.ACTIVE:
                return r
        return None

    async def finish_round(
        self,
        room: Room,
        session: AsyncSession,
    ) -> RoundResult:
        """Finish the current round and calculate scores."""
        current_round = self._get_current_round(room)
        if current_round is None:
            return RoundResult(round_number=0, results=[])

        current_round.status = RoundStatus.FINISHED
        current_round.finished_at = datetime.now(timezone.utc)

        target = current_round.target_number
        results = []

        # Calculate distances and sort by closest
        player_distances = []
        for player in room.players:
            if player.current_guess is not None:
                distance = abs(player.current_guess - target)
                player_distances.append((player, distance))
            else:
                player_distances.append((player, None))

        # Sort by distance (None = didn't guess = worst)
        player_distances.sort(key=lambda x: (x[1] is None, x[1] if x[1] is not None else 0))

        # Award points: 1st place = 10, 2nd = 5, 3rd = 3, rest = 1 (if guessed)
        points_table = [10, 5, 3]
        for i, (player, distance) in enumerate(player_distances):
            if distance is not None:
                points = points_table[i] if i < len(points_table) else 1
                player.score += points
            else:
                points = 0

            results.append({
                "player_id": player.id,
                "player_name": player.name,
                "guess": player.current_guess,
                "distance": distance,
                "points_earned": points,
            })

        return RoundResult(
            round_number=current_round.round_number,
            target_number=target,
            results=results,
        )

