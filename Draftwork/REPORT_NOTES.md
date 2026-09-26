# NextTrack — Report Notes

Supporting material for the project report. This file summarizes the
architecture, data model, algorithm, testing, and evaluation, and lists the
evidence to collect while writing up the MVP.

---

## 1. Architecture summary

NextTrack is a single-process REST API organized into four layers. The layers
are decoupled so each can be tested in isolation and so the data source could
later be swapped without touching the recommendation logic.

```
                         HTTP request (JSON)
                                 │
                                 ▼
   ┌──────────────────────────────────────────────────────────┐
   │  API layer            app/api/routes.py                    │
   │  FastAPI routes, error envelope, response serialization    │
   └──────────────────────────────────────────────────────────┘
                                 │ validated RecommendRequest
                                 ▼
   ┌──────────────────────────────────────────────────────────┐
   │  Recommendation logic   app/core/recommender.py            │
   │  exclude history → score → rank → tie-break → explain      │
   │     uses app/core/scoring.py  +  app/core/explain.py       │
   └──────────────────────────────────────────────────────────┘
                                 │ needs candidate tracks
                                 ▼
   ┌──────────────────────────────────────────────────────────┐
   │  Data layer           app/data/loader.py + tracks.json     │
   │  load + validate the local dataset (fallback candidates)   │
   └──────────────────────────────────────────────────────────┘

   Testing layer   tests/  →  exercises all three layers
```

## 2. Request flow (POST /recommend)

```
Client
  │  POST /recommend  { history, preferences, candidates? }
  ▼
FastAPI route (routes.py)
  │  1. Pydantic validates body  → RecommendRequest   (invalid → 422)
  │  2. candidates given?  yes → use them
  │                        no  → load_tracks() from tracks.json (error → 500)
  ▼
recommender.recommend(history, preferences, candidates)
  │  3. dedupe candidate IDs
  │  4. exclude tracks in history          (none left → NoCandidatesError → 404)
  │  5. normalize_weights(...)             (negative/zero → ValueError → 400)
  │  6. score each candidate via scoring.py
  │  7. sort: score → popularity → year → id  (deterministic)
  │  8. build_explanation(...) for the winner
  ▼
RecommendResponse  { recommended_track, score, score_breakdown,
                     explanation, ranked_alternatives }
  ▼
Client receives JSON
```

**Text form of the diagram requested:**
Request → FastAPI route → Pydantic validation → candidate loading →
recommender → scoring functions → response.

## 3. Data model

Each track in the dataset (and in inline candidates) has these fields:

| Field        | Type    | Constraint / range        | Purpose in scoring                |
|--------------|---------|---------------------------|-----------------------------------|
| `id`         | string  | non-empty, unique         | history matching, tie-break       |
| `title`      | string  | non-empty                 | display / explanation             |
| `artist`     | string  | non-empty                 | artist-match score                |
| `genre`      | string  | non-empty                 | genre-match score (primary signal)|
| `tempo`      | integer | 20–300 BPM                | tempo-closeness score             |
| `mood`       | string  | non-empty                 | mood-match score                  |
| `year`       | integer | 1900–2100                 | tie-break (recency)               |
| `popularity` | integer | 0–100                     | popularity score + tie-break      |

Example track:

```json
{ "id": "t28", "title": "Wildfire", "artist": "The Hours", "genre": "rock",
  "tempo": 138, "mood": "energetic", "year": 2017, "popularity": 72 }
```

## 4. Scoring formula

Overall score for a candidate track is a weighted sum of per-feature sub-scores,
each in `[0, 1]`:

```
score = w_genre·s_genre + w_artist·s_artist + w_tempo·s_tempo
      + w_mood·s_mood  + w_popularity·s_popularity
```

Sub-scores:

| Feature     | Rule                                                        |
|-------------|-------------------------------------------------------------|
| genre       | 1.0 if candidate genre == preferred genre, else 0.0         |
| mood        | 1.0 if candidate mood == preferred mood, else 0.0           |
| artist      | 1.0 if candidate artist == preferred artist, else 0.0       |
| tempo       | `max(0, 1 − |tempo − target| / 60)`                         |
| popularity  | `popularity / 100`                                          |

Default weights (`app/config.py`), normalized to sum to 1:

| genre | artist | tempo | mood | popularity |
|-------|--------|-------|------|------------|
| 0.40  | 0.20   | 0.20  | 0.10 | 0.10       |

- **Weights** may be overridden per request; `normalize_weights` rescales them to
  sum to 1 and rejects negative weights.
- **History exclusion:** candidates whose `id` appears in `history` are removed
  before scoring, so an already-heard track can never be recommended.
- **Tie-break order:** score → popularity → year (newer) → `id` (smaller). This
  makes the output fully deterministic and reproducible.

## 5. Testing summary

Run with `pytest -q` (42 tests total):

| Test file                  | Count | Covers                                              |
|----------------------------|-------|-----------------------------------------------------|
| `tests/test_scoring.py`    | 22    | each scoring function + weight normalization + errors |
| `tests/test_recommender.py`| 12    | best-track selection, history exclusion, dedupe, tie-break, breakdown, explanation, ordering |
| `tests/test_api.py`        | 8     | `/health`, `/recommend` (inline + dataset), required fields, history exclusion, 404, 400, 422 |

Edge cases covered: empty history, candidates omitted/empty, all candidates in
history (404), missing preferences (defaults), duplicate candidate IDs,
negative weights (400), malformed body (422).

## 6. Evaluation summary

`python scripts/evaluate.py` compares the recommender against random selection
over the local dataset, across five scenarios (energetic rock, calm ambient,
happy pop, energetic hiphop, calm jazz), with a fixed seed (42) and 1000 random
trials per scenario.

Representative result:

| Metric                       | Value          |
|------------------------------|----------------|
| Average recommender score    | ≈ 0.762        |
| Average random score         | ≈ 0.239        |
| Average improvement          | ≈ +220%        |
| History exclusion            | PASSED         |

Interpretation: the recommender consistently selects higher-scoring tracks than
random and never repeats a track from the listening history — a clear,
explainable improvement over random selection.

## 7. Screenshots checklist

Collect these while building/demoing for the report:

- [ ] Terminal: `pytest -q` showing **42 passed**.
- [ ] Terminal: API starting with `uvicorn app.main:app --reload`.
- [ ] Browser: Swagger UI at `http://localhost:8000/docs`.
- [ ] Terminal: `curl /health` response.
- [ ] Terminal/Swagger: a `POST /recommend` request + JSON response (showing the `explanation`).
- [ ] Terminal: a 404 (all-candidates-in-history) and a 400 (negative weights) error response.
- [ ] Terminal: `python scripts/evaluate.py` table + summary.
- [ ] (Optional) A bar chart of Rec vs Random score per scenario, drawn from the evaluation table.

Diagrams/tables to include: the architecture diagram (§1), the request-flow
diagram (§2), the data-model table (§3), the scoring-weights table (§4), and the
evaluation results table (§6).

## 8. Limitations and future work

**Limitations**
- Small demonstration dataset (30 tracks).
- Exact-match scoring for genre/mood/artist (no fuzzy/semantic similarity).
- Evaluation is against the system's own scoring objective, not human judgement.
- No persistence or external metadata in the MVP (intentional for scope).

**Future work**
- Enrich the dataset offline from Spotify / MusicBrainz.
- Infer preferences from the listening history when explicit prefs are sparse.
- Add diversity/novelty controls and partial genre matching.
- Add a web demo and a small user-study evaluation.
- Optional SQLite backing store for larger catalogs.
