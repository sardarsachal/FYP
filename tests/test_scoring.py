"""
Unit tests for the pure scoring functions (Milestone 4).

These tests exercise each scoring function in isolation, including the
edge cases that matter for a correct, explainable recommender:
matches, mismatches, missing preferences, tempo distance, and weight
normalization (including the negative-weight error case).
"""

import math

import pytest

from app.config import DEFAULT_WEIGHTS, TEMPO_RANGE_BPM
from app.core.scoring import (
    normalize_weights,
    score_artist,
    score_genre,
    score_mood,
    score_popularity,
    score_tempo,
)


# --- Genre ---------------------------------------------------------------

def test_genre_exact_match():
    assert score_genre("rock", "rock") == 1.0


def test_genre_mismatch():
    assert score_genre("rock", "jazz") == 0.0


def test_genre_no_preference():
    assert score_genre("rock", None) == 0.0


def test_genre_match_is_case_insensitive():
    assert score_genre("Rock", "rock") == 1.0


# --- Mood ----------------------------------------------------------------

def test_mood_exact_match():
    assert score_mood("calm", "calm") == 1.0


def test_mood_mismatch():
    assert score_mood("calm", "energetic") == 0.0


def test_mood_no_preference():
    assert score_mood("calm", None) == 0.0


# --- Tempo ---------------------------------------------------------------

def test_tempo_exact_match():
    assert score_tempo(120, 120) == 1.0


def test_tempo_far_away_scores_lower_than_close():
    close = score_tempo(125, 120)      # 5 BPM apart
    far = score_tempo(170, 120)        # 50 BPM apart
    assert far < close
    assert 0.0 <= far <= 1.0
    assert 0.0 <= close <= 1.0


def test_tempo_beyond_range_is_zero():
    # A difference >= TEMPO_RANGE_BPM clamps to 0.0.
    assert score_tempo(120 + TEMPO_RANGE_BPM, 120) == 0.0
    assert score_tempo(120 + TEMPO_RANGE_BPM + 40, 120) == 0.0


def test_tempo_no_target():
    assert score_tempo(120, None) == 0.0


def test_tempo_half_range_is_half_score():
    # Halfway through the range should give ~0.5 (linear falloff).
    half = score_tempo(120 + TEMPO_RANGE_BPM // 2, 120)
    assert math.isclose(half, 0.5, abs_tol=0.05)


# --- Popularity ----------------------------------------------------------

def test_popularity_100_is_one():
    assert score_popularity(100) == 1.0


def test_popularity_0_is_zero():
    assert score_popularity(0) == 0.0


def test_popularity_midpoint():
    assert score_popularity(50) == 0.5


# --- Artist --------------------------------------------------------------

def test_artist_exact_match():
    assert score_artist("Maya Reed", "Maya Reed") == 1.0


def test_artist_mismatch():
    assert score_artist("Maya Reed", "The Hours") == 0.0


def test_artist_no_preference():
    assert score_artist("Maya Reed", None) == 0.0


# --- Weight normalization ------------------------------------------------

def test_weights_normalize_to_one():
    result = normalize_weights({"genre": 2, "tempo": 2})
    assert math.isclose(sum(result.values()), 1.0, abs_tol=1e-9)


def test_weights_default_when_missing():
    result = normalize_weights(None)
    # Should cover all default features and sum to 1.
    assert set(result.keys()) == set(DEFAULT_WEIGHTS.keys())
    assert math.isclose(sum(result.values()), 1.0, abs_tol=1e-9)


def test_negative_weight_raises():
    with pytest.raises(ValueError):
        normalize_weights({"genre": -0.5, "tempo": 1.0})


def test_all_zero_weights_raises():
    with pytest.raises(ValueError):
        normalize_weights({"genre": 0, "tempo": 0, "artist": 0,
                           "mood": 0, "popularity": 0})
