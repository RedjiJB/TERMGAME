"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from termgame.models import Mission


def test_mission_creation(sample_mission_data):
    """Test creating a Mission model."""
    mission = Mission(**sample_mission_data)
    assert mission.id == "test/sample"
    assert mission.title == "Sample Mission"


def test_mission_validation():
    """Test Mission model validation."""
    with pytest.raises(ValidationError):
        Mission(id="")  # Missing required fields
