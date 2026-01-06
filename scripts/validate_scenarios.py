#!/usr/bin/env python
"""Validate all scenario YAML files.

This script checks that all scenario files in the scenarios/ directory
are valid and follow the correct schema.
"""

import sys
from pathlib import Path

import yaml


def validate_scenario(file_path: Path) -> bool:
    """Validate a single scenario file.

    Args:
        file_path: Path to scenario YAML file.

    Returns:
        True if valid, False otherwise.
    """
    try:
        with open(file_path) as f:
            data = yaml.safe_load(f)

        # Basic validation
        if "mission" not in data:
            print(f"ERROR: {file_path} - Missing 'mission' section")
            return False

        print(f"OK: {file_path}")
        return True

    except Exception as e:
        print(f"ERROR: {file_path} - {e}")
        return False


def main() -> int:
    """Main entry point."""
    scenarios_dir = Path(__file__).parent.parent / "scenarios"

    if not scenarios_dir.exists():
        print("ERROR: scenarios/ directory not found")
        return 1

    yaml_files = list(scenarios_dir.rglob("*.yml")) + list(scenarios_dir.rglob("*.yaml"))

    if not yaml_files:
        print("No scenario files found")
        return 0

    results = [validate_scenario(f) for f in yaml_files]

    print(f"\nValidated {len(results)} scenarios")
    print(f"Passed: {sum(results)}, Failed: {len(results) - sum(results)}")

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
