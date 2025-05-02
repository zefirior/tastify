from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from back.consts import ROUND_DURATION_SEC
from back.db.base import Room, RoomStatus, RoomUser, Round, RoundStages, UserRole
from back.db.query_utils import acquire_advisory_lock, end_round


async def dump_room(session, user_uuid: str, room: Room, room_users: list[RoomUser]) -> dict[str, Any]:
    role = None
    if room.created_by == user_uuid:
        role = UserRole.ADMIN.value
    elif room_user := next((ru for ru in room_users if ru.user_uuid == user_uuid), None):
        role = room_user.role

    current_round = None
    if room.rounds:
        current_round = await _dump_round(room, room.rounds[-1], session)

    total_results = defaultdict(int)
    for r in room.rounds:
        for player, score in (r.results or {}).items():
            total_results[player] += score

    return {
        'code': room.code,
        'role': role,
        'status': room.status,
        'players': [
            {
                'uuid': room_user.user_uuid,
                'nickname': room_user.nickname,
                'role': room_user.role,
            }
            for room_user in room_users
        ],
        'game_state': {
            'rounds': room.total_rounds,
            'current_round': current_round,
            'total_results': total_results,
        },
    }


async def _dump_round(room: Room, rnd: Round, session) -> dict[str, Any]:
    if room.status == RoomStatus.FINISHED or rnd.current_stage == RoundStages.END_ROUND:
        timeleft = 0
    else:
        time_passed = int((get_utc_now() - rnd.started_at).total_seconds())
        if (timeleft := ROUND_DURATION_SEC - time_passed) < 0:
            timeleft = 0
            await acquire_advisory_lock(session, room)
            await end_round(rnd)

    return {
        'number': rnd.number,
        'timeleft': timeleft,
        'group': rnd.group,
        'submissions': rnd.submissions,
        'current_stage': rnd.current_stage,
        'results': rnd.results,
        'suggester': {
            'nickname': rnd.suggester.nickname,
            'uuid': rnd.suggester.user_uuid,
        },
    }


def get_utc_now():
    dt = datetime.now(timezone.utc)
    return dt.replace(tzinfo=timezone.utc)
