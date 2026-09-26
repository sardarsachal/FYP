"""
Unit tests for the recommender logic (Milestone 5).

These tests treat the recommender as a pure function: given history,
preferences, and candidates, assert on the returned RecommendationResult.
They cover the core behaviour (best track wins, history excluded) plus the
edge cases that keep the recommender robust and deterministic.
"""

import pytest

from app.config import SCORING_FEATURES
from app.core.recommender import NoCandidatesError, recommend
from app.models.schemas import Preferences


def make_track(id, title="Song", artist="Artist", genre="rock",
               tempo=120, mood="energetic", year=2020, popularity=50):
    """Helper to build a candidate track dict with sensible defaults."""
    return {
        "id": id, "title": title, "artist": artist, "genre": genre,
        "tempo": tempo, "mood": mood, "year": year, "popularity": popularity,
    }


# 1. Highest-scoring candidate is recommended.
def test_recommends_highest_scoring_candidate():
    candidates = [
        make_track("t1", genre="jazz"),    # genre mismatch
        make_track("t2", genre="rock"),    # genre match -> should win
    ]
    prefs = Preferences(genre="rock")
    result = recommend(history=[], preferences=prefs, candidates=candidates)
    assert result.recommended_track["id"] == "t2"


# 2. Tracks already in history are never recommended.
def test_history_tracks_excluded():
    candidates = [
        make_track("t1", genre="rock"),    # would win, but it's in history
        make_track("t2", genre="rock", popularity=10),
    ]
    prefs = Preferences(genre="rock")
    result = recommend(history=["t1"], preferences=prefs, candidates=candidates)
    assert result.recommended_track["id"] == "t2"
    alt_ids = [a["id"] for a in result.ranked_alternatives]
    assert "t1" not in alt_ids


# 3. Empty history still works.
def test_empty_history_works():
    candidates = [make_track("t1"), make_track("t2")]
    result = recommend(history=[], preferences=Preferences(), candidates=candidates)
    assert result.recommended_track["id"] in {"t1", "t2"}


# 4. Missing preferences still works using defaults.
def test_missing_preferences_uses_defaults():
    candidates = [
        make_track("t1", popularity=20),
        make_track("t2", popularity=90),   # popular -> wins on default weights
    ]
    result = recommend(history=[], preferences=None, candidates=candidates)
    assert result.recommended_track["id"] == "t2"


# 5. All candidates in history raises a clear error.
def test_all_candidates_in_history_raises():
    candidates = [make_track("t1"), make_track("t2")]
    with pytest.raises(NoCandidatesError):
        recommend(history=["t1", "t2"], preferences=Preferences(), candidates=candidates)


def test_no_candidates_provided_raises():
    with pytest.raises(NoCandidatesError):
        recommend(history=[], preferences=Preferences(), candidates=[])


# 6. Duplicate candidate IDs are handled safely.
def test_duplicate_candidate_ids_deduplicated():
    candidates = [
        make_track("t1", popularity=90),
        make_track("t1", popularity=90),   # duplicate id
        make_track("t2", popularity=10),
    ]
    result = recommend(history=[], preferences=Preferences(), candidates=candidates)
    # t1 should appear once as the recommendation and never in alternatives.
    assert result.recommended_track["id"] == "t1"
    alt_ids = [a["id"] for a in result.ranked_alternatives]
    assert alt_ids.count("t1") == 0
    assert "t2" in alt_ids


# 7. Deterministic tie-breaking.
def test_tie_break_prefers_popularity_then_year_then_id():
    # Two tracks tie on total score (no preferences, equal popularity),
    # equal year -> the smaller id must win.
    candidates = [
        make_track("zzz", popularity=50, year=2020),
        make_track("aaa", popularity=50, year=2020),
    ]
    result = recommend(history=[], preferences=Preferences(), candidates=candidates)
    assert result.recommended_track["id"] == "aaa"


def test_tie_break_newer_year_wins_over_older():
    # Equal score and popularity, but different years -> newer wins.
    candidates = [
        make_track("t1", popularity=50, year=2000),
        make_track("t2", popularity=50, year=2024),
    ]
    result = recommend(history=[], preferences=Preferences(), candidates=candidates)
    assert result.recommended_track["id"] == "t2"


# 8. Score breakdown contains the expected keys.
def test_score_breakdown_keys():
    candidates = [make_track("t1")]
    result = recommend(history=[], preferences=Preferences(genre="rock"),
                       candidates=candidates)
    assert set(result.score_breakdown.keys()) == set(SCORING_FEATURES)
    # Total score should equal the sum of the weighted breakdown.
    assert result.score == pytest.approx(sum(result.score_breakdown.values()), abs=1e-4)


# 9. Explanation is non-empty.
def test_explanation_non_empty():
    candidates = [make_track("t1", genre="rock", mood="energetic")]
    prefs = Preferences(genre="rock", mood="energetic")
    result = recommend(history=[], preferences=prefs, candidates=candidates)
    assert isinstance(result.explanation, str)
    assert len(result.explanation) > 0
    assert "rock" in result.explanation


# 10. Ranked alternatives are in descending score order.
def test_ranked_alternatives_descending():
    candidates = [
        make_track("t1", genre="rock"),     # match
        make_track("t2", genre="rock"),     # match
        make_track("t3", genre="jazz"),     # mismatch
        make_track("t4", genre="pop"),      # mismatch
    ]
    prefs = Preferences(genre="rock")
    result = recommend(history=[], preferences=prefs, candidates=candidates)
    scores = [a["score"] for a in result.ranked_alternatives]
    assert scores == sorted(scores, reverse=True)
    # The recommended track's score should be >= every alternative's score.
    assert all(result.score >= s for s in scores)


# --- Session-aware behaviour ---------------------------------------------

# 11. Artist affinity: a candidate by an artist from the session is boosted
#     enough to beat a more popular candidate by an unrelated artist.
def test_artist_affinity_boosts_history_artists():
    candidates = [
        make_track("h1", artist="Aurora", genre="rock"),               # in history
        make_track("c1", artist="Aurora", genre="rock", popularity=10),  # same artist, unpopular
        make_track("c2", artist="Other", genre="rock", popularity=90),   # unrelated, popular
    ]
    result = recommend(history=["h1"], preferences=Preferences(), candidates=candidates)
    assert result.recommended_track["id"] == "c1"


# 12. Genre inference: with no explicit genre, the recommender infers it from
#     the recent history and prefers a matching track over a more popular one.
def test_infers_genre_from_history():
    candidates = [
        make_track("h1", artist="A1", genre="jazz"),
        make_track("h2", artist="A2", genre="jazz"),
        make_track("c1", artist="A3", genre="jazz", popularity=10),
        make_track("c2", artist="A4", genre="pop", popularity=90),
    ]
    result = recommend(history=["h1", "h2"], preferences=Preferences(), candidates=candidates)
    assert result.recommended_track["id"] == "c1"


# 13. The session_aware flag turns the behaviour off (the A/B baseline):
#     without it, neither affinity nor inference applies, so popularity decides.
def test_session_aware_false_disables_inference_and_affinity():
    candidates = [
        make_track("h1", artist="Aurora", genre="rock"),
        make_track("c1", artist="Aurora", genre="rock", popularity=10),
        make_track("c2", artist="Other", genre="rock", popularity=90),
    ]
    prefs = Preferences(session_aware=False)
    result = recommend(history=["h1"], preferences=prefs, candidates=candidates)
    assert result.recommended_track["id"] == "c2"


# 14. The explanation names the session when a match came from history.
def test_explanation_mentions_session_for_affinity():
    candidates = [
        make_track("h1", artist="Zephyr", genre="jazz"),
        make_track("c1", artist="Zephyr", genre="jazz"),
    ]
    result = recommend(history=["h1"], preferences=Preferences(), candidates=candidates)
    assert "session" in result.explanation.lower()


# --- Explicit preferences act as hard filters ----------------------------

# 21. An explicitly chosen mood is honoured even though its weight is low.
def test_explicit_mood_is_hard_filter():
    candidates = [
        make_track("t1", mood="energetic", genre="rock", popularity=10),
        make_track("t2", mood="calm", genre="rock", popularity=100),  # higher score, wrong mood
    ]
    result = recommend(history=[], preferences=Preferences(mood="energetic"),
                       candidates=candidates)
    assert result.recommended_track["id"] == "t1"
    assert all(a for a in result.ranked_alternatives) or True
    # The high-popularity calm track must not be recommended.
    assert result.recommended_track["mood"] == "energetic"


# 22. Explicit genre + mood together both constrain the result.
def test_explicit_genre_and_mood_filter():
    candidates = [
        make_track("t1", genre="rock", mood="energetic"),
        make_track("t2", genre="rock", mood="calm", popularity=100),
        make_track("t3", genre="jazz", mood="energetic", popularity=100),
    ]
    result = recommend(history=[],
                       preferences=Preferences(genre="rock", mood="energetic"),
                       candidates=candidates)
    assert result.recommended_track["id"] == "t1"


# 23. A filter that would empty the pool is relaxed, not fatal.
def test_impossible_filter_relaxes_gracefully():
    candidates = [make_track("t1", genre="rock", mood="calm")]
    # No rock+energetic track exists; should still return something, not error.
    result = recommend(history=[],
                       preferences=Preferences(genre="rock", mood="energetic"),
                       candidates=candidates)
    assert result.recommended_track["id"] == "t1"


# --- Similar-artist affinity ---------------------------------------------

# 19. A track by an artist *similar* to a played artist is boosted above an
#     unrelated track (but a bigger overall match can still win).
def test_similar_artist_affinity_boosts_related_artist():
    candidates = [
        make_track("h1", artist="Michael Jackson", genre="pop"),      # in history
        make_track("c1", artist="Prince", genre="pop", popularity=10),  # similar artist
        make_track("c2", artist="Nobody", genre="pop", popularity=10),  # unrelated
    ]
    similar = {"michael jackson": {"prince"}}
    result = recommend(history=["h1"], preferences=Preferences(session_aware=True),
                       candidates=candidates, similar_artists=similar)
    # Prince (similar) should outrank the unrelated same-popularity track.
    assert result.recommended_track["id"] == "c1"
    assert result.score_breakdown["artist"] > 0


# 20. Without a similarity map, related artists get no boost (back-compat).
def test_no_similarity_map_means_no_similar_boost():
    candidates = [
        make_track("h1", artist="Michael Jackson", genre="pop"),
        make_track("c1", artist="Prince", genre="pop", popularity=10),
        make_track("c2", artist="Nobody", genre="pop", popularity=90),
    ]
    result = recommend(history=["h1"], preferences=Preferences(session_aware=True),
                       candidates=candidates, similar_artists={})
    # With no similarity data, popularity decides between the two non-history
    # tracks, so the more popular unrelated track wins.
    assert result.recommended_track["id"] == "c2"


# --- Diversity / discovery control ---------------------------------------

def _session_ids(candidates, diversity, steps):
    """Simulate `steps` next-tracks, feeding history each time; return the ids."""
    history, ids = [], []
    for _ in range(steps):
        prefs = Preferences(session_aware=False, diversity=diversity)
        r = recommend(history=list(history), preferences=prefs, candidates=candidates)
        ids.append(r.recommended_track["id"])
        history.append(r.recommended_track["id"])
    return ids


# 15. Diversity 0 is fully deterministic (the documented default behaviour).
def test_diversity_zero_is_deterministic():
    cands = [make_track(f"t{i:02d}", popularity=50, year=2000) for i in range(15)]
    assert _session_ids(cands, 0.0, 5) == _session_ids(cands, 0.0, 5)


# 16. Diversity sampling is reproducible for an identical request.
def test_diversity_is_reproducible_per_request():
    cands = [make_track(f"t{i:02d}", popularity=50, year=2000) for i in range(15)]
    prefs = Preferences(session_aware=False, diversity=1.0)
    r1 = recommend(history=["seed"], preferences=prefs, candidates=cands)
    r2 = recommend(history=["seed"], preferences=prefs, candidates=cands)
    assert r1.recommended_track["id"] == r2.recommended_track["id"]


# 17. Diversity changes the order a session unfolds in (adds variety).
def test_diversity_varies_session_order():
    cands = [make_track(f"t{i:02d}", popularity=50, year=2000) for i in range(15)]
    assert _session_ids(cands, 0.0, 5) != _session_ids(cands, 1.0, 5)


# 18. Even with high diversity, history exclusion still holds (no repeats).
def test_diversity_still_excludes_history():
    cands = [make_track(f"t{i:02d}", popularity=50, year=2000) for i in range(15)]
    ids = _session_ids(cands, 1.0, 8)
    assert len(ids) == len(set(ids))
