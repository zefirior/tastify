#!/bin/bash

# Tastify Development Environment Startup Script
# Starts all services: PostgreSQL, Backend, Frontend

source "$(dirname "$0")/common.sh"

print_separator
echo -e "${CYAN}  Tastify Development Environment${NC}"
print_separator
echo ""

# Parse arguments
FORCE_KILL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --force|-f)
            FORCE_KILL=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -f, --force    Force kill processes on ports before starting"
            echo "  -h, --help     Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Step 1: Kill processes on required ports
log_step "Checking ports..."
PORTS="5173 8000"

for port in $PORTS; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        if [ "$FORCE_KILL" = true ]; then
            log_info "Killing process on port $port (PID: $pid)"
            kill -9 $pid 2>/dev/null
        else
            log_warning "Port $port is in use (PID: $pid). Use --force to kill it."
            exit 1
        fi
    fi
done
log_success "Ports are available"
echo ""

# Step 2: Check and start Docker
log_step "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    log_info "Starting Docker..."
    open -a Docker
    
    # Wait for Docker to start
    max_wait=30
    waited=0
    while ! docker info > /dev/null 2>&1; do
        if [ $waited -ge $max_wait ]; then
            log_error "Docker did not start in time. Please start Docker manually."
            exit 1
        fi
        sleep 1
        waited=$((waited + 1))
        echo -n "."
    done
    echo ""
fi
log_success "Docker is running"
echo ""

# Step 3: Start PostgreSQL
log_step "Starting PostgreSQL..."
cd "$DOCKER_DIR"
docker compose -f docker-compose.yaml up postgres -d

# Wait for PostgreSQL to be ready
log_info "Waiting for PostgreSQL to be ready..."
max_wait=30
waited=0
while ! docker compose -f docker-compose.yaml exec -T postgres pg_isready -U tastify > /dev/null 2>&1; do
    if [ $waited -ge $max_wait ]; then
        log_error "PostgreSQL did not become ready in time."
        exit 1
    fi
    sleep 1
    waited=$((waited + 1))
    echo -n "."
done
echo ""
log_success "PostgreSQL is ready"
echo ""

# Step 4: Run migrations
log_step "Running database migrations..."
cd "$BACK_DIR"
uv run alembic upgrade head
log_success "Migrations applied"
echo ""

# Step 5: Start Backend
log_step "Starting Backend..."
cd "$BACK_DIR"
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 2
if ! wait_for_service "http://localhost:8000/docs" 15; then
    log_error "Backend failed to start"
    exit 1
fi
echo ""

# Step 6: Start Frontend
log_step "Starting Frontend..."
cd "$FRONT_DIR"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    log_info "Installing frontend dependencies..."
    npm ci
fi

npm run dev &
FRONTEND_PID=$!

# Wait for frontend to be ready
sleep 2
if ! wait_for_service "http://localhost:5173" 15; then
    log_error "Frontend failed to start"
    exit 1
fi
echo ""

# Summary
print_separator
echo -e "${CYAN}  Tastify is running!${NC}"
print_separator
echo ""
echo -e "  ${GREEN}Frontend:${NC}  http://localhost:5173"
echo -e "  ${GREEN}Backend:${NC}   http://localhost:8000"
echo -e "  ${GREEN}API Docs:${NC}  http://localhost:8000/docs"
echo -e "  ${GREEN}Database:${NC}  localhost:5432"
echo ""
echo -e "  Press ${YELLOW}Ctrl+C${NC} to stop all services"
print_separator

# Wait for interrupt
trap "echo ''; log_info 'Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker compose -f $DOCKER_DIR/docker-compose.yaml stop postgres; exit 0" INT TERM

# Keep script running
wait

