"""
Feedback logging for the NextTrack user study.

This is deliberately kept *separate* from the recommender. The recommendation
path (app/core, /recommend) remains fully stateless and stores nothing. This
module is the one place NextTrack writes data, and it exists only to collect
**anonymous relevance ratings for evaluation** — it is never read back into the
recommendation logic, so it does not build a user profile or personalise
anything. Each record is an anonymous, per-browser-session rating; no account,
name, or persistent identifier is collected.

Ratings are appended as JSON Lines to study_data/feedback.jsonl.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

# Kept at the project root, outside the app package, and git-ignored: it is
# participant data, not source code.
FEEDBACK_DIR = Path(__file__).resolve().parent.parent / "study_data"
FEEDBACK_FILE = FEEDBACK_DIR / "feedback.jsonl"


def log_feedback(record: dict) -> None:
    """Append one rating record (as a JSON line), stamped with a UTC time."""
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    entry = {"timestamp": datetime.now(timezone.utc).isoformat(), **record}
    with FEEDBACK_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
