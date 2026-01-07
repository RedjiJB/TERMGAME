"""Game engine and mission state management.

This package contains the core game engine that manages mission execution,
state transitions, validation, and progression.
"""

from termgame.engine.exceptions import (
    ContainerCreationError,
    MissionAlreadyActiveError,
    MissionEngineError,
    MissionNotFoundError,
    NoActiveMissionError,
    ScenarioLoadError,
    StepNotFoundError,
    ValidationFailedError,
)
from termgame.engine.factory import create_mission_engine
from termgame.engine.mission_engine import MissionEngine
from termgame.engine.state import MissionState

__all__ = [
    "ContainerCreationError",
    "MissionAlreadyActiveError",
    "MissionEngine",
    "MissionEngineError",
    "MissionNotFoundError",
    "MissionState",
    "NoActiveMissionError",
    "ScenarioLoadError",
    "StepNotFoundError",
    "ValidationFailedError",
    "create_mission_engine",
]
