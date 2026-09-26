"""
Core recommender logic for NextTrack (Milestone 5).

Combines the validated schemas (Milestone 3) and the pure scoring functions
(Milestone 4) into a single, explainable recommendation. This module is the
"recommendation logic layer": it takes listening history, preferences, and
candidate tracks, and returns the best next track with a reason.

It is completely stateless — every call depends only on its arguments — and
contains no HTTP code, so it can be unit-tested directly. The /recommend
endpoint simply calls recommend() and serializes the result.
"""

import hashlib
import random
from collections import Counter
from dataclasses import dataclass, field

from app.config import SCORING_FEATURES
from app.core.explain import build_explanation
from app.core.scoring import (
    normalize_weights,
    score_artist_affinity,
    score_genre,
    score_mood,
    score_popularity,
    score_tempo,
)
from app.core.similarity import load_similarity_map
from app.models.schemas import Preferences

# How many of the most recent history tracks define the current "session"
# for the purpose of taste inference and artist affinity.
RECENT_HISTORY = 5

# The largest window of top candidates the diversity control will sample from
# (at diversity = 1.0). Keeps exploration within the genuinely relevant set.
DIVERSITY_MAX_WINDOW = 12


class NoCandidatesError(Exception):
    """Raised when there are no candidate tracks left to recommend."""


@dataclass
class SessionContext:
    """The effective preferences used for scoring.

    Explicit user preferences, augmented (when session_aware) with values
    inferred from the recent listening history. The `*_inferred` flags record
    whether each value came from the user or from the session, so the
    explanation can describe it honestly.
    """

    genre: str | None
    mood: str | None
    target_tempo: int | None
    preferred_artist: str | None
    history_artists: set = field(default_factory=set)
    # How many times each artist (lower-cased) appears in the recent history,
    # so repeated artists can have their affinity bonus damped.
    artist_play_counts: dict = field(default_factory=dict)
    genre_inferred: bool = False
    mood_inferred: bool = False
    tempo_inferred: bool = False


def _session_context(history_tracks: list[dict], preferences: Preferences) -> SessionContext:
    """Build the effective scoring context from preferences + session history.

    Explicit preferences always take priority. When `session_aware` is on and
    there is history, the recent history supplies artist affinity and fills in
    any preference (genre/mood/tempo) the user did not set, so the next track
    follows the flow of the session.
    """
    ctx = SessionContext(
        genre=preferences.genre,
        mood=preferences.mood,
        target_tempo=preferences.target_tempo,
        preferred_artist=preferences.preferred_artist,
    )
    if not getattr(preferences, "session_aware", True) or not history_tracks:
        return ctx

    recent = history_tracks[-RECENT_HISTORY:]
    ctx.history_artists = {t["artist"] for t in recent if t.get("artist")}
    ctx.artist_play_counts = Counter(
        t["artist"].lower() for t in recent if t.get("artist")
    )

    if ctx.genre is None:
        genres = [t["genre"] for t in recent if t.get("genre")]
        if genres:
            ctx.genre, ctx.genre_inferred = Counter(genres).most_common(1)[0][0], True
    if ctx.mood is None:
        moods = [t["mood"] for t in recent if t.get("mood")]
        if moods:
            ctx.mood, ctx.mood_inferred = Counter(moods).most_common(1)[0][0], True
    if ctx.target_tempo is None:
        tempos = [t["tempo"] for t in recent if isinstance(t.get("tempo"), int)]
        if tempos:
            ctx.target_tempo, ctx.tempo_inferred = int(round(sum(tempos) / len(tempos))), True
    return ctx


@dataclass
class RecommendationResult:
    """Plain result object returned by recommend().

    The HTTP layer maps this onto the RecommendResponse Pydantic model;
    keeping it as a dataclass here keeps the core decoupled from the API and
    trivial to assert on in tests.
    """

    recommended_track: dict
    score: float
    score_breakdown: dict
    explanation: str
    ranked_alternatives: list = field(default_factory=list)


def _as_dict(track) -> dict:
    """Accept either a Pydantic Track or a plain dict; return a dict."""
    if hasattr(track, "model_dump"):
        return track.model_dump()
    return dict(track)


def _dedupe_by_id(candidates: list[dict]) -> list[dict]:
    """Remove duplicate candidate IDs, keeping the first occurrence."""
    seen: set[str] = set()
    unique: list[dict] = []
    for candidate in candidates:
        track_id = candidate["id"]
        if track_id in seen:
            continue
        seen.add(track_id)
        unique.append(candidate)
    return unique


def _normalize_preferences(preferences) -> Preferences:
    """Accept None, a dict, or a Preferences object; return Preferences."""
    if preferences is None:
        return Preferences()
    if isinstance(preferences, Preferences):
        return preferences
    if isinstance(preferences, dict):
        return Preferences(**preferences)
    raise TypeError("preferences must be a dict, Preferences, or None")


def _apply_explicit_filters(pool: list[dict], preferences: Preferences) -> list[dict]:
    """Apply explicitly chosen genre/mood as hard filters.

    A preference the user *explicitly* selects (genre or mood) should be
    respected outright, not merely up-weighted — otherwise a low-weight feature
    like mood gets swamped by higher-weight ones and appears ignored. Filters
    are applied most-specific first and relaxed gracefully: a filter that would
    empty the pool is skipped, so a recommendation is always returned.

    Only *explicit* preferences filter; genre/mood inferred from the session
    stay soft (they nudge the ranking, they don't constrain it).
    """
    filtered = pool
    if preferences.genre:
        subset = [t for t in filtered if t["genre"].lower() == preferences.genre.lower()]
        if subset:
            filtered = subset
    if preferences.mood:
        subset = [t for t in filtered if t["mood"].lower() == preferences.mood.lower()]
        if subset:
            filtered = subset
    return filtered


def _select_with_diversity(scored: list[dict], history, diversity: float) -> dict:
    """Choose the recommendation, applying the diversity control.

    `scored` is already sorted best-first. At diversity 0 (or a single
    candidate) the top item is returned — fully deterministic. Otherwise the
    next track is sampled, score-weighted, from the top-`k` candidates, where
    `k` grows with diversity. The RNG is seeded from the request (history +
    diversity), so the choice is reproducible for a given request but varies as
    the session's history grows.
    """
    if diversity <= 0 or len(scored) == 1:
        return scored[0]

    # The window is score-aware, not a fixed size: it holds only candidates
    # whose score is within `diversity` of the best. So when many candidates tie
    # (e.g. a broad genre request) the window is wide and we get variety, but
    # when one candidate is clearly better (e.g. the only track by a requested
    # artist) the window collapses to it and it is not diluted by worse options.
    best_total = scored[0]["total"]
    threshold = best_total * (1.0 - diversity)
    window = [s for s in scored if s["total"] >= threshold][:DIVERSITY_MAX_WINDOW]
    if len(window) == 1:
        return window[0]

    seed_src = "|".join(history or []) + f"|{diversity:.3f}"
    seed = int(hashlib.md5(seed_src.encode()).hexdigest(), 16)
    rng = random.Random(seed)
    # Score-weighted so higher matches remain more likely; the small floor keeps
    # every windowed candidate reachable even when scores tie at zero.
    weights = [max(s["total"], 0.0) + 0.01 for s in window]
    return rng.choices(window, weights=weights, k=1)[0]


def recommend(history, preferences=None, candidates=None,
              similar_artists=None) -> RecommendationResult:
    """
    Recommend the single best next track.

    Args:
        history: list of track IDs the listener has already heard (may be empty).
        preferences: Preferences object, dict, or None (defaults apply).
        candidates: list of candidate tracks (Track objects or dicts).
        similar_artists: optional {artist_lower: {similar_lower}} map for graded
                         artist affinity. Defaults to the bundled Last.fm map.

    Returns:
        A RecommendationResult with the chosen track, total score, weighted
        score breakdown, explanation, and ranked alternatives.

    Raises:
        NoCandidatesError: if no candidates are supplied, or none remain after
                           excluding the listening history.
        ValueError: if the supplied weights are invalid (e.g. negative).
    """
    preferences = _normalize_preferences(preferences)

    # 1. Must have something to choose from.
    if not candidates:
        raise NoCandidatesError("No candidate tracks were provided.")

    # 2. Normalize candidates to dicts and drop duplicate IDs.
    pool = _dedupe_by_id([_as_dict(c) for c in candidates])

    # 3. Resolve the listening history to full tracks (from the pre-exclusion
    #    pool) so we can read its artists/genres/moods for session awareness,
    #    then build the effective scoring context.
    by_id = {track["id"]: track for track in pool}
    history_tracks = [by_id[h] for h in (history or []) if h in by_id]
    context = _session_context(history_tracks, preferences)

    # 4. Exclude anything already in the listening history.
    history_set = set(history or [])
    pool = [track for track in pool if track["id"] not in history_set]
    if not pool:
        raise NoCandidatesError(
            "No candidate tracks remain after excluding the listening history."
        )

    # 4b. Apply explicit genre/mood as hard filters so a chosen preference is
    #     always honoured (soft weighting alone lets low-weight mood be ignored).
    pool = _apply_explicit_filters(pool, preferences)

    # 5. Resolve weights (raises ValueError on invalid weights).
    weights = normalize_weights(preferences.weights)

    # Artist-similarity map for graded affinity (bundled unless injected).
    if similar_artists is None:
        similar_artists = load_similarity_map()

    # 6. Score every remaining candidate against the effective context.
    scored = []
    for track in pool:
        raw = {
            "genre": score_genre(track["genre"], context.genre),
            "artist": score_artist_affinity(
                track["artist"], context.preferred_artist,
                context.history_artists, similar_artists,
                context.artist_play_counts,
            ),
            "tempo": score_tempo(track["tempo"], context.target_tempo),
            "mood": score_mood(track["mood"], context.mood),
            "popularity": score_popularity(track["popularity"]),
        }
        breakdown = {f: round(raw[f] * weights[f], 4) for f in SCORING_FEATURES}
        total = round(sum(breakdown.values()), 4)
        scored.append({"track": track, "raw": raw, "breakdown": breakdown, "total": total})

    # 6. Deterministic ranking:
    #    higher total -> higher popularity -> newer year -> smaller id.
    scored.sort(
        key=lambda s: (
            -s["total"],
            -s["track"]["popularity"],
            -s["track"]["year"],
            s["track"]["id"],
        )
    )

    # 7. Choose the recommendation, applying the diversity control (a no-op at
    #    the default diversity of 0, which keeps the top pick deterministic).
    diversity = getattr(preferences, "diversity", 0.0) or 0.0
    best = _select_with_diversity(scored, history, diversity)

    explanation = build_explanation(best["track"], best["raw"], context)
    if diversity > 0 and best is not scored[0]:
        explanation += " It was chosen from your closest matches to add variety."

    alternatives = [
        {"id": s["track"]["id"], "title": s["track"]["title"], "score": s["total"]}
        for s in scored if s is not best
    ]

    return RecommendationResult(
        recommended_track=best["track"],
        score=best["total"],
        score_breakdown=best["breakdown"],
        explanation=explanation,
        ranked_alternatives=alternatives,
    )
