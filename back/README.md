# Tastify Backend

FastAPI backend for the Tastify multiplayer game.

## Quick Start

```bash
# With Docker (recommended)
docker compose -f ../docker/docker-compose.yaml up --build

# Manual
uv sync
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
```

## API Docs

When running, visit: http://localhost:8000/docs

