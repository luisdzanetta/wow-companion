"""Take a fresh snapshot of a character and store it in the DB.

Usage:
    python -m scripts.take_snapshot                                 # default char
    python -m scripts.take_snapshot --char Stormtroll --realm Thrall
"""

import argparse

from app.db.engine import SessionLocal
from app.services.snapshot_service import SnapshotService


def parse_args():
    parser = argparse.ArgumentParser(description="Take a snapshot of a character.")
    parser.add_argument("--region", default="us")
    parser.add_argument("--char", default="Stormpaladin")
    parser.add_argument("--realm", default="Alterac Mountains")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    session = SessionLocal()
    try:
        service = SnapshotService(session)
        result = service.take_snapshot(
            region=args.region, realm=args.realm, character_name=args.char
        )

        char_status = "(new)" if result.character_created else "(existing)"
        print(f"Character: {result.character.display_name}-{result.character.realm_slug} {char_status}")
        print(f"Week: {result.week_id}")
        print(f"Snapshot ID: {result.snapshot.id}")
        print(f"Taken at:  {result.snapshot.taken_at}")
        print()
        print(result.projection)

    finally:
        session.close()