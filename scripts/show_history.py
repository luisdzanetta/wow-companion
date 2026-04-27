"""Show the snapshot history for all characters in the DB."""

from app.db.engine import SessionLocal
from app.db.repositories.characters import CharacterRepository
from app.db.repositories.snapshots import SnapshotRepository


def fmt_slot(level: int | None, ilvl: int | None) -> str:
    if level is None:
        return "🔒"
    return f"+{level}/{ilvl}"


if __name__ == "__main__":
    session = SessionLocal()
    try:
        char_repo = CharacterRepository(session)
        snap_repo = SnapshotRepository(session)

        chars = char_repo.list_all()
        if not chars:
            print("No characters in DB.")
            exit()

        for char in chars:
            print(f"\n=== {char.display_name}-{char.realm_slug} ({char.region}) ===")
            snapshots = snap_repo.list_for_character(char.id, limit=10)
            if not snapshots:
                print("  No snapshots yet.")
                continue

            print(f"  {'taken_at':<26} {'week':<10} {'rating':<8} {'runs':<5} vault")
            print(f"  {'-' * 26} {'-' * 10} {'-' * 8} {'-' * 5} {'-' * 30}")
            for s in snapshots:
                slot1 = fmt_slot(s.vault_slot_1_level, s.vault_slot_1_ilvl)
                slot2 = fmt_slot(s.vault_slot_2_level, s.vault_slot_2_ilvl)
                slot3 = fmt_slot(s.vault_slot_3_level, s.vault_slot_3_ilvl)
                taken = s.taken_at.strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"  {taken:<26} {s.week_id:<10} "
                    f"{s.mythic_rating:<8.1f} {s.weekly_run_count:<5} "
                    f"{slot1} | {slot2} | {slot3}"
                )

    finally:
        session.close()