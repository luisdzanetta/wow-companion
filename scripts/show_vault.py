"""Show the Great Vault projection for the character in the fixture."""

import json
from pathlib import Path

from app.domain.parsers import parse_weekly_summary
from app.domain.vault import project_vault

FIXTURE_PATH = Path("tests/fixtures/mplus_profile_sample.json")

if __name__ == "__main__":
    with open(FIXTURE_PATH, encoding="utf-8") as f:
        raw_profile = json.load(f)

    summary = parse_weekly_summary(raw_profile)
    projection = project_vault(summary)

    print(projection)
    print()
    print(f"Current M+ score: {summary.current_score:.1f}")