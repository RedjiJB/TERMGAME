#!/usr/bin/env python3
"""Validate all mission YAML files."""

from pathlib import Path

from termgame.loaders.scenario_loader import ScenarioLoader


def main():
    scenarios_dir = Path("scenarios")
    loader = ScenarioLoader(scenarios_dir)

    missions = []
    errors = []

    for yaml_file in scenarios_dir.rglob("*.yml"):
        if yaml_file.name.startswith("_"):
            continue

        rel_path = yaml_file.relative_to(scenarios_dir)
        mission_id = str(rel_path.with_suffix("")).replace("\\", "/")

        try:
            scenario = loader.load(mission_id)
            missions.append(mission_id)
            print(f"[OK] {mission_id}")
        except Exception as e:
            errors.append((mission_id, str(e)))
            print(f"[ERROR] {mission_id}: {e}")

    print(f"\n{len(missions)} missions loaded successfully")
    if errors:
        print(f"{len(errors)} missions had errors:")
        for mission_id, error in errors:
            print(f"  - {mission_id}: {error}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
