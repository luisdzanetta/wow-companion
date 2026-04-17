"""Weekly reset window calculations.

WoW has region-specific weekly resets. All times are handled in UTC internally;
conversion to local time happens only at presentation layer.

Reset times (UTC):
  - US / Latin America / Oceania: Tuesday 15:00
  - Europe: Wednesday 07:00
  - Korea / Taiwan: Thursday (various times)
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class ResetConfig:
    """Day and hour (UTC) when the weekly reset happens.

    `weekday` follows Python convention: Monday=0, Tuesday=1, ..., Sunday=6.
    """

    weekday: int
    hour: int


RESET_BY_REGION = {
    "us": ResetConfig(weekday=1, hour=15),  # Tuesday 15:00 UTC
    "eu": ResetConfig(weekday=2, hour=7),   # Wednesday 07:00 UTC
}


@dataclass(frozen=True)
class ResetWindow:
    """The start and end of a weekly period (reset-to-reset)."""

    start: datetime  # inclusive
    end: datetime    # exclusive

    def contains(self, moment: datetime) -> bool:
        return self.start <= moment < self.end

    @property
    def iso_week_id(self) -> str:
        """A stable identifier for the week, e.g. '2026-W16'."""
        year, week, _ = self.start.isocalendar()
        return f"{year}-W{week:02d}"


def get_current_reset_window(region: str, now: datetime | None = None) -> ResetWindow:
    """Return the reset window that contains `now` for the given region.

    Args:
        region: 'us' or 'eu' (case-insensitive).
        now: Reference moment. Defaults to datetime.now(UTC). Accepts any
             timezone-aware datetime; it will be converted to UTC.

    Returns:
        A ResetWindow where start <= now < end.

    Raises:
        ValueError: if region is unknown or `now` is naive (no tzinfo).
    """
    region = region.lower()
    if region not in RESET_BY_REGION:
        raise ValueError(f"Unknown region: {region!r}. Supported: {list(RESET_BY_REGION)}")

    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        raise ValueError("`now` must be timezone-aware (pass a datetime with tzinfo).")
    else:
        now = now.astimezone(timezone.utc)

    config = RESET_BY_REGION[region]

    # Days since the most recent reset weekday. If it's the same weekday but
    # before reset hour, we still belong to the previous week.
    days_since_reset = (now.weekday() - config.weekday) % 7
    candidate_reset = now.replace(
        hour=config.hour, minute=0, second=0, microsecond=0
    ) - timedelta(days=days_since_reset)

    # Edge case: same weekday, but before reset hour → back up one week
    if candidate_reset > now:
        candidate_reset -= timedelta(days=7)

    return ResetWindow(start=candidate_reset, end=candidate_reset + timedelta(days=7))