import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.rooms import router as rooms_router
from src.api.websocket import router as ws_router
from src.games.guess_number import GuessNumberTimerJob
from src.jobs.room_cleanup import RoomCleanupJob
from src.services import connection_manager, games_storage

logger = logging.getLogger(__name__)


def init_game_registry() -> None:
    """
    Initialize the game registry.
    
    This must be called before creating routers that depend on the registry.
    Idempotent - will not re-initialize if already done.
    
    Raises:
        SystemExit: If configuration is invalid
    """
    from src.games.registry import game_registry, register_all_games
    
    # Skip if already initialized (e.g., by tests)
    if game_registry.is_initialized:
        return
    
    try:
        # Load config (validates YAML structure and rules)
        game_registry.load_config()
        
        # Register all game implementations
        register_all_games()
        
        # Validate that all enabled games have implementations
        game_registry.validate_registration()
        
        logger.info(
            f"Games configuration validated: "
            f"{len(game_registry.enabled_games)} games enabled, "
            f"default: {game_registry.default_game_type}"
        )
        
    except FileNotFoundError as e:
        logger.error(f"Games config file not found: {e}")
        raise SystemExit(1)
    except ValueError as e:
        logger.error(f"Invalid games configuration: {e}")
        raise SystemExit(1)
    except Exception as e:
        logger.error(f"Failed to initialize games: {e}")
        raise SystemExit(1)


# Initialize game registry before creating routers
# This is needed because the games router depends on the registry
init_game_registry()

# Now import and create the games router (after registry is initialized)
from src.games.registry import game_registry
from src.games.router import create_games_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect games_storage to connection_manager
    games_storage.set_connection_manager(connection_manager)
    
    # Start background tasks
    guess_number_timer_job = GuessNumberTimerJob()
    room_cleanup_job = RoomCleanupJob()
    
    tasks = [
        asyncio.create_task(guess_number_timer_job.run()),
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

# Legacy rooms API (kept for backward compatibility)
app.include_router(rooms_router, prefix="/api/rooms", tags=["rooms (legacy)"])
app.include_router(ws_router, prefix="/api/rooms", tags=["websocket (legacy)"])

# New games API
games_router = create_games_router()
app.include_router(games_router, prefix="/api/games", tags=["games"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/info")
async def api_info():
    """Get API information including available games."""
    return {
        "version": "0.1.0",
        "games": game_registry.get_all_games_info(),
        "default_game": game_registry.default_game_type,
    }
