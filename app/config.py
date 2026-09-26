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

# Repeat limit on the *session* artist affinity (not on an explicitly requested
# artist, which the user has asked for and should keep receiving).
#
# The first user study surfaced this. With an unlimited affinity bonus the
# recommender returned one artist four times in ten tracks, and participants
# rated those four 1, 1, 2, 1 — dragging the session-aware condition below the
# baseline (2.90 vs 4.10). The offline coherence metric had scored the same
# behaviour as a *success* (artist affinity 53.3% vs 0%), which is exactly the
# gap between an accuracy proxy and perceived quality that McNee, Riedl and
# Konstan (2006) describe.
#
# Once an artist has appeared this many times in the recent history it stops
# receiving the affinity bonus, so the recommender still follows a taste but
# stops amplifying one artist. Note this removes the amplifier rather than
# banning the artist: a track can still win on genre, tempo and popularity
# alone, so repeats become less likely rather than impossible.
#
# Chosen by simulating 12 ten-track sessions per setting: no limit gave 6.9
# distinct artists per 10 tracks (worst case 6 repeats); a limit of 2 gives 7.8
# (worst case 4). A limit of 1 raised the mean slightly (8.3) but not the worst
# case, and discards the taste signal after a single play.
ARTIST_AFFINITY_REPEAT_LIMIT: int = 2
