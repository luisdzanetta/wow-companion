"""Analytics service: queries snapshot history and builds personal reports."""

from sqlalchemy.orm import Session

from app.db.repositories.characters import CharacterRepository
from app.db.repositories.snapshots import SnapshotRepository
from app.domain.analytics import CharacterReport, build_character_report
from app.db.models import Character


class AnalyticsService:
    """Application service for character analytics."""

    def __init__(self, session: Session):
        self.session = session
        self.character_repo = CharacterRepository(session)
        self.snapshot_repo = SnapshotRepository(session)

    def get_character_report(self, character: Character) -> CharacterReport:
        """Build a full analytics report for a character."""
        weekly = self.snapshot_repo.list_latest_per_week(character.id)
        total = self.snapshot_repo.count_total(character.id)
        return build_character_report(
            weekly_snapshots=weekly, total_snapshot_count=total
        )

    def get_report_by_identity(
        self, region: str, realm: str, character_name: str
    ) -> CharacterReport | None:
        """Find character and build report. Returns None if char not found."""
        realm_slug = realm.lower().replace(" ", "-").replace("'", "")
        name_slug = character_name.lower()
        char = self.character_repo.get_by_identity(region, realm_slug, name_slug)
        if char is None:
            return None
        return self.get_character_report(char)