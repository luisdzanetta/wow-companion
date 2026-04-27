"""Tests for the analytics domain logic."""

from datetime import datetime, timezone

from app.db.models import Snapshot
from app.domain.analytics import build_character_report


def make_snapshot(
    week_id: str,
    taken_at: datetime,
    rating: float,
    runs: int,
    vault: tuple[int | None, int | None, int | None],
    ilvls: tuple[int | None, int | None, int | None],
) -> Snapshot:
    """Build a Snapshot in-memory (not persisted) for tests."""
    s = Snapshot(
        character_id=1,
        week_id=week_id,
        raw_data={},
        mythic_rating=rating,
        weekly_run_count=runs,
        vault_slot_1_level=vault[0],
        vault_slot_2_level=vault[1],
        vault_slot_3_level=vault[2],
        vault_slot_1_ilvl=ilvls[0],
        vault_slot_2_ilvl=ilvls[1],
        vault_slot_3_ilvl=ilvls[2],
    )
    s.taken_at = taken_at
    return s


def test_empty_history_returns_empty_report():
    report = build_character_report(weekly_snapshots=[], total_snapshot_count=0)
    assert report.distinct_weeks == 0
    assert report.weekly_trend == []
    assert report.rating_delta_last_week is None


def test_single_week_report():
    snap = make_snapshot(
        week_id="2026-W17",
        taken_at=datetime(2026, 4, 27, 13, 0, tzinfo=timezone.utc),
        rating=2985.0,
        runs=5,
        vault=(13, 12, None),
        ilvls=(272, 272, None),
    )
    report = build_character_report(weekly_snapshots=[snap], total_snapshot_count=1)

    assert report.distinct_weeks == 1
    assert report.weeks_with_full_vault == 0  # only 2 slots filled
    assert report.average_runs_per_week == 5.0
    assert report.best_rating_ever == 2985.0
    assert report.current_rating == 2985.0
    assert report.rating_delta_last_week is None  # need 2 weeks for delta


def test_multi_week_delta():
    snaps = [
        make_snapshot(
            "2026-W15", datetime(2026, 4, 13, 13, 0, tzinfo=timezone.utc),
            rating=2800.0, runs=8, vault=(10, 10, 10), ilvls=(272, 272, 272),
        ),
        make_snapshot(
            "2026-W16", datetime(2026, 4, 20, 13, 0, tzinfo=timezone.utc),
            rating=2950.0, runs=8, vault=(12, 11, 10), ilvls=(272, 272, 272),
        ),
        make_snapshot(
            "2026-W17", datetime(2026, 4, 27, 13, 0, tzinfo=timezone.utc),
            rating=3000.0, runs=10, vault=(13, 12, 11), ilvls=(272, 272, 272),
        ),
    ]
    report = build_character_report(weekly_snapshots=snaps, total_snapshot_count=3)

    assert report.distinct_weeks == 3
    assert report.weeks_with_full_vault == 3
    assert report.average_runs_per_week == round((8 + 8 + 10) / 3, 1)
    assert report.best_rating_ever == 3000.0
    assert report.best_rating_week_id == "2026-W17"
    assert report.current_rating == 3000.0
    assert report.rating_delta_last_week == 50.0


def test_partial_vault_count_correct():
    snap = make_snapshot(
        "2026-W17", datetime(2026, 4, 27, 13, 0, tzinfo=timezone.utc),
        rating=2000.0, runs=4, vault=(10, 8, None), ilvls=(272, 269, None),
    )
    report = build_character_report(weekly_snapshots=[snap], total_snapshot_count=1)

    trend = report.weekly_trend[0]
    assert trend.vault_slots_filled == 2
    assert trend.best_vault_ilvl == 272