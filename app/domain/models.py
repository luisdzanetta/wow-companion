"""Domain models for the WoW Companion app.

These Pydantic models represent WoW concepts at the business-logic level,
decoupled from the raw JSON structure returned by external APIs. They act as
a stable interface: even if the Battle.net API changes field names, only the
parsing layer needs to adapt — the rest of the app keeps using these models.
"""

from datetime import datetime, timezone
from pydantic import BaseModel, Field, computed_field


class Dungeon(BaseModel):
    """A Mythic+ dungeon."""

    id: int
    name: str


class MythicRun(BaseModel):
    """A single Mythic+ run completed by a character.

    Represents one keystone attempt, successful or not, that counts toward
    the Great Vault in the current weekly period.
    """

    keystone_level: int = Field(..., ge=0, description="Keystone difficulty level")
    dungeon: Dungeon
    completed_timestamp_ms: int = Field(
        ..., description="Unix timestamp in milliseconds (as returned by Battle.net)"
    )
    duration_ms: int = Field(..., description="Run duration in milliseconds")
    is_completed_within_time: bool

    @computed_field
    @property
    def completed_at(self) -> datetime:
        """Convert the ms timestamp to a timezone-aware datetime (UTC)."""
        return datetime.fromtimestamp(self.completed_timestamp_ms / 1000, tz=timezone.utc)

    @computed_field
    @property
    def duration_minutes(self) -> float:
        """Run duration in minutes (1 decimal place precision)."""
        return round(self.duration_ms / 1000 / 60, 1)

    def __repr__(self) -> str:
        status = "timed" if self.is_completed_within_time else "overtime"
        return f"+{self.keystone_level} {self.dungeon.name} ({status})"


class WeeklyMythicSummary(BaseModel):
    """Aggregated summary of a character's M+ activity for the current weekly period."""

    runs: list[MythicRun] = Field(default_factory=list)
    current_score: float = Field(default=0.0, description="Overall M+ score for the season")

    @computed_field
    @property
    def run_count(self) -> int:
        return len(self.runs)

    @computed_field
    @property
    def runs_sorted_by_level(self) -> list[MythicRun]:
        """Runs ordered from highest to lowest keystone level."""
        return sorted(self.runs, key=lambda r: r.keystone_level, reverse=True)