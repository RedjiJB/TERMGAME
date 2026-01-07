#!/usr/bin/env bash
# Test Docker integration locally
# Runs the full integration test suite with Docker

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "======================================"
echo "  TermGame Docker Integration Tests"
echo "======================================"
echo ""

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Detect OS for correct Python path
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    PYTHON=".venv/Scripts/python.exe"
    PYTEST=".venv/Scripts/pytest.exe"
else
    PYTHON=".venv/bin/python"
    PYTEST=".venv/bin/pytest"
fi

# Detect container engine: Docker or Podman
ENGINE="docker"
echo "Step 1: Checking container engine..."
if docker ps &> /dev/null; then
    # If DOCKER_HOST is set to Podman, prefer Podman CLI to avoid API mismatch
    if [[ -n "$DOCKER_HOST" ]] && [[ "$DOCKER_HOST" == *podman* ]]; then
        ENGINE="podman"
        print_info "DOCKER_HOST points to Podman; using Podman CLI"
    fi
    print_success "Docker daemon is running"
else
    print_warning "Docker daemon is not running"
    if command -v podman >/dev/null 2>&1; then
        print_info "Falling back to Podman Desktop"
        ENGINE="podman"
        # Start Podman machine if needed (noop on Linux/macOS)
        podman machine start >/dev/null 2>&1 || true
        # Configure Docker SDK to use Podman
        if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            export DOCKER_HOST="npipe:////./pipe/podman-machine-default"
        else
            export DOCKER_HOST="unix:///run/podman/podman.sock"
        fi
        print_success "Podman is ready (DOCKER_HOST set)"
    else
        print_error "Neither Docker nor Podman is available"
        echo ""
        echo "Install/start Docker Desktop or Podman Desktop and try again."
        exit 1
    fi
fi

# Check Alpine image exists
echo ""
echo "Step 2: Checking Alpine image..."
if $ENGINE images alpine:latest | grep -q alpine; then
    IMAGE_SIZE=$($ENGINE images alpine:latest --format "{{.Size}}")
    print_success "Alpine image available (Size: $IMAGE_SIZE)"
else
    print_warning "Alpine image not found"
    echo ""
    print_info "Pulling alpine:latest (this may take a minute)..."
    if $ENGINE pull alpine:latest; then
        print_success "Alpine image pulled successfully"
    else
        print_error "Failed to pull Alpine image"
        exit 1
    fi
fi

# Check aiosqlite is installed
echo ""
echo "Step 3: Checking test dependencies..."
if $PYTHON -c "import aiosqlite" &> /dev/null; then
    print_success "aiosqlite is installed"
else
    print_warning "aiosqlite not found"
    echo ""
    print_info "Installing aiosqlite..."
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        ./Scripts/uv.exe pip install aiosqlite
    else
        uv pip install aiosqlite
    fi
    if $PYTHON -c "import aiosqlite" &> /dev/null; then
        print_success "aiosqlite installed successfully"
    else
        print_error "Failed to install aiosqlite"
        exit 1
    fi
fi

# Clean up any leftover containers from previous runs
echo ""
echo "Step 4: Cleaning up previous test containers..."
LEFTOVER=$($ENGINE ps -a | grep termgame-test | awk '{print $1}' | wc -l)
if [ "$LEFTOVER" -gt 0 ]; then
    print_info "Found $LEFTOVER leftover test container(s)"
    $ENGINE ps -a | grep termgame-test | awk '{print $1}' | xargs $ENGINE rm -f &> /dev/null || true
    print_success "Cleaned up leftover containers"
else
    print_success "No leftover containers found"
fi

# Run the integration tests
echo ""
echo "======================================"
echo "  Running Integration Tests"
echo "======================================"
echo ""

TEST_FILE="tests/integration/test_mission_engine_docker.py"

# Check if test file exists
if [ ! -f "$TEST_FILE" ]; then
    print_error "Test file not found: $TEST_FILE"
    exit 1
fi

# Run pytest with verbose output
if $PYTEST "$TEST_FILE" -v --tb=short --no-cov; then
    echo ""
    echo "======================================"
    print_success "All integration tests passed!"
    echo "======================================"
    echo ""
    exit 0
else
    echo ""
    echo "======================================"
    print_error "Some integration tests failed"
    echo "======================================"
    echo ""
    print_info "Check the output above for details"
    echo ""

    # Check for leftover containers after failure
    LEFTOVER_AFTER=$($ENGINE ps -a | grep termgame-test | awk '{print $1}' | wc -l)
    if [ "$LEFTOVER_AFTER" -gt 0 ]; then
        print_warning "Found $LEFTOVER_AFTER container(s) after tests"
        print_info "Run this command to clean up:"
            echo "    $ENGINE ps -a | grep termgame-test | awk '{print \$1}' | xargs $ENGINE rm -f"
    fi

    exit 1
fi
