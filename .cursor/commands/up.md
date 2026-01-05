# Start Development Environment

Starts all Tastify services: PostgreSQL, Backend, and Frontend.

## Quick Start

```bash
./scripts/up.sh --force
```

## Options

| Flag | Description |
|------|-------------|
| `-f, --force` | Kill processes on ports 5173, 8000 before starting |
| `-h, --help` | Show help message |

## What it does

1. **Clears ports** - Kills any processes using ports 5173 (frontend) and 8000 (backend)
2. **Starts Docker** - Launches Docker if not running
3. **Starts PostgreSQL** - Runs postgres container via docker-compose
4. **Runs migrations** - Applies Alembic migrations to the database
5. **Starts Backend** - Uvicorn server with hot reload on port 8000
6. **Starts Frontend** - Vite dev server on port 5173

## Services

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

## Stop Services

Press `Ctrl+C` in the terminal to stop all services gracefully.

