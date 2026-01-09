"""Application configuration management.

This module handles application-wide configuration including database paths,
scenarios directory, and user settings. Configuration can be loaded from
environment variables or use sensible defaults.
"""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Application configuration.

    Attributes:
        database_url: SQLAlchemy database URL
        scenarios_dir: Path to mission scenarios directory
        user_id: Default user ID for CLI operations
        runtime_type: Container runtime to use (docker or podman)
        max_retries: Number of retry attempts for transient failures
        retry_base_delay: Initial retry delay in seconds
        retry_max_delay: Maximum retry delay in seconds
        circuit_breaker_max_failures: Circuit breaker failure threshold
        circuit_breaker_timeout: Circuit breaker reset timeout in seconds
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (None for default)
    """

    database_url: str
    scenarios_dir: Path
    user_id: int
    runtime_type: str
    max_retries: int
    retry_base_delay: float
    retry_max_delay: float
    circuit_breaker_max_failures: int
    circuit_breaker_timeout: float
    log_level: str
    log_file: str | None

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables or defaults.

        Environment Variables:
            TERMGAME_DB: Database URL (default: sqlite+aiosqlite:///termgame.db)
            TERMGAME_SCENARIOS: Scenarios directory (default: ./scenarios)
            TERMGAME_USER_ID: User ID (default: 1)
            TERMGAME_RUNTIME: Runtime type (default: docker)
            TERMGAME_MAX_RETRIES: Number of retry attempts (default: 5)
            TERMGAME_RETRY_BASE_DELAY: Initial retry delay in seconds (default: 1.0)
            TERMGAME_RETRY_MAX_DELAY: Maximum retry delay in seconds (default: 10.0)
            TERMGAME_CB_MAX_FAILURES: Circuit breaker failure threshold (default: 5)
            TERMGAME_CB_TIMEOUT: Circuit breaker reset timeout in seconds (default: 30.0)
            TERMGAME_LOG_LEVEL: Logging level (default: INFO)
            TERMGAME_LOG_FILE: Path to log file (default: None, uses ~/.termgame/termgame.log)

        Returns:
            Config instance with loaded or default values
        """
        # Get project root (assuming config.py is in src/termgame/)
        project_root = Path(__file__).parent.parent.parent

        # Database URL - default to project root
        db_url = os.getenv(
            "TERMGAME_DB",
            f"sqlite+aiosqlite:///{project_root / 'termgame.db'}",
        )

        # Scenarios directory - default to project root/scenarios
        scenarios_path = os.getenv("TERMGAME_SCENARIOS", str(project_root / "scenarios"))

        # User ID - default to 1
        user_id = int(os.getenv("TERMGAME_USER_ID", "1"))

        # Runtime type - default to docker
        runtime_type = os.getenv("TERMGAME_RUNTIME", "docker")

        # Retry configuration
        max_retries = int(os.getenv("TERMGAME_MAX_RETRIES", "5"))
        retry_base_delay = float(os.getenv("TERMGAME_RETRY_BASE_DELAY", "1.0"))
        retry_max_delay = float(os.getenv("TERMGAME_RETRY_MAX_DELAY", "10.0"))

        # Circuit breaker configuration
        circuit_breaker_max_failures = int(os.getenv("TERMGAME_CB_MAX_FAILURES", "5"))
        circuit_breaker_timeout = float(os.getenv("TERMGAME_CB_TIMEOUT", "30.0"))

        # Logging configuration
        log_level = os.getenv("TERMGAME_LOG_LEVEL", "INFO")
        log_file = os.getenv("TERMGAME_LOG_FILE")  # None if not set

        return cls(
            database_url=db_url,
            scenarios_dir=Path(scenarios_path),
            user_id=user_id,
            runtime_type=runtime_type,
            max_retries=max_retries,
            retry_base_delay=retry_base_delay,
            retry_max_delay=retry_max_delay,
            circuit_breaker_max_failures=circuit_breaker_max_failures,
            circuit_breaker_timeout=circuit_breaker_timeout,
            log_level=log_level,
            log_file=log_file,
        )

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            ValueError: If scenarios directory doesn't exist
            ValueError: If runtime type is invalid
        """
        if not self.scenarios_dir.exists():
            msg = f"Scenarios directory not found: {self.scenarios_dir}"
            raise ValueError(msg)

        if self.runtime_type not in {"docker", "podman"}:
            msg = f"Invalid runtime type: {self.runtime_type}"
            raise ValueError(msg)


def get_config() -> Config:
    """Get application configuration.

    Returns:
        Validated Config instance

    Raises:
        ValueError: If configuration is invalid
    """
    config = Config.from_env()
    config.validate()
    return config
