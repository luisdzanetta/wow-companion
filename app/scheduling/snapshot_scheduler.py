"""Scheduled snapshot job.

Runs as a long-lived process. Periodically takes snapshots of configured
characters and persists them to the database.

Uses BackgroundScheduler (runs in a separate thread) so the main thread
stays responsive to user input — making it easy to stop with Ctrl+C or
typing 'quit' in the terminal.

Designed to be run via `python -m scripts.run_scheduler`.
"""

import logging
from dataclasses import dataclass

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.apis.battlenet import get_access_token
from app.db.engine import SessionLocal
from app.services.snapshot_service import SnapshotService


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CharacterToTrack:
    """A character configured for scheduled snapshotting."""

    region: str
    realm: str
    character_name: str


def snapshot_job(characters: list[CharacterToTrack]) -> None:
    """Take snapshots for all configured characters.

    One scheduler tick → one shared access_token → multiple snapshots.
    """
    logger.info("Starting scheduled snapshot job for %d character(s)", len(characters))

    token = get_access_token()
    session = SessionLocal()
    try:
        service = SnapshotService(session)
        for char in characters:
            try:
                result = service.take_snapshot(
                    region=char.region,
                    realm=char.realm,
                    character_name=char.character_name,
                    access_token=token,
                )
                logger.info(
                    "Snapshot OK: %s (week=%s, runs=%d, rating=%.1f)",
                    result.character.display_name,
                    result.week_id,
                    result.snapshot.weekly_run_count,
                    result.snapshot.mythic_rating,
                )
            except Exception:
                logger.exception(
                    "Snapshot FAILED for %s-%s",
                    char.character_name, char.realm,
                )
    finally:
        session.close()

    logger.info("Snapshot job finished")


def build_scheduler(
    characters: list[CharacterToTrack],
    hour: int = 18,
    minute: int = 0,
) -> BackgroundScheduler:
    """Create a background scheduler that runs `snapshot_job` daily at the given UTC time."""
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        func=snapshot_job,
        trigger=CronTrigger(hour=hour, minute=minute),
        kwargs={"characters": characters},
        id="daily_snapshot",
        replace_existing=True,
        max_instances=1,
    )
    return scheduler