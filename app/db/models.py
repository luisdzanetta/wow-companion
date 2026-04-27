"""ORM models for persistent storage.

Design note: each Snapshot stores both the raw JSON response and denormalized
columns for fast queries. Raw JSON enables reprocessing; denormalized columns
enable analytical queries without JSON parsing.

Timezone handling: SQLite doesn't preserve tzinfo natively. We work around this
by (1) always writing UTC datetimes, (2) using a TypeDecorator that re-attaches
UTC tzinfo on read. The rest of the codebase can rely on every datetime being
timezone-aware UTC.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    TypeDecorator,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    """Return current UTC time as a timezone-aware datetime."""
    return datetime.now(timezone.utc)


class UTCDateTime(TypeDecorator):
    """DateTime column that ensures values are always UTC and timezone-aware.

    On write: converts to UTC if needed, raises if naive.
    On read: re-attaches UTC tzinfo (SQLite drops it).
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError(
                "Naive datetime not allowed. Pass a timezone-aware datetime "
                "(use app.db.models.utc_now())."
            )
        return value.astimezone(timezone.utc)

    def process_result_value(self, value: datetime | None, dialect):
        if value is None:
            return None
        # SQLite returns naive datetime; mark as UTC
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class Character(Base):
    """A WoW character we track."""

    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    region: Mapped[str] = mapped_column(String(4), nullable=False)
    realm_slug: Mapped[str] = mapped_column(String(64), nullable=False)
    name_slug: Mapped[str] = mapped_column(String(64), nullable=False)
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, nullable=False
    )

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
        UTCDateTime, default=utc_now, nullable=False
    )
    week_id: Mapped[str] = mapped_column(String(8), nullable=False)

    raw_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    mythic_rating: Mapped[float] = mapped_column(nullable=False, default=0.0)
    weekly_run_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

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