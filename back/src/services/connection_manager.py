import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections for rooms."""

    def __init__(self):
        # room_code -> {player_id -> WebSocket}
        self.connections: dict[str, dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_code: str, player_id: int):
        """Accept and store a WebSocket connection."""
        await websocket.accept()
        if room_code not in self.connections:
            self.connections[room_code] = {}
        self.connections[room_code][player_id] = websocket

    def disconnect(self, room_code: str, player_id: int):
        """Remove a WebSocket connection."""
        if room_code in self.connections:
            self.connections[room_code].pop(player_id, None)
            if not self.connections[room_code]:
                del self.connections[room_code]

    async def send_to_player(self, room_code: str, player_id: int, event: str, data: dict[str, Any]):
        """Send a message to a specific player."""
        if room_code in self.connections and player_id in self.connections[room_code]:
            message = json.dumps({"event": event, "data": data})
            try:
                await self.connections[room_code][player_id].send_text(message)
            except Exception:
                self.disconnect(room_code, player_id)

    async def broadcast_to_room(self, room_code: str, event: str, data: dict[str, Any], exclude_player_id: int | None = None):
        """Broadcast a message to all players in a room."""
        if room_code not in self.connections:
            return

        message = json.dumps({"event": event, "data": data})
        disconnected = []

        for player_id, websocket in self.connections[room_code].items():
            if exclude_player_id is not None and player_id == exclude_player_id:
                continue
            try:
                await websocket.send_text(message)
            except Exception:
                disconnected.append(player_id)

        # Clean up disconnected clients
        for player_id in disconnected:
            self.disconnect(room_code, player_id)

    def get_connected_players(self, room_code: str) -> list[int]:
        """Get list of connected player IDs for a room."""
        return list(self.connections.get(room_code, {}).keys())


# Global connection manager instance
connection_manager = ConnectionManager()

