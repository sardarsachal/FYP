"""
Tests for the user-study feedback endpoint (POST /feedback) and the writer
behind it (app/feedback.py).

This is the only part of NextTrack that writes data, and it writes *participant*
data, so two things are tested here that the other suites don't need to worry
about:

  - every field survives the round trip, because the analysis (and therefore
    the numbers reported in the evaluation) depends on them; and
  - validation rejects out-of-range or blank values, so a mis-click can't put a
    junk record into a study file.

Every test redirects app.feedback's output to a tmp_path first. Writing to the
real study_data/feedback.jsonl from a test run would contaminate collected
participant data with synthetic records, which is exactly the kind of thing that
invalidates a study.
"""

import json

import pytest
from fastapi.testclient import TestClient

import app.feedback as feedback_module
from app.main import app

client = TestClient(app)


@pytest.fixture
def feedback_file(tmp_path, monkeypatch):
    """Point the feedback writer at a throwaway file for the duration of a test."""
    path = tmp_path / "feedback.jsonl"
    monkeypatch.setattr(feedback_module, "FEEDBACK_DIR", tmp_path)
    monkeypatch.setattr(feedback_module, "FEEDBACK_FILE", path)
    return path


def make_rating(**overrides):
    """A valid rating payload; override single fields per test."""
    payload = {
        "session_id": "sess-abc",
        "track_id": "t01",
        "rating": 4,
        "mode": "session_aware",
        "history_length": 3,
        "explicit_prefs": False,
        "score": 0.812,
        "participant": "P1",
    }
    payload.update(overrides)
    return payload


# --- the happy path -------------------------------------------------------

def test_feedback_records_a_rating(feedback_file):
    response = client.post("/feedback", json=make_rating())

    assert response.status_code == 200
    assert response.json() == {"status": "recorded"}

    lines = feedback_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1


def test_feedback_preserves_every_field(feedback_file):
    """The analysis reads all of these, so none may be silently dropped."""
    sent = make_rating()
    client.post("/feedback", json=sent)

    record = json.loads(feedback_file.read_text(encoding="utf-8").strip())
    for key, value in sent.items():
        assert record[key] == value, f"{key} was not preserved"


def test_feedback_stamps_a_utc_timestamp(feedback_file):
    """The server stamps the time; the client never supplies it."""
    from datetime import datetime, timezone

    client.post("/feedback", json=make_rating())
    record = json.loads(feedback_file.read_text(encoding="utf-8").strip())

    stamped = datetime.fromisoformat(record["timestamp"])
    assert stamped.tzinfo is not None
    assert stamped.utcoffset() == timezone.utc.utcoffset(None)


def test_feedback_appends_rather_than_overwrites(feedback_file):
    """A second rating must not clobber the first."""
    client.post("/feedback", json=make_rating(track_id="t01", rating=5))
    client.post("/feedback", json=make_rating(track_id="t02", rating=2))

    lines = feedback_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert [json.loads(l)["track_id"] for l in lines] == ["t01", "t02"]


def test_each_record_is_one_json_line(feedback_file):
    """JSON Lines: one record per line, each independently parseable."""
    for n in range(3):
        client.post("/feedback", json=make_rating(track_id=f"t{n}"))

    lines = feedback_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3
    for line in lines:
        assert json.loads(line)["rating"] == 4


# --- validation -----------------------------------------------------------

@pytest.mark.parametrize("bad_rating", [0, 6, -1, 100])
def test_rating_outside_1_to_5_is_rejected(feedback_file, bad_rating):
    response = client.post("/feedback", json=make_rating(rating=bad_rating))

    assert response.status_code == 422
    assert not feedback_file.exists(), "a rejected rating must not be written"


def test_non_integer_rating_is_rejected(feedback_file):
    response = client.post("/feedback", json=make_rating(rating="great"))

    assert response.status_code == 422
    assert not feedback_file.exists()


@pytest.mark.parametrize("field", ["session_id", "track_id", "mode"])
def test_blank_required_fields_are_rejected(feedback_file, field):
    response = client.post("/feedback", json=make_rating(**{field: "   "}))

    assert response.status_code == 422
    assert not feedback_file.exists()


@pytest.mark.parametrize("field", ["session_id", "track_id", "rating", "mode"])
def test_missing_required_fields_are_rejected(feedback_file, field):
    payload = make_rating()
    del payload[field]

    response = client.post("/feedback", json=payload)

    assert response.status_code == 422
    assert not feedback_file.exists()


def test_participant_is_optional(feedback_file):
    """Ratings outside a facilitated session may have no participant label."""
    response = client.post("/feedback", json=make_rating(participant=None))

    assert response.status_code == 200
    record = json.loads(feedback_file.read_text(encoding="utf-8").strip())
    assert record["participant"] is None
