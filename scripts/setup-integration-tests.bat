@echo off
REM Setup script for integration testing with Docker (Windows)
REM Run this script to prepare your environment for running integration tests

setlocal enabledelayedexpansion

echo.
echo ================================
echo TermGame Integration Test Setup
echo ================================
echo.

REM Step 1: Check Docker is installed
echo Step 1: Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Docker is not installed
    echo     Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/
    exit /b 1
)
echo [OK] Docker is installed
docker --version

REM Step 2: Check Docker daemon is running
echo.
echo Step 2: Checking Docker daemon...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Docker daemon is not running
    echo     Please start Docker Desktop and try again
    exit /b 1
)
echo [OK] Docker daemon is running

REM Step 3: Check if Alpine image exists
echo.
echo Step 3: Checking Alpine Linux image...
docker images alpine:latest | findstr alpine >nul 2>&1
if %errorlevel% neq 0 (
    echo [i] Pulling alpine:latest (this may take a minute^)...
    docker pull alpine:latest
    if %errorlevel% neq 0 (
        echo [X] Failed to pull Alpine image
        exit /b 1
    )
    echo [OK] Alpine image pulled successfully
) else (
    echo [i] Alpine image already exists
)

REM Step 4: Verify Alpine image
echo.
echo Step 4: Verifying Alpine image...
docker images alpine:latest | findstr alpine >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Alpine image not found after pull
    exit /b 1
)
echo [OK] Alpine image ready

REM Step 5: Install Python test dependencies
echo.
echo Step 5: Installing Python test dependencies...

REM Check if aiosqlite is installed
.venv\Scripts\python.exe -c "import aiosqlite" >nul 2>&1
if %errorlevel% neq 0 (
    echo [i] Installing aiosqlite...
    .\Scripts\uv.exe pip install aiosqlite
    if %errorlevel% neq 0 (
        echo [X] Failed to install aiosqlite
        exit /b 1
    )
    echo [OK] aiosqlite installed successfully
) else (
    echo [i] aiosqlite already installed
)

REM Step 6: Test Docker connectivity from Python
echo.
echo Step 6: Testing Docker connectivity from Python...
.venv\Scripts\python.exe -c "import docker; client = docker.from_env(); client.version(); print('[OK] Docker SDK connected successfully')"
if %errorlevel% neq 0 (
    echo [X] Docker Python SDK test failed
    exit /b 1
)

REM Summary
echo.
echo ================================
echo [OK] Setup Complete!
echo ================================
echo.
echo Your environment is ready for integration testing.
echo.
echo Next steps:
echo.
echo   1. Run all integration tests:
echo      .venv\Scripts\pytest.exe tests\integration\test_mission_engine_docker.py -v
echo.
echo   2. Run a single test:
echo      .venv\Scripts\pytest.exe tests\integration\test_mission_engine_docker.py::test_full_mission_lifecycle -v
echo.
echo   3. Run with detailed output:
echo      .venv\Scripts\pytest.exe tests\integration\test_mission_engine_docker.py -v -s
echo.
echo For more information, see INTEGRATION_TESTING.md
echo.

endlocal
