#!/usr/bin/env bash
# Setup script for integration testing with Docker
# Run this script to prepare your environment for running integration tests

set -e  # Exit on error

echo "🚀 TermGame Integration Test Setup"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Step 1: Check Docker is installed
echo "Step 1: Checking Docker installation..."
if command -v docker &> /dev/null; then
    print_success "Docker is installed ($(docker --version))"
else
    print_error "Docker is not installed"
    echo "  Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Step 2: Check Docker daemon is running
echo ""
echo "Step 2: Checking Docker daemon..."
if docker ps &> /dev/null; then
    print_success "Docker daemon is running"
else
    print_error "Docker daemon is not running"
    echo "  Please start Docker Desktop and try again"
    exit 1
fi

# Step 3: Pull Alpine image
echo ""
echo "Step 3: Pulling Alpine Linux image..."
if docker images alpine:latest | grep -q alpine; then
    print_info "Alpine image already exists"
else
    print_info "Pulling alpine:latest (this may take a minute)..."
    if docker pull alpine:latest; then
        print_success "Alpine image pulled successfully"
    else
        print_error "Failed to pull Alpine image"
        exit 1
    fi
fi

# Step 4: Verify Alpine image
echo ""
echo "Step 4: Verifying Alpine image..."
if docker images alpine:latest | grep -q alpine; then
    IMAGE_SIZE=$(docker images alpine:latest --format "{{.Size}}")
    print_success "Alpine image ready (Size: $IMAGE_SIZE)"
else
    print_error "Alpine image not found after pull"
    exit 1
fi

# Step 5: Install Python test dependencies
echo ""
echo "Step 5: Installing Python test dependencies..."

# Detect OS for correct Python path
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    PYTHON=".venv/Scripts/python.exe"
    PYTEST=".venv/Scripts/pytest.exe"
    UV="./Scripts/uv.exe"
else
    PYTHON=".venv/bin/python"
    PYTEST=".venv/bin/pytest"
    UV="uv"
fi

# Check if aiosqlite is installed
if $PYTHON -c "import aiosqlite" &> /dev/null; then
    print_info "aiosqlite already installed"
else
    print_info "Installing aiosqlite..."
    if $UV pip install aiosqlite; then
        print_success "aiosqlite installed successfully"
    else
        print_error "Failed to install aiosqlite"
        exit 1
    fi
fi

# Step 6: Run a quick connectivity test
echo ""
echo "Step 6: Testing Docker connectivity from Python..."
TEST_SCRIPT='
import docker
try:
    client = docker.from_env()
    client.version()
    print("✓ Docker SDK connected successfully")
except Exception as e:
    print(f"✗ Docker SDK connection failed: {e}")
    exit(1)
'

if $PYTHON -c "$TEST_SCRIPT"; then
    print_success "Docker Python SDK working"
else
    print_error "Docker Python SDK test failed"
    exit 1
fi

# Step 7: Summary and next steps
echo ""
echo "===================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "===================================="
echo ""
echo "Your environment is ready for integration testing."
echo ""
echo "Next steps:"
echo ""
echo "  1. Run all integration tests:"
echo "     $PYTEST tests/integration/test_mission_engine_docker.py -v"
echo ""
echo "  2. Run a single test:"
echo "     $PYTEST tests/integration/test_mission_engine_docker.py::test_full_mission_lifecycle -v"
echo ""
echo "  3. Run with detailed output:"
echo "     $PYTEST tests/integration/test_mission_engine_docker.py -v -s"
echo ""
echo "For more information, see INTEGRATION_TESTING.md"
echo ""
