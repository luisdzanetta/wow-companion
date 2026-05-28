"""Seed the database with synthetic history for analytics demonstration.

⚠️ This generates FAKE data for portfolio purposes. Real data comes from
   `scripts/take_snapshot.py`. Each synthetic snapshot is flagged as such
   in its raw_data field.

Usage:
    python -m scripts.seed_synthetic_history
    python -m scripts.seed_synthetic_history --char Stormtroll --realm Thrall --weeks 12
"""

import argparse

from app.db.engine import SessionLocal
from app.synthetic.seed_service import SyntheticSeedService


def parse_args():
    parser = argparse.ArgumentParser(description="Seed synthetic snapshot history.")
    parser.add_argument("--region", default="us")
    parser.add_argument("--char", default="Stormtroll")
    parser.add_argument("--realm", default="Thrall")
    parser.add_argument("--weeks", type=int, default=12)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    session = SessionLocal()
    try:
        service = SyntheticSeedService(session)
        result = service.seed_character(
            region=args.region,
            realm=args.realm,
            character_name=args.char,
            num_weeks=args.weeks,
            seed=args.seed,
        )

        print(f"Synthetic seeding completed for {result['character']}")
        print(f"  Character created: {result['character_created']}")
        print(f"  Weeks newly seeded: {result['weeks_created']}")
        print(f"  Weeks skipped (already had data): {result['weeks_skipped_existing']}")
    finally:
        session.close()