# TermGame

```
  ______                    ______
 /_  __/__  _________ ___  / ____/___ _____ ___  ___
  / / / _ \/ ___/ __ `__ \/ / __/ __ `/ __ `__ \/ _ \
 / / /  __/ /  / / / / / / /_/ / /_/ / / / / / /  __/
/_/  \___/_/  /_/ /_/ /_/\____/\__,_/_/ /_/ /_/\___/
```

**A gamified terminal-based training platform for mastering Linux, Cisco IOS, and PowerShell through interactive missions.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

---

## 🎯 Overview

TermGame transforms command-line learning into an engaging, game-like experience. Practice real-world skills in isolated Docker containers with instant feedback, progress tracking, and AI-powered coaching.

### Why TermGame?

- **Safe Practice Environment**: Isolated containers prevent system damage
- **Real-World Skills**: Learn commands that matter in actual DevOps/SysAdmin work
- **Instant Validation**: Automated checking with helpful hints
- **Progress Tracking**: XP system, achievements, and skill progression
- **Mission-Based Learning**: Structured scenarios from beginner to advanced

---

## ✨ Features

### Core Features

- 🎮 **Gamified Learning**
  - Mission-based progression system
  - XP rewards and achievement unlocks
  - Difficulty levels: Beginner → Intermediate → Advanced

- 🐳 **Container-Based Sandboxes**
  - Docker runtime for Linux missions
  - Podman support (planned)
  - Isolated, safe practice environments

- 📊 **Progress Tracking**
  - SQLite database for persistence
  - Step-by-step completion tracking
  - Skill assessment and statistics

- ✅ **Intelligent Validation**
  - Multiple matcher types: exact, contains, regex
  - File existence and content checking
  - Command output validation

- 🤖 **AI Coaching** (Planned)
  - Context-aware hints
  - Personalized learning paths
  - Debugging assistance

- 🎨 **Terminal UI** (Planned)
  - Beautiful Textual-based interface
  - Real-time mission progress
  - Command history and suggestions

### Current Implementation Status

| Component | Status | Description |
|-----------|--------|-------------|
| Mission Engine | ✅ Complete | Core mission execution and state management |
| Docker Runtime | ✅ Complete | Container creation, command execution, cleanup |
| Database Layer | ✅ Complete | User profiles, progress tracking, achievements |
| Scenario Loader | ✅ Complete | YAML parsing and validation |
| Matcher System | ✅ Complete | Step validation with multiple strategies |
| Integration Tests | ✅ Complete | Full mission lifecycle testing |
| CLI Interface | 🚧 In Progress | Command-line interface |
| TUI Application | 🚧 Planned | Interactive terminal UI |
| AI Coach | 📋 Planned | Intelligent assistance system |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Docker Desktop** (or Docker Engine on Linux)
- **Git**
- **Terminal with ANSI color support**

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/RedjiJB/TERMGAME.git
cd TermGame

# 2. Install dependencies using uv (recommended)
pip install uv
uv pip install -e ".[dev]"

# 3. Set up database
.venv/Scripts/alembic.exe upgrade head  # Windows
# .venv/bin/alembic upgrade head  # Linux/macOS

# 4. Verify Docker is running
docker ps
```

### Running TermGame

**Quick Launch (Recommended):**

Choose the launcher for your platform:

```bash
# Windows (CMD) - Double-click or run:
.\play.bat

# Windows (PowerShell)
.\play.ps1

# Linux/macOS (First time only: make executable)
chmod +x play.sh
./play.sh

# Universal (Works everywhere with Python)
python play.py
```

**Manual Launch:**
```bash
# Windows
.venv\Scripts\activate
termgame tui

# Linux/macOS
source .venv/bin/activate
termgame tui
```

**What You'll See:**
```
  ______                    ______
 /_  __/__  _________ ___  / ____/___ _____ ___  ___
  / / / _ \/ ___/ __ `__ \/ / __/ __ `/ __ `__ \/ _ \
 / / /  __/ /  / / / / / / /_/ / /_/ / / / / / /  __/
/_/  \___/_/  /_/ /_/ /_/\____/\__,_/_/ /_/ /_/\___/

Terminal training platform for Linux, Cisco IOS, and PowerShell

Type help for commands, or list to see all missions

termgame > :
```

**First Time Playing:**
```bash
# Inside TermGame
> help       # See all commands
> list       # Browse available missions
> start linux/basics/navigation  # Start your first mission
> progress   # Check your XP and completed missions
```

### Available Commands

Once inside TermGame, you can use these commands:

| Command | Description |
|---------|-------------|
| `list` | Show all missions with completion checkmarks |
| `start <mission-id>` | Begin a training mission |
| `progress` | View your total XP and completed missions |
| `validate` | Check if current step is complete (during mission) |
| `hint` | Get a helpful hint for current step (during mission) |
| `abandon` | Give up current mission and cleanup container |
| `reset` | **Reset all progress** - Deletes all XP and completed missions |
| `status` | Check Docker connection health |
| `help` | Show available commands |
| `quit` | Exit TermGame (auto-cleanup containers) |

**Reset Progress:**
```bash
> reset
⚠️  Reset Progress

This will permanently delete:
  • All completed missions
  • All earned XP
  • All mission progress

Are you sure you want to reset everything? [y/N]: y

✓ Progress reset successfully!
```

### Advanced Usage

**Python API:**
python -c "
from termgame.engine.factory import create_mission_engine
from termgame.matchers.registry import MatcherRegistry
from termgame.matchers.implementations import ExactMatcher, ContainsMatcher, ExistsMatcher
from termgame.runtimes import create_runtime
from pathlib import Path
import asyncio

# Setup
registry = MatcherRegistry()
registry.register('exact', ExactMatcher)
registry.register('contains', ContainsMatcher)
registry.register('exists', ExistsMatcher)

runtime = create_runtime('docker')
engine = create_mission_engine(
    runtime=runtime,
    matcher_registry=registry,
    database_url='sqlite+aiosqlite:///termgame.db',
    scenarios_dir=Path('scenarios'),
    user_id=1
)

# Run mission
async def run():
    await engine.start_mission('linux/basics/navigation')
    print('Mission started!')

asyncio.run(run())
"
```

---

## 📚 Documentation

### Getting Started

- [Installation Guide](docs/installation.md) *(coming soon)*
- [Quick Start Tutorial](docs/quickstart.md) *(coming soon)*
- [Integration Testing](INTEGRATION_TESTING.md) - Run tests locally with Docker

### Development

- [Architecture Overview](docs/architecture.md) *(coming soon)*
- [Contributing Guide](CONTRIBUTING.md)
- [API Reference](docs/api-reference.md) *(coming soon)*
- [Mission Design Guide](docs/mission-design.md) *(coming soon)*

### Testing

- [Integration Tests Guide](docs/testing/integration-tests.md)
- [Running Tests Locally](INTEGRATION_TESTING.md)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        TermGame CLI                          │
│                    (User Interface Layer)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Mission Engine                            │
│  • State Management  • Step Validation  • Progress Tracking  │
└──────────┬──────────────────────────┬───────────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────────┐  ┌──────────────────────┐
│  Container Runtime   │  │   Matcher Registry   │
│  • Docker/Podman     │  │  • Exact/Contains    │
│  • Image Management  │  │  • Regex/Exists      │
│  • Command Execution │  │  • Custom Matchers   │
└──────────────────────┘  └──────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│                     Database Layer (SQLite)                   │
│         Users  •  MissionProgress  •  Achievements            │
└──────────────────────────────────────────────────────────────┘
```

### Key Components

#### Mission Engine (`src/termgame/engine/`)
- Orchestrates mission execution
- Manages container lifecycle
- Validates step completion
- Tracks progress in database
- Awards XP and unlocks achievements

#### Container Runtime (`src/termgame/runtimes/`)
- **DockerRuntime**: Production-ready Docker integration
- **PodmanRuntime**: Planned for rootless containers
- Async command execution with `asyncio.to_thread()`
- Best-effort cleanup on errors

#### Matcher System (`src/termgame/matchers/`)
- **ExactMatcher**: Precise string matching
- **ContainsMatcher**: Substring validation
- **RegexMatcher**: Pattern matching *(planned)*
- **ExistsMatcher**: File/directory existence
- Extensible factory pattern

#### Database (`src/termgame/db/`)
- SQLAlchemy async models
- Alembic migrations
- User profiles with total XP
- Mission progress with step tracking
- Achievement system

---

## 🎓 Creating Missions

Missions are defined in YAML format. Here's a simple example:

```yaml
mission:
  id: "linux/basics/navigation"
  title: "Directory Navigation Basics"
  difficulty: beginner
  description: "Learn fundamental directory navigation commands"
  estimated_time: 10
  tags:
    - linux
    - basics
    - navigation

environment:
  image: "ubuntu:22.04"
  setup:
    - "mkdir -p /home/learner/documents"
    - "mkdir -p /home/learner/pictures"
    - "touch /home/learner/README.txt"

steps:
  - id: "check-current-dir"
    title: "Check Current Directory"
    description: "Use the 'pwd' command to print your current working directory"
    hint: "Type 'pwd' and press Enter"
    validation:
      type: "command-output"
      command: "pwd"
      matcher: "exact"
      expected: "/home/learner"

  - id: "list-files"
    title: "List Files"
    description: "List all files and directories in the current location"
    hint: "The 'ls' command lists directory contents"
    validation:
      type: "command-output"
      command: "ls"
      matcher: "contains"
      expected: "documents"

completion:
  message: "Great job! You've mastered basic directory navigation."
  xp: 100
  unlocks:
    - "linux/basics/file-operations"
```

See `scenarios/` directory for more examples.

---

## 🧪 Testing

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=termgame --cov-report=html
```

### Integration Tests

**Requires Docker running with Alpine image:**

```bash
# Setup (one time)
docker pull alpine:latest
uv pip install aiosqlite

# Run integration tests
pytest tests/integration/test_mission_engine_docker.py -v

# Or use the setup script
./scripts/setup-integration-tests.sh  # Linux/macOS
.\scripts\setup-integration-tests.bat  # Windows
```

See [INTEGRATION_TESTING.md](INTEGRATION_TESTING.md) for detailed instructions.

### Quality Checks

```bash
# Linting
ruff check src/termgame

# Formatting
ruff format src/termgame

# Type checking
mypy src/termgame

# Run all pre-commit hooks
pre-commit run --all-files
```

---

## 🔧 Troubleshooting

### Docker Connection Errors

If you encounter "Connection aborted" or "RemoteDisconnected" errors:

1. **Check Docker is running**:
   ```bash
   docker ps
   ```

2. **View connection status** (in interactive mode):
   ```bash
   termgame tui
   # Then type: status
   ```

3. **Check logs for details**:
   ```bash
   # Default log location
   cat ~/.termgame/termgame.log

   # Or custom location if TERMGAME_LOG_FILE is set
   cat $TERMGAME_LOG_FILE
   ```

4. **Increase retry attempts** (if needed):
   ```bash
   export TERMGAME_MAX_RETRIES=7
   export TERMGAME_RETRY_MAX_DELAY=30
   termgame tui
   ```

### Circuit Breaker Active

If you see "Circuit breaker open" messages:

- **Cause**: Docker daemon is likely down or unresponsive
- **Check**: Run `docker ps` to verify Docker is running
- **Wait**: Circuit resets automatically after 30 seconds
- **Fix**: Restart Docker Desktop and try again

### Container Issues

**Container not found errors**:
- The mission container may have been manually stopped/removed
- Solution: Type `abandon` in interactive mode, then restart the mission

**Image pull failures**:
- Check internet connection
- Verify Docker Hub access
- Try pulling the image manually: `docker pull <image-name>`

### Configuration

Fine-tune retry behavior and logging via environment variables:

```bash
# Retry configuration
export TERMGAME_MAX_RETRIES=5          # Number of retry attempts (default: 5)
export TERMGAME_RETRY_BASE_DELAY=1.0   # Initial delay in seconds (default: 1.0)
export TERMGAME_RETRY_MAX_DELAY=10.0   # Maximum delay in seconds (default: 10.0)

# Circuit breaker configuration
export TERMGAME_CB_MAX_FAILURES=5      # Failure threshold (default: 5)
export TERMGAME_CB_TIMEOUT=30.0        # Reset timeout in seconds (default: 30.0)

# Logging configuration
export TERMGAME_LOG_LEVEL=DEBUG        # Logging level (default: INFO)
export TERMGAME_LOG_FILE=/path/to/log  # Custom log location (default: ~/.termgame/termgame.log)

# Then run TermGame
termgame tui
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Docker daemon not running | Start Docker Desktop, verify with `docker ps` |
| Permission denied (Linux) | Add user to docker group: `sudo usermod -aG docker $USER` |
| Slow command execution | Check Docker resource allocation in Docker Desktop settings |
| Network timeout errors | Increase retry settings or check internet connection |

For more detailed information, see:
- Architecture decisions: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Docker runtime implementation: `src/termgame/runtimes/docker_runtime.py`
- Error handling: `src/termgame/runtimes/exceptions.py`

---

## 🛠️ Development

### Project Structure

```
TermGame/
├── src/termgame/           # Main application code
│   ├── __init__.py
│   ├── cli.py              # CLI interface (WIP)
│   ├── engine/             # Mission execution engine
│   │   ├── mission_engine.py
│   │   ├── state.py
│   │   ├── exceptions.py
│   │   └── factory.py
│   ├── runtimes/           # Container runtime abstraction
│   │   ├── base.py         # Protocol definitions
│   │   ├── docker_runtime.py
│   │   └── factory.py
│   ├── matchers/           # Step validation matchers
│   │   ├── base.py
│   │   ├── implementations.py
│   │   └── registry.py
│   ├── loaders/            # Scenario YAML parsing
│   │   └── scenario_loader.py
│   ├── models/             # Pydantic data models
│   │   └── scenario.py
│   ├── db/                 # Database layer
│   │   ├── models.py       # SQLAlchemy models
│   │   └── __init__.py
│   ├── coach/              # AI coaching (planned)
│   └── tui/                # Terminal UI (planned)
├── scenarios/              # Mission YAML files
│   ├── linux/
│   │   └── basics/
│   │       └── navigation.yml
│   └── test/
│       └── simple-mission.yml
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
│       └── test_mission_engine_docker.py
├── alembic/                # Database migrations
│   ├── env.py
│   └── versions/
├── docs/                   # Documentation
│   └── testing/
│       └── integration-tests.md
├── scripts/                # Utility scripts
│   ├── setup-integration-tests.sh
│   └── setup-integration-tests.bat
├── play.bat                # Quick launcher (Windows CMD)
├── play.ps1                # Quick launcher (Windows PowerShell)
├── play.sh                 # Quick launcher (Linux/macOS)
├── play.py                 # Quick launcher (Universal Python)
├── pyproject.toml          # Project configuration
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

### Tech Stack

- **Language**: Python 3.12+
- **Container Runtime**: Docker SDK
- **Database**: SQLAlchemy (async) + Alembic
- **Validation**: Pydantic
- **Testing**: pytest + pytest-asyncio
- **Linting**: Ruff (replaces Black, isort, Flake8)
- **Type Checking**: Mypy (strict mode)
- **UI Framework**: Textual (planned)
- **Package Manager**: uv

---

## 🗺️ Roadmap

### Phase 1: Core Engine ✅
- [x] Mission Engine implementation
- [x] Docker Runtime integration
- [x] Database models and migrations
- [x] Scenario loader with YAML validation
- [x] Matcher system (exact, contains, exists)
- [x] Integration tests

### Phase 2: CLI & TUI 🚧
- [ ] CLI commands (list, start, progress, abandon)
- [ ] Terminal UI with Textual
- [ ] Mission selection interface
- [ ] Progress dashboard
- [ ] Real-time step validation feedback

### Phase 3: Content & Polish
- [ ] 20+ Linux beginner missions
- [ ] Intermediate Linux missions
- [ ] Cisco IOS scenarios (with GNS3/EVE-NG integration)
- [ ] PowerShell missions
- [ ] Achievement system UI
- [ ] Leaderboards (optional)

### Phase 4: AI & Advanced Features
- [ ] AI-powered coaching with Claude
- [ ] Personalized learning paths
- [ ] Adaptive difficulty
- [ ] Hint generation
- [ ] Code review and suggestions

### Phase 5: Community & Ecosystem
- [ ] Mission marketplace
- [ ] User-submitted scenarios
- [ ] Plugin system
- [ ] API for third-party integrations
- [ ] Web dashboard (optional)

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Set up development environment**: See [CONTRIBUTING.md](CONTRIBUTING.md)
3. **Create a feature branch**: `git checkout -b feature/your-feature`
4. **Make your changes** with tests and documentation
5. **Run quality checks**: `pre-commit run --all-files`
6. **Submit a pull request**

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Areas We Need Help

- 🎓 **Mission Creators**: Design new scenarios
- 🐛 **Bug Hunters**: Find and fix issues
- 📝 **Documentation Writers**: Improve docs and tutorials
- 🎨 **UI/UX Designers**: Enhance terminal interface
- 🧪 **Test Engineers**: Expand test coverage
- 🌍 **Translators**: Multi-language support (future)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Docker** for containerization technology
- **Textual** for the amazing TUI framework
- **Anthropic** for Claude Code development assistance
- **Alembic** for database migrations
- **SQLAlchemy** for async ORM
- **Pydantic** for data validation
- **Ruff** for blazing-fast linting

---

## 📞 Support & Community

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/RedjiJB/TERMGAME/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/RedjiJB/TERMGAME/discussions)
- 📖 **Documentation**: [docs/](docs/) directory
- 🧪 **Integration Testing**: [INTEGRATION_TESTING.md](INTEGRATION_TESTING.md)

---

**Made with ❤️ by the TermGame community**

*Learn by doing. Master the terminal.*
