"""Mission engine exceptions.

This module defines the exception hierarchy for the mission engine,
providing clear error semantics for different failure modes.
"""


class MissionEngineError(Exception):
    """Base exception for mission engine errors.

    All mission engine exceptions inherit from this base class,
    allowing for catch-all error handling when needed.
    """


class MissionNotFoundError(MissionEngineError):
    """Mission scenario not found or failed to load."""


class MissionAlreadyActiveError(MissionEngineError):
    """Attempt to start a mission that is already active."""


class ContainerCreationError(MissionEngineError):
    """Error creating or managing container environment."""


class ValidationFailedError(MissionEngineError):
    """Step validation failed or encountered an error."""


class StepNotFoundError(MissionEngineError):
    """Step ID not found in mission scenario."""


class ScenarioLoadError(MissionEngineError):
    """Error loading or parsing scenario YAML file."""
