"""
Pure scoring functions for NextTrack (Milestone 4).

Each function scores one feature of a candidate track against the user's
preferences and returns a value in [0, 1], where 1 means "perfect match".
The functions are intentionally pure (no I/O, no global state) so they are
trivial to unit-test and easy to reason about in the report.

The full recommender (a later milestone) will combine these per-feature
scores using normalized weights into a single overall score per track.
"""

from app.config import (
    DEFAULT_WEIGHTS,
    SCORING_FEATURES,
    SIMILAR_ARTIST_SCORE,
    TEMPO_RANGE_BPM,
)


def normalize_weights(weights: dict[str, float] | None) -> dict[str, float]:
    """
    Return weights that sum to 1.0, one per scoring feature.

    - If `weights` is None or empty, the default weights are used.
    - Any feature missing from the supplied dict defaults to 0.0.
    - Negative weights are rejected.
    - The result is rescaled so its values sum to exactly 1.0.

    Raises:
        ValueError: if any weight is negative, or if all weights are zero
                    (which would make normalization impossible).
    """
    if not weights:
        weights = dict(DEFAULT_WEIGHTS)

    # Build a complete weight map covering every scoring feature.
    resolved: dict[str, float] = {}
    for feature in SCORING_FEATURES:
        value = weights.get(feature, 0.0)
        if value < 0:
            raise ValueError(f"weight for '{feature}' must not be negative")
        resolved[feature] = float(value)

    total = sum(resolved.values())
    if total == 0:
        raise ValueError("weights must not all be zero")

    return {feature: value / total for feature, value in resolved.items()}


def score_genre(candidate_genre: str, preferred_genre: str | None) -> float:
    """1.0 if the candidate's genre matches the preference, else 0.0."""
    if not preferred_genre:
        return 0.0
    return 1.0 if candidate_genre.lower() == preferred_genre.lower() else 0.0


def score_mood(candidate_mood: str, preferred_mood: str | None) -> float:
    """1.0 if the candidate's mood matches the preference, else 0.0."""
    if not preferred_mood:
        return 0.0
    return 1.0 if candidate_mood.lower() == preferred_mood.lower() else 0.0


def score_tempo(candidate_tempo: int, target_tempo: int | None) -> float:
    """
    Score tempo closeness in [0, 1].

    An exact match returns 1.0. The score decreases linearly as the absolute
    BPM difference grows, reaching 0.0 once the difference is at least
    TEMPO_RANGE_BPM. Returns 0.0 when no target tempo is supplied.
    """
    if target_tempo is None:
        return 0.0
    difference = abs(candidate_tempo - target_tempo)
    closeness = 1.0 - (difference / TEMPO_RANGE_BPM)
    # Clamp to [0, 1] so very large differences do not go negative.
    return max(0.0, min(1.0, closeness))


def score_popularity(popularity: int) -> float:
    """Convert a 0–100 popularity value into a 0–1 score."""
    # Clamp defensively in case an out-of-range value slips through.
    clamped = max(0, min(100, popularity))
    return clamped / 100.0


def score_artist(candidate_artist: str, preferred_artist: str | None) -> float:
    """1.0 if the candidate's artist matches the preference, else 0.0."""
    if not preferred_artist:
        return 0.0
    return 1.0 if candidate_artist.lower() == preferred_artist.lower() else 0.0


def score_artist_affinity(
    candidate_artist: str,
    preferred_artist: str | None,
    history_artists: set[str] | None = None,
    similar_map: dict[str, set[str]] | None = None,
) -> float:
    """
    Artist score capturing explicit, implicit (session), and *similar* affinity.

    - 1.0 if the candidate's artist matches the explicitly preferred artist OR
      an artist heard in the recent listening history (exact affinity).
    - SIMILAR_ARTIST_SCORE if the candidate's artist is *similar* (per the
      Last.fm similarity map) to a preferred or recently played artist — this is
      the "recommend related artists" signal.
    - 0.0 otherwise.

    All signals come from the request (history/preferences) plus static
    reference data, so no user profile is stored.
    """
    ca = candidate_artist.lower()

    # Exact affinity (explicit preference or session history).
    seed_artists: set[str] = set()
    if preferred_artist:
        seed_artists.add(preferred_artist.lower())
    if history_artists:
        seed_artists.update(a.lower() for a in history_artists)

    if ca in seed_artists:
        return 1.0

    # Similar-artist affinity: is the candidate related to any seed artist?
    if similar_map and seed_artists:
        for seed in seed_artists:
            if ca in similar_map.get(seed, ()):  # candidate is similar to a seed
                return SIMILAR_ARTIST_SCORE
    return 0.0
