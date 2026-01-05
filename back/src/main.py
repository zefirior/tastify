import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.rooms import router as rooms_router
from src.api.websocket import router as ws_router
from src.jobs.game_timer import GameTimerJob
from src.jobs.room_cleanup import RoomCleanupJob
from src.services import connection_manager, games_storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect games_storage to connection_manager
    games_storage.set_connection_manager(connection_manager)
    
    # Start background tasks
    game_timer_job = GameTimerJob()
    room_cleanup_job = RoomCleanupJob()
    
    tasks = [
        asyncio.create_task(game_timer_job.run()),
        asyncio.create_task(room_cleanup_job.run()),
        asyncio.create_task(games_storage.start()),
    ]
    
    yield
    
    # Cleanup
    games_storage.stop()
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Tastify API",
    description="Backend for Tastify - collaborative music taste game",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rooms_router, prefix="/api/rooms", tags=["rooms"])
app.include_router(ws_router, prefix="/api/rooms", tags=["websocket"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
