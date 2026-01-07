@echo off
REM Advanced Docker integration test runner for Windows
REM Supports different test modes and options

setlocal enabledelayedexpansion

REM Default values
set "TEST_FILE=tests\integration\test_mission_engine_docker.py"
set "VERBOSE=-v"
set "COVERAGE="
set "SPECIFIC_TEST="
set "SHOW_OUTPUT="
set "SETUP_ONLY=false"
set "NO_CLEANUP=false"

REM Parse command line arguments
:parse_args
if "%1"=="" goto :end_parse
if /i "%1"=="-h" goto :show_help
if /i "%1"=="--help" goto :show_help
if /i "%1"=="-s" set "SETUP_ONLY=true" & shift & goto :parse_args
if /i "%1"=="--setup" set "SETUP_ONLY=true" & shift & goto :parse_args
if /i "%1"=="-t" set "SPECIFIC_TEST=::%2" & shift & shift & goto :parse_args
if /i "%1"=="--test" set "SPECIFIC_TEST=::%2" & shift & shift & goto :parse_args
if /i "%1"=="-q" set "VERBOSE=" & shift & goto :parse_args
if /i "%1"=="--quiet" set "VERBOSE=" & shift & goto :parse_args
if /i "%1"=="-vv" set "VERBOSE=-vv" & shift & goto :parse_args
if /i "%1"=="--very-verbose" set "VERBOSE=-vv" & shift & goto :parse_args
if /i "%1"=="-o" set "SHOW_OUTPUT=-s" & shift & goto :parse_args
if /i "%1"=="--output" set "SHOW_OUTPUT=-s" & shift & goto :parse_args
if /i "%1"=="--cov" set "COVERAGE=--cov=termgame --cov-report=term-missing" & shift & goto :parse_args
if /i "%1"=="--no-cleanup" set "NO_CLEANUP=true" & shift & goto :parse_args
echo [X] Unknown option: %1
echo Run with --help for usage information
exit /b 1

:show_help
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   -h, --help              Show this help message
echo   -s, --setup             Setup only (don't run tests^)
echo   -t, --test NAME         Run specific test
echo   -q, --quiet             Less verbose output
echo   -vv, --very-verbose     Very verbose output
echo   -o, --output            Show test output (pytest -s flag^)
echo   --cov                   Run with coverage report
echo   --no-cleanup            Don't cleanup containers before/after
echo.
echo Examples:
echo   %0                              # Run all tests
echo   %0 -t test_full_mission_lifecycle  # Run single test
echo   %0 -vv -o                       # Very verbose with output
echo   %0 --cov                        # Run with coverage
exit /b 0

:end_parse

echo.
echo ======================================
echo   Docker Integration Test Runner
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

REM Step 2: Check Alpine image
echo.
echo Step 2: Checking Alpine image...
%ENGINE_CMD% images alpine:latest | findstr alpine >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Alpine image not found, pulling...
    %ENGINE_CMD% pull alpine:latest
    if %errorlevel% neq 0 (
        echo [X] Failed to pull Alpine image
        exit /b 1
    )
    echo [OK] Alpine image ready
) else (
    echo [OK] Alpine image available
)

REM Step 3: Check aiosqlite
echo.
echo Step 3: Checking dependencies...
.venv\Scripts\python.exe -c "import aiosqlite" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Installing aiosqlite...
    .\Scripts\uv.exe pip install aiosqlite >nul 2>&1
    if %errorlevel% neq 0 (
        echo [X] Failed to install aiosqlite
        exit /b 1
    )
)
echo [OK] Dependencies ready

REM Step 4: Cleanup
if not "%NO_CLEANUP%"=="true" (
    echo.
    echo Step 4: Cleaning up old containers...
    %ENGINE_CMD% ps -a | findstr termgame-test >nul 2>&1
    if %errorlevel% equ 0 (
        echo [i] Removing old containers...
        for /f "tokens=1" %%i in ('%ENGINE_CMD% ps -a ^| findstr termgame-test') do (
            %ENGINE_CMD% rm -f %%i >nul 2>&1
        )
        echo [OK] Cleanup complete
    ) else (
        echo [OK] No old containers found
    )
)

REM Exit if setup only
if "%SETUP_ONLY%"=="true" (
    echo.
    echo [OK] Setup complete! Ready to run tests.
    exit /b 0
)

REM Step 5: Run tests
echo.
echo ======================================
echo   Running Tests
echo ======================================
echo.

if not "%SPECIFIC_TEST%"=="" (
    echo [i] Running specific test: %SPECIFIC_TEST%
    echo.
)

REM Build pytest command
set "PYTEST_CMD=.venv\Scripts\pytest.exe %TEST_FILE%%SPECIFIC_TEST% %VERBOSE% %SHOW_OUTPUT% %COVERAGE% --tb=short"

REM Show command if very verbose
if "%VERBOSE%"=="-vv" (
    echo [i] Command: %PYTEST_CMD%
    echo.
)

REM Run tests
%PYTEST_CMD%
if %errorlevel% equ 0 (
    echo.
    echo ======================================
    echo [OK] All tests passed!
    echo ======================================
    echo.

    if not "%COVERAGE%"=="" (
        echo.
        echo [i] Coverage report generated
    )

    exit /b 0
) else (
    set TEST_EXIT_CODE=%errorlevel%
    echo.
    echo ======================================
    echo [X] Tests failed
    echo ======================================
    echo.

    REM Check for leftover containers
    if not "%NO_CLEANUP%"=="true" (
        %ENGINE_CMD% ps -a | findstr termgame-test >nul 2>&1
        if !errorlevel! equ 0 (
            echo.
            echo [!] Found containers after tests
            echo [i] Cleaning up...
            for /f "tokens=1" %%i in ('%ENGINE_CMD% ps -a ^| findstr termgame-test') do (
                %ENGINE_CMD% rm -f %%i >nul 2>&1
            )
        )
    )

    exit /b !TEST_EXIT_CODE!
)

endlocal
