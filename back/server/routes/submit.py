from litestar import Response, post
from litestar.exceptions import HTTPException
from sqlalchemy.orm.attributes import flag_modified

from back.db.base import RoomStatus, RoundStages, create_session
from back.db.query_utils import end_round, get_last_round, get_room, get_room_users


@post('/room/{room_code:str}/submit/group')
async def submit_group(room_code: str, user_uuid: str, group_id: str) -> Response:
    async with create_session() as session:
        room = await get_room(
            session,
            room_code,
            forbidden_created_by=user_uuid,
            required_status=RoomStatus.RUNNING,
            lock=True,
        )

        current_round = await get_last_round(
            room.rounds,
            required_suggester=user_uuid,
            required_stage=RoundStages.GROUP_SUGGESTION,
        )

        current_round.group_id = group_id
        current_round.current_stage = RoundStages.TRACKS_SUBMISSION

    return Response(status_code=200, content={})


@post('/room/{room_code:str}/submit/track')
async def submit_track(room_code: str, user_uuid: str, track_id: str | None = None) -> Response:
    async with create_session() as session:
        room = await get_room(
            session,
            room_code,
            forbidden_created_by=user_uuid,
            required_status=RoomStatus.RUNNING,
            lock=True,
        )

        if not room.rounds:
            raise RuntimeError('Unreachable')
        current_round = await get_last_round(
            room.rounds,  # type: ignore
            forbidden_suggester=user_uuid,
            required_stage=RoundStages.TRACKS_SUBMISSION,
        )
        if user_uuid in current_round.submissions:
            raise HTTPException(status_code=400, detail='User already submitted')

        current_round.submissions[user_uuid] = track_id
        flag_modified(current_round, 'submissions')

        players = await get_room_users(session, room_code)
        if len(current_round.submissions) == len(players) - 1:
            await end_round(current_round)

    return Response(status_code=200, content={})
