from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.db.base import Base
from src.models import Room, Player, GameRound  # noqa: F401 - Register models


@pytest.fixture(scope="session")
def postgres_container():
    """Start a PostgreSQL container for tests."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def database_url(postgres_container) -> str:
    """Get the database URL for the test container."""
    url = postgres_container.get_connection_url()
    # Testcontainers may return postgresql+psycopg2:// or postgresql://
    # We need to use asyncpg for async support
    url = url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    url = url.replace("postgresql://", "postgresql+asyncpg://")
    return url


@pytest_asyncio.fixture(scope="session")
async def test_engine(database_url):
    """Create a test database engine."""
    engine = create_async_engine(database_url, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with savepoint rollback after each test."""
    async with test_engine.connect() as conn:
        # Start a transaction that will be rolled back at the end
        trans = await conn.begin()
        
        async_session = async_sessionmaker(
            bind=conn, 
            class_=AsyncSession, 
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        
        async with async_session() as session:
            yield session
        
        # Rollback the outer transaction to discard all changes from the test
        await trans.rollback()


@pytest_asyncio.fixture
async def client(test_engine, monkeypatch) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client with mocked database."""
    from src import db
    from src.main import app
    
    # Create a session maker for this test
    test_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Mock the session maker
    monkeypatch.setattr(db.database, "async_session_maker", test_session_maker)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

