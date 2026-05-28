"""Long-running scheduler process.

Tracks configured characters by taking daily snapshots.

Usage:
    python -m scripts.run_scheduler

Stop the scheduler:
  - Type 'quit' (or 'q') and press Enter, OR
  - Press Ctrl+C
"""

import logging

from app.scheduling.snapshot_scheduler import (
    CharacterToTrack,
    build_scheduler,
    snapshot_job,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)


CHARACTERS_TO_TRACK = [
    CharacterToTrack(region="us", realm="Thrall", character_name="Stormtroll"),
]


if __name__ == "__main__":
    print("Running initial snapshot job (sanity check)...")
    snapshot_job(CHARACTERS_TO_TRACK)

    print("\nStarting background scheduler.")
    print("Daily snapshot scheduled for 18:00 UTC.")
    print("Type 'quit' (or 'q') and press Enter to stop. Ctrl+C also works.\n")

    scheduler = build_scheduler(CHARACTERS_TO_TRACK, hour=18, minute=0)
    scheduler.start()

    try:
        while True:
            user_input = input("scheduler> ").strip().lower()
            if user_input in ("quit", "q", "exit"):
                break
            elif user_input == "":
                continue
            else:
                print(f"Unknown command: {user_input!r}. Type 'quit' to stop.")
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        print("\nShutting down scheduler...")
        scheduler.shutdown(wait=False)
        print("Stopped.")