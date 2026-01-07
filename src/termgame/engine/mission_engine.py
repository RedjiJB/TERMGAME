"""Mission execution engine.

This module handles the execution of missions, including state management,
validation, and progression through mission steps.
"""

from datetime import UTC, datetime
from pathlib import Path

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
    ) -> None:
        """Initialize the mission engine.

        Args:
            runtime: Container runtime implementation.
            matcher_registry: Registry of validation matchers.
            session_factory: SQLAlchemy async session factory.
            scenarios_dir: Directory containing scenario YAML files.
            user_id: Current user ID (default 1 for MVP).
        """
        self._runtime = runtime
        self._matcher_registry = matcher_registry
        self._session_factory = session_factory
        self._user_id = user_id
        self._loader = ScenarioLoader(scenarios_dir)
        self._active_missions: dict[str, MissionState] = {}

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
        except Exception as e:
            msg = f"Failed to create container: {e}"
            raise ContainerCreationError(msg) from e

        # Run setup commands
        try:
            for setup_cmd in scenario.environment.setup:
                await self._runtime.execute_command(container, setup_cmd)
        except Exception as e:
            # Cleanup container on setup failure
            await self._cleanup_container(container)
            msg = f"Setup failed: {e}"
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

        except Exception as e:
            msg = f"Validation execution failed: {e}"
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
                progress = result.scalar_one_or_none()

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
            progress = result.scalar_one_or_none()
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
                select(MissionProgress).where(
                    MissionProgress.user_id == self._user_id,
                    MissionProgress.mission_id == mission_id,
                )
            )
            progress = result.scalar_one_or_none()

            if not progress:
                return None

            status = "completed" if progress.completed else "active"

            return {
                "status": status,
                "current_step": progress.current_step_index,
                "xp_earned": progress.xp_earned if progress.completed else 0,
            }

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
        progress = result.scalar_one_or_none()

        if progress:
            progress.completed = True
            progress.completed_at = datetime.now(UTC)
            progress.xp_earned = completion.xp

            # Award XP to user
            user_result = await session.execute(select(User).where(User.id == self._user_id))
            user = user_result.scalar_one_or_none()
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
