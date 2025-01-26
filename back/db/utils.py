from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from back.consts import ROUND_DURATION_SEC
from back.db.base import Room, RoomUser, UserRole, Round


def dump_room(user_uuid: str, room: Room, room_users: list[RoomUser]) -> dict[str, Any]:
    role = None
    if room.created_by == user_uuid:
        role = UserRole.ADMIN.value
    elif room_user := next((ru for ru in room_users if ru.user_uuid == user_uuid), None):
        role = room_user.role

    if room.rounds:
        cur: Round = room.rounds[-1]  # type: ignore
        current_round = {
            'number': cur.number,
            'timeleft': (get_utc_now() - cur.started_at).total_seconds() + ROUND_DURATION_SEC,
            'group_id': cur.group_id,
            'submissions': cur.submissions,
            'current_stage': cur.current_stage,
            'results': cur.results,
            'suggester': {
                'nickname': cur.suggester.nickname,
                'uuid': cur.suggester.user_uuid,
            },
        }
    else:
        current_round = None

    total_results = defaultdict(int)
    for r in room.rounds:
        for player, score in r.results.items():
            total_results[player] += score

    return {
        'code': room.code,
        'role': role,
        'status': room.status,
        'players': [
            {
                'uuid': room_user.user_uuid,
                'nickname': room_user.nickname,
                'score': room.game_state.get('points', {}).get(room_user.user_uuid, 0),
                'role': room_user.role,
            }
            for room_user in room_users
        ],
        'game_state': {
            'rounds': 0,  # todo put actual number of total rounds in the game
            'current_round': current_round,
            'total_results': total_results,
        },
    }


def get_utc_now():
    dt = datetime.now(timezone.utc)
    return dt.replace(tzinfo=timezone.utc)
