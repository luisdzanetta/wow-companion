"""Preview synthetic history generation without persisting to DB."""

from app.synthetic.history_generator import generate_history


if __name__ == "__main__":
    history = generate_history(num_weeks=12)

    print(f"{'Week':<6} {'Runs':<6} {'Rating':<9} {'Keystones'}")
    print("-" * 60)
    for week_stats in history:
        keystones = ", ".join(f"+{lvl}" for lvl in week_stats.keystone_levels)
        print(
            f"{week_stats.week_offset:<6} "
            f"{week_stats.run_count:<6} "
            f"{week_stats.mythic_rating:<9} "
            f"{keystones}"
        )