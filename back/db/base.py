from contextlib import asynccontextmanager
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic_settings import BaseSettings
from sqlalchemy import JSON, ForeignKey, UniqueConstraint, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

Session = async_sessionmaker(expire_on_commit=False)


class UserRole(str, Enum):
    PLAYER = 'PLAYER'
    ADMIN = 'ADMIN'


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
async def create_session():
    session = Session()
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


class User(Base):
    __tablename__ = "user"


class Room(Base):
    __tablename__ = "room"

    code: Mapped[str] = mapped_column(nullable=False, unique=True)
    game_state: Mapped[dict[str, Any]] = mapped_column(type_=JSON, nullable=False)
    created_by: Mapped[UUID] = mapped_column(ForeignKey(User.pk), nullable=False)


class RoomUser(Base):
    __tablename__ = "room_user"

    room_uuid: Mapped[UUID] = mapped_column(ForeignKey(Room.pk), nullable=False)
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey(User.pk), nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    nickname: Mapped[str] = mapped_column(nullable=False)

    user: Mapped[User] = relationship(User, uselist=False)

    __table_args__ = (
        UniqueConstraint(room_uuid, user_uuid),
    )


async def _create_all(engine: AsyncEngine, drop: bool = False):
    async with engine.begin() as conn:
        if drop:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _main():
    settings = DBSettings(echo=True)
    engine = settings.setup()
    await _create_all(engine, drop=True)

    room_code = '1234'
    room_stmt = select(Room).where(Room.code == room_code)
    async with create_session() as session:
        if not (room := (await session.execute(room_stmt)).scalar()):
            user = User(pk=str(uuid4()))
            session.add(user)
            await session.flush()
            room = Room(code=room_code, game_state={'is_active': True}, created_by=user.pk)
            session.add(room)
            await session.flush()
        print(f'{room.pk = }')


if __name__ == '__main__':
    import asyncio

    asyncio.run(_main())
