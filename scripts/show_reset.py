"""Show the current weekly reset window and confirm edge cases."""

from datetime import datetime, timezone
from app.domain.time import get_current_reset_window


def fmt(dt: datetime) -> str:
    return dt.strftime("%A %Y-%m-%d %H:%M UTC")


if __name__ == "__main__":
    # --- Current window ---
    window = get_current_reset_window("us")
    print("Current US reset window:")
    print(f"  start: {fmt(window.start)}")
    print(f"  end:   {fmt(window.end)}")
    print(f"  id:    {window.iso_week_id}")
    print()

    # --- Edge case tests ---
    print("Edge case tests (US region):")
    cases = [
        ("Tuesday 14:59 UTC (pre-reset)", datetime(2026, 4, 14, 14, 59, tzinfo=timezone.utc)),
        ("Tuesday 15:00 UTC (reset moment)", datetime(2026, 4, 14, 15, 0, tzinfo=timezone.utc)),
        ("Tuesday 15:01 UTC (post-reset)", datetime(2026, 4, 14, 15, 1, tzinfo=timezone.utc)),
        ("Friday noon UTC", datetime(2026, 4, 17, 12, 0, tzinfo=timezone.utc)),
        ("Monday 23:59 UTC", datetime(2026, 4, 20, 23, 59, tzinfo=timezone.utc)),
    ]
    for label, moment in cases:
        w = get_current_reset_window("us", now=moment)
        print(f"  {label}")
        print(f"    → window {w.iso_week_id}: {fmt(w.start)} to {fmt(w.end)}")