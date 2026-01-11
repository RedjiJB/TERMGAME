#!/usr/bin/env python3
"""Fix mission schema validation errors."""

import re
from pathlib import Path


def fix_mission_file(filepath):
    """Fix common schema issues in a mission file."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original = content
    changes = []

    # 1. Fix estimated_time: "30 minutes" -> estimated_time: 30
    if match := re.search(r'estimated_time:\s*"(\d+)\s*minutes?"', content):
        old = match.group(0)
        new = f"estimated_time: {match.group(1)}"
        content = content.replace(old, new)
        changes.append("Fixed estimated_time format")

    # 2. Fix difficulty: expert/master -> advanced
    for invalid in ["expert", "master", "practice"]:
        if f'difficulty: "{invalid}"' in content or f"difficulty: {invalid}" in content:
            content = re.sub(rf'difficulty:\s*"?{invalid}"?', "difficulty: advanced", content)
            changes.append(f"Changed difficulty from {invalid} to advanced")

    # 3. Fix environment.runtime or environment.base_image -> environment.image
    if "runtime:" in content and "image:" not in content:
        # Replace runtime: "docker" with proper image
        content = re.sub(
            r'environment:\s*\n\s*runtime:\s*"docker"',
            'environment:\n  image: "ubuntu:22.04"',
            content,
        )
        changes.append("Fixed environment.runtime -> environment.image")

    if "base_image:" in content:
        content = content.replace("base_image:", "image:")
        changes.append("Fixed base_image -> image")

    # 4. Fix environment.setup from string to list
    # Look for setup: | pattern
    setup_match = re.search(r"setup:\s*\|\s*\n((?:\s{4,}.*\n)+)", content)
    if setup_match:
        setup_block = setup_match.group(1)
        # Convert multiline string to list
        commands = [line.strip() for line in setup_block.split("\n") if line.strip()]
        list_format = "\n".join(f'    - "{cmd}"' for cmd in commands)
        content = content.replace(setup_match.group(0), f"setup:\n{list_format}\n")
        changes.append("Fixed environment.setup format (string -> list)")

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return changes
    return None


# Find all new mission files
week_dirs = [
    "scenarios/linux/week2",
    "scenarios/linux/week3",
    "scenarios/linux/week4",
    "scenarios/linux/week5",
    "scenarios/linux/week6",
    "scenarios/linux/week7",
    "scenarios/linux/week9",
    "scenarios/linux/week11",
]

print("Fixing mission schema issues...")
print("=" * 50)

fixed_count = 0
for week_dir in week_dirs:
    week_path = Path(week_dir)
    if not week_path.exists():
        continue

    for yml_file in week_path.glob("*.yml"):
        changes = fix_mission_file(yml_file)
        if changes:
            fixed_count += 1
            print(f"\n✓ {yml_file.name}")
            for change in changes:
                print(f"  - {change}")

print(f"\n{'=' * 50}")
print(f"Fixed {fixed_count} mission files")
print("\nNote: Additional manual fixes may be needed for:")
print("  - Steps missing 'title' field")
print("  - Validation as list instead of object")
print("  - Missing 'matcher' field in validation")
print("  - Missing 'completion' section")
