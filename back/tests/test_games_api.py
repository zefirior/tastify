"""Tests for the new games API."""

import pytest
from httpx import AsyncClient

from src.models import RoomStatus


class TestGamesInfo:
    """Tests for GET /api/games endpoint."""

    async def test_list_games(self, client: AsyncClient):
        """Test listing available games."""
        response = await client.get("/api/games")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "games" in data
        assert "default_game" in data
        assert data["default_game"] == "guess_number"
        
        # Should have at least guess_number game
        assert len(data["games"]) >= 1
        
        guess_number = next((g for g in data["games"] if g["game_type"] == "guess_number"), None)
        assert guess_number is not None
        assert guess_number["display_name"] == "Guess the Number"
        assert guess_number["is_default"] is True
        assert "actions" in guess_number


class TestCreateRoom:
    """Tests for POST /api/games/{game}/rooms endpoint."""

    async def test_create_room_success(self, client: AsyncClient):
        """Test creating a room for guess_number game."""
        response = await client.post(
            "/api/games/guess_number/rooms",
            json={"player_name": "TestPlayer"},
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "room" in data
        assert "player_id" in data
        assert data["room"]["game_type"] == "guess_number"
        assert data["room"]["status"] == RoomStatus.WAITING.value
        assert len(data["room"]["code"]) == 6
        assert data["room"]["players"][0]["name"] == "TestPlayer"
        assert data["room"]["players"][0]["is_host"] is True

    async def test_create_room_invalid_game(self, client: AsyncClient):
        """Test creating a room for non-existent game."""
        response = await client.post(
            "/api/games/nonexistent_game/rooms",
            json={"player_name": "TestPlayer"},
        )
        
        assert response.status_code == 404

    async def test_create_room_empty_name(self, client: AsyncClient):
        """Test creating a room with empty player name."""
        response = await client.post(
            "/api/games/guess_number/rooms",
            json={"player_name": ""},
        )
        
        assert response.status_code == 422


class TestJoinRoom:
    """Tests for POST /api/games/{game}/rooms/{code}/join endpoint."""

    async def test_join_room_success(self, client: AsyncClient):
        """Test joining an existing room."""
        # Create a room first
        create_response = await client.post(
            "/api/games/guess_number/rooms",
            json={"player_name": "Host"},
        )
        room_code = create_response.json()["room"]["code"]
        
        # Join the room
        join_response = await client.post(
            f"/api/games/guess_number/rooms/{room_code}/join",
            json={"player_name": "Player2"},
        )
        
        assert join_response.status_code == 200
        data = join_response.json()
        
        assert len(data["room"]["players"]) == 2
        assert data["room"]["players"][1]["name"] == "Player2"
        assert data["room"]["players"][1]["is_host"] is False

    async def test_join_nonexistent_room(self, client: AsyncClient):
        """Test joining a room that doesn't exist."""
        response = await client.post(
            "/api/games/guess_number/rooms/XXXXXX/join",
            json={"player_name": "Player"},
        )
        
        assert response.status_code == 404

    async def test_join_wrong_game_type(self, client: AsyncClient):
        """Test joining a room with wrong game type in URL."""
        # Create a guess_number room
        create_response = await client.post(
            "/api/games/guess_number/rooms",
            json={"player_name": "Host"},
        )
        room_code = create_response.json()["room"]["code"]
        
        # Try to join with wrong game type (even though it's not enabled)
        response = await client.post(
            f"/api/games/nonexistent/rooms/{room_code}/join",
            json={"player_name": "Player2"},
        )
        
        # Should fail because game type is not found
        assert response.status_code == 404


class TestGetRoomState:
    """Tests for GET /api/games/{game}/rooms/{code} endpoint."""

    async def test_get_room_success(self, client: AsyncClient):
        """Test getting room state."""
        # Create a room first
        create_response = await client.post(
            "/api/games/guess_number/rooms",
            json={"player_name": "Host"},
        )
        room_code = create_response.json()["room"]["code"]
        
        # Get room state
        get_response = await client.get(f"/api/games/guess_number/rooms/{room_code}")
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["code"] == room_code
        assert data["game_type"] == "guess_number"

    async def test_get_nonexistent_room(self, client: AsyncClient):
        """Test getting a room that doesn't exist."""
        response = await client.get("/api/games/guess_number/rooms/XXXXXX")
        
        assert response.status_code == 404


class TestExecuteAction:
    """Tests for POST /api/games/{game}/rooms/{code}/actions endpoint."""

    async def test_start_game_action(self, client: AsyncClient):
        """Test starting a game via action endpoint."""
        # Create room
        create_response = await client.post(
            "/api/games/guess_number/rooms",
            json={"player_name": "Host"},
        )
        data = create_response.json()
        room_code = data["room"]["code"]
        host_id = data["player_id"]
        
        # Add another player
        await client.post(
            f"/api/games/guess_number/rooms/{room_code}/join",
            json={"player_name": "Player2"},
        )
        
        # Start game via action
        action_response = await client.post(
            f"/api/games/guess_number/rooms/{room_code}/actions?player_id={host_id}",
            json={"action": "start_game"},
        )
        
        assert action_response.status_code == 200
        action_data = action_response.json()
        
        assert action_data["success"] is True
        assert action_data["room"]["status"] == RoomStatus.PLAYING.value
        assert action_data["room"]["current_round_number"] == 1

    async def test_submit_guess_action(self, client: AsyncClient):
        """Test submitting a guess via action endpoint."""
        # Create room with 2 players and start game
        create_response = await client.post(
            "/api/games/guess_number/rooms",
            json={"player_name": "Host"},
        )
        data = create_response.json()
        room_code = data["room"]["code"]
        host_id = data["player_id"]
        
        await client.post(
            f"/api/games/guess_number/rooms/{room_code}/join",
            json={"player_name": "Player2"},
        )
        
        # Start game
        await client.post(
            f"/api/games/guess_number/rooms/{room_code}/actions?player_id={host_id}",
            json={"action": "start_game"},
        )
        
        # Submit guess
        guess_response = await client.post(
            f"/api/games/guess_number/rooms/{room_code}/actions?player_id={host_id}",
            json={"action": "submit_guess", "guess": 50},
        )
        
        assert guess_response.status_code == 200
        guess_data = guess_response.json()
        
        assert guess_data["success"] is True
        
        # Verify guess was saved
        player = next(p for p in guess_data["room"]["players"] if p["id"] == host_id)
        assert player["current_guess"] == 50

    async def test_start_game_not_host(self, client: AsyncClient):
        """Test starting a game as non-host."""
        # Create room
        create_response = await client.post(
            "/api/games/guess_number/rooms",
            json={"player_name": "Host"},
        )
        room_code = create_response.json()["room"]["code"]
        
        # Add another player
        join_response = await client.post(
            f"/api/games/guess_number/rooms/{room_code}/join",
            json={"player_name": "Player2"},
        )
        player2_id = join_response.json()["player_id"]
        
        # Try to start game as non-host
        action_response = await client.post(
            f"/api/games/guess_number/rooms/{room_code}/actions?player_id={player2_id}",
            json={"action": "start_game"},
        )
        
        assert action_response.status_code == 200
        assert action_response.json()["success"] is False

    async def test_start_game_not_enough_players(self, client: AsyncClient):
        """Test starting a game with only one player."""
        # Create room
        create_response = await client.post(
            "/api/games/guess_number/rooms",
            json={"player_name": "Host"},
        )
        data = create_response.json()
        room_code = data["room"]["code"]
        host_id = data["player_id"]
        
        # Try to start game
        action_response = await client.post(
            f"/api/games/guess_number/rooms/{room_code}/actions?player_id={host_id}",
            json={"action": "start_game"},
        )
        
        assert action_response.status_code == 200
        assert action_response.json()["success"] is False

    async def test_submit_guess_before_game_starts(self, client: AsyncClient):
        """Test submitting a guess before game starts."""
        # Create room
        create_response = await client.post(
            "/api/games/guess_number/rooms",
            json={"player_name": "Host"},
        )
        data = create_response.json()
        room_code = data["room"]["code"]
        host_id = data["player_id"]
        
        # Try to submit guess
        guess_response = await client.post(
            f"/api/games/guess_number/rooms/{room_code}/actions?player_id={host_id}",
            json={"action": "submit_guess", "guess": 50},
        )
        
        assert guess_response.status_code == 200
        assert guess_response.json()["success"] is False

    async def test_invalid_action(self, client: AsyncClient):
        """Test submitting an invalid action."""
        # Create room
        create_response = await client.post(
            "/api/games/guess_number/rooms",
            json={"player_name": "Host"},
        )
        data = create_response.json()
        room_code = data["room"]["code"]
        host_id = data["player_id"]
        
        # Submit invalid action
        response = await client.post(
            f"/api/games/guess_number/rooms/{room_code}/actions?player_id={host_id}",
            json={"action": "invalid_action"},
        )
        
        # Should fail validation
        assert response.status_code == 422

    async def test_player_not_in_room(self, client: AsyncClient):
        """Test executing action when player is not in room."""
        # Create room
        create_response = await client.post(
            "/api/games/guess_number/rooms",
            json={"player_name": "Host"},
        )
        room_code = create_response.json()["room"]["code"]
        
        # Try to execute action with non-existent player
        response = await client.post(
            f"/api/games/guess_number/rooms/{room_code}/actions?player_id=99999",
            json={"action": "start_game"},
        )
        
        assert response.status_code == 403

