"""Exploratory script: dump the M+ profile JSON to understand the API structure.

Usage:
    python -m scripts.explore_mplus                                    # fixture mode
    python -m scripts.explore_mplus --live                             # live, default char
    python -m scripts.explore_mplus --live --char Stormpaladin --realm "Alterac Mountains"
"""

import argparse
import json
import sys
from pathlib import Path

from app.apis.battlenet import get_access_token, get_mythic_keystone_profile

DEFAULT_CHARACTER = "Stormtroll"
DEFAULT_REALM = "Thrall"
FIXTURE_PATH = Path("tests/fixtures/mplus_profile_sample.json")


def load_from_fixture() -> dict:
    """Load M+ profile from the local fixture file."""
    with open(FIXTURE_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_from_api(character: str, realm: str) -> dict:
    """Fetch M+ profile from the live Battle.net API."""
    token = get_access_token()
    return get_mythic_keystone_profile(token, realm=realm, character_name=character)


def parse_args():
    parser = argparse.ArgumentParser(description="Explore the M+ profile endpoint.")
    parser.add_argument("--live", action="store_true", help="Fetch from live API instead of fixture")
    parser.add_argument("--char", default=DEFAULT_CHARACTER, help="Character name")
    parser.add_argument("--realm", default=DEFAULT_REALM, help="Realm name")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.live:
        print(f"Fetching live M+ profile for {args.char}-{args.realm}...\n")
        try:
            profile = load_from_api(args.char, args.realm)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

        # Save live response to inspect later (gitignored)
        output_path = Path(f"scripts/_mplus_profile_{args.char.lower()}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        print(f"Full JSON saved to: {output_path}\n")
    else:
        print(f"Loading M+ profile from fixture: {FIXTURE_PATH}\n")
        profile = load_from_fixture()

    # Summary
    print("Top-level keys:")
    for key, value in profile.items():
        if isinstance(value, list):
            print(f"  - {key}: list with {len(value)} item(s)")
        elif isinstance(value, dict):
            print(f"  - {key}: dict with keys {list(value.keys())}")
        else:
            print(f"  - {key}: {value}")

    best_runs = profile.get("current_period", {}).get("best_runs", [])
    print(f"\nWeekly runs: {len(best_runs)}")

    if best_runs:
        print("\nRuns (sorted by keystone level, descending):")
        sorted_runs = sorted(best_runs, key=lambda r: r["keystone_level"], reverse=True)
        for i, run in enumerate(sorted_runs, 1):
            timed = "in time" if run["is_completed_within_time"] else "OVERTIME"
            dungeon = run["dungeon"]["name"]
            level = run["keystone_level"]
            print(f"  {i:2d}. +{level:2d}  {dungeon:30s}  ({timed})")