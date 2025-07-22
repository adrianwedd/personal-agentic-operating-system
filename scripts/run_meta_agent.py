"""Run the meta-agent to update guidelines and manage its log."""

from __future__ import annotations

import os
from datetime import datetime

from agent.meta_agent import run_meta_agent

LOG_FILE = "logs/meta_agent.log"


def _append_log(text: str) -> None:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as fh:
        fh.write(f"{datetime.utcnow().isoformat()} {text}\n")


def _last_update() -> str | None:
    try:
        with open(LOG_FILE) as fh:
            lines = fh.read().splitlines()
        return lines[-1] if lines else None
    except FileNotFoundError:
        return None


def main(show_last: bool = False) -> None:
    if show_last:
        last = _last_update()
        print(last or "No updates yet")
        return
    result = run_meta_agent()
    if result:
        print(result)
        _append_log(result)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the meta-agent")
    parser.add_argument(
        "--show-last",
        action="store_true",
        help="Display the most recent guideline update",
    )
    args = parser.parse_args()
    main(show_last=args.show_last)
