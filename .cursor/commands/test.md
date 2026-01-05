# Running Tests

## Prerequisites

- **Docker** must be running (backend tests use testcontainers for PostgreSQL)
- **uv** installed for Python dependency management
- **Node.js** and **npm** installed for frontend

## All Tests (Backend + Frontend)

```bash
./scripts/run-tests.sh
```

## Backend Only

Using the script:
```bash
./scripts/run-tests.sh --backend-only
```

Or directly with pytest:
```bash
cd back
uv sync --all-extras  # Install dev dependencies
uv run pytest -v
```

### Run specific test file:
```bash
cd back && uv run pytest tests/test_game_timer.py -v
```

### Run specific test:
```bash
cd back && uv run pytest "tests/test_game_timer.py::TestGameTimerJob::test_all_players_voted_returns_true_when_all_guessed" -v
```

### Run with output (useful for debugging):
```bash
cd back && uv run pytest -v -s
```

## Frontend Only

Using the script:
```bash
./scripts/run-tests.sh --frontend-only
```

Or directly:
```bash
cd front
npm ci  # if node_modules not installed
npm run build
```

## E2E Tests (Playwright)

```bash
./scripts/run-tests.sh --e2e
```

Or directly:
```bash
cd front
npm run test
```

