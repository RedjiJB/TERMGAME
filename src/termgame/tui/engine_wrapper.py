"""TUI wrapper for Mission Engine integration.

This module provides async utilities for integrating the Mission Engine
with the Textual TUI, handling engine lifecycle and state management.
"""

from typing import Any

from termgame.cli_utils import create_cli_engine
from termgame.config import Config, get_config
from termgame.engine.mission_engine import MissionEngine


class TUIEngineWrapper:
    """Wrapper for Mission Engine in TUI context.

    Manages engine lifecycle, state, and provides convenient methods
    for TUI screens to interact with missions.
    """

    def __init__(self) -> None:
        """Initialize the engine wrapper."""
        self._engine: MissionEngine | None = None
        self._config: Config | None = None

    async def initialize(self) -> None:
        """Initialize the mission engine.

        Must be called before using any engine methods.
        """
        if self._engine is None:
            self._config = get_config()
            self._engine = await create_cli_engine(self._config)

    @property
    def engine(self) -> MissionEngine:
        """Get the mission engine instance.

        Returns:
            MissionEngine instance

        Raises:
            RuntimeError: If engine not initialized
        """
        if self._engine is None:
            msg = "Engine not initialized. Call initialize() first."
            raise RuntimeError(msg)
        return self._engine

    async def start_mission(self, mission_id: str) -> dict[str, Any]:
        """Start a mission and return first step info.

        Args:
            mission_id: Mission identifier

        Returns:
            Dictionary with step information

        Raises:
            Exception: If mission start fails
        """
        await self.engine.start_mission(mission_id)
        step_info = await self.engine.get_current_step(mission_id)

        if step_info:
            return {
                "success": True,
                "step": step_info,
            }

        return {
            "success": False,
            "error": "Failed to retrieve first step",
        }

    async def validate_step(self, mission_id: str) -> dict[str, Any]:
        """Validate current step and get next step or completion status.

        Args:
            mission_id: Mission identifier

        Returns:
            Dictionary with validation result and next step info
        """
        try:
            # Get current step info before validation
            current_step = await self.engine.get_current_step(mission_id)
            if not current_step:
                return {
                    "success": False,
                    "error": "No active step found",
                }

            # Validate
            success = await self.engine.validate_step(mission_id)

            if success:
                # Check if there's a next step
                next_step = await self.engine.get_current_step(mission_id)
                if next_step:
                    return {
                        "success": True,
                        "completed": False,
                        "next_step": next_step,
                        "message": f"Step {int(current_step['index']) + 1} complete!",
                    }

                # Mission complete
                progress = await self.engine.get_mission_status(mission_id)
                return {
                    "success": True,
                    "completed": True,
                    "xp_earned": progress.get("xp_earned", 0) if progress else 0,
                    "message": "Mission Complete! 🎉",
                }

            return {
                "success": False,
                "error": "Step validation failed",
                "message": "Validation failed. Check your work and try again.",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Validation error: {e}",
            }

    async def get_hint(self, mission_id: str) -> str | None:
        """Get hint for current step.

        Args:
            mission_id: Mission identifier

        Returns:
            Hint text or None if unavailable
        """
        try:
            return await self.engine.get_hint(mission_id)
        except Exception:
            return None

    async def abandon_mission(self, mission_id: str) -> bool:
        """Abandon current mission.

        Args:
            mission_id: Mission identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            await self.engine.abandon_mission(mission_id)
            return True
        except Exception:
            return False

    async def get_progress(self, mission_id: str | None = None) -> dict[str, Any]:
        """Get mission progress.

        Args:
            mission_id: Optional mission ID for specific progress

        Returns:
            Dictionary with progress information
        """
        if mission_id:
            try:
                status = await self.engine.get_mission_status(mission_id)
                return status if status else {}
            except Exception:
                return {}

        # TODO: Implement overall progress retrieval
        return {
            "total_xp": 0,
            "missions_completed": 0,
            "active_missions": 0,
        }


# Global engine wrapper instance for TUI
_engine_wrapper: TUIEngineWrapper | None = None


def get_engine_wrapper() -> TUIEngineWrapper:
    """Get or create the global engine wrapper instance.

    Returns:
        TUIEngineWrapper instance
    """
    global _engine_wrapper
    if _engine_wrapper is None:
        _engine_wrapper = TUIEngineWrapper()
    return _engine_wrapper
