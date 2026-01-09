# TermGame Architecture

## Overview

TermGame follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────┐
│            User Interface Layer              │
│  ┌──────────────┐      ┌──────────────┐    │
│  │  CLI (Typer) │      │  TUI (Textual)│    │
│  └──────────────┘      └──────────────┘    │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│           Application Layer                  │
│  ┌──────────────┐      ┌──────────────┐    │
│  │ Mission Engine│      │    Coach     │    │
│  └──────────────┘      └──────────────┘    │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│          Infrastructure Layer                │
│  ┌──────────────┐  ┌──────────┐  ┌───────┐ │
│  │   Runtimes   │  │ Matchers │  │   DB  │ │
│  └──────────────┘  └──────────┘  └───────┘ │
└─────────────────────────────────────────────┘
```

## Components

### User Interface Layer

#### CLI (Typer)
- Command-line interface for quick actions
- Mission management
- Progress tracking

#### TUI (Textual)
- Full-screen terminal interface
- Rich, interactive experience
- Mission navigation and execution

### Application Layer

#### Mission Engine
- Core game logic
- State management
- Mission progression
- Validation orchestration

#### Coach
- AI-powered hints
- Contextual guidance
- Learning path recommendations

### Infrastructure Layer

#### Runtimes
- Container abstraction (Docker/Podman)
- Sandbox lifecycle management
- Command execution

#### Matchers
- Output validation
- Command verification
- File system checks

#### Database
- User progress tracking
- Achievement storage
- Mission history

## Data Flow

1. User initiates mission via CLI/TUI
2. Mission Engine loads scenario YAML
3. Runtime creates isolated container
4. User executes commands
5. Matchers validate outputs
6. Engine updates progress
7. Database persists state
8. Coach provides hints if needed

## Design Principles

- **Modularity**: Clear component boundaries
- **Testability**: Dependency injection, protocols
- **Extensibility**: Plugin architecture for matchers
- **Security**: Isolated sandboxes, input validation
- **Performance**: Async I/O, resource management

## Technology Choices

- **Python 3.12+**: Modern Python features
- **Textual**: Rich TUI framework
- **Typer**: Type-safe CLI
- **Pydantic**: Data validation
- **SQLAlchemy**: Database ORM
- **Docker SDK**: Container management

## Future Enhancements

- [ ] Multi-user support
- [ ] Leaderboards
- [ ] Custom scenario editor
- [ ] Plugin system for custom matchers
- [ ] Web dashboard

---

## Architecture Decision Record: Connection Resilience

### Context

During development and testing, we observed intermittent Docker connection failures:
- `Connection aborted, RemoteDisconnected('Remote end closed connection without response')`
- `ConnectionResetError` during command execution
- Silent timeouts on long-running commands

These failures stem from Docker SDK internal limitations we cannot modify:
- `poll.poll()` blocks indefinitely without timeout
- Socket reads hang on stale connections
- Connection pooling without validation
- Timeouts disabled during streaming operations

### Problem Statement

**Goal**: Provide robust, user-friendly experience when Docker connections fail intermittently.

**Requirements**:
1. Automatically retry transient failures
2. Prevent hammering dead Docker daemon
3. Provide clear feedback during retries
4. Allow configuration of retry behavior
5. Distinguish transient vs permanent errors
6. Enable debugging via structured logging

### Solution Architecture

#### Layer 1: Structured Exception Hierarchy

**File**: `src/termgame/runtimes/exceptions.py`

```python
class RuntimeError(Exception):
    """Base exception with transient flag."""
    def __init__(self, message: str, transient: bool = False):
        self.transient = transient

class ConnectionError(RuntimeError):
    """Transient - can retry."""
    def __init__(self, message: str):
        super().__init__(message, transient=True)

class ContainerNotFoundError(RuntimeError):
    """Non-transient - don't retry."""
    def __init__(self, message: str):
        super().__init__(message, transient=False)
```

**Benefits**:
- Typed exceptions replace error strings
- `transient` flag guides retry logic
- Enables specific error handling per layer

#### Layer 2: Circuit Breaker Pattern

**File**: `src/termgame/runtimes/health.py`

```python
@dataclass
class HealthCheck:
    consecutive_failures: int = 0
    circuit_open: bool = False
    max_failures: int = 5        # Configurable
    circuit_timeout: float = 30.0  # seconds

    def record_failure(self):
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.max_failures:
            self.circuit_open = True

    def should_attempt(self) -> bool:
        if not self.circuit_open:
            return True
        # Auto-reset after timeout
        if time.time() - self.last_success > self.circuit_timeout:
            self.circuit_open = False
            return True
        return False
```

**Benefits**:
- Prevents cascading failures
- Gives daemon time to recover
- Auto-resets after 30s timeout

#### Layer 3: Enhanced Retry Logic

**File**: `src/termgame/runtimes/docker_runtime.py`

Improvements over previous implementation:
- **Retries**: 5 attempts (was 3)
- **Backoff**: 1s → 2s → 4s → 8s → 10s (was 0.5s → 0.75s → 1.125s)
- **Connection validation**: Pings Docker before retries
- **Progress feedback**: Users see retry attempts
- **Health tracking**: Feeds circuit breaker

#### Layer 4: Structured Logging

**File**: `src/termgame/logging_config.py`

- Console: ERROR+ only (transient warnings hidden from users)
- File: All messages at configured level (default INFO)
- Default: `~/.termgame/termgame.log`
- Configurable via `TERMGAME_LOG_LEVEL` and `TERMGAME_LOG_FILE`

#### Layer 5: User Feedback

**Progress indicators** during retries:
```
⟳ Retry 2/5: Reconnecting to Docker daemon
```

**Context-specific error messages**:
```
Docker Connection Error

What's happening:
  • Cannot communicate with Docker daemon
  • Connection unstable or daemon stopped

How to fix:
  1. Check Docker Desktop is running
  2. Run: docker ps
  3. Restart Docker if necessary
```

**Status command** for diagnostics:
```bash
> status
Docker Connection Status

✓ Circuit Breaker: CLOSED
Consecutive failures: 0
Last successful operation: 14:23:45

Log file: ~/.termgame/termgame.log
```

### Configuration

All behavior configurable via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `TERMGAME_MAX_RETRIES` | 5 | Number of retry attempts |
| `TERMGAME_RETRY_BASE_DELAY` | 1.0 | Initial delay (seconds) |
| `TERMGAME_RETRY_MAX_DELAY` | 10.0 | Maximum delay (seconds) |
| `TERMGAME_CB_MAX_FAILURES` | 5 | Circuit breaker threshold |
| `TERMGAME_CB_TIMEOUT` | 30.0 | Circuit reset timeout (seconds) |
| `TERMGAME_LOG_LEVEL` | INFO | Logging level |
| `TERMGAME_LOG_FILE` | ~/.termgame/termgame.log | Log file path |

### Alternative Approaches Considered

1. **Custom Connection Pooling** - Rejected: Docker SDK already pools connections
2. **Subprocess Execution** - Rejected: Loses type safety, harder to test
3. **Aggressive Timeouts** - Rejected: Could break legitimate long commands
4. **Podman as Primary** - Deferred: Docker is more widely used

### Trade-offs

**Positive**:
- ✅ Recovers from ~90% of transient failures automatically
- ✅ Better UX with progress feedback
- ✅ Easier debugging with structured logs
- ✅ Configurable for power users

**Negative**:
- ⚠️ Increased latency (~25s max before complete failure)
- ⚠️ Added complexity (circuit breaker state)
- ⚠️ Possible false positives with slow daemons

**Mitigations**:
- Latency acceptable for resilience; configurable
- Comprehensive tests (37 tests, high coverage)
- 30s timeout is generous; configurable

### Testing

**Unit Tests** (37 tests total):
- `test_runtimes_exceptions.py`: 8 tests
- `test_health_check.py`: 13 tests
- `test_docker_runtime.py`: 16 tests

**Coverage**:
- `health.py`: 100%
- `exceptions.py`: 93.75%
- `docker_runtime.py`: 84.56%

**Manual Testing**:
1. Start mission
2. Restart Docker Desktop mid-mission
3. Execute command
4. Verify: Retries succeed, mission continues

### References

- [Circuit Breaker Pattern - Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Exponential Backoff - Google Cloud](https://cloud.google.com/iot/docs/how-tos/exponential-backoff)
- [Docker SDK Issues](https://github.com/docker/docker-py/issues/1375)
