"""Show a personal analytics report for a character.

Usage:
    python -m scripts.show_report                                    # default char
    python -m scripts.show_report --char Stormtroll --realm Thrall
"""

import argparse

from app.db.engine import SessionLocal
from app.services.analytics_service import AnalyticsService


def parse_args():
    parser = argparse.ArgumentParser(description="Show analytics for a character.")
    parser.add_argument("--region", default="us")
    parser.add_argument("--char", default="Stormpaladin")
    parser.add_argument("--realm", default="Alterac Mountains")
    return parser.parse_args()


def fmt_delta(delta: float | None) -> str:
    if delta is None:
        return "(no prior week)"
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta}"


if __name__ == "__main__":
    args = parse_args()

    session = SessionLocal()
    try:
        service = AnalyticsService(session)
        report = service.get_report_by_identity(
            region=args.region, realm=args.realm, character_name=args.char
        )

        if report is None:
            print(f"Character not found: {args.char}-{args.realm} ({args.region})")
            print("Run 'python -m scripts.take_snapshot' first.")
            exit(1)

        print(f"=== Report: {args.char}-{args.realm} ===\n")

        print(f"Total snapshots taken:      {report.total_snapshots}")
        print(f"Distinct weeks tracked:     {report.distinct_weeks}")
        print(f"Weeks with full vault (3/3): {report.weeks_with_full_vault}")
        print(f"Average runs per week:      {report.average_runs_per_week}")
        print()
        print(f"Best rating ever:    {report.best_rating_ever} (week {report.best_rating_week_id})")
        print(f"Current rating:      {report.current_rating}")
        print(f"Delta vs prior week: {fmt_delta(report.rating_delta_last_week)}")
        print()

        if report.weekly_trend:
            print("Weekly trend:")
            print(f"  {'week':<10} {'rating':<8} {'runs':<5} {'vault':<7} {'best ilvl'}")
            print(f"  {'-' * 10} {'-' * 8} {'-' * 5} {'-' * 7} {'-' * 9}")
            for w in report.weekly_trend:
                vault = f"{w.vault_slots_filled}/3"
                ilvl = str(w.best_vault_ilvl) if w.best_vault_ilvl else "-"
                print(
                    f"  {w.week_id:<10} {w.mythic_rating:<8.1f} "
                    f"{w.weekly_run_count:<5} {vault:<7} {ilvl}"
                )

    finally:
        session.close()