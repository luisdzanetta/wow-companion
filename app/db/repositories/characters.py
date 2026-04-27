"""Repository for Character entity: encapsulates all DB operations."""

from sqlalchemy.orm import Session

from app.db.models import Character


class CharacterRepository:
    """Data access for Character records."""

    def __init__(self, session: Session):
        self.session = session

    # --- Read ---

    def get_by_id(self, character_id: int) -> Character | None:
        return self.session.get(Character, character_id)

    def get_by_identity(
        self, region: str, realm_slug: str, name_slug: str
    ) -> Character | None:
        """Find a character by its natural identity tuple."""
        return (
            self.session.query(Character)
            .filter_by(
                region=region.lower(),
                realm_slug=realm_slug.lower(),
                name_slug=name_slug.lower(),
            )
            .first()
        )

    def list_all(self) -> list[Character]:
        return self.session.query(Character).order_by(Character.display_name).all()

    # --- Write ---

    def create(
        self, region: str, realm: str, character_name: str
    ) -> Character:
        """Create and persist a new Character."""
        char = Character(
            region=region.lower(),
            realm_slug=realm.lower().replace(" ", "-").replace("'", ""),
            name_slug=character_name.lower(),
            display_name=character_name,
        )
        self.session.add(char)
        self.session.flush()  # assigns the auto-generated id without committing
        return char

    def get_or_create(
        self, region: str, realm: str, character_name: str
    ) -> tuple[Character, bool]:
        """Return existing Character or create a new one.

        Returns:
            (character, created) where `created` is True if a new row was inserted.
        """
        realm_slug = realm.lower().replace(" ", "-").replace("'", "")
        name_slug = character_name.lower()

        existing = self.get_by_identity(region, realm_slug, name_slug)
        if existing:
            return existing, False

        new_char = self.create(region=region, realm=realm, character_name=character_name)
        return new_char, True