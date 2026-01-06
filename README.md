# TermGame

A terminal-based CLI training platform for teaching Linux, Cisco IOS, and PowerShell skills through gamified missions.

## Overview

TermGame provides an interactive learning environment where users can practice command-line skills through carefully designed missions and challenges. The platform supports:

- **Linux Training**: Master shell commands, file operations, and system administration
- **Cisco IOS**: Learn network device configuration and management
- **PowerShell**: Develop Windows automation and scripting skills

## Features

- 🎮 Gamified learning experience with missions and challenges
- 🐳 Isolated container-based sandboxes for safe practice
- 📊 Progress tracking and skill assessment
- 🤖 AI-powered coaching and hints
- 🎨 Beautiful terminal UI built with Textual
- 📝 Extensive scenario library

## Requirements

- Python 3.12 or higher
- Docker or Podman
- Terminal with ANSI color support

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/RedjiJB/termgame.git
cd termgame

# Install using uv (recommended)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

### Running TermGame

```bash
# Start the TUI
termgame

# List available missions
termgame list

# Start a specific mission
termgame start linux/basics/navigation

# View your progress
termgame progress
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
ruff check .

# Run type checking
mypy src/termgame
```

### Project Structure

```
termgame/
├── src/termgame/      # Main application code
│   ├── cli.py         # CLI interface
│   ├── tui/           # Terminal UI components
│   ├── engine/        # Game engine
│   ├── runtimes/      # Container runtime management
│   ├── matchers/      # Command validation
│   ├── coach/         # AI coaching system
│   ├── models/        # Data models
│   └── db/            # Database layer
├── scenarios/         # Mission scenarios
├── tests/             # Test suite
└── docs/              # Documentation
```

## Documentation

- [Architecture Documentation](docs/architecture.md)
- [Mission Design Guide](docs/mission-design.md)
- [API Reference](docs/api-reference.md)
- [Contributing Guide](CONTRIBUTING.md)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 Documentation: [docs/](docs/)
- 🐛 Issue Tracker: [GitHub Issues](https://github.com/RedjiJB/termgame/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/RedjiJB/termgame/discussions)
