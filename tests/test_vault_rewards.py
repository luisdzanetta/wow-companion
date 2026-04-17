# em tests/test_vault_rewards.py (arquivo novo opcional)
from app.config.vault_rewards import get_reward_ilvl, get_reward_track


def test_plus_10_caps_at_myth():
    assert get_reward_ilvl(10) == 272


def test_high_keystones_clamped_to_max():
    assert get_reward_ilvl(15) == 272
    assert get_reward_ilvl(20) == 272


def test_low_keystones_clamped_to_min():
    assert get_reward_ilvl(1) == 259  # below table, clamped to +2 reward
    assert get_reward_ilvl(0) == 259


def test_track_lookup():
    assert get_reward_track(272) == "Myth 1/6"
    assert get_reward_track(259) == "Hero 1/6"
    assert get_reward_track(999) is None  # unknown ilvl