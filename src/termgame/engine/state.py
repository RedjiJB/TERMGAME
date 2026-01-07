"""Mission state management.

This module defines the in-memory state representation for active missions,
tracking current progress and container information.
"""

from dataclasses import dataclass, field

from termgame.models.scenario import Scenario, Step
from termgame.runtimes.base import Container


@dataclass
class MissionState:
    """In-memory state for an active mission.

    Tracks the current step, completed steps, and container information
    for a mission in progress.

    Attributes:
        mission_id: Unique mission identifier.
        user_id: User ID who started the mission.
        scenario: Loaded scenario definition.
        container: Running container for this mission.
        current_step_index: Index of current step (0-based).
        completed_steps: List of completed step IDs.
    """

    mission_id: str
    user_id: int
    scenario: Scenario
    container: Container
    current_step_index: int = 0
    completed_steps: list[str] = field(default_factory=list)

    @property
    def current_step(self) -> Step | None:
        """Get current step from scenario.

        Returns:
            Current Step object, or None if all steps completed.
        """
        if self.current_step_index < len(self.scenario.steps):
            return self.scenario.steps[self.current_step_index]
        return None

    @property
    def is_completed(self) -> bool:
        """Check if all steps completed.

        Returns:
            True if current_step_index >= total steps, False otherwise.
        """
        return self.current_step_index >= len(self.scenario.steps)

    def advance_step(self) -> None:
        """Move to next step.

        Adds current step ID to completed_steps and increments the index.
        Does nothing if already at the end.
        """
        if not self.is_completed:
            current = self.current_step
            if current:
                self.completed_steps.append(current.id)
            self.current_step_index += 1
