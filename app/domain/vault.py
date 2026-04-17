"""Great Vault logic.

Rules (Mythic+ vault, as of Midnight S1):
  - Three slots unlock at 1, 4, and 8 weekly keystone runs completed.
  - Each slot's reward ilvl is based on the 1st, 4th, and 8th best keystone
    level completed this week (sorted descending).
  - Overtimed runs still count as completed for slot unlock purposes.
"""

from dataclasses import dataclass

from app.config.vault_rewards import get_reward_ilvl, get_reward_track
from app.domain.models import MythicRun, WeeklyMythicSummary


SLOT_THRESHOLDS = (1, 4, 8)  # minimum runs needed to unlock each slot


@dataclass(frozen=True)
class VaultSlot:
    """A single Great Vault slot projection."""

    slot_number: int
    threshold: int
    is_unlocked: bool
    runs_needed: int
    reward_keystone_level: int | None
    reward_ilvl: int | None
    reward_track: str | None  # e.g. "Hero 4/6", "Myth 1/6"

    def __repr__(self) -> str:
        if not self.is_unlocked:
            return f"Slot {self.slot_number}: 🔒 {self.runs_needed} more run(s) needed"
        track = f" ({self.reward_track})" if self.reward_track else ""
        return (
            f"Slot {self.slot_number}: +{self.reward_keystone_level} "
            f"→ ilvl {self.reward_ilvl}{track}"
        )


@dataclass(frozen=True)
class VaultProjection:
    """Full Great Vault projection for the current week."""

    total_runs: int
    slots: tuple[VaultSlot, ...]

    def __repr__(self) -> str:
        lines = [f"Great Vault ({self.total_runs} run(s) this week):"]
        for slot in self.slots:
            lines.append(f"  {slot!r}")
        return "\n".join(lines)


def project_vault(summary: WeeklyMythicSummary) -> VaultProjection:
    """Compute Great Vault projection from a weekly M+ summary."""
    runs_desc = summary.runs_sorted_by_level
    total_runs = len(runs_desc)

    slots = tuple(
        _build_slot(slot_number=i + 1, threshold=t, runs_desc=runs_desc)
        for i, t in enumerate(SLOT_THRESHOLDS)
    )

    return VaultProjection(total_runs=total_runs, slots=slots)


def _build_slot(
    slot_number: int, threshold: int, runs_desc: list[MythicRun]
) -> VaultSlot:
    """Build a single slot projection.

    The reward is determined by the run at position `threshold` in the sorted list
    (1-indexed). Example: slot 2 (threshold=4) uses the 4th best run.
    """
    total_runs = len(runs_desc)
    is_unlocked = total_runs >= threshold

    if not is_unlocked:
        return VaultSlot(
            slot_number=slot_number,
            threshold=threshold,
            is_unlocked=False,
            runs_needed=threshold - total_runs,
            reward_keystone_level=None,
            reward_ilvl=None,
            reward_track=None,
        )

    defining_run = runs_desc[threshold - 1]
    reward_ilvl = get_reward_ilvl(defining_run.keystone_level)
    return VaultSlot(
        slot_number=slot_number,
        threshold=threshold,
        is_unlocked=True,
        runs_needed=0,
        reward_keystone_level=defining_run.keystone_level,
        reward_ilvl=reward_ilvl,
        reward_track=get_reward_track(reward_ilvl),
    )