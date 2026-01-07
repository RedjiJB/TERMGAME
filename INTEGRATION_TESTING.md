# Quick Start: Integration Testing

Run the Mission Engine integration tests locally with Docker in 5 minutes.

## Prerequisites

✅ **Docker Desktop installed and running**
- Windows/Mac: Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
- Linux: `curl -fsSL https://get.docker.com | sh`

✅ **Python 3.12+ with virtual environment**
- Already set up if you've cloned this repo

## Quick Setup (3 commands)

### 1. Pull Alpine Image

```bash
docker pull alpine:latest
```

Expected: `Status: Downloaded newer image for alpine:latest`

### 2. Install Test Dependencies

```bash
# Windows
./Scripts/uv.exe pip install aiosqlite

# Linux/macOS
uv pip install aiosqlite
```

Expected: `Installed 1 package in XXms`

### 3. Run Integration Tests

```bash
# Windows
.venv/Scripts/pytest.exe tests/integration/test_mission_engine_docker.py -v

# Linux/macOS
.venv/bin/pytest tests/integration/test_mission_engine_docker.py -v
```

**Expected Output:**
```
============================== test session starts ==============================
collected 4 items

tests/integration/test_mission_engine_docker.py::test_full_mission_lifecycle PASSED [ 25%]
tests/integration/test_mission_engine_docker.py::test_step_validation_failure PASSED [ 50%]
tests/integration/test_mission_engine_docker.py::test_mission_cleanup PASSED [ 75%]
tests/integration/test_mission_engine_docker.py::test_get_hint PASSED [100%]

============================== 4 passed in 12.34s ===============================
```

✅ **Success!** All integration tests passed.

## What Just Happened?

The tests verified:
1. ✅ Docker runtime creates containers correctly
2. ✅ Mission engine executes setup commands
3. ✅ Step validation works with all matcher types
4. ✅ Progress is tracked in the database
5. ✅ XP is awarded on mission completion
6. ✅ Containers are cleaned up properly

## Troubleshooting

### Tests Skipped?

```
SKIPPED [4] Docker daemon not running
```

**Fix:**
1. Ensure Docker Desktop is running (check system tray/menu bar)
2. Run `docker ps` to verify
3. Pull Alpine: `docker pull alpine:latest`

### Permission Denied (Linux)?

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Container Already Exists?

```bash
docker rm -f termgame-test-simple-mission-1
```

## Next Steps

- 📚 [Detailed testing guide](docs/testing/integration-tests.md)
- 🔧 Run specific tests: `pytest tests/integration/test_mission_engine_docker.py::test_full_mission_lifecycle -v`
- 🐛 Debug mode: Add `-s` flag to see all output
- 🚀 Ready to build missions? Check `scenarios/` directory

## Quick Commands Reference

```bash
# Verify Docker is ready
docker ps

# Check Alpine image exists
docker images alpine

# Run single test
.venv/Scripts/pytest.exe tests/integration/test_mission_engine_docker.py::test_full_mission_lifecycle -v

# Run with output
.venv/Scripts/pytest.exe tests/integration/test_mission_engine_docker.py -v -s

# Clean up test containers
docker ps -a | grep termgame | awk '{print $1}' | xargs docker rm -f
```

## Test Scenarios

The integration tests use a simple test mission (`scenarios/test/simple-mission.yml`):

1. **Step 1:** Echo test - verifies command execution
2. **Step 2:** File exists - checks setup created files
3. **Step 3:** File content - validates file content matching

**Container:** Alpine Linux (7MB, fast startup)
**Duration:** ~3 seconds per test
**Cleanup:** Automatic

---

**Need help?** See the [full integration testing guide](docs/testing/integration-tests.md) for detailed troubleshooting and CI/CD setup.
