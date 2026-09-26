"""
Human-readable explanation builder for NextTrack (Milestone 5).

Turns a recommended track plus its per-feature sub-scores into a short,
plain-English sentence describing *why* it was chosen. This is what makes
the recommender "explainable": every recommendation comes with a reason a
person can read and check.

Pure function, no I/O — easy to test.
"""


def _join_reasons(reasons: list[str]) -> str:
    """Join reason fragments with commas and a trailing 'and'."""
    if len(reasons) == 1:
        return reasons[0]
    if len(reasons) == 2:
        return f"{reasons[0]} and {reasons[1]}"
    return f"{', '.join(reasons[:-1])}, and {reasons[-1]}"


def build_explanation(track: dict, raw_scores: dict, context) -> str:
    """
    Build an explanation string for a chosen track.

    Args:
        track: the recommended track dict (needs at least 'title', 'artist').
        raw_scores: unweighted per-feature scores in [0, 1] with keys
                    genre, artist, tempo, mood, popularity.
        context: the effective scoring context (a SessionContext) exposing
                 genre, mood, target_tempo, preferred_artist, history_artists,
                 and the genre_inferred / mood_inferred / tempo_inferred flags.
                 The flags let the explanation say whether a match came from an
                 explicit preference or was inferred from the listening session.

    Returns:
        A sentence such as:
        'Recommended "Coastal Drive" because it matches the preferred genre
         rock, continues the energetic mood of your session, and is by
         The Hours, an artist from your recent listening.'
    """
    title = track.get("title", "this track")
    reasons: list[str] = []

    # Each reason is only mentioned when there was a preference (explicit or
    # inferred from the session) AND the candidate actually matched it, so the
    # explanation never claims a match that did not happen.
    if getattr(context, "genre", None) and raw_scores.get("genre", 0) == 1.0:
        if getattr(context, "genre_inferred", False):
            reasons.append(f"continues the {context.genre} genre of your session")
        else:
            reasons.append(f"matches the preferred genre {context.genre}")

    if getattr(context, "mood", None) and raw_scores.get("mood", 0) == 1.0:
        if getattr(context, "mood_inferred", False):
            reasons.append(f"continues the {context.mood} mood of your session")
        else:
            reasons.append(f"matches the {context.mood} mood")

    artist_raw = raw_scores.get("artist", 0)
    artist = track.get("artist")
    preferred = getattr(context, "preferred_artist", None)
    if artist_raw == 1.0 and artist:
        if preferred and artist.lower() == preferred.lower():
            reasons.append(f"matches the preferred artist {preferred}")
        else:
            reasons.append(f"is by {artist}, an artist from your recent session")
    elif artist_raw > 0 and artist:
        # Partial score = a Last.fm-similar (related) artist, not an exact match.
        if preferred:
            reasons.append(f"is by {artist}, an artist similar to {preferred}")
        else:
            reasons.append(f"is by {artist}, similar to artists from your session")

    if getattr(context, "target_tempo", None) is not None and raw_scores.get("tempo", 0) >= 0.5:
        if getattr(context, "tempo_inferred", False):
            reasons.append("keeps a similar tempo to your session")
        else:
            reasons.append("is close to the target tempo")

    # Popularity is a mild signal; only highlight it when the track is
    # genuinely popular (raw popularity score >= 0.7, i.e. 70/100+).
    if raw_scores.get("popularity", 0) >= 0.7:
        reasons.append("is a popular track")

    # Fallback when nothing specific matched (e.g. no preferences supplied):
    # the track still won on overall score.
    if not reasons:
        reasons.append("it scored highest among the available candidates")

    return f'Recommended "{title}" because it {_join_reasons(reasons)}.'
