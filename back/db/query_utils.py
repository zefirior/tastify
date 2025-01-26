from litestar.exceptions import HTTPException
from sqlalchemy import select, func, sql
from sqlalchemy.orm.attributes import flag_modified

from back.db.base import User, Room, RoomUser, RoomStatus, Round, RoundStages


async def get_or_create_user(session, user_uuid: str) -> User:
    user_stmt = select(User).where(User.pk == user_uuid)
    if not (user := (await session.execute(user_stmt)).scalar()):
        user = User(pk=user_uuid)
        session.add(user)
        await session.flush()
    return user


async def get_or_404_room(session, room_code: str) -> Room:
    room_stmt = select(Room).where(Room.code == room_code)
    if not (room := (await session.execute(room_stmt)).scalar()):
        raise HTTPException(status_code=404, detail="Room not found")
    return room


async def get_room_users(session, room_code) -> list[RoomUser]:
    room_user_stmt = select(RoomUser).join(Room).where(Room.code == room_code).order_by(RoomUser.user_uuid)
    room_users_result = await session.execute(room_user_stmt)
    return [item[0] for item in room_users_result.all()]


async def get_room(
    session,
    room_code,
    forbidden_created_by: str | None = None,
    required_created_by: str | None = None,
    required_status: RoomStatus | None = None,
    lock: bool = False,
) -> Room:
    room = await get_or_404_room(session, room_code)
    if forbidden_created_by and room.created_by == forbidden_created_by:
        raise HTTPException(status_code=403, detail="Forbidden")
    if required_created_by and room.created_by != required_created_by:
        raise HTTPException(status_code=403, detail="Forbidden")
    if required_status and room.status != required_status:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid room status: expected {required_status}, got {room.status}",
        )
    if lock:
        await acquire_advisory_lock(session, room)
    return room


async def get_last_round(
    rounds: list[Round],
    forbidden_suggester: str | None = None,
    required_suggester: str | None = None,
    required_stage: RoundStages | None = None,
) -> Round:
    if not rounds:
        raise RuntimeError("Unreachable")
    rnd = rounds[-1]

    if forbidden_suggester and rnd.suggester.user_uuid == forbidden_suggester:
        raise HTTPException(status_code=403, detail="Forbidden")
    if required_suggester and rnd.suggester.user_uuid != required_suggester:
        raise HTTPException(status_code=403, detail="Forbidden")
    if required_stage and rnd.current_stage != required_stage:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid round stage: expected {required_stage}, got {rnd.current_stage}",
        )
    return rnd


async def create_round(
    session,
    room_uuid: str,
    suggester_uuid: str,
    number: int,
    room_users: list[RoomUser],
):
    new_round = Round(
        room_uuid=room_uuid,
        suggester_uuid=suggester_uuid,
        number=number,
        submissions={},
        current_stage=RoundStages.GROUP_SUGGESTION,
        results={u.user_uuid: 0 for u in room_users},
    )
    session.add(new_round)


async def end_round(rnd: Round) -> None:
    rnd.current_stage = RoundStages.END_ROUND
    for player_uuid, track_id in rnd.submissions.items():
        if not track_id:
            continue
        rnd.results[player_uuid] += 1
        rnd.results[rnd.suggester.user_uuid] += 1
    flag_modified(rnd, "results")


async def acquire_advisory_lock(session, obj) -> None:
    key = func.hashtext(func.concat(obj.__tablename__, ':', obj.pk))
    await session.execute(sql.select(func.pg_advisory_lock(key)))
    await session.refresh(obj)
