# Tastify

A collaborative game for sharing music tastes. Players suggest bands and earn points based on the popularity of their choices.

**Current MVP**: Guess the Number - Players try to guess a randomly generated number. The closest guess wins!

## Architecture

```
/back           - FastAPI backend (Python)
/front          - React frontend (TypeScript)
/docker         - Docker Compose files
/scripts        - Utility scripts
```

## Tech Stack

### Backend
- Python 3.12+
- FastAPI + Uvicorn
- SQLAlchemy (async) + asyncpg
- Alembic (migrations)
- PostgreSQL
- pytest + testcontainers

### Frontend
- React 19 + TypeScript
- Vite
- MobX (state management)
- TailwindCSS v4
- Playwright (E2E tests)

## Getting Started

### Prerequisites
- Docker & Docker Compose

### Local Development

**Start everything with Docker Compose**:
```bash
docker compose -f docker/docker-compose.yaml up --build
```

**Open the app**: http://localhost:5173

The setup includes:
- PostgreSQL database
- Backend with hot-reload
- Frontend with hot-reload

To stop:
```bash
docker compose -f docker/docker-compose.yaml down
```

### Manual Setup (without Docker)

If you prefer running services manually:

1. **Start PostgreSQL only**:
   ```bash
   docker compose -f docker/docker-compose.yaml up postgres -d
   ```

2. **Setup Backend**:
   ```bash
   cd back
   uv sync
   uv run alembic upgrade head
   uv run uvicorn src.main:app --reload
   ```

3. **Setup Frontend**:
   ```bash
   cd front
   npm install
   npm run dev
   ```

### Running Tests

```bash
# Run all tests
./scripts/run-tests.sh

# Backend only
./scripts/run-tests.sh --backend-only

# Frontend only
./scripts/run-tests.sh --frontend-only

# Include E2E tests
./scripts/run-tests.sh --e2e
```

## Game Flow

1. Player creates a room and becomes the host
2. Other players join using the 6-character room code
3. Host starts the game (minimum 2 players)
4. Each round:
   - A target number (1-100) is generated
   - Players have 30 seconds to submit their guesses
   - Points are awarded: 1st = 10pts, 2nd = 5pts, 3rd = 3pts, others = 1pt
5. After 3 rounds, the player with the most points wins

## API Endpoints

- `POST /api/rooms` - Create a new room
- `POST /api/rooms/{code}/join` - Join a room
- `GET /api/rooms/{code}` - Get room state
- `POST /api/rooms/{code}/start` - Start the game (host only)
- `POST /api/rooms/{code}/guess` - Submit a guess
- `WS /api/rooms/{code}/ws` - WebSocket for real-time updates

## WebSocket Events

- `player_joined` / `player_left` - Player connection changes
- `game_started` - Game has begun
- `round_started` / `round_finished` - Round lifecycle
- `game_finished` - Game complete with final standings
- `guess_submitted` - A player submitted their guess

## Deployment

The project deploys automatically via GitHub Actions on push to `main`.

```bash
# Manual deployment using Docker Compose
docker compose -f docker/remote.docker-compose.yaml up --build -d
```

## License

MIT
