"""
Pydantic models for NextTrack (Milestone 3).

These define the shape of the data flowing in and out of the future
/recommend endpoint. Pydantic validates incoming JSON automatically, so
malformed requests are rejected with a clear 422 error before any
recommendation logic runs.

No endpoint uses these yet — they are defined here so the recommender and
the API layer (built in later milestones) can rely on validated data.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator

# Realistic bounds used for validation. Kept here (rather than in config.py)
# because they describe what a *valid track* is, not how scoring behaves.
MIN_TEMPO = 20      # very slow ballad / ambient
MAX_TEMPO = 300     # extreme upper bound (e.g. fast electronic)
MIN_YEAR = 1900     # recorded-music era
MAX_YEAR = 2100     # generous upper bound to avoid yearly maintenance


class Track(BaseModel):
    """A single music track and its metadata used for scoring."""

    id: str
    title: str
    artist: str
    genre: str
    tempo: int
    mood: str
    year: int
    popularity: int

    # Optional presentation/enrichment fields. Present on tracks built by the
    # enrichment pipeline (scripts/enrich_dataset.py); absent on the original
    # curated tracks. They play no part in scoring — they exist so the web
    # frontend can play the track and show cover art.
    youtube_id: Optional[str] = None
    cover_url: Optional[str] = None
    mbid: Optional[str] = None
    source: Optional[str] = None

    @field_validator("id", "title", "artist", "genre", "mood")
    @classmethod
    def not_empty(cls, value: str) -> str:
        """Reject empty or whitespace-only text fields."""
        if not value or not value.strip():
            raise ValueError("must not be empty")
        return value

    @field_validator("tempo")
    @classmethod
    def realistic_tempo(cls, value: int) -> int:
        if not (MIN_TEMPO <= value <= MAX_TEMPO):
            raise ValueError(f"tempo must be between {MIN_TEMPO} and {MAX_TEMPO} BPM")
        return value

    @field_validator("year")
    @classmethod
    def realistic_year(cls, value: int) -> int:
        if not (MIN_YEAR <= value <= MAX_YEAR):
            raise ValueError(f"year must be between {MIN_YEAR} and {MAX_YEAR}")
        return value

    @field_validator("popularity")
    @classmethod
    def popularity_in_range(cls, value: int) -> int:
        if not (0 <= value <= 100):
            raise ValueError("popularity must be between 0 and 100")
        return value


class Preferences(BaseModel):
    """
    User-supplied recommendation preferences.

    Every field is optional. Missing preferences will later be filled in by
    defaults or inferred from the listening history, so we deliberately do
    not require any of them here.
    """

    genre: Optional[str] = None
    mood: Optional[str] = None
    target_tempo: Optional[int] = None
    year_min: Optional[int] = None
    preferred_artist: Optional[str] = None
    weights: Optional[dict[str, float]] = None

    # When True (default), the recommender treats the listening history as an
    # implicit taste signal: it boosts tracks by artists heard in the session
    # and, where a preference is not explicitly set, infers it from the recent
    # history so recommendations follow the flow of the session. Set to False
    # for the "explicit preferences only" baseline (used for A/B evaluation).
    session_aware: bool = True

    # Diversity / discovery control in [0, 1]. At 0 the recommender is fully
    # deterministic (always the top-scoring candidate). As it rises, the next
    # track is sampled (score-weighted) from a widening window of the top
    # matches, adding variety and novelty to counter content-based
    # over-specialisation. Sampling is seeded from the request, so behaviour is
    # reproducible for a given request but explores across a session.
    diversity: float = 0.0

    @field_validator("diversity")
    @classmethod
    def diversity_in_range(cls, value: float) -> float:
        if not (0.0 <= value <= 1.0):
            raise ValueError("diversity must be between 0 and 1")
        return value


class RecommendRequest(BaseModel):
    """The request body for the future POST /recommend endpoint."""

    # List of previously played track IDs. May be empty (no history yet).
    history: list[str] = Field(default_factory=list)

    # Preferences object; defaults to an all-None Preferences if omitted.
    preferences: Preferences = Field(default_factory=Preferences)

    # Candidate tracks to choose from. Optional: when omitted, the API will
    # fall back to the bundled local dataset.
    candidates: Optional[list[Track]] = None


class RecommendResponse(BaseModel):
    """The response body returned by the future POST /recommend endpoint."""

    recommended_track: Track
    score: float
    explanation: str
    score_breakdown: dict[str, float]
    ranked_alternatives: list[dict] = Field(default_factory=list)


class FeedbackRequest(BaseModel):
    """One anonymous relevance rating from the user study.

    Collected only for evaluation; never used to personalise recommendations.
    """

    session_id: str                       # anonymous, per-browser-session id
    track_id: str                         # the rated recommendation
    rating: int                           # 1 (poor) .. 5 (great)
    mode: str                             # "session_aware" or "baseline"
    history_length: int = 0               # how deep into the session
    explicit_prefs: bool = False          # did the user set any preference?
    score: Optional[float] = None         # the recommender's own score
    participant: Optional[str] = None     # optional facilitator label (e.g. "P3")

    @field_validator("rating")
    @classmethod
    def rating_in_range(cls, value: int) -> int:
        if not (1 <= value <= 5):
            raise ValueError("rating must be between 1 and 5")
        return value

    @field_validator("session_id", "track_id", "mode")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must not be empty")
        return value
