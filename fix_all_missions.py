#!/usr/bin/env python3
"""
Comprehensive mission schema fixer.
Fixes all validation errors in newly created missions.
"""

import re
from pathlib import Path
from typing import Any

import yaml


def fix_mission_data(data: dict[str, Any]) -> dict[str, Any]:
    """Fix mission data structure to match expected schema."""

    # Fix mission metadata
    if "mission" in data:
        mission = data["mission"]

        # Fix estimated_time: convert "30 minutes" to 30
        if "estimated_time" in mission:
            if isinstance(mission["estimated_time"], str):
                match = re.search(r"(\d+)", mission["estimated_time"])
                if match:
                    mission["estimated_time"] = int(match.group(1))

        # Fix difficulty: expert/master/practice -> advanced
        if "difficulty" in mission:
            if mission["difficulty"] in ["expert", "master", "practice"]:
                mission["difficulty"] = "advanced"

    # Fix environment
    if "environment" in data:
        env = data["environment"]

        # Fix runtime/base_image -> image
        if "runtime" in env and "image" not in env:
            env["image"] = "ubuntu:22.04"
            del env["runtime"]

        if "base_image" in env:
            env["image"] = env["base_image"]
            del env["base_image"]

        # Fix setup: convert multiline string to list
        if "setup" in env and isinstance(env["setup"], str):
            # Parse multiline string into list of commands
            commands = [line.strip() for line in env["setup"].strip().split("\n") if line.strip()]
            env["setup"] = commands

    # Fix steps
    if "steps" in data:
        for step in data["steps"]:
            # Add missing title (use description as title if missing)
            if "title" not in step:
                if "description" in step:
                    # Use first line of description as title
                    desc_lines = step["description"].strip().split("\n")
                    step["title"] = desc_lines[0][:50]  # First 50 chars
                else:
                    step["title"] = step.get("id", "Step").replace("-", " ").title()

            # Fix validation: convert list to dict
            if "validation" in step:
                val = step["validation"]

                # If validation is a list, take first item
                if isinstance(val, list):
                    step["validation"] = val[0] if val else {}
                    val = step["validation"]

                # Add missing matcher field (infer from type)
                if isinstance(val, dict) and "matcher" not in val:
                    if val.get("type") == "command-output":
                        if "comparison" in val:
                            val["matcher"] = val["comparison"]
                            del val["comparison"]
                        else:
                            val["matcher"] = "contains"  # Default
                    elif val.get("type") == "file-exists":
                        val["matcher"] = "exists"

    # Add missing completion section
    if "completion" not in data:
        difficulty = data.get("mission", {}).get("difficulty", "intermediate")
        xp_map = {"beginner": 200, "intermediate": 300, "advanced": 550}
        data["completion"] = {
            "message": f"Congratulations! You've completed this {difficulty} mission.",
            "xp": xp_map.get(difficulty, 300),
            "unlocks": [],
        }

    return data


def fix_mission_file(filepath: Path) -> bool:
    """Fix a single mission file."""
    print(f"Fixing: {filepath.name}...", end=" ")

    try:
        # Read YAML
        with open(filepath, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Fix data structure
        fixed_data = fix_mission_data(data)

        # Write back
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(fixed_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        print("OK")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    # Directories to scan
    week_dirs = [
        Path("scenarios/linux/week2"),
        Path("scenarios/linux/week3"),
        Path("scenarios/linux/week4"),
        Path("scenarios/linux/week5"),
        Path("scenarios/linux/week6"),
        Path("scenarios/linux/week7"),
        Path("scenarios/linux/week9"),
        Path("scenarios/linux/week10"),
        Path("scenarios/linux/week11"),
        Path("scenarios/linux/week13"),
        Path("scenarios/linux/week14"),
    ]

    # Mission patterns to fix
    missions_to_fix = [
        # Originally fixed missions
        "command-line-mastery-advanced",
        "navigation-advanced-intermediate",
        "file-basics-beginner",
        "advanced-find-techniques",
        "command-basics-beginner",
        "advanced-text-processing",
        "environment-basics-beginner",
        "shell-config-intermediate",
        "filesystem-basics-beginner",
        "links-inodes-intermediate",
        "disk-basics-beginner",
        "disk-analysis-intermediate",
        "process-basics-beginner",
        "job-control-intermediate",
        "practice-process-troubleshooting",
        "shell-scripting-intermediate",
        "shell-scripting-advanced",
        "shell-scripting-expert",
        # Additional missions with errors
        "compression-advanced",
        "compression-basics-beginner",
        "cron-advanced",
        "practice-backup-automation",
        "shell-scripting-beginner",
        "shell-scripting-master",
        "practice-log-parsing",
        "practice-remote-admin",
        "ssh-basics-beginner",
        "ssh-keys-intermediate",
        "practice-log-analysis",
        "practice-environment-debugging",
        "practice-disk-optimization",
    ]

    print("=" * 60)
    print("Mission Schema Fixer")
    print("=" * 60)
    print()

    fixed = 0
    failed = 0

    for week_dir in week_dirs:
        if not week_dir.exists():
            continue

        for yml_file in week_dir.glob("*.yml"):
            if any(pattern in yml_file.stem for pattern in missions_to_fix):
                if fix_mission_file(yml_file):
                    fixed += 1
                else:
                    failed += 1

    print()
    print("=" * 60)
    print(f"Results: {fixed} fixed, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
