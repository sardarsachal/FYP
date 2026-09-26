# NextTrack — Music Recommendation API

A stateless RESTful API that recommends the **next track** to play, based on a
listener's recent history, their preferences, and a pool of available tracks —
**without** user accounts or long-term tracking. All recommendation context
comes from the request itself, and every recommendation is returned with a
plain-English explanation of *why* it was chosen.

> **Status:** Working API (`/health`, `/recommend`, `/catalogue`, `/feedback`),
> an interactive **web app** with an embedded music player, a 395-track dataset
> enriched from external sources (MusicBrainz / AcousticBrainz / Last.fm /
> YouTube) of which 190 are playable, 98 passing automated tests, a
> reproducible three-part offline evaluation suite, and a completed blind A/B
> **user study** (3 participants, 30 ratings) whose result contradicted the
> offline metrics and drove a change to the recommender.
>
> **Web demo:** run the server (below) and open <http://localhost:8000>.
> Use `localhost`, **not** `127.0.0.1` — YouTube refuses to play embedded
> video on a page served from a bare IP address.

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
- `GET /catalogue` — the dataset plus genre/mood vocabularies (`playable_only` filter).
- `POST /feedback` — record one anonymous user-study rating.
- Content-based, preference-weighted scoring (genre, artist, tempo, mood, popularity).
- Listening-history exclusion (never recommends an already-heard track).
- Deterministic, reproducible tie-breaking.
- Request validation and clean error responses.
- Bundled local dataset (395 tracks) with optional inline candidates.
- Automated unit + API tests.
- Recommender-vs-random evaluation script.

**Implemented (beyond the MVP):**
- **External metadata enrichment** — the catalogue is built offline from
  MusicBrainz, AcousticBrainz, Last.fm, YouTube and the Cover Art Archive.
- **Session-aware taste inference** — genre/mood/tempo inferred from the
  request's history when the user sets no explicit preference.
- **Similar-artist affinity** — a Last.fm-derived artist graph, so the
  recommender can follow a taste rather than only an exact artist match.
- **Explicit genre/mood hard filters** — a stated preference constrains the
  candidate pool rather than merely adding weight.
- **Diversity control** — score-aware sampling to avoid over-specialisation.
- **Web app** with an embedded player and a blind A/B **study mode**.

**Future (could-have):** SQLite storage for larger catalogues, fuzzy/semantic
genre matching, and learning the feature weights from collected study data.

## Technical stack

- **Python 3.10+** (the code uses PEP 604 `X | None` annotations)
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
│   ├── main.py                    # FastAPI app + route wiring
│   ├── config.py                  # scoring weights + tempo range constants
│   ├── feedback.py                # appends user-study ratings (the only writer)
│   ├── api/
│   │   └── routes.py              # all five endpoints
│   ├── core/
│   │   ├── scoring.py             # pure per-feature scoring functions
│   │   ├── recommender.py         # combine scores, filter, rank, tie-break
│   │   ├── similarity.py          # similar-artist lookup
│   │   └── explain.py             # builds the human-readable explanation
│   ├── data/
│   │   ├── loader.py              # loads + validates the dataset
│   │   ├── tracks.json            # 395 tracks (the shipped catalogue)
│   │   ├── tracks.curated.json    # the original 30 hand-authored tracks
│   │   ├── tracks.enriched.json   # 365 externally sourced tracks
│   │   └── artist_similarity.json # Last.fm-derived artist graph
│   ├── models/
│   │   └── schemas.py             # Pydantic request/response models
│   └── web/
│       └── index.html             # single-page web demo + study mode
├── scripts/
│   ├── evaluate.py                # three-part evaluation suite
│   ├── analyze_feedback.py        # user-study analysis
│   ├── enrich_dataset.py          # offline metadata enrichment pipeline
│   └── seed_tracks.py             # the fixed seed list (92 artist/title pairs)
├── tests/                         # 98 tests
│   ├── test_scoring.py            # scoring functions
│   ├── test_recommender.py        # recommender logic
│   ├── test_api.py                # API via FastAPI TestClient
│   ├── test_feedback.py           # POST /feedback + the rating writer
│   ├── test_analyze_feedback.py   # study-analysis statistics
│   └── test_web_endpoints.py      # /catalogue and the web demo route
├── study_data/                    # ratings (git-ignored: participant data)
├── results/                       # archived test + evaluation output
├── sample_request.json            # example POST /recommend body
├── .env.example                   # optional API keys for enrichment
├── requirements.txt
└── README.md
```

## Setup (macOS)

Requires **Python 3.10 or newer**.

```bash
cd nexttrack

# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. (Optional, for the enrichment pipeline only) add API keys
cp .env.example .env     # then fill in the keys you have; all are optional
```

Nothing in the API or the tests needs a key — the keys are used only by the
offline enrichment script.

## Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

- Web demo: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

> **Open the demo at `localhost`, not `127.0.0.1`.** YouTube refuses to play
> embedded video on a page served from a bare IP address, so
> `http://127.0.0.1:8000` shows "Video unavailable" on every track while
> `http://localhost:8000` plays normally.

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
pytest -q          # all 98 tests
pytest -v          # verbose, per-test names
```

## Run the evaluation script

```bash
python scripts/evaluate.py                          # all three sections
python scripts/evaluate.py --section random         # vs random baseline
python scripts/evaluate.py --section sensitivity    # weight robustness
python scripts/evaluate.py --section ab             # session-aware vs baseline

python scripts/evaluate.py --dataset curated        # the original 30 tracks
```

The suite has three parts, each producing report-ready output:

1. **Recommender vs random** — across five scenarios the recommender averages
   **0.962** against **0.728** for the average random pick (**+32.3%**), and
   never repeats a history track.
2. **Weight sensitivity analysis** — scales each feature weight by ±25–50% (one
   at a time) and checks whether the top recommendation changes. It stays stable
   **94.0%** of the time, and the sensitivity is confined to the low-weight
   tie-breakers (tempo, popularity), while the dominant genre weight can vary by
   ±50% without changing the pick — evidence the chosen weights behave as
   intended.
3. **Session-aware vs baseline (A/B)** — plays seeded sessions with no explicit
   preferences and measures *session coherence* (a metric independent of the
   recommender's own objective). Session-aware holds genre coherence at
   **100% vs 8.3%**, mood at **91.7% vs 36.7%** and artist affinity at
   **41.7% vs 0%**, confirming the history-based upgrade works.

### Artist repeat cap — a change driven by the user study

Artist affinity was deliberately reduced from 53.3% to 41.7%. The first user
study (2 participants, 20 ratings) rated session-aware recommendations *below*
the baseline — 2.90 vs 4.10. The cause was visible in the data: session-aware
returned one artist four times in ten tracks and those four were rated
1, 1, 2, 1, while the baseline spread ten tracks over eight artists.

The offline coherence metric had scored that same repetition as a **success**,
which is the gap between an accuracy proxy and perceived quality that McNee,
Riedl and Konstan (2006) describe. So the metric was not wrong to measure
artist affinity — it was wrong to treat more of it as always better.

`ARTIST_AFFINITY_REPEAT_LIMIT` (`app/config.py`) now withholds the affinity
bonus once an artist has been heard twice in the recent history. An explicitly
requested artist is exempt: the user asked for it. Measured over 12 simulated
ten-track sessions:

| | Distinct artists / 10 | Most-repeated artist | Worst case |
|---|---|---|---|
| Before | 6.9 | 3.1 | 6 |
| After | **7.8** | **2.3** | **4** |

The cap removes the amplifier rather than banning the artist — a track can
still win on genre, tempo and popularity alone — so repeats become less likely
rather than impossible. Genre coherence (100%) and the random-baseline and
sensitivity results are unchanged; mood coherence rose slightly (90% → 91.7%).

**This change has not yet been re-tested with participants.** Whether it
actually raises perceived quality is the open question the re-test answers.

### Why the margin over random is modest — and why that is the honest number

`--dataset` re-runs the comparison on either catalogue, because the two give
very different-looking results:

| Catalogue | Recommender | Random | Improvement |
|---|---|---|---|
| `full` (395 tracks) | 0.962 | 0.728 | **+32.3%** |
| `curated` (30 tracks) | 0.962 | 0.931 | **+3.8%** |

Two things drive this, and both make the baseline *harder*, not the recommender
worse. First, an explicit genre or mood is now a **hard filter**, so the random
baseline draws from the already-relevant pool rather than the whole catalogue —
"random among relevant" is a far stronger opponent than "random among
everything". Second, on only 30 tracks the filtered pool is tiny, so random
nearly ties the recommender (three of the five scenarios reach +0.0%); the
395-track catalogue is what gives the recommender room to discriminate.

Earlier drafts of this project reported a much larger margin (≈ +220%) measured
against a random pick over the *unfiltered* 30-track catalogue. That figure is
not reproducible under the current design and should not be quoted: the
comparison it describes no longer exists.

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

The study is **within-subjects and blind**: method assignment is block
randomised so each participant receives an equal number of session-aware and
baseline recommendations, the app sends no explicit preferences, and diversity
is held constant across conditions, so the only difference between them is the
history-based adaptation being tested. `scripts/analyze_feedback.py` reports
per-participant means alongside design checks (assignment balance and rating
pacing), so the validity of a collected run can be read straight off the data.

### Results — the hypothesis was rejected

Three participants, 30 ratings, two sessions each. Full output in
`results/user_study.txt`; the raw anonymous records are in
`results/user_study_ratings.jsonl`.

| Condition | n | Mean rating | SD |
|---|---|---|---|
| Session-aware | 14 | **2.36** | 1.60 |
| Baseline | 16 | **4.00** | 1.55 |

Mann–Whitney **U = 52.5, p = 0.0100** — significant at α = 0.05, with a large
effect (rank-biserial *r* = +0.531). All three participants agreed in
direction (−1.60, −0.80, −2.83).

**The hypothesis that listeners prefer session-aware recommendations is
rejected, and the baseline was significantly preferred.** Every offline metric
in this project favours session-awareness; the listeners did not.

**Why.** Session-aware used **5 distinct artists across 14 tracks**, against
the baseline's **9 across 16**. Within a participant's own session a repeated
artist cost session-aware **1.18 rating points** (2.78 → 1.60) but the
baseline only **0.29** (4.09 → 3.80). The session-affinity bonus was pulling
the same artist back repeatedly, and listeners heard that as monotony.

The session-coherence metric had scored exactly this behaviour as a *success*
(artist affinity 53.3% vs 0%). It was measuring something real but treating
more of it as always better — the gap between an accuracy proxy and perceived
quality described by McNee, Riedl and Konstan (2006), observed here on this
system.

The artist repeat cap described above is the response to this finding. It is
justified by the study data and by simulation, but it was introduced *after*
these sessions and **has not been re-tested with participants** — so whether
it actually improves perceived quality is still an open question.

**Data quality and limits.** Median rating latency 20.8s with 0 of 29 gaps
under 3 seconds, so every rating followed an actual listen; assignment balance
was 5/5, 5/5 and 4/6. But this is a convenience sample of three, the catalogue
is chart-seeded so most tracks were familiar, ratings are relative to the
session rather than absolute quality, and no post-session questionnaire was
administered — so no claim is made about explanation clarity, trust or
usability. The result is indicative, not generalisable.

> **Build provenance.** All 30 ratings predate the artist repeat cap. The
> offline figures elsewhere in this README are from the current (post-cap)
> build, so the two sets describe different versions of the recommender.

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

# keyless build from the hand seeds alone -> 92 tracks:
python scripts/enrich_dataset.py

# how the SHIPPED 395-track catalogue was built (needs keys in .env):
#   --per-genre 40  also pulls the top 40 Last.fm tracks per genre, which is
#                   what takes the catalogue past the 92 hand seeds
#   --similar       also builds app/data/artist_similarity.json
#   --apply         merges the real tracks into app/data/tracks.json,
#                   rebuilding it from tracks.curated.json each time
python scripts/enrich_dataset.py --per-genre 40 --similar --apply
```

**On YouTube quota.** A `search.list` call costs 100 units against a default
10,000/day allowance, so roughly **100 tracks can gain a playable video per
day**. That is why 190 of 395 tracks are currently playable rather than all of
them; re-running on a later day extends the coverage. The API's
`videoEmbeddable` flag is not sufficient on its own — some videos it reports as
embeddable still refuse to play with error 150 — so ids are verified in a real
embed before being added, and known-bad ones are kept in `YOUTUBE_BLOCKLIST`.

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
  "score": 0.962,
  "explanation": "Recommended \"Wildfire\" because it matches the preferred genre rock, matches the energetic mood, matches the preferred artist The Hours, is close to the target tempo, and is a popular track.",
  "score_breakdown": { "genre": 0.4, "artist": 0.2, "tempo": 0.19, "mood": 0.1, "popularity": 0.072 },
  "ranked_alternatives": [
    { "id": "r008", "title": "Seven Nation Army", "score": 0.7733 },
    { "id": "r004", "title": "Mr. Brightside", "score": 0.77 }
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
`scripts/evaluate.py` (+32.3% over a random-among-relevant baseline; see the
evaluation section for why that margin is the honest one).

## Known limitations

- Demonstration-scale catalogue (395 tracks, 190 of them playable). At this
  size high genre coherence is easier than it would be over a production
  catalogue, so the coherence figures show the mechanism works rather than
  proving behaviour at scale.
- Only 190 tracks carry a playable video: the YouTube Data API allows roughly
  100 lookups per day on the free quota, so coverage grows a day at a time.
- Exact-match scoring for genre/mood/artist (no fuzzy or semantic similarity).
- Evaluation measures the recommender against its own scoring objective, not
  human-judged musical quality.
- The recommendation path stores nothing and calls no external service at
  request time; enrichment happens offline and study ratings are written by a
  separate module that is never read back into the recommender.

## Future improvements

Four items previously listed here — offline external enrichment, history-based
taste inference, diversity controls, and the web demo — are now implemented and
are described above. What remains:

- **Partial (fuzzy) genre matching** — "rock" and "indie rock" currently do not
  match, which is transparent but coarse.
- **Learn the feature weights from collected study data** rather than setting
  them by hand, then re-test them.
- **Re-test the artist repeat cap with participants.** The user study has
  been run (see above) and motivated the cap, but the cap itself was
  introduced afterwards and has not been put in front of listeners. Re-running
  the same blind A/B against the capped build is the immediate next step.
- **Recruit a larger, less familiar sample.** Three participants on a
  chart-seeded catalogue is indicative only; a larger sample and less familiar
  music would separate session fit from track familiarity.
- **Investigate whether artist repetition is the whole story.** It is the
  best-evidenced cause, but session-awareness also narrows genre and mood,
  which may contribute to the monotony participants reported.
- **Extend playable coverage** beyond 190 tracks as YouTube quota allows.
- **Optional SQLite storage** for larger catalogues.
