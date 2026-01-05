"""Tests for GuessNumberTimerJob functionality."""

from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch

import pytest

from src.games.guess_number import GuessNumberTimerJob
from src.games.registry import game_registry
from src.models import Room, RoomStatus, GameRound, RoundStatus
from src.services.room_service import RoomService


class TestGuessNumberTimerJob:
    """Tests for GuessNumberTimerJob."""

    @pytest.mark.asyncio
    async def test_all_players_voted_returns_true_when_all_guessed(self, session):
        """Should return True when all players have submitted guesses."""
        service = RoomService(session)
        room, player1 = await service.create_room("Player1")
        room, player2 = await service.join_room(room.code, "Player2")

        # Both players have guessed
        player1.current_guess = 50
        player2.current_guess = 75

        job = GuessNumberTimerJob()
        assert job._all_players_voted(room) is True

    @pytest.mark.asyncio
    async def test_all_players_voted_returns_false_when_not_all_guessed(
        self, session
    ):
        """Should return False when not all players have submitted guesses."""
        service = RoomService(session)
        room, player1 = await service.create_room("Player1")
        room, player2 = await service.join_room(room.code, "Player2")

        # Only one player has guessed
        player1.current_guess = 50
        player2.current_guess = None

        job = GuessNumberTimerJob()
        assert job._all_players_voted(room) is False

    @pytest.mark.asyncio
    async def test_all_players_voted_returns_false_for_empty_players(
        self, session
    ):
        """Should return False when room has no players."""
        # Create a mock room with empty players list
        room = Room()
        room.players = []

        job = GuessNumberTimerJob()
        assert job._all_players_voted(room) is False

    @pytest.mark.asyncio
    async def test_finish_round_broadcasts_results(self, session):
        """Should broadcast round results when finishing a round."""
        service = RoomService(session)
        room, player1 = await service.create_room("Player1")
        room, player2 = await service.join_room(room.code, "Player2")

        # Start game and submit guesses
        await service.start_game(room, player1.id)
        player1.current_guess = 50
        player2.current_guess = 75

        # Get the current round
        game_round = room.rounds[0]

        job = GuessNumberTimerJob()

        with patch(
            "src.games.guess_number.jobs.timer.connection_manager.broadcast_to_room",
            new_callable=AsyncMock
        ) as mock_broadcast:
            await job._finish_round(session, game_round)

            # Should broadcast ROUND_FINISHED
            mock_broadcast.assert_called_once()
            call_args = mock_broadcast.call_args
            assert call_args[0][0] == room.code
            # WSEventType is passed but broadcast_to_room may convert it
            event_type = call_args[0][1]
            event_value = (
                event_type.value if hasattr(event_type, 'value') else event_type
            )
            assert event_value == "round_finished"

    @pytest.mark.asyncio
    async def test_round_finishes_early_when_all_voted(self, session):
        """Should finish round immediately when all players have voted."""
        service = RoomService(session)
        room, player1 = await service.create_room("Player1")
        room, player2 = await service.join_room(room.code, "Player2")

        # Start game
        await service.start_game(room, player1.id)

        # Submit guesses (all players voted)
        player1.current_guess = 50
        player2.current_guess = 75
        await session.flush()

        job = GuessNumberTimerJob()

        with patch(
            "src.games.guess_number.jobs.timer.connection_manager.broadcast_to_room",
            new_callable=AsyncMock
        ) as mock_broadcast:
            await job._check_and_finish_rounds(session)

            # Round should be finished despite time not expiring
            mock_broadcast.assert_called()
            call_args = mock_broadcast.call_args
            event_type = call_args[0][1]
            event_value = (
                event_type.value if hasattr(event_type, 'value') else event_type
            )
            assert event_value == "round_finished"

    @pytest.mark.asyncio
    async def test_round_does_not_finish_early_when_not_all_voted(self, session):
        """Should NOT finish round early when not all players have voted."""
        service = RoomService(session)
        room, player1 = await service.create_room("Player1")
        room, player2 = await service.join_room(room.code, "Player2")

        # Start game
        await service.start_game(room, player1.id)

        # Only one player has voted
        player1.current_guess = 50
        player2.current_guess = None
        await session.flush()

        job = GuessNumberTimerJob()

        with patch(
            "src.games.guess_number.jobs.timer.connection_manager.broadcast_to_room",
            new_callable=AsyncMock
        ) as mock_broadcast:
            await job._check_and_finish_rounds(session)

            # Round should NOT be finished yet
            mock_broadcast.assert_not_called()

    @pytest.mark.asyncio
    async def test_next_round_starts_after_delay(self, session):
        """Should start next round after between_rounds_delay_seconds."""
        service = RoomService(session)
        room, player1 = await service.create_room("Player1")
        room, player2 = await service.join_room(room.code, "Player2")

        # Start game and finish first round
        await service.start_game(room, player1.id)
        player1.current_guess = 50
        player2.current_guess = 75

        # Finish the round
        await service.finish_round(room)
        await session.flush()

        # Set finished_at to be enough time ago
        game_round = room.rounds[0]
        game_settings = game_registry.get_settings(room.game_type)
        between_rounds_delay = game_settings.get("between_rounds_delay_seconds", 5)
        game_round.finished_at = datetime.now(timezone.utc) - timedelta(
            seconds=between_rounds_delay + 1
        )
        await session.flush()

        job = GuessNumberTimerJob()

        with patch(
            "src.games.guess_number.jobs.timer.connection_manager.broadcast_to_room",
            new_callable=AsyncMock
        ) as mock_broadcast:
            await job._check_and_start_rounds(session)

            # Should broadcast ROUND_STARTED
            mock_broadcast.assert_called()
            call_args = mock_broadcast.call_args
            event_type = call_args[0][1]
            event_value = (
                event_type.value if hasattr(event_type, 'value') else event_type
            )
            assert event_value == "round_started"

    @pytest.mark.asyncio
    async def test_next_round_does_not_start_before_delay(self, session):
        """Should NOT start next round before delay has passed."""
        service = RoomService(session)
        room, player1 = await service.create_room("Player1")
        room, player2 = await service.join_room(room.code, "Player2")

        # Start game and finish first round
        await service.start_game(room, player1.id)
        player1.current_guess = 50
        player2.current_guess = 75

        # Finish the round
        await service.finish_round(room)
        await session.flush()

        # finished_at is now, so delay hasn't passed yet
        job = GuessNumberTimerJob()

        with patch(
            "src.games.guess_number.jobs.timer.connection_manager.broadcast_to_room",
            new_callable=AsyncMock
        ) as mock_broadcast:
            await job._check_and_start_rounds(session)

            # Should NOT broadcast yet
            mock_broadcast.assert_not_called()

    @pytest.mark.asyncio
    async def test_game_finishes_after_3_rounds(self, session):
        """Should finish game after 3 rounds."""
        service = RoomService(session)
        room, player1 = await service.create_room("Player1")
        room, player2 = await service.join_room(room.code, "Player2")

        # Start game
        await service.start_game(room, player1.id)

        # Simulate completing 3 rounds
        room.current_round_number = 3
        game_round = room.rounds[0]
        game_round.round_number = 3
        game_round.status = RoundStatus.FINISHED
        game_settings = game_registry.get_settings(room.game_type)
        between_rounds_delay = game_settings.get("between_rounds_delay_seconds", 5)
        game_round.finished_at = datetime.now(timezone.utc) - timedelta(
            seconds=between_rounds_delay + 1
        )
        await session.flush()

        job = GuessNumberTimerJob()

        with patch(
            "src.games.guess_number.jobs.timer.connection_manager.broadcast_to_room",
            new_callable=AsyncMock
        ) as mock_broadcast:
            await job._check_and_start_rounds(session)

            # Should broadcast GAME_FINISHED, not ROUND_STARTED
            mock_broadcast.assert_called()
            call_args = mock_broadcast.call_args
            event_type = call_args[0][1]
            event_value = (
                event_type.value if hasattr(event_type, 'value') else event_type
            )
            assert event_value == "game_finished"

            # Room status should be FINISHED
            assert room.status == RoomStatus.FINISHED
