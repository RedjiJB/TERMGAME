"""CLI utility functions for engine and user management.

This module provides helper functions for CLI commands including engine
initialization, user management, and database operations.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from termgame.config import Config
from termgame.db.models import Base, User
from termgame.engine.mission_engine import MissionEngine
from termgame.matchers.implementations import ContainsMatcher, ExactMatcher, ExistsMatcher
from termgame.matchers.registry import MatcherRegistry
from termgame.runtimes import create_runtime


async def ensure_database(database_url: str) -> None:
    """Ensure database exists and is up to date.

    Args:
        database_url: SQLAlchemy database URL

    Note:
        In production, you should use Alembic migrations instead.
        This is a convenience function for development/testing.
    """
    engine = create_async_engine(database_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


async def get_or_create_user(
    session_factory: async_sessionmaker[AsyncSession],
    user_id: int,
) -> User:
    """Get existing user or create default user.

    Args:
        session_factory: SQLAlchemy async session factory
        user_id: User ID to get or create

    Returns:
        User instance
    """
    async with session_factory() as session:
        # Try to get existing user
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            # Create default user
            user = User(
                username=f"user_{user_id}",
                email=f"user_{user_id}@termgame.local",
                total_xp=0,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

        return user


def create_matcher_registry() -> MatcherRegistry:
    """Create and configure matcher registry with all matchers.

    Returns:
        Configured MatcherRegistry instance
    """
    registry = MatcherRegistry()
    registry.register("exact", ExactMatcher)
    registry.register("contains", ContainsMatcher)
    registry.register("exists", ExistsMatcher)
    return registry


async def create_cli_engine(config: Config) -> MissionEngine:
    """Create fully configured mission engine for CLI use.

    Args:
        config: Application configuration

    Returns:
        Initialized MissionEngine instance
    """
    # Ensure database exists
    await ensure_database(config.database_url)

    # Create engine and session factory
    engine = create_async_engine(config.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    # Ensure user exists
    await get_or_create_user(session_factory, config.user_id)

    # Create runtime and matchers
    runtime = create_runtime(config.runtime_type)
    matcher_registry = create_matcher_registry()

    # Create mission engine
    return MissionEngine(
        runtime=runtime,
        matcher_registry=matcher_registry,
        session_factory=session_factory,
        scenarios_dir=config.scenarios_dir,
        user_id=config.user_id,
    )
