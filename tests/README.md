# TermGame Test Suite

Comprehensive test suite for TermGame covering all recent improvements including mission reorganization, schema validation, UI enhancements, and Docker image functionality.

## Quick Start

```bash
# Install test dependencies
pip install pytest pytest-cov pyyaml docker

# Run all tests
pytest

# Run quick tests (no Docker, no slow tests)
python tests/test_suite_runner.py quick

# Run specific test categories
python tests/test_suite_runner.py schema
python tests/test_suite_runner.py unit
python tests/test_suite_runner.py integration
```

## Test Categories

### 1. Mission Schema Tests (`test_mission_schema.py`)

Tests that all missions comply with the expected Pydantic schema after reorganization.

**What it tests:**
- ✅ Valid YAML syntax in all mission files
- ✅ Required fields present (mission, environment, steps, completion)
- ✅ Difficulty values are valid (beginner/intermediate/advanced only)
- ✅ `estimated_time` is an integer, not a string
- ✅ `environment.image` field exists
- ✅ `environment.setup` is a list, not a string
- ✅ Steps have required fields (id, title, description, validation)
- ✅ Validation is a dict, not a list
- ✅ Validation has `matcher` field
- ✅ Completion section has required fields
- ✅ No week references in tags (week2, week3, etc.)
- ✅ No course codes in tags (cst8207, etc.)

**Run:**
```bash
pytest tests/unit/test_mission_schema.py -v
```

### 2. Mission Organization Tests (`test_mission_schema.py`)

Tests the topic-based directory reorganization.

**What it tests:**
- ✅ Topic-based directories exist (navigation, file-operations, etc.)
- ✅ No week directories remain (week2, week3, etc.)
- ✅ Mission IDs use topic format: `linux/{topic}/{name}`
- ✅ Each topic directory has mission files
- ✅ Total mission count is at least 60
- ✅ Difficulty distribution is balanced (15+ per level)

**Run:**
```bash
pytest tests/unit/test_mission_schema.py::TestMissionOrganization -v
```

### 3. CLI List Command Tests (`test_cli_list.py`)

Tests CLI and interactive mode list functionality.

**What it tests:**
- ✅ List command displays all missions
- ✅ Missions sorted by difficulty (beginner → intermediate → advanced)
- ✅ Difficulty filtering works
- ✅ Table column widths are correct (ID: 40, Title: 35, etc.)
- ✅ Interactive mode uses wider columns (ID: 45)
- ✅ Completion status displays correctly
- ✅ Mission count displayed accurately

**Run:**
```bash
pytest tests/unit/test_cli_list.py -v
```

### 4. Docker Image Tests (`test_docker_image.py`)

Tests Docker image build and essential command availability.

**What it tests:**
- ✅ Dockerfile exists and is valid
- ✅ All essential packages included (nano, vim, gzip, tar, etc.)
- ✅ Image can be built successfully
- ✅ Commands are available: nano, vim, compression tools, network tools
- ✅ Process tools available: htop, ps, top, kill
- ✅ Text processing: grep, sed, awk
- ✅ Man pages available
- ✅ Cron available for automation missions
- ✅ Learner user exists with sudo access
- ✅ Image size is reasonable (<1GB)

**Run:**
```bash
# Requires Docker image to be built first
docker build -f docker/Dockerfile.ubuntu-full -t termgame/ubuntu-full:latest .

pytest tests/integration/test_docker_image.py -v -m docker
```

### 5. Mission Data Integrity Tests (`test_mission_data_integrity.py`)

Tests data integrity after reorganization.

**What it tests:**
- ✅ No duplicate mission IDs
- ✅ Mission IDs match file paths
- ✅ Valid topic directories used
- ✅ Balanced difficulty distribution (20%+ each level)
- ✅ Reasonable time estimates (5-120 minutes)
- ✅ Non-empty descriptions (20+ characters)
- ✅ All missions have at least one step
- ✅ Topic directory names follow kebab-case
- ✅ XP rewards match difficulty levels
- ✅ Completion messages exist
- ✅ Unlock references are valid

**Run:**
```bash
pytest tests/integration/test_mission_data_integrity.py -v
```

## Test Runners

### Using pytest directly

```bash
# All tests
pytest

# With coverage
pytest --cov=src/termgame --cov-report=term-missing

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run specific test file
pytest tests/unit/test_mission_schema.py

# Run specific test class
pytest tests/unit/test_mission_schema.py::TestMissionSchema

# Run specific test
pytest tests/unit/test_mission_schema.py::TestMissionSchema::test_difficulty_values_are_valid

# Run tests matching pattern
pytest -k "schema"

# Exclude slow and Docker tests
pytest -m "not slow and not docker"
```

### Using the test runner script

```bash
# Quick tests (unit only, no Docker)
python tests/test_suite_runner.py quick

# All tests
python tests/test_suite_runner.py all

# Specific categories
python tests/test_suite_runner.py unit
python tests/test_suite_runner.py integration
python tests/test_suite_runner.py schema
python tests/test_suite_runner.py docker

# Verbose
python tests/test_suite_runner.py schema -v
```

## Test Markers

Tests are marked with the following markers:

- `@pytest.mark.slow` - Tests that take >5 seconds
- `@pytest.mark.docker` - Tests requiring Docker to be running
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.unit` - Unit tests

**Examples:**

```bash
# Skip slow tests
pytest -m "not slow"

# Only run Docker tests
pytest -m docker

# Run unit tests only
pytest -m unit
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Install dependencies
pip install pytest pytest-cov pyyaml

# Run non-Docker tests (for environments without Docker)
pytest -m "not docker" --cov=src/termgame --cov-report=xml

# Run all tests (with Docker)
pytest --cov=src/termgame --cov-report=xml
```

## Test Coverage

Current test coverage areas:

| Area | Coverage | Tests |
|------|----------|-------|
| Mission Schema | ✅ Comprehensive | 15+ tests |
| Mission Organization | ✅ Comprehensive | 8+ tests |
| CLI List Command | ✅ Good | 10+ tests |
| Interactive Mode | ✅ Good | 8+ tests |
| Docker Image | ✅ Comprehensive | 12+ tests |
| Data Integrity | ✅ Comprehensive | 15+ tests |

**Total:** 70+ tests covering all recent improvements

## Writing New Tests

### Test Structure

```python
import pytest

class TestFeatureName:
    """Test description."""

    @pytest.fixture
    def my_fixture(self):
        """Fixture description."""
        return "test data"

    def test_something(self, my_fixture):
        """Test that something works."""
        assert my_fixture == "test data"

    @pytest.mark.slow
    def test_slow_operation(self):
        """Test that takes time."""
        # Slow operation
        pass

    @pytest.mark.docker
    def test_docker_feature(self):
        """Test requiring Docker."""
        # Docker-specific test
        pass
```

### Using Fixtures

Available fixtures in `conftest.py`:

- `valid_mission_schema` - Complete valid mission
- `beginner_mission`, `intermediate_mission`, `advanced_mission` - Missions by difficulty
- `mission_list` - List of mixed difficulty missions
- `scenarios_directory` - Path to scenarios
- `topic_based_topics` - List of topic directories
- `difficulty_order` - Difficulty sorting order
- `expected_docker_packages` - Required Docker packages
- `docker_image_name` - Docker image name
- `dockerfile_path` - Dockerfile path

## Troubleshooting

### Docker tests failing

Build the Docker image first:
```bash
docker build -f docker/Dockerfile.ubuntu-full -t termgame/ubuntu-full:latest .
```

Or skip Docker tests:
```bash
pytest -m "not docker"
```

### Scenarios directory not found

Tests auto-skip if `scenarios/linux` doesn't exist. Run from project root:
```bash
cd /path/to/TermGame
pytest
```

### Import errors

Install test dependencies:
```bash
pip install pytest pytest-cov pyyaml docker
```

## Test Reports

Generate HTML coverage report:
```bash
pytest --cov=src/termgame --cov-report=html
# Open htmlcov/index.html in browser
```

Generate XML report for CI:
```bash
pytest --cov=src/termgame --cov-report=xml --junitxml=test-results.xml
```

## Contributing

When adding new features:

1. Write tests first (TDD)
2. Use appropriate markers (`@pytest.mark.slow`, `@pytest.mark.docker`)
3. Add fixtures to `conftest.py` if reusable
4. Update this README with new test categories
5. Run full test suite before committing:
   ```bash
   pytest --cov=src/termgame
   ```
