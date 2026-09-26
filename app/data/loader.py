"""
Data layer for NextTrack (Milestone 2).

Responsible for loading the local track dataset from tracks.json and
validating that each track has the fields the recommendation engine will
need later. Keeping data access in one place means we can swap the source
(JSON now, SQLite or an external API later) without touching the API or
the recommendation logic.
"""

import json
from pathlib import Path

# The fields every track must contain. The recommendation engine (built in
# a later milestone) relies on all of these being present and correctly typed.
REQUIRED_FIELDS = {
    "id": str,
    "title": str,
    "artist": str,
    "genre": str,
    "tempo": int,
    "mood": str,
    "year": int,
    "popularity": int,
}

# Path to the bundled dataset, resolved relative to this file so it works
# no matter which directory the server is started from.
DATA_FILE = Path(__file__).parent / "tracks.json"


class DatasetError(Exception):
    """Raised when the track dataset is missing, unreadable, or invalid."""


def _validate_track(track, index):
    """
    Check a single track dictionary against REQUIRED_FIELDS.

    Raises DatasetError with a clear message if a field is missing or has
    the wrong type. `index` is included so problems are easy to locate.
    """
    if not isinstance(track, dict):
        raise DatasetError(f"Track at position {index} is not a JSON object.")

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in track:
            raise DatasetError(
                f"Track at position {index} is missing required field '{field}'."
            )
        value = track[field]
        # bool is a subclass of int in Python; reject it explicitly so a
        # stray true/false does not pass as a tempo/year/popularity.
        if expected_type is int and isinstance(value, bool):
            raise DatasetError(
                f"Track at position {index} field '{field}' must be an integer, "
                f"got a boolean."
            )
        if not isinstance(value, expected_type):
            raise DatasetError(
                f"Track at position {index} field '{field}' must be "
                f"{expected_type.__name__}, got {type(value).__name__}."
            )
    return track


def load_tracks(path=DATA_FILE):
    """
    Load and validate all tracks from the dataset file.

    Args:
        path: Optional path to a tracks JSON file (defaults to the bundled
              dataset). Useful for tests that supply their own fixture.

    Returns:
        A list of validated track dictionaries.

    Raises:
        DatasetError: if the file is missing, not valid JSON, not a list,
                      empty, or contains an invalid track.
    """
    path = Path(path)

    if not path.exists():
        raise DatasetError(f"Dataset file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise DatasetError(f"Dataset file is not valid JSON: {exc}") from exc

    if not isinstance(data, list):
        raise DatasetError("Dataset must be a JSON array of track objects.")

    if len(data) == 0:
        raise DatasetError("Dataset is empty; expected at least one track.")

    validated = [_validate_track(track, i) for i, track in enumerate(data)]

    # Guard against duplicate IDs, which would break history matching later.
    ids = [t["id"] for t in validated]
    if len(ids) != len(set(ids)):
        raise DatasetError("Dataset contains duplicate track IDs.")

    return validated


if __name__ == "__main__":
    # Quick manual check: `python -m app.data.loader` prints how many tracks
    # loaded and a sample. Handy during development.
    tracks = load_tracks()
    print(f"Loaded {len(tracks)} tracks.")
    print("First track:", tracks[0])
