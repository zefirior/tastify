from typing import Any

from back.db.base import Room, RoomUser, UserRole


def dump_room(user_uuid: str, room: Room, room_users: list[RoomUser]) -> dict[str, Any]:
    role = None
    if room.created_by == user_uuid:
        role = UserRole.ADMIN.value
    elif room_user := next((ru for ru in room_users if ru.user_uuid == user_uuid), None):
        role = room_user.role

    return {
        'code': room.code,
        'role': role,
        'players': [
            {
                'uuid': room_user.user_uuid,
                'nickname': room_user.nickname,
                'score': room.game_state.get('points', {}).get(room_user.user_uuid, 0),
                'role': room_user.role,
            }
            for room_user in room_users
        ],
    }
