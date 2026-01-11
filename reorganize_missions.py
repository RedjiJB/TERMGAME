#!/usr/bin/env python3
"""
Reorganize missions to remove week references and use topic-based structure.
"""

import re
from pathlib import Path
from typing import Any

import yaml

# Mapping from week directories to topic-based directories
DIRECTORY_MAPPING = {
    "week2": "navigation",
    "week3": "file-operations",
    "week4": "text-processing",
    "week5": "environment",
    "week6": "filesystem",
    "week7": "disk-management",
    "week9": "processes",
    "week10": "automation",
    "week11": "scripting",
    "week13": "networking",
    "week14": "remote-access",
}


def update_mission_content(data: dict[str, Any], old_week: str, new_topic: str) -> dict[str, Any]:
    """Update mission content to remove week references."""

    # Update mission ID
    if "mission" in data:
        mission = data["mission"]

        # Update ID: linux/week2/xxx -> linux/navigation/xxx
        if "id" in mission:
            mission["id"] = mission["id"].replace(f"/{old_week}/", f"/{new_topic}/")

        # Remove week and course tags
        if "tags" in mission:
            tags = mission["tags"]
            # Remove weekX and cst8207 tags
            tags = [tag for tag in tags if not re.match(r"^week\d+$", tag) and tag != "cst8207"]
            # Add topic tag if not present
            if new_topic not in tags:
                tags.append(new_topic)
            mission["tags"] = tags

    return data


def process_mission_file(filepath: Path, old_week: str, new_topic: str, new_dir: Path) -> bool:
    """Process a single mission file."""
    print(f"  Processing: {filepath.name}...", end=" ")

    try:
        # Read YAML
        with open(filepath, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Update content
        updated_data = update_mission_content(data, old_week, new_topic)

        # Write to new location
        new_file = new_dir / filepath.name
        with open(new_file, "w", encoding="utf-8") as f:
            yaml.dump(
                updated_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True
            )

        print("OK")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def reorganize_missions():
    """Main reorganization function."""
    base_path = Path("scenarios/linux")

    print("=" * 70)
    print("Mission Reorganization - Remove Week References")
    print("=" * 70)
    print()

    print("Directory Mapping:")
    for old_week, new_topic in DIRECTORY_MAPPING.items():
        print(f"  {old_week:15s} -> {new_topic}")
    print()

    total_processed = 0
    total_failed = 0

    # Process each week directory
    for old_week, new_topic in DIRECTORY_MAPPING.items():
        old_dir = base_path / old_week
        new_dir = base_path / new_topic

        if not old_dir.exists():
            print(f"Skipping {old_week}: directory not found")
            continue

        print(f"\n{old_week} -> {new_topic}")
        print("-" * 70)

        # Create new directory
        new_dir.mkdir(exist_ok=True)

        # Process each mission file
        mission_files = list(old_dir.glob("*.yml"))
        print(f"Found {len(mission_files)} missions")

        for mission_file in mission_files:
            if process_mission_file(mission_file, old_week, new_topic, new_dir):
                total_processed += 1
            else:
                total_failed += 1

    print()
    print("=" * 70)
    print(f"Results: {total_processed} processed, {total_failed} failed")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Review the new directories in scenarios/linux/")
    print("2. Test that missions load correctly")
    print("3. Delete old week directories if everything works")
    print("4. Update documentation (README, CHANGELOG, etc.)")


if __name__ == "__main__":
    reorganize_missions()
