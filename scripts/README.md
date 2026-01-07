# TermGame Scripts

Utility scripts for development, testing, and setup.

## 🧪 Testing Scripts

### test-docker-integration (.sh / .bat)

**Simple integration test runner** - Checks Docker, pulls images, and runs all integration tests.

**Usage:**
```bash
# Linux/macOS
./scripts/test-docker-integration.sh

# Windows
.\scripts\test-docker-integration.bat
```

**What it does:**
1. ✓ Checks Docker daemon is running
2. ✓ Verifies/pulls Alpine image
3. ✓ Installs aiosqlite if needed
4. ✓ Cleans up old test containers
5. ✓ Runs all integration tests
6. ✓ Reports results with colored output

**Exit codes:**
- `0` - All tests passed
- `1` - Tests failed or setup error

---

### test-docker (.sh / .bat)

**Advanced integration test runner** - Supports options for different test modes.

**Usage:**
```bash
# Linux/macOS
./scripts/test-docker.sh [OPTIONS]

# Windows
.\scripts\test-docker.bat [OPTIONS]
```

**Options:**

| Flag | Description |
|------|-------------|
| `-h, --help` | Show help message |
| `-s, --setup` | Setup only (don't run tests) |
| `-t, --test NAME` | Run specific test |
| `-q, --quiet` | Less verbose output |
| `-vv, --very-verbose` | Very verbose output |
| `-o, --output` | Show test output (pytest -s) |
| `--cov` | Run with coverage report |
| `--no-cleanup` | Don't cleanup containers |

**Examples:**

```bash
# Run all tests
./scripts/test-docker.sh

# Run specific test
./scripts/test-docker.sh -t test_full_mission_lifecycle

# Very verbose with output
./scripts/test-docker.sh -vv -o

# Run with coverage
./scripts/test-docker.sh --cov

# Setup only (check environment)
./scripts/test-docker.sh --setup

# Quiet mode
./scripts/test-docker.sh -q

# Keep containers for debugging
./scripts/test-docker.sh --no-cleanup
```

**Advanced usage:**
```bash
# Run single test with output and coverage
./scripts/test-docker.sh -t test_mission_cleanup -o --cov

# Very verbose, show output, no cleanup (for debugging)
./scripts/test-docker.sh -vv -o --no-cleanup
```

---

## 🔧 Setup Scripts

### setup-integration-tests (.sh / .bat)

**Complete environment setup** for integration testing.

**Usage:**
```bash
# Linux/macOS
./scripts/setup-integration-tests.sh

# Windows
.\scripts\setup-integration-tests.bat
```

**What it does:**
1. ✓ Checks Docker installation
2. ✓ Verifies Docker daemon is running
3. ✓ Pulls Alpine image
4. ✓ Verifies image integrity
5. ✓ Installs Python dependencies (aiosqlite)
6. ✓ Tests Docker SDK connectivity
7. ✓ Provides next steps

**Exit codes:**
- `0` - Setup successful
- `1` - Setup failed (Docker not available, etc.)

---

## 📂 Script Comparison

| Script | Purpose | Interactivity | Best For |
|--------|---------|---------------|----------|
| `setup-integration-tests` | One-time setup | High | First-time setup |
| `test-docker-integration` | Simple test runner | Low | CI/CD, quick checks |
| `test-docker` | Advanced test runner | Medium | Development, debugging |

---

## 🚀 Quick Start Workflow

### First Time Setup

```bash
# 1. Run setup script
./scripts/setup-integration-tests.sh

# 2. Run simple test to verify
./scripts/test-docker-integration.sh
```

### Daily Development

```bash
# Quick test during development
./scripts/test-docker.sh

# Test specific functionality
./scripts/test-docker.sh -t test_full_mission_lifecycle -o

# Before committing
./scripts/test-docker.sh --cov
```

### Debugging Failed Tests

```bash
# Run with very verbose output, keep containers
./scripts/test-docker.sh -vv -o --no-cleanup

# Inspect the container
docker ps -a | grep termgame-test
docker logs CONTAINER_ID
docker exec -it CONTAINER_ID sh

# Cleanup when done
docker rm -f CONTAINER_ID
```

---

## 🐛 Troubleshooting

### Docker Daemon Not Running

**Error:**
```
[X] Docker daemon is not running
```

**Solution:**
1. Start Docker Desktop (Windows/macOS)
2. Or start Docker daemon: `sudo systemctl start docker` (Linux)

### Alpine Image Not Found

**Error:**
```
[X] Failed to pull Alpine image
```

**Solution:**
1. Check internet connection
2. Verify Docker Hub is accessible
3. Try manual pull: `docker pull alpine:latest`

### Tests Pass Locally But Fail in CI

**Possible causes:**
- Different Docker versions
- Image availability
- Network restrictions
- Resource constraints

**Solution:**
```bash
# Check Docker version matches CI
docker --version

# Verify image
docker images alpine:latest

# Run tests in CI mode (quiet, no color)
./scripts/test-docker.sh -q
```

### Leftover Containers

**Symptom:**
```
Error: Container name already in use
```

**Solution:**
```bash
# List termgame test containers
docker ps -a | grep termgame-test

# Remove all
docker ps -a | grep termgame-test | awk '{print $1}' | xargs docker rm -f

# Or use test script with cleanup
./scripts/test-docker.sh  # Cleans up automatically
```

---

## 📊 Performance Tips

### Fast Test Iterations

```bash
# Setup once
./scripts/test-docker.sh --setup

# Run tests multiple times (skips setup)
./scripts/test-docker.sh
./scripts/test-docker.sh -t test_specific_thing
./scripts/test-docker.sh -t another_test
```

### Pre-pull Images

```bash
# Pull all common images upfront
docker pull alpine:latest
docker pull ubuntu:22.04

# Tests run faster (no pull time)
./scripts/test-docker.sh
```

### Parallel Testing (Future)

Currently not supported, but planned:
```bash
# Future: Run tests in parallel
./scripts/test-docker.sh --parallel -n 4
```

---

## 🔐 Security Notes

### Container Isolation

- All test containers are isolated
- No privileged mode
- No host mounts
- Automatically cleaned up

### Network Access

- Test containers have network access (for package installation)
- Can be restricted with `--network none` in Docker runtime

### Resource Limits

Currently no limits set. To add:
```bash
# Edit test scenario YAML
environment:
  image: "alpine:latest"
  resources:
    memory: "512m"
    cpus: "1"
```

---

## 📝 Script Maintenance

### Adding New Test Suites

1. Create test file in `tests/integration/`
2. Update `TEST_FILE` variable in scripts
3. Add test-specific options if needed

### Updating Docker Images

Edit test scenarios in `scenarios/test/` to use new images:
```yaml
environment:
  image: "ubuntu:24.04"  # Update version
```

### CI/CD Integration

Use the simple script in CI pipelines:
```yaml
# GitHub Actions example
- name: Run Integration Tests
  run: ./scripts/test-docker-integration.sh
```

Or advanced script with options:
```yaml
- name: Run Integration Tests with Coverage
  run: ./scripts/test-docker.sh --cov --quiet
```

---

## 🆘 Getting Help

- **Script issues**: Check script output for error details
- **Test failures**: See [Integration Testing Guide](../INTEGRATION_TESTING.md)
- **Docker issues**: See [Docker documentation](https://docs.docker.com/)
- **General help**: [GitHub Discussions](https://github.com/RedjiJB/TERMGAME/discussions)

---

**Script Versions:**
- `test-docker-integration`: v1.0
- `test-docker`: v1.0
- `setup-integration-tests`: v1.0
