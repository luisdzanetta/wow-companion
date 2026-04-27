"""Repository for Snapshot entity."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Snapshot


class SnapshotRepository:
    """Data access for Snapshot records."""

    def __init__(self, session: Session):
        self.session = session

    # --- Read ---

    def get_by_id(self, snapshot_id: int) -> Snapshot | None:
        return self.session.get(Snapshot, snapshot_id)

    def list_for_character(
        self, character_id: int, limit: int | None = None
    ) -> list[Snapshot]:
        """Return snapshots for a character, newest first."""
        query = (
            self.session.query(Snapshot)
            .filter_by(character_id=character_id)
            .order_by(Snapshot.taken_at.desc())
        )
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def latest_for_character(self, character_id: int) -> Snapshot | None:
        """Return the most recent snapshot for a character, or None."""
        return (
            self.session.query(Snapshot)
            .filter_by(character_id=character_id)
            .order_by(Snapshot.taken_at.desc())
            .first()
        )

    def latest_for_week(
        self, character_id: int, week_id: str
    ) -> Snapshot | None:
        """Return the most recent snapshot for a character within a given week."""
        return (
            self.session.query(Snapshot)
            .filter_by(character_id=character_id, week_id=week_id)
            .order_by(Snapshot.taken_at.desc())
            .first()
        )

    # --- Write ---

    def create(
        self,
        character_id: int,
        week_id: str,
        raw_data: dict,
        mythic_rating: float,
        weekly_run_count: int,
        vault_slot_1_level: int | None = None,
        vault_slot_2_level: int | None = None,
        vault_slot_3_level: int | None = None,
        vault_slot_1_ilvl: int | None = None,
        vault_slot_2_ilvl: int | None = None,
        vault_slot_3_ilvl: int | None = None,
        taken_at: datetime | None = None,
    ) -> Snapshot:
        """Create and persist a new Snapshot."""
        snapshot = Snapshot(
            character_id=character_id,
            week_id=week_id,
            raw_data=raw_data,
            mythic_rating=mythic_rating,
            weekly_run_count=weekly_run_count,
            vault_slot_1_level=vault_slot_1_level,
            vault_slot_2_level=vault_slot_2_level,
            vault_slot_3_level=vault_slot_3_level,
            vault_slot_1_ilvl=vault_slot_1_ilvl,
            vault_slot_2_ilvl=vault_slot_2_ilvl,
            vault_slot_3_ilvl=vault_slot_3_ilvl,
        )
        if taken_at is not None:
            snapshot.taken_at = taken_at
        self.session.add(snapshot)
        self.session.flush()
        return snapshot