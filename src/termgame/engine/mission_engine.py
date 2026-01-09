"""Mission execution engine.

This module handles the execution of missions, including state management,
validation, and progression through mission steps.
"""

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from termgame.db.models import MissionProgress, User
from termgame.engine.exceptions import (
    ContainerCreationError,
    MissionAlreadyActiveError,
    MissionNotFoundError,
    ScenarioLoadError,
    StepNotFoundError,
    ValidationFailedError,
)
from termgame.engine.state import MissionState
from termgame.loaders.scenario_loader import ScenarioLoader
from termgame.matchers.registry import MatcherRegistry
from termgame.runtimes.base import Container, ContainerRuntime
from termgame.runtimes.exceptions import (
    ConnectionError as RuntimeConnectionError,
)
from termgame.runtimes.exceptions import (
    ContainerNotFoundError,
    ImagePullError,
)

# Type alias for progress callback
ProgressCallback = Callable[[str, int, int], None]


class MissionEngine:
    """Core engine for executing missions and managing state.

    The MissionEngine coordinates container runtimes, validation matchers,
    and mission progression logic.
    """

    def __init__(
        self,
        runtime: ContainerRuntime,
        matcher_registry: MatcherRegistry,
        session_factory: async_sessionmaker[AsyncSession],
        scenarios_dir: Path,
        user_id: int = 1,
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        """Initialize the mission engine.

        Args:
            runtime: Container runtime implementation.
            matcher_registry: Registry of validation matchers.
            session_factory: SQLAlchemy async session factory.
            scenarios_dir: Directory containing scenario YAML files.
            user_id: Current user ID (default 1 for MVP).
            progress_callback: Optional callback for progress updates during retries.
        """
        self._runtime = runtime
        self._matcher_registry = matcher_registry
        self._session_factory = session_factory
        self._user_id = user_id
        self._progress_callback = progress_callback
        self._loader = ScenarioLoader(scenarios_dir)
        self._active_missions: dict[str, MissionState] = {}
        self._logger = logging.getLogger(__name__)

    async def start_mission(self, mission_id: str) -> None:
        """Start a mission.

        Loads the scenario, creates a container, runs setup commands,
        and initializes mission state.

        Args:
            mission_id: Unique identifier for the mission.

        Raises:
            MissionNotFoundError: If scenario cannot be loaded.
            MissionAlreadyActiveError: If mission already active.
            ContainerCreationError: If container creation fails.
        """
        # Check if already active
        if mission_id in self._active_missions:
            msg = f"Mission already active: {mission_id}"
            raise MissionAlreadyActiveError(msg)

        # Load scenario
        try:
            scenario = self._loader.load(mission_id)
        except ScenarioLoadError as e:
            raise MissionNotFoundError(str(e)) from e

        # Create container
        container_name = f"termgame-{mission_id.replace('/', '-')}-{self._user_id}"
        try:
            container = await self._runtime.create_container(
                image=scenario.environment.image,
                name=container_name,
                working_dir=scenario.environment.workdir,
            )
        except ImagePullError as e:
            msg = f"Failed to pull image: {e}"
            self._logger.error(msg)
            raise ContainerCreationError(msg) from e
        except RuntimeConnectionError as e:
            msg = f"Docker connection error: {e}"
            self._logger.error(msg)
            raise ContainerCreationError(msg) from e
        except Exception as e:
            msg = f"Failed to create container: {e}"
            self._logger.error(msg)
            raise ContainerCreationError(msg) from e

        # Run setup commands
        try:
            for setup_cmd in scenario.environment.setup:
                await self._runtime.execute_command(container, setup_cmd)
        except RuntimeConnectionError as e:
            # Cleanup container on setup failure
            await self._cleanup_container(container)
            msg = f"Docker connection error during setup: {e}"
            self._logger.error(msg)
            raise ContainerCreationError(msg) from e
        except Exception as e:
            # Cleanup container on setup failure
            await self._cleanup_container(container)
            msg = f"Setup failed: {e}"
            self._logger.error(msg)
            raise ContainerCreationError(msg) from e

        # Create mission state
        state = MissionState(
            mission_id=mission_id,
            user_id=self._user_id,
            scenario=scenario,
            container=container,
        )
        self._active_missions[mission_id] = state

        # Persist to database
        async with self._session_factory() as session:
            # Check for existing active progress (shouldn't exist, but handle gracefully)
            result = await session.execute(
                select(MissionProgress).where(
                    MissionProgress.user_id == self._user_id,
                    MissionProgress.mission_id == mission_id,
                    MissionProgress.completed == False,  # noqa: E712
                )
            )
            existing_progress = result.scalars().first()

            if existing_progress:
                # Update existing record instead of creating duplicate
                step_id = state.current_step.id if state.current_step else None
                existing_progress.current_step_id = step_id
                existing_progress.current_step_index = 0
                existing_progress.container_id = container.id
                existing_progress.container_name = container.name
                existing_progress.started_at = datetime.now(UTC)
                existing_progress.last_activity = datetime.now(UTC)
            else:
                # Create new progress record
                progress = MissionProgress(
                    user_id=self._user_id,
                    mission_id=mission_id,
                    current_step_id=state.current_step.id if state.current_step else None,
                    current_step_index=0,
                    container_id=container.id,
                    container_name=container.name,
                )
                session.add(progress)

            await session.commit()

    async def validate_step(self, mission_id: str, step_id: str | None = None) -> bool:
        """Validate completion of a mission step.

        Executes validation logic based on step configuration and updates
        progress if validation passes.

        Args:
            mission_id: Mission identifier.
            step_id: Step identifier (optional, defaults to current step).

        Returns:
            True if step validation passes, False otherwise.

        Raises:
            MissionNotFoundError: If mission not active.
            StepNotFoundError: If step_id provided but not found.
            ValidationFailedError: If validation execution fails.
        """
        # Get active mission state
        state = self._active_missions.get(mission_id)
        if not state:
            msg = f"Mission not active: {mission_id}"
            raise MissionNotFoundError(msg)

        # Determine which step to validate
        if step_id is None:
            step = state.current_step
            if not step:
                return False  # No more steps
        else:
            # Find step by ID
            step = next((s for s in state.scenario.steps if s.id == step_id), None)
            if not step:
                msg = f"Step not found: {step_id}"
                raise StepNotFoundError(msg)

        # Execute validation based on type
        validation = step.validation

        try:
            if validation.type == "command-output":
                # Execute command and get output
                actual = await self._runtime.execute_command(
                    state.container,
                    validation.command or "",
                )
                # Strip whitespace for comparison
                actual = actual.strip()
            elif validation.type == "file-exists":
                # Check if file exists
                cmd = f"test -f {validation.file} && echo 'true' || echo 'false'"
                output = await self._runtime.execute_command(state.container, cmd)
                actual = output.strip()
            elif validation.type == "file-content":
                # Read file content
                cmd = f"cat {validation.file}"
                actual = await self._runtime.execute_command(state.container, cmd)
                actual = actual.strip()

        except ContainerNotFoundError as e:
            msg = f"Container lost during validation: {e}"
            self._logger.error(msg)
            raise ValidationFailedError(msg) from e
        except RuntimeConnectionError as e:
            msg = f"Connection error during validation: {e}"
            self._logger.warning(msg)
            raise ValidationFailedError(msg) from e
        except Exception as e:
            msg = f"Validation execution failed: {e}"
            self._logger.error(msg)
            raise ValidationFailedError(msg) from e

        # Get matcher and validate
        matcher = self._matcher_registry.create(validation.matcher)
        is_valid = matcher.matches(actual, validation.expected)

        # If valid and this is the current step, advance
        if is_valid and step == state.current_step:
            state.advance_step()

            # Update database
            async with self._session_factory() as session:
                result = await session.execute(
                    select(MissionProgress).where(
                        MissionProgress.user_id == self._user_id,
                        MissionProgress.mission_id == mission_id,
                        MissionProgress.completed == False,  # noqa: E712
                    )
                )
                progress = result.scalars().first()

                if progress:
                    progress.current_step_index = state.current_step_index
                    progress.current_step_id = state.current_step.id if state.current_step else None
                    progress.steps_completed = state.completed_steps
                    progress.last_activity = datetime.now(UTC)

                    # Check if mission completed
                    if state.is_completed:
                        await self._complete_mission(mission_id, session)

                    await session.commit()

        return is_valid

    async def get_current_step(self, mission_id: str) -> dict[str, str | int] | None:
        """Get current step information.

        Args:
            mission_id: Mission identifier.

        Returns:
            Step information as dict with id, title, description, hint, index, total.
            Returns None if mission not active or completed.
        """
        state = self._active_missions.get(mission_id)
        if not state or not state.current_step:
            return None

        step = state.current_step
        return {
            "id": step.id,
            "title": step.title,
            "description": step.description,
            "hint": step.hint,
            "index": state.current_step_index,
            "total": len(state.scenario.steps),
        }

    async def get_hint(self, mission_id: str) -> str | None:
        """Get hint for current step.

        Args:
            mission_id: Mission identifier.

        Returns:
            Hint text, or None if mission not active or completed.
        """
        state = self._active_missions.get(mission_id)
        if not state or not state.current_step:
            return None
        return state.current_step.hint

    async def execute_command(self, mission_id: str, command: str) -> str:
        """Execute a command in the mission's container.

        Args:
            mission_id: Mission identifier.
            command: Command to execute.

        Returns:
            Command output as string.

        Raises:
            MissionNotFoundError: If mission not active.
        """
        state = self._active_missions.get(mission_id)
        if not state:
            msg = f"No active mission: {mission_id}"
            raise MissionNotFoundError(msg)

        return await self._runtime.execute_command(state.container, command)

    async def abandon_mission(self, mission_id: str) -> None:
        """Abandon an active mission and cleanup resources.

        Stops and removes the container, removes mission from active state,
        and updates database to clear container references.

        Args:
            mission_id: Mission identifier.
        """
        state = self._active_missions.get(mission_id)
        if not state:
            return

        # Cleanup container
        await self._cleanup_container(state.container)

        # Remove from active missions
        del self._active_missions[mission_id]

        # Update database - clear container info but keep progress
        async with self._session_factory() as session:
            result = await session.execute(
                select(MissionProgress).where(
                    MissionProgress.user_id == self._user_id,
                    MissionProgress.mission_id == mission_id,
                    MissionProgress.completed == False,  # noqa: E712
                )
            )
            progress = result.scalars().first()
            if progress:
                progress.container_id = None
                progress.container_name = None
                await session.commit()

    async def get_mission_status(self, mission_id: str) -> dict[str, str | int | None] | None:
        """Get current status of a mission.

        Returns mission progress including status, current step, and XP earned.

        Args:
            mission_id: Mission identifier.

        Returns:
            Dictionary with status information or None if no progress found.
            Dictionary contains: status, current_step, xp_earned
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(MissionProgress)
                .where(
                    MissionProgress.user_id == self._user_id,
                    MissionProgress.mission_id == mission_id,
                )
                .order_by(MissionProgress.started_at.desc())
            )
            progress = result.scalars().first()

            if not progress:
                return None

            status = "completed" if progress.completed else "active"

            return {
                "status": status,
                "current_step": progress.current_step_index,
                "xp_earned": progress.xp_earned if progress.completed else 0,
            }

    def get_docker_health(self) -> dict[str, Any]:
        """Get Docker connection health status.

        Returns:
            Dict with health metrics for debugging including circuit breaker state,
            consecutive failures, last success timestamp, and current status.
        """
        if hasattr(self._runtime, "_health"):
            health = self._runtime._health  # noqa: SLF001
            return {
                "circuit_open": health.circuit_open,
                "consecutive_failures": health.consecutive_failures,
                "last_success": health.last_success,
                "should_attempt": health.should_attempt(),
            }
        return {"error": "Health monitoring not available"}

    async def _complete_mission(self, mission_id: str, session: AsyncSession) -> None:
        """Mark mission as completed and award XP.

        Args:
            mission_id: Mission identifier.
            session: Active database session.
        """
        state = self._active_missions.get(mission_id)
        if not state:
            return

        completion = state.scenario.completion

        # Update progress
        result = await session.execute(
            select(MissionProgress).where(
                MissionProgress.user_id == self._user_id,
                MissionProgress.mission_id == mission_id,
                MissionProgress.completed == False,  # noqa: E712
            )
        )
        progress = result.scalars().first()

        if progress:
            progress.completed = True
            progress.completed_at = datetime.now(UTC)
            progress.xp_earned = completion.xp

            # Award XP to user
            user_result = await session.execute(select(User).where(User.id == self._user_id))
            user = user_result.scalars().first()
            if user:
                user.total_xp += completion.xp

        # Cleanup container
        await self._cleanup_container(state.container)

        # Remove from active missions
        del self._active_missions[mission_id]

    async def _cleanup_container(self, container: Container) -> None:
        """Cleanup container resources.

        Best-effort cleanup that doesn't raise exceptions.

        Args:
            container: Container to cleanup.
        """
        try:
            await self._runtime.stop_container(container)
            await self._runtime.remove_container(container)
        except Exception:
            # Log but don't raise - best effort cleanup
            pass
