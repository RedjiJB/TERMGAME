"""Mission data model."""

from pydantic import BaseModel, ConfigDict, Field


class Mission(BaseModel):
    """Represents a training mission.

    Missions are composed of multiple steps that guide users through
    learning objectives.
    """

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Unique mission identifier")
    title: str = Field(..., description="Mission title")
    description: str = Field(..., description="Mission description")
    difficulty: str = Field("beginner", description="Difficulty level")
