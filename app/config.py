"""
Configuration constants for NextTrack (Milestone 4).

Central place for scoring weights and tunable parameters. Keeping these in
one file makes the recommendation behaviour easy to adjust and easy to cite
in the project report, without hunting through the logic code.
"""

# Default importance of each feature when the request does not supply weights.
# These are normalized to sum to 1.0 before use (see normalize_weights), so
# the raw numbers below just express *relative* importance.
DEFAULT_WEIGHTS: dict[str, float] = {
    "genre": 0.40,
    "artist": 0.20,
    "tempo": 0.20,
    "mood": 0.10,
    "popularity": 0.10,
}

# The set of features the recommender scores. Used to validate weight keys.
SCORING_FEATURES = tuple(DEFAULT_WEIGHTS.keys())

# Tempo difference (in BPM) at which the tempo score falls to 0.
# A candidate whose tempo differs from the target by this much or more
# scores 0 for tempo; an exact match scores 1.0; values in between scale
# linearly.
TEMPO_RANGE_BPM: int = 60

# Artist-affinity score awarded when a candidate's artist is not an exact match
# but is *similar* (per the Last.fm similarity map) to a preferred or recently
# played artist. Below the exact-match score of 1.0, so exact affinity still
# wins, but well above 0 so related artists are meaningfully preferred.
SIMILAR_ARTIST_SCORE: float = 0.6
