"""Pytest configuration and fixtures."""

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
