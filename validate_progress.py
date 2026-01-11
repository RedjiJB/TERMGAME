#!/usr/bin/env python3
"""
Quick validation script for TermGame progress.

Runs essential tests to validate recent improvements:
- Mission schema compliance
- Topic-based organization
- No week/course references
- Docker image essentials
"""

import subprocess
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def run_command(cmd, description):
    """Run a command and report status."""
    print(f"→ {description}...")
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if result.returncode == 0:
        print("  ✓ PASSED\n")
        return True
    print("  ✗ FAILED\n")
    if result.stdout:
        print("  Output:", result.stdout[:500])
    if result.stderr:
        print("  Error:", result.stderr[:500])
    return False


def main():
    """Run validation checks."""
    print_header("TermGame Progress Validation")

    results = {}

    # Check 1: Mission Schema Validation
    print_header("1. Mission Schema Validation")
    results["schema"] = run_command(
        ["pytest", "tests/unit/test_mission_schema.py::TestMissionSchema", "-q"],
        "Validating all mission schemas",
    )

    # Check 2: Organization Validation
    print_header("2. Mission Organization")
    results["organization"] = run_command(
        ["pytest", "tests/unit/test_mission_schema.py::TestMissionOrganization", "-q"],
        "Validating topic-based organization",
    )

    # Check 3: Mission Counts
    print_header("3. Mission Count & Distribution")
    results["counts"] = run_command(
        ["pytest", "tests/unit/test_mission_schema.py::TestMissionCounts", "-q"],
        "Validating mission counts and difficulty distribution",
    )

    # Check 4: Data Integrity
    print_header("4. Data Integrity")
    results["integrity"] = run_command(
        [
            "pytest",
            "tests/integration/test_mission_data_integrity.py::TestMissionDataIntegrity",
            "-q",
        ],
        "Validating mission data integrity",
    )

    # Check 5: CLI Functionality
    print_header("5. CLI & Interactive Mode")
    results["cli"] = run_command(
        ["pytest", "tests/unit/test_cli_list.py::TestCLIListCommand", "-q"],
        "Validating CLI list functionality",
    )

    # Check 6: Dockerfile (optional, skip if not available)
    print_header("6. Docker Configuration (Optional)")
    dockerfile = Path("docker/Dockerfile.ubuntu-full")
    if dockerfile.exists():
        results["docker_config"] = run_command(
            [
                "pytest",
                "tests/integration/test_docker_image.py::TestDockerImageBuild::test_dockerfile_exists",
                "-q",
            ],
            "Validating Docker configuration",
        )
    else:
        print("  ⊘ Skipped (Docker not configured)\n")
        results["docker_config"] = None

    # Summary
    print_header("Validation Summary")

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len([v for v in results.values() if v is not None])

    print(f"  Total Tests:  {total}")
    print(f"  ✓ Passed:     {passed}")
    print(f"  ✗ Failed:     {failed}")
    print(f"  ⊘ Skipped:    {skipped}")
    print()

    if failed == 0:
        print("  🎉 All validation checks passed!")
        print()
        return 0
    print(f"  ⚠️  {failed} validation check(s) failed")
    print()
    print("  Run full test suite for details:")
    print("    pytest tests/ -v")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
