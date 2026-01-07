"""Database models using SQLAlchemy.

This module defines all SQLAlchemy ORM models for persistent storage
of users, mission progress, and achievements.
"""

from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""


class User(Base):
    """User account and profile.

    Tracks user information and total experience points earned.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # Relationships
    progress: Mapped[list["MissionProgress"]] = relationship(back_populates="user")


class MissionProgress(Base):
    """Track user progress through missions.

    Stores current state of active missions and completed missions,
    including container information and step completion history.
    """

    __tablename__ = "mission_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    mission_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Current state
    current_step_id: Mapped[str | None] = mapped_column(String(255))
    current_step_index: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Container information
    container_id: Mapped[str | None] = mapped_column(String(255))
    container_name: Mapped[str | None] = mapped_column(String(255))

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Metadata
    steps_completed: Mapped[list[str]] = mapped_column(JSON, default=list)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="progress")


class Achievement(Base):
    """Track user achievements and mission completions.

    Records when users complete missions and the XP awarded.
    """

    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    mission_id: Mapped[str] = mapped_column(String(255), nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    xp_awarded: Mapped[int] = mapped_column(Integer)
