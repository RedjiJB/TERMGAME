"""Factory for creating configured MissionEngine instances.

This module provides a helper function to create properly configured
MissionEngine instances with all required dependencies.
"""

from pathlib import Path

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from termgame.engine.mission_engine import MissionEngine
from termgame.matchers.registry import MatcherRegistry
from termgame.runtimes.base import ContainerRuntime


def create_mission_engine(
    runtime: ContainerRuntime,
    matcher_registry: MatcherRegistry,
    database_url: str,
    scenarios_dir: Path,
    user_id: int = 1,
) -> MissionEngine:
    """Create a configured MissionEngine instance.

    Args:
        runtime: Container runtime implementation (Docker or Podman).
        matcher_registry: Configured matcher registry with registered matchers.
        database_url: SQLAlchemy database URL (e.g., 'sqlite:///termgame.db').
        scenarios_dir: Path to scenarios directory containing YAML files.
        user_id: Current user ID (default 1 for MVP).

    Returns:
        Configured MissionEngine instance ready to execute missions.

    Example:
        >>> from pathlib import Path
        >>> from termgame.matchers import MatcherRegistry, ExactMatcher
        >>> from termgame.runtimes import create_runtime
        >>>
        >>> runtime = create_runtime("docker")
        >>> registry = MatcherRegistry()
        >>> registry.register("exact", ExactMatcher)
        >>>
        >>> engine = create_mission_engine(
        ...     runtime=runtime,
        ...     matcher_registry=registry,
        ...     database_url="sqlite:///termgame.db",
        ...     scenarios_dir=Path("scenarios"),
        ...     user_id=1
        ... )
        >>> await engine.start_mission("linux/basics/navigation")
    """
    # Create async database engine and session factory
    async_engine = create_async_engine(database_url, echo=False)
    session_factory = async_sessionmaker(async_engine, expire_on_commit=False)

    # Create and return mission engine
    return MissionEngine(
        runtime=runtime,
        matcher_registry=matcher_registry,
        session_factory=session_factory,
        scenarios_dir=scenarios_dir,
        user_id=user_id,
    )
