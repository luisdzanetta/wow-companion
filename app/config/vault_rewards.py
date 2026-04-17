"""Great Vault reward tables by expansion/season.

⚠️ These values change every season. Keep this file as the single source of
truth; don't hardcode item levels anywhere else.

Source: in-game Great Vault tooltip, or Wowhead season guides.
"""


# --- Midnight Season 1 ---
# Values sourced from Wowhead, April 2026.
# Keystone level 10+ caps the reward at Myth 1/6 (ilvl 272).
MIDNIGHT_S1_MPLUS_REWARDS = {
    # keystone_level: reward_item_level
    2: 259,
    3: 259,
    4: 263,
    5: 263,
    6: 266,
    7: 269,
    8: 269,
    9: 269,
    10: 272,
    # 11+ caps at 272 (handled by get_reward_ilvl clamping)
}

# Track name per vault reward ilvl (for display purposes).
MIDNIGHT_S1_TRACK_BY_ILVL = {
    259: "Hero 1/6",
    263: "Hero 2/6",
    266: "Hero 3/6",
    269: "Hero 4/6",
    272: "Myth 1/6",
}


def get_reward_ilvl(
    keystone_level: int, rewards_table: dict = MIDNIGHT_S1_MPLUS_REWARDS
) -> int:
    """Return reward item level for a given keystone level.

    Levels above the table's max are clamped to the max (typical behavior for
    vault rewards — they have a cap per season).
    Levels below the min are clamped to the min.
    """
    if not rewards_table:
        raise ValueError("Rewards table is empty.")

    max_level = max(rewards_table.keys())
    min_level = min(rewards_table.keys())

    clamped = max(min_level, min(keystone_level, max_level))
    return rewards_table[clamped]


def get_reward_track(
    ilvl: int, track_table: dict = MIDNIGHT_S1_TRACK_BY_ILVL
) -> str | None:
    """Return the track name (e.g. 'Hero 4/6') for a given reward ilvl.

    Returns None if the ilvl is not mapped.
    """
    return track_table.get(ilvl)