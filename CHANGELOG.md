# Changelog

All notable changes to TermGame will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - 2026-01-08 Session

#### User Interface Improvements
- **ASCII Art Logo**: Professional startup banner with TermGame ASCII art logo
- **Progress Tracking in List**: `list` command now shows checkmarks (✓) for completed missions
- **Real Progress Display**: `progress` command queries database for actual XP and completion stats
- **Reset Progress Command**: New `reset` command to wipe all progress with confirmation prompt
- **Cross-Platform Launchers**: Quick-start scripts for all platforms
  - `play.bat` - Windows batch file (double-click to launch)
  - `play.ps1` - Windows PowerShell script
  - `play.sh` - Linux/macOS bash script
  - `play.py` - Universal Python launcher (works everywhere)

#### Connection Resilience
- **Enhanced Retry Logic**: Now catches `OSError` family (includes `requests.exceptions.ConnectionError`)
- **Fixed Connection Validation**: Moved validation outside try block to prevent incorrect exception wrapping
- **Graceful Retry Messages**: Only show retry progress for 3+ attempts (silent quick recoveries)
- **Separate Line Retry Messages**: Retry indicators now appear on their own line for cleaner output
- **Automatic Container Cleanup**: Containers cleanup automatically on quit/exit/Ctrl+C
- **Reduced Console Clutter**: Changed console logging from WARNING to ERROR level

### Fixed - 2026-01-08 Session
- 🐛 **Connection Error Handling**: `requests.exceptions.ConnectionError` now properly caught and retried
- 🐛 **Connection Validation Bug**: Fixed retry logic where connection validation raised exceptions inside try block
- 🐛 **Exit Cleanup**: Fixed bug where quitting without `abandon` left Docker containers running
- 🐛 **Console Spam**: Reduced logging noise by showing only ERROR+ on console (all logs still in file)
- 🐛 **Progress Not Updating**: `progress` command now shows real database values instead of zeros
- 🐛 **Missing Completion Status**: `list` command now queries database for completion checkmarks

### Changed - 2026-01-08 Session
- **Logging Level**: Console handler changed from WARNING to ERROR (transient warnings hidden)
- **Retry Threshold**: Retry messages only appear starting from attempt 3 (was all attempts)
- **Progress Display**: Shows actual database values with proper formatting
- **List Display**: Added completion checkmark column and completion count in footer

### Documentation - 2026-01-08 Session
- Updated README with Quick Launch section for all platforms
- Added Available Commands reference table
- Added Reset Progress usage example
- Updated Project Structure to include launcher scripts
- Added CHANGELOG entries for all improvements

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
