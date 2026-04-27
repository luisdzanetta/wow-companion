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
    # --- Analytics ---

    def list_latest_per_week(self, character_id: int) -> list[Snapshot]:
        """Return one snapshot per week (the most recent of each), oldest first.

        Useful as the canonical "weekly history" of a character.
        """
        from sqlalchemy import func, and_

        # Subquery: for each week, find the most recent taken_at
        latest_subq = (
            self.session.query(
                Snapshot.week_id.label("week_id"),
                func.max(Snapshot.taken_at).label("max_taken_at"),
            )
            .filter(Snapshot.character_id == character_id)
            .group_by(Snapshot.week_id)
            .subquery()
        )

        # Main query: snapshots that match (week_id, max_taken_at)
        return (
            self.session.query(Snapshot)
            .join(
                latest_subq,
                and_(
                    Snapshot.week_id == latest_subq.c.week_id,
                    Snapshot.taken_at == latest_subq.c.max_taken_at,
                ),
            )
            .filter(Snapshot.character_id == character_id)
            .order_by(Snapshot.week_id.asc())
            .all()
        )

    def count_total(self, character_id: int) -> int:
        """Return total number of snapshots stored for a character."""
        return (
            self.session.query(Snapshot)
            .filter_by(character_id=character_id)
            .count()
        )

    def count_distinct_weeks(self, character_id: int) -> int:
        """Return number of distinct weeks the character has snapshots for."""
        from sqlalchemy import func, distinct

        return (
            self.session.query(func.count(distinct(Snapshot.week_id)))
            .filter(Snapshot.character_id == character_id)
            .scalar()
        )