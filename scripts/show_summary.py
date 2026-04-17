"""Show a weekly M+ summary using the domain models."""

import json
from pathlib import Path

from app.domain.parsers import parse_weekly_summary

FIXTURE_PATH = Path("tests/fixtures/mplus_profile_sample.json")

if __name__ == "__main__":
    with open(FIXTURE_PATH, encoding="utf-8") as f:
        raw_profile = json.load(f)

    summary = parse_weekly_summary(raw_profile)

    print(f"Current M+ score: {summary.current_score:.1f}")
    print(f"Weekly runs: {summary.run_count}")
    print()
    print("Runs (sorted by keystone level):")
    for run in summary.runs_sorted_by_level:
        print(
            f"  {run!r}  "
            f"[duration: {run.duration_minutes} min, "
            f"completed at: {run.completed_at.strftime('%Y-%m-%d %H:%M UTC')}]"
        )