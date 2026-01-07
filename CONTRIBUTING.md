# Contributing to TermGame

Thank you for your interest in contributing to TermGame! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions with the community.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/RedjiJB/TERMGAME.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Set up the development environment (see below)

## Development Environment Setup

```bash
# Install Python 3.12+ if not already installed
# Install uv package manager
pip install uv

# Install dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Verify setup
pytest
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

- All new features must include tests
- Aim for >80% code coverage
- Use pytest for testing
- Follow the Arrange-Act-Assert pattern

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=termgame

# Run specific test file
pytest tests/unit/test_engine.py

# Run tests matching a pattern
pytest -k "test_mission"
```

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

1. Update documentation to reflect changes
2. Add tests for new functionality
3. Ensure all tests pass: `pytest`
4. Ensure code quality checks pass: `ruff check .` and `mypy src/termgame`
5. Update CHANGELOG.md with your changes
6. Create a pull request with a clear description

### PR Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Type hints added
- [ ] CHANGELOG.md updated
- [ ] All CI checks passing
- [ ] Code reviewed

## Creating Scenarios

See [docs/mission-design.md](docs/mission-design.md) for detailed guidance on creating missions.

Basic scenario structure:

```yaml
mission:
  id: "linux/basics/file-operations"
  title: "File Operations 101"
  difficulty: beginner
  description: "Learn basic file operations"

steps:
  - id: "create-file"
    description: "Create a file named 'hello.txt'"
    validation:
      type: "file-exists"
      params:
        path: "/home/user/hello.txt"
```

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

## Questions?

- Open a [GitHub Discussion](https://github.com/RedjiJB/TERMGAME/discussions)
- Check [documentation](docs/)
- Review existing issues

Thank you for contributing to TermGame!
