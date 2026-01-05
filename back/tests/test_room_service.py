import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import RoomStatus, RoundStatus
from src.services.room_service import RoomService


class TestRoomService:
    async def test_create_room(self, session: AsyncSession):
        """Test creating a room."""
        service = RoomService(session)
        room, player = await service.create_room("TestHost")
        
        assert room.code is not None
        assert len(room.code) == 6
        assert room.status == RoomStatus.WAITING
        assert room.host_id == player.id
        assert player.name == "TestHost"
        assert player.is_host is True

    async def test_join_room(self, session: AsyncSession):
        """Test joining a room."""
        service = RoomService(session)
        room, host = await service.create_room("Host")
        await session.commit()
        
        result = await service.join_room(room.code, "Player2")
        
        assert result is not None
        room, player = result
        assert player.name == "Player2"
        assert player.is_host is False
        assert player.room_id == room.id

    async def test_join_nonexistent_room(self, session: AsyncSession):
        """Test joining a room that doesn't exist."""
        service = RoomService(session)
        result = await service.join_room("XXXXXX", "Player")
        
        assert result is None

    async def test_start_game(self, session: AsyncSession):
        """Test starting a game."""
        service = RoomService(session)
        room, host = await service.create_room("Host")
        await session.commit()
        
        await service.join_room(room.code, "Player2")
        await session.commit()
        
        # Reload room
        room = await service.get_room_by_code(room.code)
        game_round = await service.start_game(room, host.id)
        
        assert game_round is not None
        assert game_round.round_number == 1
        assert game_round.status == RoundStatus.ACTIVE
        assert room.status == RoomStatus.PLAYING

    async def test_submit_guess(self, session: AsyncSession):
        """Test submitting a guess."""
        service = RoomService(session)
        room, host = await service.create_room("Host")
        await session.commit()
        
        await service.join_room(room.code, "Player2")
        await session.commit()
        
        room = await service.get_room_by_code(room.code)
        await service.start_game(room, host.id)
        await session.commit()
        
        room = await service.get_room_by_code(room.code)
        success = await service.submit_guess(room, host.id, 42)
        
        assert success is True
        player = next(p for p in room.players if p.id == host.id)
        assert player.current_guess == 42

    async def test_finish_round(self, session: AsyncSession):
        """Test finishing a round and calculating scores."""
        service = RoomService(session)
        room, host = await service.create_room("Host")
        await session.commit()
        
        result = await service.join_room(room.code, "Player2")
        player2 = result[1]
        await session.commit()
        
        room = await service.get_room_by_code(room.code)
        await service.start_game(room, host.id)
        await session.commit()
        
        room = await service.get_room_by_code(room.code)
        current_round = room.rounds[0]
        target = current_round.target_number
        
        # Host guesses exactly right
        await service.submit_guess(room, host.id, target)
        # Player2 guesses 10 off
        await service.submit_guess(room, player2.id, target + 10)
        await session.commit()
        
        room = await service.get_room_by_code(room.code)
        results = await service.finish_round(room)
        
        assert len(results) == 2
        # Host should win (10 points)
        host_result = next(r for r in results if r["player_id"] == host.id)
        assert host_result["points_earned"] == 10
        assert host_result["distance"] == 0

