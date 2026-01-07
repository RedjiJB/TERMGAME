"""Scenario data models matching YAML structure.

This module defines Pydantic models that represent the complete structure
of mission YAML files, including metadata, environment setup, steps, and completion criteria.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MissionMetadata(BaseModel):
    """Mission metadata from YAML."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Unique mission identifier")
    title: str = Field(..., description="Mission title")
    difficulty: Literal["beginner", "intermediate", "advanced"] = Field(
        ..., description="Difficulty level"
    )
    description: str = Field(..., description="Mission description")
    estimated_time: int = Field(..., description="Estimated completion time in minutes")
    tags: list[str] = Field(default_factory=list, description="Mission tags")


class Environment(BaseModel):
    """Container environment configuration."""

    model_config = ConfigDict(frozen=True)

    image: str = Field(..., description="Docker/Podman container image")
    setup: list[str] = Field(default_factory=list, description="Setup commands to run in container")


class StepValidation(BaseModel):
    """Validation rules for a mission step."""

    model_config = ConfigDict(frozen=True)

    type: Literal["command-output", "file-content", "file-exists"] = Field(
        ..., description="Validation type"
    )
    command: str | None = Field(None, description="Command to execute for validation")
    file: str | None = Field(None, description="File path to check")
    matcher: Literal["exact", "contains", "regex", "exists"] = Field(
        ..., description="Matcher type for validation"
    )
    expected: str | None = Field(None, description="Expected value or pattern")


class Step(BaseModel):
    """Mission step definition."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Unique step identifier")
    title: str = Field(..., description="Step title")
    description: str = Field(..., description="Step description and instructions")
    hint: str = Field(..., description="Hint to help user complete the step")
    validation: StepValidation = Field(..., description="Validation rules for this step")


class Completion(BaseModel):
    """Mission completion configuration."""

    model_config = ConfigDict(frozen=True)

    message: str = Field(..., description="Completion message shown to user")
    xp: int = Field(..., description="Experience points awarded for completion")
    unlocks: list[str] = Field(
        default_factory=list, description="Mission IDs unlocked upon completion"
    )


class Scenario(BaseModel):
    """Complete scenario loaded from YAML file.

    Represents the full structure of a mission scenario including
    metadata, environment setup, step-by-step instructions with validation,
    and completion criteria.
    """

    model_config = ConfigDict(frozen=True)

    mission: MissionMetadata = Field(..., description="Mission metadata")
    environment: Environment = Field(..., description="Container environment setup")
    steps: list[Step] = Field(..., description="Ordered list of mission steps")
    completion: Completion = Field(..., description="Completion configuration and rewards")
