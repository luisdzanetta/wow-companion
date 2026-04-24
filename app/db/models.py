"""ORM models for persistent storage.

Design note: each Snapshot stores both the raw JSON response and denormalized
columns for fast queries. Raw JSON enables reprocessing; denormalized columns
enable analytical queries without JSON parsing.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    """Return current UTC time. Wrapped in a function so it's called at insert time."""
    return datetime.now(timezone.utc)


class Character(Base):
    """A WoW character we track."""

    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Natural identity (case-insensitive, stored lowercase)
    region: Mapped[str] = mapped_column(String(4), nullable=False)
    realm_slug: Mapped[str] = mapped_column(String(64), nullable=False)
    name_slug: Mapped[str] = mapped_column(String(64), nullable=False)

    # Display name (keeps original casing, e.g. "Stormpaladin")
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationship: one character has many snapshots
    snapshots: Mapped[list["Snapshot"]] = relationship(
        back_populates="character",
        cascade="all, delete-orphan",
        order_by="Snapshot.taken_at.desc()",
    )

    __table_args__ = (
        UniqueConstraint("region", "realm_slug", "name_slug", name="uq_character_identity"),
    )

    def __repr__(self) -> str:
        return f"<Character id={self.id} {self.display_name}-{self.realm_slug} ({self.region})>"


class Snapshot(Base):
    """A point-in-time snapshot of a character's state, sourced from the API."""

    __tablename__ = "snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )

    taken_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    week_id: Mapped[str] = mapped_column(String(8), nullable=False)  # e.g. "2026-W16"

    # Full raw API response — preserved for reprocessing
    raw_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Denormalized fields for fast analytical queries
    mythic_rating: Mapped[float] = mapped_column(nullable=False, default=0.0)
    weekly_run_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Vault projection (nullable because slots may be locked)
    vault_slot_1_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vault_slot_2_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vault_slot_3_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vault_slot_1_ilvl: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vault_slot_2_ilvl: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vault_slot_3_ilvl: Mapped[int | None] = mapped_column(Integer, nullable=True)

    character: Mapped["Character"] = relationship(back_populates="snapshots")

    __table_args__ = (
        Index("ix_snapshot_character_week", "character_id", "week_id"),
        Index("ix_snapshot_taken_at", "taken_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Snapshot id={self.id} char={self.character_id} "
            f"week={self.week_id} runs={self.weekly_run_count}>"
        )