# Changelog

All notable changes to TermGame will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - 2026-01-11 Session

#### PowerShell Mission Content - Complete Windows Server Curriculum
- **66 New PowerShell Missions Created**: Comprehensive Windows Server administration training
  - Total PowerShell content: 16,750 XP worth of missions
  - Complete 15-week Windows Server course coverage
  - Progressive difficulty: 22 Beginner, 31 Intermediate, 13 Advanced
  - Windows Server Core container environment (ltsc2022)

**Mission Breakdown by Topic:**
- **Basics** (6 missions, beginner): PowerShell fundamentals, cmdlets, Get-Help, navigation, aliases, tab completion
- **Files** (4 missions, beginner): File operations with New-Item, Copy-Item, Remove-Item, properties
- **Cmdlets** (5 missions, beginner → intermediate): Syntax, parameters, discovery, advanced parameters, best practices
- **Objects** (5 missions, intermediate): Pipeline, Select-Object, Where-Object, ForEach-Object, methods
- **Processes** (4 missions, beginner → intermediate): Get-Process, process management, services, scheduled tasks
- **Users** (4 missions, beginner → intermediate): User/group management, properties, bulk operations
- **Security** (4 missions, intermediate): Permissions, Get-Acl, Set-Acl, inheritance
- **Networking** (4 missions, beginner → intermediate): Network basics, Test-Connection, DNS, troubleshooting
- **Shares** (4 missions, intermediate): SMB file shares, permissions, access, troubleshooting
- **Compression** (3 missions, beginner): Compress-Archive, Expand-Archive, backup scenarios
- **Backup** (4 missions, intermediate): Backup strategies, Copy-Item backups, wbadmin, disaster recovery
- **Registry** (5 missions, intermediate → advanced): Registry basics, navigation, read/modify operations, safety
- **Encryption** (4 missions, advanced): BitLocker intro/enable/manage, certificates
- **Scripting** (6 missions, intermediate → advanced): Functions, parameters, loops, conditionals, error handling, best practices
- **Cloud** (4 missions, advanced): Azure PowerShell, resources, VMs, hybrid cloud

**Key Features:**
- Windows Server Core containers (mcr.microsoft.com/windows/servercore:ltsc2022)
- Full Windows feature support (Registry, BitLocker, SMB, etc.)
- Real-world Windows administration scenarios
- Azure cloud integration and hybrid infrastructure
- Progressive unlock chains for guided learning
- Comprehensive validation across all mission types

#### Testing Infrastructure
- **Comprehensive PowerShell Test Suite**: 41 automated tests validating all PowerShell missions
  - `test_powershell_mission_schema.py`: 26 tests for YAML structure, fields, organization
  - `test_powershell_content_quality.py`: 15 tests for content quality, command syntax, descriptions
- **Test Coverage**:
  - Schema validation (required fields, data types, format)
  - PowerShell-specific requirements (Windows Server Core image, execution policy, workdir)
  - Content quality (PowerShell cmdlet usage, code examples, hint quality)
  - Mission organization (topic structure, counts, distribution)
  - Progression quality (unlock chains, difficulty progression, XP distribution)
  - Command syntax validation (PowerShell cmdlets vs Linux commands)
- All 66 PowerShell missions verified and passing

#### Documentation Updates
- **README.md**: Reorganized mission library section with collapsible details
  - Added summary table showing 126 total missions, 25,800+ total XP
  - Compact topic lists for quick scanning
  - Reduced verbosity while maintaining essential information
  - Added Windows Containers requirements and troubleshooting
- **CHANGELOG.md**: Updated with accurate XP totals and difficulty distribution
- **docs/WINDOWS_CONTAINERS.md**: Comprehensive guide for PowerShell mission setup
  - Docker Desktop configuration for Windows containers
  - Image pulling instructions and troubleshooting
  - Performance optimization tips
  - FAQ and common issues

#### User Interface Improvements
- **Enhanced mission list display** with color-coded platforms:
  - Added "Platform" column showing Linux (green) or PowerShell (blue)
  - Color-coded mission IDs: Linux (bright green), PowerShell (bright blue)
  - Color-coded titles: Linux (white), PowerShell (cyan)
  - Difficulty colors: Beginner (green), Intermediate (yellow), Advanced (red)
  - Improved table legibility with better column widths and borders
  - Missions sorted by platform (Linux first), then difficulty
- **Better error messages** for Windows container issues:
  - Specific detection of Windows Server Core image errors
  - Step-by-step instructions to switch to Windows containers mode
  - Clear explanation of image size and pull time expectations
  - Helpful notes about platform limitations
- **Context-aware quick tips** when starting missions:
  - Shows "PowerShell cmdlets" for PowerShell missions
  - Shows "Linux commands" for Linux missions
- **Cleaner error output**:
  - Suppressed verbose logging tracebacks for expected user errors
  - Image pull errors now show only user-friendly messages
  - Reduced console clutter during error scenarios

### Added - 2026-01-09 Session

#### Mission Content Expansion
- **20 New Missions Created**: Comprehensive gap-filling across weeks 2-14
  - Total content added: 9,050 XP worth of missions
  - Playtime added: ~12.8 hours of educational content
  - Complete difficulty progressions from beginner to expert/master

#### Week 2 - Navigation and Shell Arguments
- **navigation-advanced-intermediate.yml** (300 XP, 30 min)
  - Directory stack operations (pushd/popd/dirs)
  - Advanced navigation shortcuts and productivity functions
  - Batch directory operations and find integration
- **command-line-mastery-advanced.yml** (550 XP, 50 min)
  - xargs fundamentals and advanced options (-n, -I, -P)
  - Parallel command execution techniques
  - Complex command pipelines and automation patterns
  - Professional argument parsing with getopts

#### Week 3 - File Operations and Finding
- **file-basics-beginner.yml** (200 XP, 25 min)
  - Essential commands: ls, cat, head, tail, less
  - File operations: cp, mv, rm with safety practices
  - Wildcard patterns (*, ?, []) for batch operations
- **advanced-find-techniques.yml** (500 XP, 45 min)
  - Advanced find tests (time, size, type combinations)
  - Efficient use of -exec and xargs
  - Complex real-world file organization scenarios

#### Week 4 - Text Processing and Commands
- **command-basics-beginner.yml** (250 XP, 30 min)
  - Text search with grep (case-insensitive, line numbers, invert)
  - Counting with wc, sorting with sort, deduplication with uniq
  - Column extraction with cut, command chaining with pipes
- **advanced-text-processing.yml** (550 XP, 50 min)
  - Stream editing with sed (substitution, deletion, ranges)
  - AWK programming and field processing
  - Data transformation with tr and paste
  - Real-world log analysis and reporting

#### Week 5 - Environment Variables
- **environment-basics-beginner.yml** (200 XP, 25 min)
  - Environment variable concepts and viewing (env, printenv, echo)
  - Setting shell vs environment variables (export)
  - Understanding PATH and command lookup
  - Variable best practices and naming conventions
- **shell-config-intermediate.yml** (300 XP, 35 min)
  - Shell configuration files (.bashrc, .bash_profile)
  - Creating useful aliases for productivity
  - PATH modification and personal bin directories
  - Persistent environment variable configuration

#### Week 6 - Filesystem Structure
- **filesystem-basics-beginner.yml** (250 XP, 30 min)
  - Linux filesystem hierarchy (/, /etc, /home, /var, /usr)
  - Absolute vs relative paths, special path components (., .., ~)
  - File types and identification
  - Introduction to file permissions
- **links-inodes-intermediate.yml** (350 XP, 40 min)
  - Understanding inodes and metadata
  - Hard links vs symbolic links (differences and use cases)
  - Practical applications (versioning, configuration management)
  - Finding and managing links, inode exhaustion

#### Week 7 - Disk Management
- **disk-basics-beginner.yml** (200 XP, 25 min)
  - Checking disk space with df (filesystem usage)
  - Analyzing directory usage with du
  - Finding large files consuming space
  - Safe cleanup strategies and best practices
- **disk-analysis-intermediate.yml** (300 XP, 35 min)
  - Interactive analysis with ncdu
  - Understanding and monitoring inode usage
  - Compression strategies (gzip, bzip2, xz)
  - Duplicate file detection with checksums
  - Disk usage trend tracking and monitoring

#### Week 9 - Process Management
- **process-basics-beginner.yml** (200 XP, 25 min)
  - Process concepts and the ps command
  - Process states and lifecycle
  - Basic process control (kill, killall)
  - Monitoring with top and /proc filesystem
- **job-control-intermediate.yml** (300 XP, 35 min)
  - Job control (jobs, fg, bg, disown)
  - Process signals (SIGTERM, SIGKILL, SIGHUP, SIGSTOP, SIGCONT)
  - Process priorities (nice, renice)
  - Persistent processes (nohup, disown)
  - Advanced monitoring with watch
- **practice-process-troubleshooting.yml** (700 XP, 55 min)
  - Real-world performance troubleshooting scenarios
  - CPU and memory analysis techniques
  - Handling zombie processes
  - Process priority optimization
  - System health checks and reporting

#### Week 11 - Shell Scripting
- **shell-scripting-intermediate.yml** (350 XP, 40 min)
  - Advanced conditionals (if-elif-else) and test operators
  - Case statements for pattern matching
  - Functions for code reusability
  - Error handling and validation
  - Practical backup script implementation
- **shell-scripting-advanced.yml** (600 XP, 55 min)
  - Bash arrays (indexed and associative)
  - Regular expressions and pattern matching
  - Process management and background jobs
  - Professional argument parsing with getopts
  - Production-ready system monitoring script
- **shell-scripting-expert.yml** (750 XP, 60 min)
  - Comprehensive log analyzer with statistics
  - Deployment automation with rollback capability
  - System health monitor with JSON output
  - Integrated operations toolkit framework

#### Content Quality Improvements
- **Equitable Difficulty Distribution**: All weeks 2-14 now have comprehensive progressions
- **Smooth Learning Paths**: Missions range from beginner through expert/master levels
- **Real-World Focus**: Scenarios based on actual system administration tasks
- **Comprehensive Coverage**: Topics include navigation, text processing, disk management, processes, and scripting
- **Professional Standards**: Production-ready scripts with error handling, logging, and best practices

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
