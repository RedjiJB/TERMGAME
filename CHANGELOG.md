# Changelog

All notable changes to TermGame will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Core Engine & Runtime
- **Mission Engine**: Complete implementation of the core mission execution engine
  - State management with in-memory and database persistence
  - Step-by-step validation and progression
  - XP awarding and achievement unlocking
  - Best-effort container cleanup on errors
  - Support for concurrent mission execution (planned)

- **Docker Runtime**: Production-ready Docker container integration
  - Async container creation and management using `asyncio.to_thread()`
  - Command execution with bash -c wrapper for shell feature support
  - Automatic image pulling
  - Best-effort cleanup for stop/remove operations
  - Support for custom Docker daemon URLs

- **Container Runtime Abstraction**: Protocol-based design for extensibility
  - `ContainerRuntime` protocol for runtime implementations
  - `Container` protocol for container metadata
  - Factory pattern for runtime creation
  - Podman support (planned)

#### Database & Models
- **SQLAlchemy Async Models**: Complete database layer implementation
  - `User` model with total XP tracking
  - `MissionProgress` model with step completion tracking
  - `Achievement` model for unlocked achievements
  - Foreign key relationships and constraints

- **Alembic Migrations**: Database versioning system
  - Initial migration creating core tables (users, mission_progress, achievements)
  - Migration management with `alembic upgrade/downgrade`

- **Pydantic Data Models**: Type-safe scenario structure
  - `Scenario` model matching YAML structure
  - `MissionMetadata`, `Environment`, `Step`, `StepValidation`, `Completion`
  - Frozen models for immutability
  - Comprehensive field descriptions

#### Validation & Matchers
- **Matcher System**: Extensible validation framework
  - `MatcherRegistry` for matcher management
  - `ExactMatcher` for precise string comparison
  - `ContainsMatcher` for substring validation
  - `ExistsMatcher` for file/directory existence checking
  - `RegexMatcher` (planned)
  - Factory pattern for matcher creation

- **Scenario Loader**: YAML parsing and validation
  - Automatic scenario caching
  - Pydantic validation on load
  - Clear error messages for invalid YAML
  - Support for nested directory structures

#### Testing Infrastructure
- **Integration Tests**: Comprehensive end-to-end testing
  - Full mission lifecycle testing (start → validate → complete)
  - Step validation behavior tests
  - Container cleanup verification
  - Hint retrieval testing
  - Docker availability checking with graceful skipping
  - Test scenario (`test/simple-mission.yml`)

- **Setup Scripts**: Automated integration test setup
  - `scripts/setup-integration-tests.sh` (Linux/macOS)
  - `scripts/setup-integration-tests.bat` (Windows)
  - Docker daemon verification
  - Alpine image pulling
  - Dependency installation
  - Connectivity testing

#### Documentation
- **Integration Testing Guide**: Complete testing documentation
  - Quick start guide (`INTEGRATION_TESTING.md`)
  - Detailed guide (`docs/testing/integration-tests.md`)
  - Prerequisites and setup instructions
  - Troubleshooting common issues
  - CI/CD integration examples
  - Performance benchmarks

- **README Updates**: Comprehensive project overview
  - Current implementation status table
  - Architecture diagram
  - Complete feature list with status
  - Quick start instructions
  - Technology stack documentation
  - Detailed roadmap

#### Scenarios
- **Linux Basics**: Initial scenario library
  - `linux/basics/navigation.yml` - Directory navigation tutorial
  - `test/simple-mission.yml` - Integration testing scenario

### Changed
- **Project Structure**: Organized into logical modules
  - Separated engine, runtimes, matchers, loaders, models, db
  - Clear separation of concerns
  - Protocol-based interfaces

- **Code Quality**: Strict quality standards
  - Ruff linting with comprehensive ruleset
  - Mypy strict mode type checking
  - Pre-commit hooks for automated checks
  - 100% type hint coverage in core modules

### Fixed
- **Type Safety**: Resolved mypy strict mode errors
  - Fixed variable shadowing in mission engine
  - Corrected type annotations in Docker runtime
  - Added proper type narrowing with assertions
  - Removed unreachable code blocks

- **Code Style**: Applied consistent formatting
  - Updated to `datetime.UTC` from deprecated `timezone.utc`
  - Sorted `__all__` exports alphabetically
  - Fixed import ordering
  - Removed trailing whitespace and EOF issues

### Developer Experience
- **Error Handling**: Clear exception hierarchy
  - `MissionEngineError` base exception
  - `MissionNotFoundError`, `MissionAlreadyActiveError`
  - `ContainerCreationError`, `ValidationFailedError`
  - `StepNotFoundError`, `ScenarioLoadError`

- **Logging & Debugging**: Foundation for observability
  - Structured error messages
  - Clear validation failure reasons
  - Container lifecycle events (planned)

### Performance
- **Optimization Strategies**: Efficient design choices
  - In-memory caching for scenarios
  - Async I/O for database and container operations
  - Thread pool for blocking Docker SDK calls
  - Minimal container overhead with Alpine image

### Security
- **Container Isolation**: Safe execution environment
  - No privileged containers
  - No host mounts by default
  - Best-effort resource cleanup
  - Command injection protection with `shlex.quote()`

### Infrastructure
- **Development Tools**: Modern Python toolchain
  - `uv` for fast package management
  - `ruff` for linting and formatting
  - `mypy` for static type checking
  - `pytest` with async support
  - `pre-commit` for automated checks
  - `alembic` for database migrations

## [0.1.0] - 2026-01-07

### Initial Release

#### Core Features
- Mission Engine implementation
- Docker Runtime integration
- Database layer with SQLAlchemy
- Matcher system for validation
- Scenario loader
- Integration tests

#### Components Delivered
- ✅ Mission execution engine
- ✅ Docker container runtime
- ✅ Database models and migrations
- ✅ YAML scenario loader
- ✅ Validation matchers
- ✅ Integration test suite
- ✅ Comprehensive documentation

#### Known Limitations
- CLI interface not yet implemented
- TUI application planned for next release
- AI coaching system planned
- Limited scenario library (2 scenarios)
- Podman runtime not yet implemented
- Regex matcher planned

#### Next Steps
- Phase 2: CLI & TUI implementation
- Expand scenario library
- Add AI coaching integration
- Implement Podman runtime
- Add regex matcher support

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.1.0 | 2026-01-07 | Initial release with core engine, Docker runtime, and testing |
| Unreleased | - | Active development |

---

## Breaking Changes

None yet - first release.

---

## Migration Guide

### From Nothing to 0.1.0

**Database Setup:**
```bash
# Initialize database with Alembic
alembic upgrade head
```

**Docker Setup:**
```bash
# Pull required images
docker pull alpine:latest
docker pull ubuntu:22.04
```

**Dependencies:**
```bash
# Install with uv (recommended)
uv pip install -e ".[dev]"

# Install aiosqlite for testing
uv pip install aiosqlite
```

---

## Contributors

- **Claude Sonnet 4.5** - Core engine implementation, Docker runtime, documentation
- **RedjiJB** - Project conception, architecture, oversight

---

## Links

- [GitHub Repository](https://github.com/RedjiJB/TERMGAME)
- [Issue Tracker](https://github.com/RedjiJB/TERMGAME/issues)
- [Discussions](https://github.com/RedjiJB/TERMGAME/discussions)
- [Documentation](docs/)

---

**Legend:**
- ✅ Complete
- 🚧 In Progress
- 📋 Planned
- ⚠️ Deprecated
- 🔒 Security Fix
- 🐛 Bug Fix
- ⚡ Performance Improvement
