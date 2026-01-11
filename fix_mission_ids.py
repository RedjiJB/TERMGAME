#!/usr/bin/env python3
"""Fix mission IDs to include linux/ prefix."""

from pathlib import Path

import yaml


def fix_mission_id(mission_file: Path, scenarios_dir: Path):
    """Fix mission ID to match file path."""
    with open(mission_file, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Get the relative path
    rel_path = mission_file.relative_to(scenarios_dir)
    expected_id = "linux/" + str(rel_path.with_suffix("")).replace("\\", "/")

    current_id = data.get("mission", {}).get("id", "")

    if current_id != expected_id:
        print(f"Fixing {mission_file.name}")
        print(f"  Current: {current_id}")
        print(f"  New: {expected_id}")

        # Update the ID
        data["mission"]["id"] = expected_id

        # Write back
        with open(mission_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        return True

    return False


def main():
    """Fix all mission IDs."""
    scenarios_dir = Path("scenarios/linux")

    if not scenarios_dir.exists():
        print(f"Error: {scenarios_dir} not found")
        return 1

    fixed_count = 0

    for mission_file in sorted(scenarios_dir.rglob("*.yml")):
        if fix_mission_id(mission_file, scenarios_dir):
            fixed_count += 1

    print(f"\nFixed {fixed_count} mission IDs")
    return 0


if __name__ == "__main__":
    exit(main())
