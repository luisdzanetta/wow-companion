"""Personal analytics over a character's snapshot history.

Pure domain logic that consumes Snapshot data and returns insights. The
service/script layer is responsible for fetching snapshots and presenting
results — this module only computes.
"""

from dataclasses import dataclass
from datetime import datetime

from app.db.models import Snapshot


@dataclass(frozen=True)
class WeeklyTrend:
    """A single data point in a character's weekly progression."""

    week_id: str
    taken_at: datetime
    mythic_rating: float
    weekly_run_count: int
    vault_slots_filled: int  # 0-3
    best_vault_ilvl: int | None  # max ilvl across the 3 slots, None if all locked


@dataclass(frozen=True)
class CharacterReport:
    """Aggregate report for a character across all stored history."""

    total_snapshots: int
    distinct_weeks: int
    weeks_with_full_vault: int
    average_runs_per_week: float
    best_rating_ever: float
    best_rating_week_id: str | None
    current_rating: float
    rating_delta_last_week: float | None  # change vs previous week
    weekly_trend: list[WeeklyTrend]


def _vault_slots_filled(snapshot: Snapshot) -> int:
    """Count how many vault slots are filled (have a level set)."""
    return sum(
        1
        for level in (
            snapshot.vault_slot_1_level,
            snapshot.vault_slot_2_level,
            snapshot.vault_slot_3_level,
        )
        if level is not None
    )


def _best_vault_ilvl(snapshot: Snapshot) -> int | None:
    """Max ilvl across the 3 slots, or None if all locked."""
    ilvls = [
        ilvl
        for ilvl in (
            snapshot.vault_slot_1_ilvl,
            snapshot.vault_slot_2_ilvl,
            snapshot.vault_slot_3_ilvl,
        )
        if ilvl is not None
    ]
    return max(ilvls) if ilvls else None


def build_weekly_trend(snapshots: list[Snapshot]) -> list[WeeklyTrend]:
    """Convert a list of weekly snapshots (one per week) into trend data points."""
    return [
        WeeklyTrend(
            week_id=s.week_id,
            taken_at=s.taken_at,
            mythic_rating=s.mythic_rating,
            weekly_run_count=s.weekly_run_count,
            vault_slots_filled=_vault_slots_filled(s),
            best_vault_ilvl=_best_vault_ilvl(s),
        )
        for s in snapshots
    ]


def build_character_report(
    weekly_snapshots: list[Snapshot],
    total_snapshot_count: int,
) -> CharacterReport:
    """Build an aggregate report from a character's weekly snapshots.

    Args:
        weekly_snapshots: One snapshot per week, oldest first.
            (Use SnapshotRepository.list_latest_per_week.)
        total_snapshot_count: Raw count of all snapshots ever taken
            (typically larger than len(weekly_snapshots)).
    """
    if not weekly_snapshots:
        return CharacterReport(
            total_snapshots=total_snapshot_count,
            distinct_weeks=0,
            weeks_with_full_vault=0,
            average_runs_per_week=0.0,
            best_rating_ever=0.0,
            best_rating_week_id=None,
            current_rating=0.0,
            rating_delta_last_week=None,
            weekly_trend=[],
        )

    trend = build_weekly_trend(weekly_snapshots)

    full_vault_count = sum(1 for w in trend if w.vault_slots_filled == 3)
    avg_runs = sum(w.weekly_run_count for w in trend) / len(trend)

    best_week = max(trend, key=lambda w: w.mythic_rating)
    current = trend[-1]

    rating_delta = None
    if len(trend) >= 2:
        rating_delta = round(current.mythic_rating - trend[-2].mythic_rating, 1)

    return CharacterReport(
        total_snapshots=total_snapshot_count,
        distinct_weeks=len(trend),
        weeks_with_full_vault=full_vault_count,
        average_runs_per_week=round(avg_runs, 1),
        best_rating_ever=best_week.mythic_rating,
        best_rating_week_id=best_week.week_id,
        current_rating=current.mythic_rating,
        rating_delta_last_week=rating_delta,
        weekly_trend=trend,
    )