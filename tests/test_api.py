"""
API-level tests for NextTrack (Milestone 6).

These use FastAPI's TestClient to exercise the running app end-to-end:
request validation, candidate loading, the recommender, and the response/
error shapes. No network or server process is needed — TestClient calls the
app in-process.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def make_track(id, title="Song", artist="Artist", genre="rock",
               tempo=120, mood="energetic", year=2020, popularity=50):
    """Helper to build a valid candidate track payload."""
    return {
        "id": id, "title": title, "artist": artist, "genre": genre,
        "tempo": tempo, "mood": mood, "year": year, "popularity": popularity,
    }


# 1. Health check.
def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok", "service": "nexttrack", "version": "0.1.0",
    }


# 2. Valid /recommend with inline candidates.
def test_recommend_with_inline_candidates():
    payload = {
        "history": [],
        "preferences": {"genre": "rock"},
        "candidates": [
            make_track("t1", genre="jazz"),
            make_track("t2", genre="rock"),
        ],
    }
    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    assert response.json()["recommended_track"]["id"] == "t2"


# 3. Valid /recommend without candidates uses the local dataset.
def test_recommend_uses_local_dataset_when_candidates_omitted():
    payload = {"history": [], "preferences": {"genre": "rock"}}
    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    # The recommended track should come from the bundled dataset (rock genre).
    assert response.json()["recommended_track"]["genre"] == "rock"


# 4. Response contains all required fields.
def test_response_contains_required_fields():
    payload = {"history": [], "preferences": {"genre": "rock"}}
    response = client.post("/recommend", json=payload)
    body = response.json()
    for key in ("recommended_track", "score", "explanation",
                "score_breakdown", "ranked_alternatives"):
        assert key in body
    assert isinstance(body["explanation"], str) and body["explanation"]


# 5. Tracks in history are not recommended.
def test_history_tracks_not_recommended():
    payload = {
        "history": ["t1"],
        "preferences": {"genre": "rock"},
        "candidates": [
            make_track("t1", genre="rock", popularity=99),  # in history
            make_track("t2", genre="rock", popularity=10),
        ],
    }
    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["recommended_track"]["id"] == "t2"
    alt_ids = [a["id"] for a in body["ranked_alternatives"]]
    assert "t1" not in alt_ids


# 6. All candidates in history returns 404.
def test_all_candidates_in_history_returns_404():
    payload = {
        "history": ["t1", "t2"],
        "preferences": {},
        "candidates": [make_track("t1"), make_track("t2")],
    }
    response = client.post("/recommend", json=payload)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NO_CANDIDATES"


# 7. Invalid negative weights returns 400.
def test_negative_weights_returns_400():
    payload = {
        "history": [],
        "preferences": {"weights": {"genre": -1.0, "tempo": 1.0}},
        "candidates": [make_track("t1")],
    }
    response = client.post("/recommend", json=payload)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_REQUEST"


# 8. Malformed request body returns 422.
def test_malformed_body_returns_422():
    # history must be a list of strings; sending an int is invalid.
    response = client.post("/recommend", json={"history": 123})
    assert response.status_code == 422
