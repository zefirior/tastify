from collections.abc import AsyncIterator

import pytest_asyncio
import spotipy
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import AsyncTestClient, create_async_test_client
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from back.db.base import Session, create_all, create_session
from back.server.app import get_routes


@pytest_asyncio.fixture(scope='session')
async def postgres():
    with PostgresContainer('postgres:16', driver='asyncpg') as postgres:
        async_engine = create_async_engine(postgres.get_connection_url(), echo=True)
        await create_all(async_engine, drop=True)
        yield postgres


@pytest_asyncio.fixture(autouse=True)
async def db(postgres: PostgresContainer):
    async_engine = create_async_engine(postgres.get_connection_url(), echo=True)
    Session.configure(bind=async_engine)
    yield async_engine
    await async_engine.dispose()


@pytest_asyncio.fixture()
def create_test_session(postgres):
    async_engine = create_async_engine(postgres.get_connection_url(), echo=True)
    session_maker = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    yield create_session(session_maker)


@pytest_asyncio.fixture()
def spotify_client(mocker):
    return mocker.create_autospec(spotipy.Spotify)


@pytest_asyncio.fixture()
async def test_client(spotify_client) -> AsyncIterator[AsyncTestClient[Litestar]]:
    async with create_async_test_client(
        route_handlers=get_routes(), dependencies={'spotify_client': Provide(lambda: spotify_client)}
    ) as client:
        yield client
