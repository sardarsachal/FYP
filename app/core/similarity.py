"""
Artist-similarity lookup for NextTrack.

Loads a bundled, static map of artist -> set of similar artists (built offline
from Last.fm by scripts/enrich_dataset.py and stored in
app/data/artist_similarity.json). This is reference data, like the track
dataset — it contains no user information, so using it keeps the recommender
stateless.

The map lets the recommender award partial artist affinity to tracks by artists
*related* to what the listener has played or asked for, not only exact matches.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

SIMILARITY_FILE = Path(__file__).resolve().parent.parent / "data" / "artist_similarity.json"


@lru_cache(maxsize=1)
def load_similarity_map(path: str | None = None) -> dict[str, set[str]]:
    """Return {artist_lower: {similar_artist_lower, ...}}.

    Returns an empty map if the file is absent, so the recommender simply falls
    back to exact-match affinity when no similarity data has been built yet.
    """
    file_path = Path(path) if path else SIMILARITY_FILE
    if not file_path.exists():
        return {}
    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return {
        artist.lower(): {s.lower() for s in similars}
        for artist, similars in raw.items()
    }
