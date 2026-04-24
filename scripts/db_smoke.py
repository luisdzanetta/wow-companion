"""Smoke test: create a character, read it back."""

from app.db.engine import SessionLocal
from app.db.models import Character

if __name__ == "__main__":
    session = SessionLocal()
    try:
        # Check if Stormpaladin already exists (so we can re-run this script)
        existing = session.query(Character).filter_by(
            region="us", realm_slug="alterac-mountains", name_slug="stormpaladin"
        ).first()

        if existing:
            print(f"Found existing: {existing!r}")
        else:
            new_char = Character(
                region="us",
                realm_slug="alterac-mountains",
                name_slug="stormpaladin",
                display_name="Stormpaladin",
            )
            session.add(new_char)
            session.commit()
            session.refresh(new_char)
            print(f"Created: {new_char!r}")

        # List all characters
        all_chars = session.query(Character).all()
        print(f"\nAll characters in DB ({len(all_chars)}):")
        for char in all_chars:
            print(f"  {char!r}")

    finally:
        session.close()