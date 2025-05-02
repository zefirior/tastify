from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic_settings import BaseSettings
from sqlalchemy import BIGINT, JSON, DateTime, ForeignKey, UniqueConstraint, select, text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

Session = async_sessionmaker(expire_on_commit=False)


class RoomStatus(str, Enum):
    NEW = 'NEW'
    RUNNING = 'RUNNING'
    FINISHED = 'FINISHED'


class UserRole(str, Enum):
    PLAYER = 'PLAYER'
    ADMIN = 'ADMIN'


class RoundStages(str, Enum):
    GROUP_SUGGESTION = 'GROUP_SUGGESTION'
    TRACKS_SUBMISSION = 'TRACKS_SUBMISSION'
    END_ROUND = 'END_ROUND'


class DBSettings(BaseSettings):
    url: str = 'postgresql+asyncpg://postgres@localhost:5432/postgres'
    echo: bool = False

    class Config:
        env_prefix = 'DB_'

    def setup(self) -> AsyncEngine:
        async_engine = create_async_engine(self.url, echo=self.echo)
        Session.configure(bind=async_engine)
        return async_engine


@asynccontextmanager
async def create_session(sessionmaker=None):
    session = (sessionmaker or Session)()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


class Base(DeclarativeBase):
    pk: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))

    type_annotation_map = {
        int: BIGINT,
        datetime: DateTime(timezone=True),
    }


class User(Base):
    __tablename__ = 'user'


class Room(Base):
    __tablename__ = 'room'

    code: Mapped[str] = mapped_column(nullable=False, unique=True)
    game_state: Mapped[dict[str, Any]] = mapped_column(type_=JSON, nullable=False)
    created_by: Mapped[UUID] = mapped_column(ForeignKey(User.pk), nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default=RoomStatus.NEW.value)
    total_rounds: Mapped[int] = mapped_column(nullable=True)

    rounds: Mapped[list['Round']] = relationship(
        'Round', lazy='joined', back_populates='room', uselist=True, order_by=lambda: Round.number
    )


class RoomUser(Base):
    __tablename__ = 'room_user'

    room_uuid: Mapped[UUID] = mapped_column(ForeignKey(Room.pk), nullable=False)
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey(User.pk), nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    nickname: Mapped[str] = mapped_column(nullable=False)

    user: Mapped[User] = relationship(User, uselist=False)

    __table_args__ = (UniqueConstraint(room_uuid, user_uuid),)


class Round(Base):
    __tablename__ = 'round'

    room_uuid: Mapped[UUID] = mapped_column(ForeignKey(Room.pk), nullable=False)
    suggester_uuid: Mapped[UUID] = mapped_column(ForeignKey(RoomUser.pk), nullable=False)

    number: Mapped[int] = mapped_column(nullable=False)
    started_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text('now()'))
    group: Mapped[dict[str, str]] = mapped_column(type_=JSON, nullable=True)
    submissions: Mapped[dict[str, dict[str, str]]] = mapped_column(type_=JSON, nullable=True)
    current_stage: Mapped[str] = mapped_column(nullable=False)
    results: Mapped[dict[str, str]] = mapped_column(type_=JSON, nullable=True)

    room: Mapped[Room] = relationship(Room, uselist=False, lazy='joined', back_populates='rounds')
    suggester: Mapped[RoomUser] = relationship(RoomUser, uselist=False, lazy='joined')


async def create_all(engine: AsyncEngine, drop: bool = False):
    async with engine.begin() as conn:
        if drop:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _main():
    settings = DBSettings(echo=True)
    engine = settings.setup()

    await create_all(engine, drop=True)
    async with create_session() as session:
        room_code = '1234'
        room_stmt = select(Room).where(Room.code == room_code)
        if not (room := (await session.execute(room_stmt)).scalar()):
            user = User(pk='BBBB')
            session.add(user)
            await session.flush()
            room = Room(code=room_code, game_state={}, created_by=user.pk, pk='AAAA', status=RoomStatus.NEW.value)
            session.add(room)
            await session.flush()
        print(f'{room.pk = }')


if __name__ == '__main__':
    import asyncio

    asyncio.run(_main())
