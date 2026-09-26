"""
Tests for the two endpoints the web demo depends on but which the API suite
didn't cover: GET /catalogue and GET / (the single-page player).

/catalogue?playable_only=true in particular is load-bearing for the user study:
study mode picks recommendations from the playable pool, so if that filter ever
stopped working, participants would be shown tracks that cannot play.
"""

from pathlib import Path

from fastapi.testclient import TestClient

import app.api.routes as routes
from app.main import app

client = TestClient(app)


# --- GET /catalogue -------------------------------------------------------

def test_catalogue_returns_tracks_and_vocabularies():
    response = client.get("/catalogue")

    assert response.status_code == 200
    body = response.json()
    assert len(body["tracks"]) > 0
    assert len(body["genres"]) > 0
    assert len(body["moods"]) > 0


def test_catalogue_vocabularies_are_sorted_and_unique():
    body = client.get("/catalogue").json()

    for key in ("genres", "moods"):
        values = body[key]
        assert values == sorted(values)
        assert len(values) == len(set(values))


def test_playable_only_returns_only_tracks_with_a_video():
    """The web demo relies on this so it never surfaces an unplayable track."""
    body = client.get("/catalogue", params={"playable_only": "true"}).json()

    assert len(body["tracks"]) > 0
    for track in body["tracks"]:
        assert track.get("youtube_id"), f"{track['id']} has no youtube_id"


def test_playable_only_is_a_strict_subset():
    everything = client.get("/catalogue").json()["tracks"]
    playable = client.get("/catalogue",
                          params={"playable_only": "true"}).json()["tracks"]

    assert len(playable) < len(everything), "expected some unplayable tracks"
    assert {t["id"] for t in playable} <= {t["id"] for t in everything}


def test_catalogue_defaults_to_the_full_dataset():
    default = client.get("/catalogue").json()["tracks"]
    explicit = client.get("/catalogue",
                          params={"playable_only": "false"}).json()["tracks"]

    assert len(default) == len(explicit)


# --- GET / (web demo) -----------------------------------------------------

def test_web_demo_is_served_as_html():
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_web_demo_returns_404_when_the_page_is_missing(monkeypatch, tmp_path):
    """The NO_WEB_DEMO branch: the API should still start without the demo."""
    monkeypatch.setattr(routes, "WEB_DIR", Path(tmp_path))

    response = client.get("/")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NO_WEB_DEMO"
