# API Reference

## CLI Commands

### `termgame start <mission-id>`
Start a mission by its identifier.

**Arguments:**
- `mission-id`: Mission identifier (e.g., `linux/basics/navigation`)

### `termgame list`
List all available missions.

### `termgame progress`
Show learning progress and statistics.

### `termgame tui`
Launch the Terminal User Interface.

## Python API

### Mission Engine

```python
from termgame.engine import MissionEngine

engine = MissionEngine()
await engine.start_mission("linux/basics/navigation")
```

### Runtime Management

```python
from termgame.runtimes import create_runtime

runtime = create_runtime("docker")
container = await runtime.create_container("ubuntu:22.04")
```

## Configuration

Configuration via environment variables:

- `TERMGAME_DATA_DIR`: Data directory
- `TERMGAME_RUNTIME`: Container runtime (docker/podman)
- `TERMGAME_LOG_LEVEL`: Logging level

## Models

See source code documentation for Pydantic models.
