# Integration Testing with Docker

This guide explains how to run the Mission Engine integration tests locally with Docker.

## Prerequisites

### 1. Docker Installation

**Windows:**
- Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
- Ensure WSL 2 backend is enabled (recommended)
- Start Docker Desktop from the Start menu

**Linux:**
```bash
# Install Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Start Docker daemon
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (optional, avoids sudo)
sudo usermod -aG docker $USER
newgrp docker
```

**macOS:**
- Install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
- Start Docker Desktop from Applications

### 2. Verify Docker Installation

```bash
# Check Docker is running
docker --version

# Test Docker daemon
docker ps

# Expected output: list of running containers (may be empty)
```

## Setup for Integration Tests

### Step 1: Pull Required Docker Image

The integration tests use Alpine Linux (lightweight, fast):

```bash
docker pull alpine:latest
```

**Expected output:**
```
latest: Pulling from library/alpine
<hash>: Pull complete
Digest: sha256:...
Status: Downloaded newer image for alpine:latest
docker.io/library/alpine:latest
```

**Verify image is available:**
```bash
docker images alpine

# Expected output:
# REPOSITORY   TAG       IMAGE ID       CREATED        SIZE
# alpine       latest    <id>           X days ago     7.33MB
```

### Step 2: Verify Integration Test Dependencies

```bash
# Ensure you're in the project directory
cd C:\TermGame  # Windows
# cd /path/to/TermGame  # Linux/macOS

# Check aiosqlite is installed
.venv/Scripts/python.exe -c "import aiosqlite; print('aiosqlite OK')"  # Windows
# .venv/bin/python -c "import aiosqlite; print('aiosqlite OK')"  # Linux/macOS

# If not installed:
./Scripts/uv.exe pip install aiosqlite  # Windows
# uv pip install aiosqlite  # Linux/macOS
```

## Running Integration Tests

### Run All Integration Tests

```bash
# Windows
.venv/Scripts/pytest.exe tests/integration/test_mission_engine_docker.py -v

# Linux/macOS
.venv/bin/pytest tests/integration/test_mission_engine_docker.py -v
```

**Expected output (success):**
```
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.0.2, pluggy-1.6.0
collecting ... collected 4 items

tests/integration/test_mission_engine_docker.py::test_full_mission_lifecycle PASSED [ 25%]
tests/integration/test_mission_engine_docker.py::test_step_validation_failure PASSED [ 50%]
tests/integration/test_mission_engine_docker.py::test_mission_cleanup PASSED [ 75%]
tests/integration/test_mission_engine_docker.py::test_get_hint PASSED [100%]

============================== 4 passed in 15.23s =============================
```

### Run Specific Test

```bash
# Test full mission lifecycle only
.venv/Scripts/pytest.exe tests/integration/test_mission_engine_docker.py::test_full_mission_lifecycle -v -s

# The -s flag shows print output during test execution
```

### Run with Detailed Output

```bash
# Show all output including Docker operations
.venv/Scripts/pytest.exe tests/integration/test_mission_engine_docker.py -v -s --log-cli-level=DEBUG
```

### Run All Integration Tests (Multiple Files)

```bash
# Run all tests marked as integration
.venv/Scripts/pytest.exe tests/integration/ -v -m integration
```

## Understanding Test Behavior

### What the Tests Do

1. **test_full_mission_lifecycle**
   - Creates Alpine container with name `termgame-test-simple-mission-1`
   - Runs setup commands to create test files
   - Validates 3 mission steps sequentially
   - Verifies XP awarded (50 points)
   - Cleans up container

2. **test_step_validation_failure**
   - Tests validating non-current steps
   - Verifies step doesn't auto-advance
   - Ensures current step tracking is correct

3. **test_mission_cleanup**
   - Tests mission abandonment
   - Verifies container cleanup
   - Checks database state is updated

4. **test_get_hint**
   - Tests hint retrieval for current step
   - Validates hint content matches scenario

### Inspecting Containers During Tests

To see containers created during test runs:

```bash
# In another terminal while tests run
docker ps -a | grep termgame

# You should see:
# termgame-test-simple-mission-1  (if test is running)
```

**Note:** Containers are automatically cleaned up after each test completes.

## Troubleshooting

### Tests Are Skipped

**Output:**
```
SKIPPED [4] Docker daemon not running
```

**Solutions:**

1. **Docker daemon not running:**
   ```bash
   # Windows: Start Docker Desktop
   # Linux:
   sudo systemctl start docker
   # macOS: Start Docker Desktop
   ```

2. **Alpine image missing:**
   ```bash
   docker pull alpine:latest
   ```

3. **Verify Docker availability:**
   ```bash
   # Test the check function
   cd tests/integration
   ../../.venv/Scripts/python.exe -c "from test_mission_engine_docker import docker_available; print(f'Docker available: {docker_available()}')"
   ```

### Image Not Found Error

**Error:**
```
docker.errors.ImageNotFound: ... no such image: docker.io/library/alpine:latest
```

**Solution:**
```bash
docker pull alpine:latest
```

### Permission Denied (Linux)

**Error:**
```
permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or run tests with sudo (not recommended)
sudo .venv/bin/pytest tests/integration/test_mission_engine_docker.py -v
```

### Container Already Exists

**Error:**
```
Conflict. The container name ... is already in use
```

**Solution:**
```bash
# List containers
docker ps -a | grep termgame

# Remove stale containers
docker rm -f termgame-test-simple-mission-1

# Or remove all stopped containers
docker container prune -f
```

### Slow Test Execution

**Issue:** First test run is slow (30-60 seconds)

**Reason:** Docker is pulling the Alpine image for the first time.

**Solution:** Pre-pull the image:
```bash
docker pull alpine:latest
```

Subsequent runs will be fast (5-15 seconds total).

## Cleanup After Testing

### Remove Test Containers

```bash
# Remove any leftover test containers
docker ps -a | grep termgame | awk '{print $1}' | xargs docker rm -f

# Windows PowerShell:
docker ps -a | Select-String termgame | ForEach-Object { docker rm -f ($_ -split '\s+')[0] }
```

### Remove Alpine Image (Optional)

```bash
# Free up ~7MB of disk space
docker rmi alpine:latest

# Re-pull later when needed
docker pull alpine:latest
```

## Continuous Integration (CI)

### GitHub Actions Example

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      docker:
        image: docker:dind
        options: --privileged

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -r requirements.txt
          uv pip install aiosqlite

      - name: Pull Docker images
        run: docker pull alpine:latest

      - name: Run integration tests
        run: pytest tests/integration/ -v -m integration
```

## Performance Benchmarks

Expected execution times (on modern hardware with image cached):

- Single test: ~2-4 seconds
- Full suite (4 tests): ~8-15 seconds
- First run (pulling Alpine): +30-60 seconds

**Optimization tips:**
- Pre-pull images before running tests
- Use `pytest-xdist` for parallel execution (future enhancement)
- Use lighter images when possible (Alpine is already minimal)

## Next Steps

After confirming integration tests pass locally:

1. **Add more scenarios** - Create additional test missions
2. **Test Ubuntu image** - Run tests with `ubuntu:22.04` for production scenarios
3. **CI/CD integration** - Set up automated testing in GitHub Actions
4. **Performance testing** - Measure container overhead and optimize
5. **Security testing** - Verify container isolation and resource limits
