# Contributing to TermGame

Thank you for your interest in contributing to TermGame! This document provides guidelines and instructions for contributing to this gamified terminal training platform.

## Code of Conduct

Please be respectful and constructive in all interactions with the community. We're here to learn together and build an amazing educational tool.

## Getting Started

### Prerequisites

Before you begin, ensure you have:
- **Python 3.12+** installed
- **Docker Desktop** (or Docker Engine on Linux) running
- **Git** for version control
- A terminal with ANSI color support

### Initial Setup

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/TERMGAME.git
   cd TermGame
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/RedjiJB/TERMGAME.git
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```
5. **Set up the development environment** (see below)

## Development Environment Setup

### Quick Setup

```bash
# 1. Install uv package manager (fast, modern pip replacement)
pip install uv

# 2. Install all dependencies (including dev tools)
uv pip install -e ".[dev]"

# 3. Set up database
.venv/Scripts/alembic.exe upgrade head  # Windows
# .venv/bin/alembic upgrade head  # Linux/macOS

# 4. Install pre-commit hooks for automatic code quality checks
pre-commit install

# 5. Verify setup
pytest tests/unit/ -v

# 6. Set up integration tests (requires Docker)
docker pull alpine:latest
uv pip install aiosqlite
pytest tests/integration/test_mission_engine_docker.py -v
```

### What Gets Installed

- **Core Dependencies**: `docker`, `sqlalchemy`, `pydantic`, `pyyaml`, `alembic`
- **Dev Tools**: `pytest`, `mypy`, `ruff`, `pre-commit`, `pytest-cov`, `pytest-asyncio`
- **Type Stubs**: `types-docker`, `types-pyyaml`

### Verifying Your Setup

```bash
# Check Python version
python --version  # Should be 3.12+

# Check Docker
docker ps  # Should connect successfully

# Check installed packages
uv pip list | grep termgame

# Run all checks
pre-commit run --all-files
```

## Development Workflow

### 1. Code Style

We use the following tools to maintain code quality:

- **ruff**: Linting and formatting (replaces black, isort, flake8)
- **mypy**: Static type checking
- **pre-commit**: Automated checks before commits

```bash
# Format and lint code
ruff format .
ruff check . --fix

# Type checking
mypy src/termgame

# Run all pre-commit hooks
pre-commit run --all-files
```

### 2. Writing Tests

All new features must include tests. We use pytest with async support.

#### Test Guidelines

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test end-to-end workflows with Docker
- **Aim for >80% code coverage** on new code
- **Follow Arrange-Act-Assert pattern**
- **Use descriptive test names**: `test_mission_engine_advances_step_after_validation`

#### Running Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run unit tests with coverage
pytest tests/unit/ --cov=termgame --cov-report=html

# Run specific test file
pytest tests/unit/test_engine.py -v

# Run tests matching a pattern
pytest -k "test_mission" -v

# Run integration tests (requires Docker)
pytest tests/integration/test_mission_engine_docker.py -v

# Run all tests (unit + integration)
pytest -v
```

#### Writing Integration Tests

Integration tests require Docker to be running. They test the full mission lifecycle.

```python
import pytest
from termgame.engine.mission_engine import MissionEngine
from termgame.runtimes import create_runtime

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_mission_flow():
    """Test complete mission from start to finish."""
    runtime = create_runtime("docker")
    engine = MissionEngine(...)

    # Start mission (creates container)
    await engine.start_mission("test/simple-mission")

    # Validate steps
    assert await engine.validate_step("test/simple-mission")

    # Cleanup
    await engine.abandon_mission("test/simple-mission")
```

See `tests/integration/test_mission_engine_docker.py` for examples.

#### Test Coverage Requirements

- **New features**: Must have unit tests
- **Bug fixes**: Add regression test
- **Integration changes**: Update integration tests
- **Minimum coverage**: 80% on modified files

### 3. Type Hints

All code must include proper type hints:

```python
from typing import List, Optional

def process_command(command: str, timeout: Optional[int] = None) -> List[str]:
    """Process a command and return output lines."""
    ...
```

### 4. Documentation

- Add docstrings to all public functions, classes, and modules
- Use Google-style docstrings
- Update relevant documentation in `docs/`

```python
def validate_scenario(scenario_path: str) -> bool:
    """Validate a scenario YAML file.

    Args:
        scenario_path: Path to the scenario YAML file.

    Returns:
        True if scenario is valid, False otherwise.

    Raises:
        FileNotFoundError: If scenario file doesn't exist.
        ValueError: If scenario format is invalid.
    """
    ...
```

## Commit Guidelines

Follow Conventional Commits specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Maintenance tasks

Examples:
```
feat: add PowerShell scenario support
fix: resolve container cleanup race condition
docs: update mission design guide
test: add integration tests for matcher system
```

## Pull Request Process

1. **Update documentation** to reflect your changes
2. **Add tests** for new functionality (unit + integration if applicable)
3. **Ensure all tests pass**:
   ```bash
   pytest tests/unit/ -v  # Must pass
   pytest tests/integration/ -v  # Should pass if Docker available
   ```
4. **Run quality checks**:
   ```bash
   ruff check src/termgame
   ruff format src/termgame
   mypy src/termgame
   ```
5. **Update CHANGELOG.md** with your changes
6. **Commit with descriptive message** following Conventional Commits
7. **Push to your fork** and **create a pull request**
8. **Link related issues** in the PR description
9. **Respond to review feedback** promptly

### PR Checklist

Before submitting your pull request, verify:

- [ ] **Tests added/updated**
  - [ ] Unit tests for new functionality
  - [ ] Integration tests if changing engine/runtime
  - [ ] All tests passing locally
- [ ] **Documentation updated**
  - [ ] README.md if adding features
  - [ ] Docstrings for all new functions/classes
  - [ ] CHANGELOG.md entry added
- [ ] **Code quality**
  - [ ] Type hints added to all new code
  - [ ] Ruff checks passing
  - [ ] Mypy checks passing (no errors in strict mode)
  - [ ] Pre-commit hooks passing
- [ ] **Git hygiene**
  - [ ] Commits follow Conventional Commits format
  - [ ] Branch is up to date with main
  - [ ] No merge conflicts
- [ ] **Review ready**
  - [ ] PR description is clear and complete
  - [ ] Related issues are linked
  - [ ] Ready for code review

## Creating Scenarios

Scenarios are the heart of TermGame. They define missions that users complete to learn new skills.

### Scenario Structure

All scenarios are YAML files located in `scenarios/`. Here's the complete structure:

```yaml
mission:
  id: "linux/basics/file-operations"
  title: "File Operations 101"
  difficulty: beginner  # beginner, intermediate, or advanced
  description: "Learn basic file operations"
  estimated_time: 15  # in minutes
  tags:
    - linux
    - basics
    - files

environment:
  image: "ubuntu:22.04"  # Docker image to use
  setup:
    - "mkdir -p /home/learner"  # Commands run before mission starts
    - "cd /home/learner"

steps:
  - id: "create-file"
    title: "Create a File"
    description: "Create a file named 'hello.txt' in the current directory"
    hint: "Use the 'touch' command to create an empty file"
    validation:
      type: "file-exists"
      file: "/home/learner/hello.txt"
      matcher: "exists"

  - id: "write-content"
    title: "Write Content"
    description: "Write 'Hello, World!' to the file"
    hint: "Use echo with output redirection: echo 'text' > file"
    validation:
      type: "file-content"
      file: "/home/learner/hello.txt"
      matcher: "contains"
      expected: "Hello, World!"

completion:
  message: "Great job! You've mastered basic file operations."
  xp: 100
  unlocks:
    - "linux/basics/advanced-files"
```

### Validation Types

- **command-output**: Validate the output of a command
  ```yaml
  validation:
    type: "command-output"
    command: "pwd"
    matcher: "exact"
    expected: "/home/learner"
  ```

- **file-exists**: Check if a file or directory exists
  ```yaml
  validation:
    type: "file-exists"
    file: "/path/to/file"
    matcher: "exists"
  ```

- **file-content**: Validate the contents of a file
  ```yaml
  validation:
    type: "file-content"
    file: "/path/to/file"
    matcher: "contains"
    expected: "expected text"
  ```

### Matcher Types

- **exact**: String must match exactly
- **contains**: String must contain the expected value
- **exists**: File/directory must exist (for file-exists validation)
- **regex**: Pattern matching *(planned)*

### Testing Your Scenario

```bash
# 1. Place your YAML in scenarios/ directory
# scenarios/my-category/my-mission.yml

# 2. Test loading
python -c "
from termgame.loaders.scenario_loader import ScenarioLoader
from pathlib import Path

loader = ScenarioLoader(Path('scenarios'))
scenario = loader.load('my-category/my-mission')
print(f'Loaded: {scenario.mission.title}')
"

# 3. Test with mission engine
# (See integration tests for examples)
```

See `scenarios/linux/basics/navigation.yml` and `scenarios/test/simple-mission.yml` for complete examples.

## Reporting Bugs

When reporting bugs, please include:

- Python version
- TermGame version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

## Feature Requests

We welcome feature requests! Please:

- Check existing issues first
- Clearly describe the feature and use case
- Explain why it would be valuable
- Consider creating a proof of concept

## Areas We Need Help

We welcome contributions in many areas! Here are specific ways you can help:

### 🎓 Mission Creators
- Design new Linux scenarios (beginner, intermediate, advanced)
- Create PowerShell learning missions
- Develop Cisco IOS training scenarios
- Write challenge missions for experienced users

### 🐛 Bug Hunters
- Test the application and report issues
- Reproduce reported bugs
- Fix known issues
- Improve error handling

### 📝 Documentation Writers
- Write tutorials and guides
- Improve API documentation
- Create video walkthroughs
- Translate documentation

### 🎨 UI/UX Designers
- Design the terminal UI with Textual
- Improve user experience
- Create ASCII art and themes
- Design progress visualizations

### 🧪 Test Engineers
- Write unit tests
- Expand integration test coverage
- Create performance benchmarks
- Set up CI/CD pipelines

### 🚀 Feature Developers
- Implement CLI commands
- Build the TUI application
- Integrate AI coaching
- Add Podman runtime support

## Getting Help

### Questions?

- 💬 [GitHub Discussions](https://github.com/RedjiJB/TERMGAME/discussions) - Ask questions, share ideas
- 📖 [Documentation](docs/) - Read guides and references
- 🐛 [GitHub Issues](https://github.com/RedjiJB/TERMGAME/issues) - Search existing issues
- 🧪 [Integration Testing Guide](INTEGRATION_TESTING.md) - Set up local testing

### Resources

- [README.md](README.md) - Project overview
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [Integration Testing](INTEGRATION_TESTING.md) - Local Docker testing
- [API Reference](docs/api-reference.md) *(coming soon)*

---

**Thank you for contributing to TermGame!** 🎮

Together, we're making command-line learning accessible and fun for everyone.
