"""Smoke test: exercise the Character repository."""

from app.db.engine import SessionLocal
from app.db.repositories.characters import CharacterRepository

if __name__ == "__main__":
    session = SessionLocal()
    try:
        repo = CharacterRepository(session)

        # Idempotent: get_or_create handles "already exists" case
        char, created = repo.get_or_create(
            region="us",
            realm="Alterac Mountains",
            character_name="Stormpaladin",
        )
        status = "Created" if created else "Found existing"
        print(f"{status}: {char!r}")

        char2, created2 = repo.get_or_create(
            region="us",
            realm="Thrall",
            character_name="Stormtroll",
        )
        status2 = "Created" if created2 else "Found existing"
        print(f"{status2}: {char2!r}")

        session.commit()

        # List all
        print("\nAll characters in DB:")
        for c in repo.list_all():
            print(f"  {c!r}")

    finally:
        session.close()