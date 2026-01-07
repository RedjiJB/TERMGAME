@echo off
REM Test Docker integration locally
REM Runs the full integration test suite with Docker

setlocal enabledelayedexpansion

echo.
echo ======================================
echo   TermGame Docker Integration Tests
echo ======================================
echo.

REM Step 1: Check container engine (Docker or Podman)
set "ENGINE_CMD=docker"
echo Step 1: Checking container engine...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Docker daemon not available, checking Podman...
    where podman >nul 2>&1
    if %errorlevel% neq 0 (
        echo [X] Neither Docker nor Podman is available
        echo.
        echo Please install/start Docker Desktop or Podman Desktop and try again.
        exit /b 1
    )
    echo [i] Falling back to Podman Desktop
    podman machine start >nul 2>&1
    set "DOCKER_HOST=npipe:////./pipe/podman-machine-default"
    set "ENGINE_CMD=podman"
    echo [OK] Podman is ready (DOCKER_HOST set)
) else (
    REM If DOCKER_HOST points to Podman, prefer Podman CLI to avoid API mismatch
    if defined DOCKER_HOST (
        echo %DOCKER_HOST% | findstr /I podman >nul 2>&1
        if %errorlevel% equ 0 (
            set "ENGINE_CMD=podman"
            echo [i] DOCKER_HOST points to Podman; using Podman CLI
        )
    )
    echo [OK] Docker daemon is running
)

REM Step 2: Check Alpine image exists
echo.
echo Step 2: Checking Alpine image...
%ENGINE_CMD% images alpine:latest | findstr alpine >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Alpine image not found
    echo.
    echo [i] Pulling alpine:latest (this may take a minute^)...
    %ENGINE_CMD% pull alpine:latest
    if %errorlevel% neq 0 (
        echo [X] Failed to pull Alpine image
        exit /b 1
    )
    echo [OK] Alpine image pulled successfully
) else (
    echo [OK] Alpine image available
)

REM Step 3: Check aiosqlite is installed
echo.
echo Step 3: Checking test dependencies...
.venv\Scripts\python.exe -c "import aiosqlite" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] aiosqlite not found
    echo.
    echo [i] Installing aiosqlite...
    .\Scripts\uv.exe pip install aiosqlite
    if %errorlevel% neq 0 (
        echo [X] Failed to install aiosqlite
        exit /b 1
    )
    echo [OK] aiosqlite installed successfully
) else (
    echo [OK] aiosqlite is installed
)

REM Step 4: Clean up leftover containers
echo.
echo Step 4: Cleaning up previous test containers...
%ENGINE_CMD% ps -a | findstr termgame-test >nul 2>&1
if %errorlevel% equ 0 (
    echo [i] Found leftover test containers
    for /f "tokens=1" %%i in ('%ENGINE_CMD% ps -a ^| findstr termgame-test') do (
        %ENGINE_CMD% rm -f %%i >nul 2>&1
    )
    echo [OK] Cleaned up leftover containers
) else (
    echo [OK] No leftover containers found
)

REM Run the integration tests
echo.
echo ======================================
echo   Running Integration Tests
echo ======================================
echo.

set TEST_FILE=tests\integration\test_mission_engine_docker.py

REM Check if test file exists
if not exist "%TEST_FILE%" (
    echo [X] Test file not found: %TEST_FILE%
    exit /b 1
)

REM Run pytest with verbose output
.venv\Scripts\pytest.exe %TEST_FILE% -v --tb=short --no-cov
if %errorlevel% equ 0 (
    echo.
    echo ======================================
    echo [OK] All integration tests passed!
    echo ======================================
    echo.
    exit /b 0
) else (
    echo.
    echo ======================================
    echo [X] Some integration tests failed
    echo ======================================
    echo.
    echo [i] Check the output above for details
    echo.

    REM Check for leftover containers after failure
    %ENGINE_CMD% ps -a | findstr termgame-test >nul 2>&1
    if %errorlevel% equ 0 (
        echo [!] Found container^(s^) after tests
        echo [i] Run this command to clean up:
        echo     %ENGINE_CMD% ps -a ^| findstr termgame-test
        echo     %ENGINE_CMD% rm -f CONTAINER_ID
    )

    exit /b 1
)

endlocal
