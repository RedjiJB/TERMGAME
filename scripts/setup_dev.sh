#!/bin/bash
# Development environment setup script for Unix-like systems

set -e

echo "Setting up TermGame development environment..."

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.12"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "ERROR: Python 3.12+ required. Found: $PYTHON_VERSION"
    exit 1
fi
echo "Python version OK: $PYTHON_VERSION"

# Install uv if not present
echo "Checking for uv package manager..."
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
else
    echo "uv already installed"
fi

# Install dependencies
echo "Installing dependencies..."
uv pip install -e ".[dev]"

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Create necessary directories
echo "Creating project directories..."
mkdir -p scenarios/{linux,ios,powershell}
mkdir -p logs data

echo ""
echo "Setup complete! Run 'pytest' to verify installation."
