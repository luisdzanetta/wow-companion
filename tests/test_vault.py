"""Tests for the Great Vault projection logic."""

from app.domain.models import Dungeon, MythicRun, WeeklyMythicSummary
from app.domain.vault import project_vault


def make_run(level: int, timed: bool = True) -> MythicRun:
    """Helper: build a minimal MythicRun for tests."""
    return MythicRun(
        keystone_level=level,
        dungeon=Dungeon(id=1, name="Test Dungeon"),
        completed_timestamp_ms=1_700_000_000_000,
        duration_ms=1_800_000,
        is_completed_within_time=timed,
    )


def test_empty_week_has_all_slots_locked():
    summary = WeeklyMythicSummary(runs=[], current_score=0.0)
    projection = project_vault(summary)

    assert projection.total_runs == 0
    assert all(not s.is_unlocked for s in projection.slots)
    assert projection.slots[0].runs_needed == 1
    assert projection.slots[1].runs_needed == 4
    assert projection.slots[2].runs_needed == 8


def test_one_run_unlocks_only_slot_1():
    summary = WeeklyMythicSummary(runs=[make_run(10)], current_score=100.0)
    projection = project_vault(summary)

    assert projection.slots[0].is_unlocked
    assert projection.slots[0].reward_keystone_level == 10

    assert not projection.slots[1].is_unlocked
    assert projection.slots[1].runs_needed == 3

    assert not projection.slots[2].is_unlocked


def test_four_runs_unlock_slots_1_and_2():
    runs = [make_run(13), make_run(12), make_run(11), make_run(10)]
    summary = WeeklyMythicSummary(runs=runs, current_score=100.0)
    projection = project_vault(summary)

    # slot 1 = 1st best = +13
    assert projection.slots[0].reward_keystone_level == 13
    # slot 2 = 4th best = +10
    assert projection.slots[1].reward_keystone_level == 10
    # slot 3 still locked
    assert not projection.slots[2].is_unlocked


def test_eight_runs_unlock_all_slots():
    # sorted descending: +15, +14, +13, +12, +11, +10, +9, +8
    runs = [make_run(lvl) for lvl in (15, 14, 13, 12, 11, 10, 9, 8)]
    summary = WeeklyMythicSummary(runs=runs, current_score=100.0)
    projection = project_vault(summary)

    assert projection.slots[0].reward_keystone_level == 15
    assert projection.slots[1].reward_keystone_level == 12
    assert projection.slots[2].reward_keystone_level == 8


def test_runs_are_sorted_regardless_of_input_order():
    # deliberately scrambled input
    runs = [make_run(8), make_run(15), make_run(10), make_run(12)]
    summary = WeeklyMythicSummary(runs=runs, current_score=0.0)
    projection = project_vault(summary)

    assert projection.slots[0].reward_keystone_level == 15
    assert projection.slots[1].reward_keystone_level == 8  # 4th best