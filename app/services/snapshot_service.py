"""Snapshot service: orchestrates fetching, parsing, and persisting character state.

This is the application layer that coordinates multiple subsystems (API client,
domain logic, persistence) to fulfill a use case: "take a snapshot of a character
this week".
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.apis.battlenet import (
    get_access_token,
    get_mythic_keystone_profile,
)
from app.db.models import Character, Snapshot
from app.db.repositories.characters import CharacterRepository
from app.db.repositories.snapshots import SnapshotRepository
from app.domain.parsers import parse_weekly_summary
from app.domain.time import get_current_reset_window
from app.domain.vault import VaultProjection, project_vault


@dataclass(frozen=True)
class SnapshotResult:
    """Outcome of a snapshot operation."""

    character: Character
    snapshot: Snapshot
    projection: VaultProjection
    week_id: str
    character_created: bool  # True if a new Character was inserted


class SnapshotService:
    """Coordinates snapshot creation across API, domain, and DB layers."""

    def __init__(self, session: Session):
        self.session = session
        self.character_repo = CharacterRepository(session)
        self.snapshot_repo = SnapshotRepository(session)

    def take_snapshot(
        self,
        region: str,
        realm: str,
        character_name: str,
        access_token: str | None = None,
    ) -> SnapshotResult:
        """Fetch fresh data from the API and persist a snapshot.

        Args:
            region: 'us' or 'eu'.
            realm: Realm name (any casing — will be normalized).
            character_name: Character name (any casing).
            access_token: Optional pre-fetched token. If None, fetches a new one.

        Returns:
            SnapshotResult with the persisted entities and computed projection.
        """
        # 1. Fetch from API
        token = access_token or get_access_token()
        raw_profile = get_mythic_keystone_profile(
            access_token=token, realm=realm, character_name=character_name
        )

        # 2. Parse into domain models
        summary = parse_weekly_summary(raw_profile)

        # 3. Compute vault projection
        projection = project_vault(summary)

        # 4. Determine current week
        week = get_current_reset_window(region=region)

        # 5. Persist character (idempotent)
        character, created = self.character_repo.get_or_create(
            region=region, realm=realm, character_name=character_name
        )

        # 6. Persist snapshot
        snapshot = self.snapshot_repo.create(
            character_id=character.id,
            week_id=week.iso_week_id,
            raw_data=raw_profile,
            mythic_rating=summary.current_score,
            weekly_run_count=summary.run_count,
            vault_slot_1_level=projection.slots[0].reward_keystone_level,
            vault_slot_2_level=projection.slots[1].reward_keystone_level,
            vault_slot_3_level=projection.slots[2].reward_keystone_level,
            vault_slot_1_ilvl=projection.slots[0].reward_ilvl,
            vault_slot_2_ilvl=projection.slots[1].reward_ilvl,
            vault_slot_3_ilvl=projection.slots[2].reward_ilvl,
        )

        # 7. Commit transaction
        self.session.commit()
        self.session.refresh(character)
        self.session.refresh(snapshot)

        return SnapshotResult(
            character=character,
            snapshot=snapshot,
            projection=projection,
            week_id=week.iso_week_id,
            character_created=created,
        )