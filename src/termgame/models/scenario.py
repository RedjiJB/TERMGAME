"""Scenario data model."""

from pydantic import BaseModel, ConfigDict, Field


class Scenario(BaseModel):
    """Represents a mission scenario loaded from YAML.

    Scenarios define the structure and validation rules for missions.
    """

    model_config = ConfigDict(frozen=True)

    mission_id: str = Field(..., description="Mission identifier")
    version: str = Field("1.0", description="Scenario version")
