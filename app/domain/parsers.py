"""Parsers: convert raw API JSON into domain models.

This layer isolates the rest of the app from external API shapes. If Blizzard
changes a field name, only the parsing code needs to update.
"""

from app.domain.models import Dungeon, MythicRun, WeeklyMythicSummary


def parse_mythic_run(raw: dict) -> MythicRun:
    """Parse a single run from the Battle.net best_runs array."""
    return MythicRun(
        keystone_level=raw["keystone_level"],
        dungeon=Dungeon(
            id=raw["dungeon"]["id"],
            name=raw["dungeon"]["name"],
        ),
        completed_timestamp_ms=raw["completed_timestamp"],
        duration_ms=raw["duration"],
        is_completed_within_time=raw["is_completed_within_time"],
    )


def parse_weekly_summary(profile: dict) -> WeeklyMythicSummary:
    """Parse the full M+ profile response into a weekly summary."""
    best_runs_raw = profile.get("current_period", {}).get("best_runs", [])
    runs = [parse_mythic_run(r) for r in best_runs_raw]

    current_score = profile.get("current_mythic_rating", {}).get("rating", 0.0)

    return WeeklyMythicSummary(runs=runs, current_score=current_score)