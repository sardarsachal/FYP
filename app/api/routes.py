"""
API routes for NextTrack.

- GET  /            the single-page web demo
- GET  /health      liveness check (Milestone 1)
- GET  /catalogue   the bundled catalogue + genre/mood vocabularies
- POST /recommend   recommend the next track (Milestone 6)
- POST /feedback    record one anonymous user-study rating

The /recommend route is deliberately thin: it validates input (via the
RecommendRequest schema), loads candidates (from the request or the local
dataset), calls the existing recommend() function, and serializes the
result. All recommendation logic lives in app/core; nothing here computes
scores.
"""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

from app.core.recommender import NoCandidatesError, recommend
from app.data.loader import DatasetError, load_tracks
from app.feedback import log_feedback
from app.models.schemas import FeedbackRequest, RecommendRequest, RecommendResponse

# An APIRouter lets us define endpoints separately from the app instance,
# keeping main.py clean and making the routes easy to test and extend.
router = APIRouter()

# Service metadata reported by the health check.
SERVICE_NAME = "nexttrack"
SERVICE_VERSION = "0.1.0"

# The single-page web demo lives next to the app package.
WEB_DIR = Path(__file__).resolve().parent.parent / "web"


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    """Build a consistent error envelope: {"error": {"code", "message"}}."""
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


@router.get("/", include_in_schema=False)
def web_demo():
    """Serve the single-page web demo (the interactive music player)."""
    index = WEB_DIR / "index.html"
    if not index.exists():
        return _error(404, "NO_WEB_DEMO", "Web demo not found.")
    return FileResponse(index)


@router.get("/catalogue", tags=["recommendation"])
def catalogue(playable_only: bool = False):
    """
    Return the bundled catalogue plus the genre/mood vocabularies.

    Read-only convenience for the web frontend: it uses this to populate the
    preference controls and to pick a starting track. It stores no user state,
    so it does not affect the API's stateless design.

    `playable_only=true` returns only tracks with a YouTube id, which the web
    demo uses so it never surfaces a track it cannot play.
    """
    try:
        tracks = load_tracks()
    except DatasetError as exc:
        return _error(500, "DATASET_ERROR", str(exc))

    if playable_only:
        tracks = [t for t in tracks if t.get("youtube_id")]

    genres = sorted({t["genre"] for t in tracks})
    moods = sorted({t["mood"] for t in tracks})
    return {"tracks": tracks, "genres": genres, "moods": moods}


@router.get("/health", tags=["system"])
def health_check():
    """
    Simple liveness check.

    Returns a small JSON object confirming the service is up. Useful for
    quick manual testing (curl), and later for monitoring/uptime checks.
    """
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
    }


@router.post("/recommend", response_model=RecommendResponse, tags=["recommendation"])
def recommend_track(request: RecommendRequest, playable_only: bool = False):
    """
    Recommend the next track.

    Flow: validate (done by FastAPI via RecommendRequest) -> load candidates
    -> recommend() -> serialize. Stateless: nothing is stored between calls.

    Candidate source:
        - If the request supplies `candidates`, those are used.
        - If `candidates` is omitted/null, the bundled local dataset is used.

    Errors (clean envelope):
        - 404 NO_CANDIDATES  : nothing left to recommend (e.g. all in history).
        - 400 INVALID_REQUEST: bad user input the schema can't catch (e.g.
                               negative weights).
        - 500 DATASET_ERROR  : the local dataset failed to load.
        - 422 (FastAPI)      : malformed request body.
    """
    # 1. Determine the candidate pool.
    candidates = request.candidates
    if candidates is None:
        try:
            candidates = load_tracks()
        except DatasetError as exc:
            return _error(500, "DATASET_ERROR", str(exc))

    # The web demo passes playable_only so it never recommends a track without a
    # YouTube id (e.g. one still awaiting an id due to daily API quota).
    if playable_only:
        candidates = [t for t in candidates if t.get("youtube_id")]

    # 2. Run the recommender and translate its errors into HTTP responses.
    try:
        result = recommend(
            history=request.history,
            preferences=request.preferences,
            candidates=candidates,
        )
    except NoCandidatesError as exc:
        return _error(404, "NO_CANDIDATES", str(exc))
    except ValueError as exc:
        # e.g. invalid weights from normalize_weights.
        return _error(400, "INVALID_REQUEST", str(exc))

    # 3. Map the core result onto the API response model.
    return RecommendResponse(
        recommended_track=result.recommended_track,
        score=result.score,
        explanation=result.explanation,
        score_breakdown=result.score_breakdown,
        ranked_alternatives=result.ranked_alternatives,
    )


@router.post("/feedback", tags=["evaluation"])
def submit_feedback(feedback: FeedbackRequest):
    """
    Record one anonymous relevance rating for the user study.

    This is separate from /recommend and does not influence recommendations —
    it only appends an evaluation record. Recommendation remains stateless.
    """
    log_feedback(feedback.model_dump())
    return {"status": "recorded"}
