"""Service that seeds synthetic snapshot history into the database.

Orchestrates: stat generation → vault projection → snapshot persistence.
Idempotent: rerunning won't duplicate snapshots for the same week.
"""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.db.models import Character
from app.db.repositories.characters import CharacterRepository
from app.db.repositories.snapshots import SnapshotRepository
from app.domain.models import Dungeon, MythicRun, WeeklyMythicSummary
from app.domain.time import get_current_reset_window
from app.domain.vault import project_vault
from app.synthetic.history_generator import SyntheticWeekStats, generate_history


PLACEHOLDER_DUNGEON = Dungeon(id=0, name="Synthetic Dungeon")


def _build_runs(stats: SyntheticWeekStats) -> list[MythicRun]:
    """Convert raw keystone levels into MythicRun objects for vault projection."""
    return [
        MythicRun(
            keystone_level=level,
            dungeon=PLACEHOLDER_DUNGEON,
            completed_timestamp_ms=0,  # placeholder — synthetic
            duration_ms=1_800_000,     # 30 min placeholder
            is_completed_within_time=True,
        )
        for level in stats.keystone_levels
    ]


class SyntheticSeedService:
    """Coordinates the seeding of synthetic history for a character."""

    def __init__(self, session: Session):
        self.session = session
        self.character_repo = CharacterRepository(session)
        self.snapshot_repo = SnapshotRepository(session)

    def seed_character(
        self,
        region: str,
        realm: str,
        character_name: str,
        num_weeks: int = 12,
        seed: int = 42,
    ) -> dict:
        """Seed `num_weeks` of synthetic snapshots for a character.

        Idempotent: if a snapshot already exists for a target week, that week
        is skipped (preserves whatever already exists).

        Returns a summary dict for reporting.
        """
        # 1. Get or create the character
        char, created = self.character_repo.get_or_create(
            region=region, realm=realm, character_name=character_name
        )

        # 2. Determine target weeks (working backwards from current week)
        current_window = get_current_reset_window(region=region)
        # Week offset 0 = oldest (num_weeks-1 weeks ago), num_weeks-1 = most recent past
        # We skip the CURRENT week so we don't overwrite real data.
        target_windows = [
            self._past_window(current_window, weeks_ago=num_weeks - i)
            for i in range(num_weeks)
        ]

        # 3. Generate synthetic stats and persist as snapshots
        history = generate_history(num_weeks=num_weeks, seed=seed)
        created_count = 0
        skipped_count = 0

        for stats, window in zip(history, target_windows):
            existing = self.snapshot_repo.latest_for_week(char.id, window.iso_week_id)
            if existing:
                skipped_count += 1
                continue

            self._persist_synthetic_snapshot(char, stats, window)
            created_count += 1

        self.session.commit()

        return {
            "character": char.display_name,
            "character_created": created,
            "weeks_created": created_count,
            "weeks_skipped_existing": skipped_count,
        }

    def _past_window(self, current_window, weeks_ago: int):
        """Return a ResetWindow shifted `weeks_ago` weeks before `current_window`."""
        from app.domain.time import ResetWindow
        delta = timedelta(weeks=weeks_ago)
        return ResetWindow(
            start=current_window.start - delta,
            end=current_window.end - delta,
        )

    def _persist_synthetic_snapshot(
        self, char: Character, stats: SyntheticWeekStats, window
    ) -> None:
        """Build a single snapshot from synthetic stats and save it."""
        runs = _build_runs(stats)
        summary = WeeklyMythicSummary(runs=runs, current_score=stats.mythic_rating)
        projection = project_vault(summary)

        # Snapshot timestamp: just before that week's reset (i.e. end of the week)
        taken_at = window.end - timedelta(hours=1)

        # Mark this snapshot as synthetic in the raw_data field — transparency
        raw_data = {
            "_synthetic": True,
            "_generator_seed": 42,
            "synthetic_stats": {
                "week_offset": stats.week_offset,
                "run_count": stats.run_count,
                "keystone_levels": stats.keystone_levels,
            },
        }

        self.snapshot_repo.create(
            character_id=char.id,
            week_id=window.iso_week_id,
            raw_data=raw_data,
            mythic_rating=stats.mythic_rating,
            weekly_run_count=stats.run_count,
            vault_slot_1_level=projection.slots[0].reward_keystone_level,
            vault_slot_2_level=projection.slots[1].reward_keystone_level,
            vault_slot_3_level=projection.slots[2].reward_keystone_level,
            vault_slot_1_ilvl=projection.slots[0].reward_ilvl,
            vault_slot_2_ilvl=projection.slots[1].reward_ilvl,
            vault_slot_3_ilvl=projection.slots[2].reward_ilvl,
            taken_at=taken_at,
        )