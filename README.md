# NextTrack — Music Recommendation API

A stateless RESTful API that recommends the **next track** to play, based on a
listener's recent history, their preferences, and a pool of available tracks —
**without** user accounts or long-term tracking. All recommendation context
comes from the request itself, and every recommendation is returned with a
plain-English explanation of *why* it was chosen.

> **Status:** Working API (`/health`, `/recommend`, `/catalogue`), an
> interactive **web app** with an embedded music player, a 122-track dataset
> enriched from external sources (MusicBrainz / AcousticBrainz / Last.fm /
> YouTube), 42 passing automated tests, and a reproducible evaluation script
> comparing the recommender against random selection.
>
> **Web demo:** run the server (below) and open <http://localhost:8000>.

---

## Project overview

The API receives a sequence of previously played track IDs, a set of preference
parameters, and (optionally) the candidate tracks to choose from. It scores each
candidate using explainable content-based rules, excludes tracks already heard,
and returns the highest-scoring track plus a score breakdown and explanation.

The design is deliberately **privacy-friendly and stateless**: no login, no
stored user profiles, and no data retained between requests.

## MVP features

**Implemented (must-have):**
- `GET /health` — liveness check.
- `POST /recommend` — recommend the next track with explanation.
- Content-based, preference-weighted scoring (genre, artist, tempo, mood, popularity).
- Listening-history exclusion (never recommends an already-heard track).
- Deterministic, reproducible tie-breaking.
- Request validation and clean error responses.
- Bundled local dataset (30 sample tracks) with optional inline candidates.
- Automated unit + API tests.
- Recommender-vs-random evaluation script.

**Future (could-have):** external metadata enrichment (Spotify/MusicBrainz),
SQLite storage, history-based taste inference, a web demo, diversity controls.

## Technical stack

- **Python 3.9+**
- **FastAPI** — web framework (automatic validation + interactive docs)
- **Uvicorn** — ASGI server
- **Pydantic** — request/response validation
- **Pytest** — testing

*Why this stack:* FastAPI gives typed request validation and auto-generated docs
with very little code, which keeps the prototype simple while remaining
academically credible. JSON-first local data means no database is needed for the
MVP, and the layered structure allows external data sources to be added later
without touching the recommendation logic.

## Folder structure

```text
nexttrack/
├── app/
│   ├── main.py              # FastAPI app + route wiring
│   ├── config.py            # scoring weights + tempo range constants
│   ├── api/
│   │   └── routes.py        # /health and /recommend endpoints
│   ├── core/
│   │   ├── scoring.py       # pure per-feature scoring functions
│   │   ├── recommender.py   # combine scores, exclude history, rank, tie-break
│   │   └── explain.py       # builds the human-readable explanation
│   ├── data/
│   │   ├── loader.py        # loads + validates the dataset
│   │   └── tracks.json      # 30 sample tracks
│   └── models/
│       └── schemas.py       # Pydantic request/response models
├── scripts/
│   └── evaluate.py          # recommender vs random comparison
├── tests/
│   ├── test_scoring.py      # unit tests for scoring functions
│   ├── test_recommender.py  # unit tests for the recommender
│   └── test_api.py          # API tests via FastAPI TestClient
├── sample_request.json      # example POST /recommend body
├── requirements.txt
├── README.md
└── REPORT_NOTES.md          # notes + checklist for the project report
```

## Setup (macOS)

```bash
cd nexttrack

# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

- Interactive API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Test `/health`

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"ok","service":"nexttrack","version":"0.1.0"}
```

## Test `/recommend`

Using the bundled dataset (no `candidates` field) via the sample request file:

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

Or with inline candidates:

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"history":[],"preferences":{"genre":"rock"},
       "candidates":[
         {"id":"a1","title":"Jazz One","artist":"X","genre":"jazz","tempo":90,"mood":"calm","year":2018,"popularity":40},
         {"id":"a2","title":"Rock One","artist":"Y","genre":"rock","tempo":125,"mood":"energetic","year":2021,"popularity":70}]}'
```

## Run the automated tests

```bash
pytest -q          # all 42 tests
pytest -v          # verbose, per-test names
```

## Run the evaluation script

```bash
python scripts/evaluate.py                 # all three sections
python scripts/evaluate.py --section random        # vs random baseline
python scripts/evaluate.py --section sensitivity    # weight robustness
python scripts/evaluate.py --section ab             # session-aware vs baseline
```

The suite has three parts, each producing report-ready output:

1. **Recommender vs random** — across five scenarios, the recommender scores
   ~+267% above the average random pick and never repeats a history track.
2. **Weight sensitivity analysis** — scales each feature weight by ±25–50% (one
   at a time) and checks whether the top recommendation changes. It stays stable
   ~88% of the time, and the sensitivity is confined to the low-weight
   tie-breakers (tempo, popularity), while the dominant genre weight can vary by
   ±50% without changing the pick — evidence the chosen weights behave as
   intended.
3. **Session-aware vs baseline (A/B)** — plays seeded sessions with no explicit
   preferences and measures *session coherence* (a metric independent of the
   recommender's own objective). Session-aware keeps genre coherence at 100% vs
   ~8% for the explicit-only baseline, confirming the history-based upgrade works.

## User study (in-app ratings)

The web app has a **Study mode (blind A/B)** for user testing. When enabled it
randomly assigns the session-aware or baseline method to each recommendation,
**hides the explanation/breakdown** (so the method is blind), and asks for a
**1–5 relevance rating**. Ratings are posted to `POST /feedback` and appended to
`study_data/feedback.jsonl` — this is the only data NextTrack stores, it is
anonymous, and it is **never read back into the recommender** (recommendation
stays stateless).

```bash
python scripts/analyze_feedback.py     # mean rating per method + A/B effect
```

The full protocol (hypotheses, participants, procedure, questionnaire, analysis,
and the planned iterate-and-re-test step) is in
`Draftwork/USER_STUDY_PLAN.md`.

## Dataset enrichment (real tracks from external sources)

The bundled dataset can be extended with **real tracks** whose metadata is
pulled from external music services by an **offline** script. This satisfies the
brief's "get data from elsewhere" while keeping the live API stateless — the
enrichment runs once and writes a static JSON file; `/recommend` never calls any
external service.

Sources (all metadata used for scoring comes from these, not hand-authored):

| Source | Provides | Key needed |
|---|---|---|
| MusicBrainz | canonical id/title/artist, release year, genre tags | none |
| AcousticBrainz | tempo (BPM) and mood, from community audio analysis | none |
| Last.fm | popularity (listener counts) | free key (optional) |
| YouTube Data API | an embeddable video id for playback | free key (optional) |
| Cover Art Archive | album cover image url | none |

The seed is a **fixed list** of `(artist, title, genre)` queries
(`scripts/seed_tracks.py`), chosen so the resulting catalogue is *reproducible* —
unlike live charts, which change daily and would make evaluation non-repeatable.
Missing external data is never fatal: per-genre fallbacks fill tempo/mood, so
every seed track yields a valid record.

```bash
# keyless dry run over a few tracks (prints results, writes nothing):
python scripts/enrich_dataset.py --limit 5 --dry-run

# full keyless build -> app/data/tracks.enriched.json (preview, 92 tracks):
python scripts/enrich_dataset.py

# with popularity + youtube ids (put keys in .env; see .env.example) and merge
# the real tracks into the bundled dataset (backs up the original first):
python scripts/enrich_dataset.py --apply
```

## Example API request and response

**Request** (`POST /recommend`):

```json
{
  "history": ["t02"],
  "preferences": { "genre": "rock", "mood": "energetic", "target_tempo": 135 }
}
```

**Response**:

```json
{
  "recommended_track": {
    "id": "t28", "title": "Wildfire", "artist": "The Hours",
    "genre": "rock", "tempo": 138, "mood": "energetic",
    "year": 2017, "popularity": 72
  },
  "score": 0.7453,
  "explanation": "Recommended \"Wildfire\" because it matches the preferred genre rock, matches the energetic mood, is close to the target tempo, and is a popular track.",
  "score_breakdown": { "genre": 0.4, "artist": 0.0, "tempo": 0.1733, "mood": 0.1, "popularity": 0.072 },
  "ranked_alternatives": [
    { "id": "t10", "title": "Breaking Static", "score": 0.7367 }
  ]
}
```

## Recommendation algorithm (brief)

Each candidate track is scored as a **weighted sum of per-feature sub-scores**,
each in the range `[0, 1]`:

```
score = w_genre·s_genre + w_artist·s_artist + w_tempo·s_tempo
      + w_mood·s_mood  + w_popularity·s_popularity
```

- `s_genre`, `s_mood`, `s_artist` — `1.0` on an exact match with the preference, else `0.0`.
- `s_tempo` — linear closeness: `1 − |tempo − target| / 60`, clamped to `[0, 1]`.
- `s_popularity` — `popularity / 100`.
- **Weights** come from the request (or sensible defaults) and are normalized to sum to 1.
- **History exclusion:** any candidate whose `id` is in the history is removed before scoring.

**Session awareness (`session_aware`, default on).** The listening history in the
request is used as an *implicit* taste signal, statelessly:

- **Artist affinity** — the `artist` score also fires for candidates by an artist
  heard in the recent session, so the recommender continues "more from artists
  you've been playing" without any stored profile.
- **Taste inference** — when the user does not set `genre`, `mood`, or
  `target_tempo`, they are inferred from the recent history (most common
  genre/mood, mean tempo), so the next track follows the flow of the session.
  Explicit preferences always take priority.

Set `session_aware: false` for the "explicit preferences only" baseline — this is
the A/B comparison used in evaluation and user testing.
- **Tie-breaking** (deterministic): higher score → higher popularity → newer year → smaller `id`.

This is **better than random** because it provably maximizes a stated
preference-similarity objective and never repeats a heard track — verified by
`scripts/evaluate.py` (≈ +220% average score over random in testing).

## Known limitations

- Small bundled dataset (30 tracks) intended for demonstration.
- Exact-match scoring for genre/mood/artist (no fuzzy or semantic similarity).
- Evaluation measures the recommender against its own scoring objective, not
  human-judged musical quality.
- No persistence and no external metadata in the MVP (by design).

## Future improvements

- Enrich the dataset from external sources (Spotify / MusicBrainz) offline.
- Infer taste from the listening history when explicit preferences are sparse.
- Add diversity/novelty controls and partial (fuzzy) genre matching.
- Add a small web demo and a user-study-based evaluation.
- Optional SQLite storage for larger catalogs.
