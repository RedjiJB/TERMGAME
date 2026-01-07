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
    """

    database_url: str
    scenarios_dir: Path
    user_id: int
    runtime_type: str

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables or defaults.

        Environment Variables:
            TERMGAME_DB: Database URL (default: sqlite+aiosqlite:///termgame.db)
            TERMGAME_SCENARIOS: Scenarios directory (default: ./scenarios)
            TERMGAME_USER_ID: User ID (default: 1)
            TERMGAME_RUNTIME: Runtime type (default: docker)

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

        return cls(
            database_url=db_url,
            scenarios_dir=Path(scenarios_path),
            user_id=user_id,
            runtime_type=runtime_type,
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
