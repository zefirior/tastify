#!/bin/bash

# Tastify Test Runner
# Runs backend and frontend tests

source "$(dirname "$0")/common.sh"

# Parse arguments
RUN_BACKEND=true
RUN_FRONTEND=true
RUN_E2E=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            RUN_FRONTEND=false
            shift
            ;;
        --frontend-only)
            RUN_BACKEND=false
            shift
            ;;
        --e2e)
            RUN_E2E=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --backend-only   Run only backend tests"
            echo "  --frontend-only  Run only frontend tests"
            echo "  --e2e            Also run Playwright E2E tests"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_separator
echo -e "${CYAN}  Tastify Test Runner${NC}"
print_separator
echo ""

# Track results
BACKEND_RESULT=0
FRONTEND_RESULT=0
E2E_RESULT=0

# Run backend tests
if [ "$RUN_BACKEND" = true ]; then
    log_step "Running backend tests..."
    cd "$BACK_DIR"
    
    # Check if Docker is running (required for testcontainers)
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running! Backend tests require Docker for testcontainers."
        log_info "Please start Docker and try again."
        BACKEND_RESULT=1
    else
        # Check for uv
        if command_exists uv; then
            log_info "Using uv to run tests"
            # Ensure dev dependencies are installed
            uv sync --all-extras > /dev/null 2>&1
            if uv run pytest -v; then
                log_success "Backend tests passed!"
            else
                BACKEND_RESULT=1
                log_error "Backend tests failed!"
            fi
        else
            log_warning "uv not found, trying pytest directly"
            if pytest -v; then
                log_success "Backend tests passed!"
            else
                BACKEND_RESULT=1
                log_error "Backend tests failed!"
            fi
        fi
    fi
    
    echo ""
fi

# Run frontend tests (type check)
if [ "$RUN_FRONTEND" = true ]; then
    log_step "Running frontend type check..."
    cd "$FRONT_DIR"
    
    if [ ! -d "node_modules" ]; then
        log_info "Installing frontend dependencies..."
        npm ci
    fi
    
    if npm run build 2>&1; then
        log_success "Frontend build passed!"
    else
        FRONTEND_RESULT=1
        log_error "Frontend build failed!"
    fi
    
    echo ""
fi

# Run E2E tests
if [ "$RUN_E2E" = true ]; then
    log_step "Running Playwright E2E tests..."
    cd "$FRONT_DIR"
    
    if [ ! -d "node_modules" ]; then
        log_info "Installing frontend dependencies..."
        npm ci
    fi
    
    # Install Playwright browsers if needed
    npx playwright install --with-deps chromium
    
    if npm run test; then
        log_success "E2E tests passed!"
    else
        E2E_RESULT=1
        log_error "E2E tests failed!"
    fi
    
    echo ""
fi

# Summary
print_separator
echo -e "${CYAN}  Test Results Summary${NC}"
print_separator

if [ "$RUN_BACKEND" = true ]; then
    if [ $BACKEND_RESULT -eq 0 ]; then
        echo -e "  Backend:  ${GREEN}✓ PASSED${NC}"
    else
        echo -e "  Backend:  ${RED}✗ FAILED${NC}"
    fi
fi

if [ "$RUN_FRONTEND" = true ]; then
    if [ $FRONTEND_RESULT -eq 0 ]; then
        echo -e "  Frontend: ${GREEN}✓ PASSED${NC}"
    else
        echo -e "  Frontend: ${RED}✗ FAILED${NC}"
    fi
fi

if [ "$RUN_E2E" = true ]; then
    if [ $E2E_RESULT -eq 0 ]; then
        echo -e "  E2E:      ${GREEN}✓ PASSED${NC}"
    else
        echo -e "  E2E:      ${RED}✗ FAILED${NC}"
    fi
fi

print_separator

# Exit with error if any test failed
if [ $BACKEND_RESULT -ne 0 ] || [ $FRONTEND_RESULT -ne 0 ] || [ $E2E_RESULT -ne 0 ]; then
    exit 1
fi

exit 0

