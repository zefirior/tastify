import pytest
from httpx import AsyncClient

from src.models import RoomStatus


class TestCreateRoom:
    async def test_create_room_success(self, client: AsyncClient):
        """Test creating a new room."""
        response = await client.post(
            "/api/rooms",
            json={"player_name": "TestPlayer"},
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "room" in data
        assert "player_id" in data
        assert data["room"]["status"] == RoomStatus.WAITING.value
        assert len(data["room"]["code"]) == 6
        assert data["room"]["players"][0]["name"] == "TestPlayer"
        assert data["room"]["players"][0]["is_host"] is True

    async def test_create_room_empty_name(self, client: AsyncClient):
        """Test creating a room with empty player name."""
        response = await client.post(
            "/api/rooms",
            json={"player_name": ""},
        )
        
        assert response.status_code == 422


class TestJoinRoom:
    async def test_join_room_success(self, client: AsyncClient):
        """Test joining an existing room."""
        # Create a room first
        create_response = await client.post(
            "/api/rooms",
            json={"player_name": "Host"},
        )
        room_code = create_response.json()["room"]["code"]
        
        # Join the room
        join_response = await client.post(
            f"/api/rooms/{room_code}/join",
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
            "/api/rooms/XXXXXX/join",
            json={"player_name": "Player"},
        )
        
        assert response.status_code == 404


class TestGetRoom:
    async def test_get_room_success(self, client: AsyncClient):
        """Test getting room state."""
        # Create a room first
        create_response = await client.post(
            "/api/rooms",
            json={"player_name": "Host"},
        )
        room_code = create_response.json()["room"]["code"]
        
        # Get room state
        get_response = await client.get(f"/api/rooms/{room_code}")
        
        assert get_response.status_code == 200
        assert get_response.json()["code"] == room_code

    async def test_get_nonexistent_room(self, client: AsyncClient):
        """Test getting a room that doesn't exist."""
        response = await client.get("/api/rooms/XXXXXX")
        
        assert response.status_code == 404


class TestStartGame:
    async def test_start_game_success(self, client: AsyncClient):
        """Test starting a game as host."""
        # Create room
        create_response = await client.post(
            "/api/rooms",
            json={"player_name": "Host"},
        )
        data = create_response.json()
        room_code = data["room"]["code"]
        host_id = data["player_id"]
        
        # Add another player
        await client.post(
            f"/api/rooms/{room_code}/join",
            json={"player_name": "Player2"},
        )
        
        # Start game
        start_response = await client.post(
            f"/api/rooms/{room_code}/start?player_id={host_id}",
        )
        
        assert start_response.status_code == 200
        assert start_response.json()["status"] == RoomStatus.PLAYING.value
        assert start_response.json()["current_round_number"] == 1

    async def test_start_game_not_host(self, client: AsyncClient):
        """Test starting a game as non-host."""
        # Create room
        create_response = await client.post(
            "/api/rooms",
            json={"player_name": "Host"},
        )
        room_code = create_response.json()["room"]["code"]
        
        # Add another player
        join_response = await client.post(
            f"/api/rooms/{room_code}/join",
            json={"player_name": "Player2"},
        )
        player2_id = join_response.json()["player_id"]
        
        # Try to start game as non-host
        start_response = await client.post(
            f"/api/rooms/{room_code}/start?player_id={player2_id}",
        )
        
        assert start_response.status_code == 400

    async def test_start_game_not_enough_players(self, client: AsyncClient):
        """Test starting a game with only one player."""
        # Create room
        create_response = await client.post(
            "/api/rooms",
            json={"player_name": "Host"},
        )
        data = create_response.json()
        room_code = data["room"]["code"]
        host_id = data["player_id"]
        
        # Try to start game
        start_response = await client.post(
            f"/api/rooms/{room_code}/start?player_id={host_id}",
        )
        
        assert start_response.status_code == 400


class TestSubmitGuess:
    async def test_submit_guess_success(self, client: AsyncClient):
        """Test submitting a guess."""
        # Create room with 2 players and start game
        create_response = await client.post(
            "/api/rooms",
            json={"player_name": "Host"},
        )
        data = create_response.json()
        room_code = data["room"]["code"]
        host_id = data["player_id"]
        
        await client.post(
            f"/api/rooms/{room_code}/join",
            json={"player_name": "Player2"},
        )
        
        await client.post(
            f"/api/rooms/{room_code}/start?player_id={host_id}",
        )
        
        # Submit guess
        guess_response = await client.post(
            f"/api/rooms/{room_code}/guess",
            json={"player_id": host_id, "guess": 50},
        )
        
        assert guess_response.status_code == 200
        
        # Verify guess was saved (player's current_guess should be set)
        player = next(p for p in guess_response.json()["players"] if p["id"] == host_id)
        assert player["current_guess"] == 50

    async def test_submit_guess_game_not_started(self, client: AsyncClient):
        """Test submitting a guess before game starts."""
        # Create room
        create_response = await client.post(
            "/api/rooms",
            json={"player_name": "Host"},
        )
        data = create_response.json()
        room_code = data["room"]["code"]
        host_id = data["player_id"]
        
        # Try to submit guess
        guess_response = await client.post(
            f"/api/rooms/{room_code}/guess",
            json={"player_id": host_id, "guess": 50},
        )
        
        assert guess_response.status_code == 400

