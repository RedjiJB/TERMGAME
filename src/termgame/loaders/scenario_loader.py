"""YAML scenario loader with caching.

This module provides a loader for mission scenarios stored in YAML files,
with built-in caching to avoid re-parsing the same files.
"""

from pathlib import Path

import yaml
from pydantic import ValidationError

from termgame.engine.exceptions import ScenarioLoadError
from termgame.models.scenario import Scenario


class ScenarioLoader:
    """Load and cache mission scenarios from YAML files.

    The loader parses YAML files into Pydantic Scenario models and
    caches them in memory for efficient repeated access.

    Args:
        scenarios_dir: Root directory containing scenario YAML files.
    """

    def __init__(self, scenarios_dir: Path) -> None:
        """Initialize scenario loader.

        Args:
            scenarios_dir: Root directory containing scenario YAML files.
        """
        self.scenarios_dir = scenarios_dir
        self._cache: dict[str, Scenario] = {}

    def load(self, mission_id: str) -> Scenario:
        """Load a scenario by mission ID.

        The mission ID is converted to a file path by appending .yml extension.
        For example, 'linux/basics/navigation' becomes 'linux/basics/navigation.yml'.

        Args:
            mission_id: Mission identifier (e.g., 'linux/basics/navigation').

        Returns:
            Parsed Scenario model.

        Raises:
            ScenarioLoadError: If scenario file not found or invalid.
        """
        # Check cache first
        if mission_id in self._cache:
            return self._cache[mission_id]

        # Convert mission_id to file path
        scenario_path = self.scenarios_dir / f"{mission_id}.yml"

        if not scenario_path.exists():
            msg = f"Scenario file not found: {scenario_path}"
            raise ScenarioLoadError(msg)

        # Load and parse YAML
        try:
            with scenario_path.open("r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            msg = f"Invalid YAML in {scenario_path}: {e}"
            raise ScenarioLoadError(msg) from e
        except OSError as e:
            msg = f"Error reading {scenario_path}: {e}"
            raise ScenarioLoadError(msg) from e

        # Validate with Pydantic model
        try:
            scenario = Scenario(**yaml_data)
        except ValidationError as e:
            msg = f"Invalid scenario structure in {scenario_path}: {e}"
            raise ScenarioLoadError(msg) from e

        # Cache and return
        self._cache[mission_id] = scenario
        return scenario

    def clear_cache(self, mission_id: str | None = None) -> None:
        """Clear scenario cache.

        Args:
            mission_id: Specific mission to clear, or None to clear all.
        """
        if mission_id:
            self._cache.pop(mission_id, None)
        else:
            self._cache.clear()
