"""Synthetic history generator for portfolio/demo purposes.

Generates plausible weekly snapshots for a character to populate the database
with enough historical data for analytical visualization. Uses a seeded random
generator so output is reproducible.

⚠️ This is NOT real game data. It's intentionally crafted to look realistic
   for demoing the analytics layer.
"""

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class SyntheticWeekStats:
    """Statistics describing a character's M+ activity for a synthetic week."""

    week_offset: int          # 0 = oldest, 11 = most recent
    run_count: int
    keystone_levels: list[int]  # sorted desc, length == run_count
    mythic_rating: float


def _evolution_profile(week_offset: int) -> dict:
    """Return (mean_level, std_level, min_runs, max_runs, base_rating) for a week.

    Defines the natural progression of a character over a season.
    """
    if week_offset < 2:
        # Early season: low keys, fewer runs
        return dict(mean_level=7, std_level=1.5, min_runs=3, max_runs=5, base_rating=1900)
    elif week_offset < 6:
        # Mid-early: growing
        return dict(mean_level=10, std_level=1.5, min_runs=5, max_runs=8, base_rating=2400)
    elif week_offset < 10:
        # Mid-late: consolidation
        return dict(mean_level=13, std_level=1.5, min_runs=6, max_runs=10, base_rating=3000)
    else:
        # Late season: top performance
        return dict(mean_level=15, std_level=1.5, min_runs=8, max_runs=10, base_rating=3300)


def _is_bad_week(week_offset: int) -> bool:
    """A couple of "off weeks" sprinkled in for realism."""
    return week_offset in (3, 7)  # weeks 4 and 8 of the 12-week history


def generate_week_stats(week_offset: int, rng: random.Random) -> SyntheticWeekStats:
    """Generate plausible stats for a single week.

    Args:
        week_offset: 0 (oldest) to 11 (most recent)
        rng: seeded random.Random instance for reproducibility
    """
    profile = _evolution_profile(week_offset)

    # "Off weeks": fewer runs, lower rating gain
    if _is_bad_week(week_offset):
        run_count = rng.randint(1, 3)
    else:
        run_count = rng.randint(profile["min_runs"], profile["max_runs"])

    # Generate keystone levels around the mean for that week
    levels = []
    for _ in range(run_count):
        level = int(round(rng.gauss(profile["mean_level"], profile["std_level"])))
        level = max(2, min(level, 18))  # clamp realistic bounds
        levels.append(level)
    levels.sort(reverse=True)  # descending

    # Rating: base + small variance, increases slightly over time
    rating = profile["base_rating"] + rng.uniform(-100, 150) + (week_offset * 15)
    rating = round(rating, 1)

    return SyntheticWeekStats(
        week_offset=week_offset,
        run_count=run_count,
        keystone_levels=levels,
        mythic_rating=rating,
    )


def generate_history(num_weeks: int = 12, seed: int = 42) -> list[SyntheticWeekStats]:
    """Generate `num_weeks` of synthetic stats, oldest first.

    Same seed → same output. Determinism is the point.
    """
    rng = random.Random(seed)
    return [generate_week_stats(i, rng) for i in range(num_weeks)]