"""Pytest configuration and fixtures."""

from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def sample_mission_data():
    """Provide sample mission data for testing."""
    return {
        "id": "test/sample",
        "title": "Sample Mission",
        "description": "A sample mission for testing",
        "difficulty": "beginner",
    }


@pytest.fixture
def valid_mission_schema() -> dict[str, Any]:
    """Provide a complete valid mission schema."""
    return {
        "mission": {
            "id": "linux/test/sample-mission",
            "title": "Sample Test Mission",
            "difficulty": "beginner",
            "description": "A comprehensive test mission for validation",
            "estimated_time": 15,
            "tags": ["linux", "test", "sample"],
        },
        "environment": {
            "image": "ubuntu:22.04",
            "workdir": "/home/learner",
            "setup": [
                "mkdir -p /home/learner/test",
                "echo 'test' > /home/learner/test/file.txt",
            ],
        },
        "steps": [
            {
                "id": "step-1",
                "title": "First Step",
                "description": "This is the first step",
                "hint": "Try running the command",
                "validation": {
                    "type": "command-output",
                    "command": "cat test/file.txt",
                    "matcher": "contains",
                    "expected": "test",
                },
            },
        ],
        "completion": {
            "message": "Great job! You completed the test mission.",
            "xp": 200,
            "unlocks": [],
        },
    }


@pytest.fixture
def beginner_mission() -> dict[str, Any]:
    """Provide a beginner difficulty mission."""
    return {
        "id": "linux/basics/test-beginner",
        "title": "Beginner Test",
        "difficulty": "beginner",
        "time": 10,
        "description": "A beginner level test mission",
    }


@pytest.fixture
def intermediate_mission() -> dict[str, Any]:
    """Provide an intermediate difficulty mission."""
    return {
        "id": "linux/intermediate/test-intermediate",
        "title": "Intermediate Test",
        "difficulty": "intermediate",
        "time": 30,
        "description": "An intermediate level test mission",
    }


@pytest.fixture
def advanced_mission() -> dict[str, Any]:
    """Provide an advanced difficulty mission."""
    return {
        "id": "linux/advanced/test-advanced",
        "title": "Advanced Test",
        "difficulty": "advanced",
        "time": 60,
        "description": "An advanced level test mission",
    }


@pytest.fixture
def mission_list(beginner_mission, intermediate_mission, advanced_mission):
    """Provide a list of missions with mixed difficulties."""
    return [beginner_mission, intermediate_mission, advanced_mission]


@pytest.fixture
def scenarios_directory() -> Path:
    """Get the scenarios directory path."""
    return Path("scenarios/linux")


@pytest.fixture
def topic_based_topics():
    """Provide list of expected topic-based directories."""
    return [
        "navigation",
        "file-operations",
        "text-processing",
        "environment",
        "filesystem",
        "disk-management",
        "processes",
        "automation",
        "scripting",
        "networking",
        "remote-access",
    ]


@pytest.fixture
def difficulty_order():
    """Provide difficulty sorting order."""
    return {
        "beginner": 0,
        "intermediate": 1,
        "advanced": 2,
    }


@pytest.fixture
def expected_docker_packages():
    """Provide list of packages expected in Docker image."""
    return [
        "nano",
        "vim",
        "gzip",
        "bzip2",
        "tar",
        "zip",
        "unzip",
        "curl",
        "wget",
        "htop",
        "grep",
        "sed",
        "awk",
        "cron",
        "sudo",
        "git",
        "make",
        "bc",
    ]


@pytest.fixture
def docker_image_name():
    """Provide the Docker image name."""
    return "termgame/ubuntu-full:latest"


@pytest.fixture
def dockerfile_path():
    """Provide the Dockerfile path."""
    return Path("docker/Dockerfile.ubuntu-full")
