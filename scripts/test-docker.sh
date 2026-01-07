#!/usr/bin/env bash
# Advanced Docker integration test runner
# Supports different test modes and options

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper functions
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }

# Detect Python/pytest paths
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    PYTHON=".venv/Scripts/python.exe"
    PYTEST=".venv/Scripts/pytest.exe"
else
    PYTHON=".venv/bin/python"
    PYTEST=".venv/bin/pytest"
fi

# Default values
TEST_FILE="tests/integration/test_mission_engine_docker.py"
VERBOSE="-v"
COVERAGE=""
SPECIFIC_TEST=""
SHOW_OUTPUT=""
SETUP_ONLY=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -h, --help              Show this help message"
            echo "  -s, --setup             Setup only (don't run tests)"
            echo "  -t, --test NAME         Run specific test (e.g., test_full_mission_lifecycle)"
            echo "  -q, --quiet             Less verbose output"
            echo "  -vv, --very-verbose     Very verbose output"
            echo "  -o, --output            Show test output (pytest -s flag)"
            echo "  --cov                   Run with coverage report"
            echo "  --no-cleanup            Don't cleanup containers before/after"
            echo ""
            echo "Examples:"
            echo "  $0                              # Run all tests"
            echo "  $0 -t test_full_mission_lifecycle  # Run single test"
            echo "  $0 -vv -o                       # Very verbose with output"
            echo "  $0 --cov                        # Run with coverage"
            exit 0
            ;;
        -s|--setup)
            SETUP_ONLY=true
            shift
            ;;
        -t|--test)
            SPECIFIC_TEST="::$2"
            shift 2
            ;;
        -q|--quiet)
            VERBOSE=""
            shift
            ;;
        -vv|--very-verbose)
            VERBOSE="-vv"
            shift
            ;;
        -o|--output)
            SHOW_OUTPUT="-s"
            shift
            ;;
        --cov)
            COVERAGE="--cov=termgame --cov-report=term-missing"
            shift
            ;;
        --no-cleanup)
            NO_CLEANUP=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Run with --help for usage information"
            exit 1
            ;;
    esac
done

echo ""
echo "======================================"
echo "  Docker Integration Test Runner"
echo "======================================"
echo ""

# Step 1: Check Docker
echo "Step 1: Checking Docker daemon..."
if ! docker ps &> /dev/null; then
    print_error "Docker daemon is not running"
    echo ""
    echo "Please start Docker Desktop and try again."
    exit 1
fi
print_success "Docker daemon is running"

# Step 2: Check/pull Alpine image
echo ""
echo "Step 2: Checking Alpine image..."
if docker images alpine:latest | grep -q alpine; then
    print_success "Alpine image available"
else
    print_warning "Alpine image not found, pulling..."
    docker pull alpine:latest
    print_success "Alpine image ready"
fi

# Step 3: Check aiosqlite
echo ""
echo "Step 3: Checking dependencies..."
if ! $PYTHON -c "import aiosqlite" &> /dev/null; then
    print_warning "Installing aiosqlite..."
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        ./Scripts/uv.exe pip install aiosqlite
    else
        uv pip install aiosqlite
    fi
fi
print_success "Dependencies ready"

# Step 4: Cleanup
if [ "$NO_CLEANUP" != true ]; then
    echo ""
    echo "Step 4: Cleaning up old containers..."
    LEFTOVER=$(docker ps -a | grep termgame-test | wc -l)
    if [ "$LEFTOVER" -gt 0 ]; then
        print_info "Removing $LEFTOVER old container(s)..."
        docker ps -a | grep termgame-test | awk '{print $1}' | xargs docker rm -f &> /dev/null || true
        print_success "Cleanup complete"
    else
        print_success "No old containers found"
    fi
fi

# Exit if setup only
if [ "$SETUP_ONLY" = true ]; then
    echo ""
    print_success "Setup complete! Ready to run tests."
    exit 0
fi

# Step 5: Run tests
echo ""
echo "======================================"
echo "  Running Tests"
echo "======================================"
echo ""

if [ -n "$SPECIFIC_TEST" ]; then
    print_info "Running specific test: $SPECIFIC_TEST"
fi

# Build pytest command
PYTEST_CMD="$PYTEST $TEST_FILE$SPECIFIC_TEST $VERBOSE $SHOW_OUTPUT $COVERAGE --tb=short --no-cov"

# Show command if very verbose
if [ "$VERBOSE" = "-vv" ]; then
    print_info "Command: $PYTEST_CMD"
    echo ""
fi

# Run tests
if $PYTEST_CMD; then
    echo ""
    echo "======================================"
    print_success "All tests passed!"
    echo "======================================"
    echo ""

    # Show coverage summary if enabled
    if [ -n "$COVERAGE" ]; then
        echo ""
        print_info "Coverage report generated"
    fi

    exit 0
else
    EXIT_CODE=$?
    echo ""
    echo "======================================"
    print_error "Tests failed"
    echo "======================================"
    echo ""

    # Check for leftover containers
    if [ "$NO_CLEANUP" != true ]; then
        LEFTOVER_AFTER=$(docker ps -a | grep termgame-test | wc -l)
        if [ "$LEFTOVER_AFTER" -gt 0 ]; then
            echo ""
            print_warning "Found $LEFTOVER_AFTER container(s) after tests"
            print_info "Cleaning up..."
            docker ps -a | grep termgame-test | awk '{print $1}' | xargs docker rm -f &> /dev/null || true
        fi
    fi

    exit $EXIT_CODE
fi
