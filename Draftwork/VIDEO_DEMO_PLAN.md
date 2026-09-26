# NextTrack — Video Demonstration Plan

A 3–5 minute screen-recorded demonstration, exported as **MP4**. Target
length ~4:30. The plan gives a second-by-second timeline: what is on screen,
what to say (narration script), the exact commands to run, and the outputs to
highlight. It covers motivation, prototype, tests, evaluation, and limitations.

> **Honesty rules (say these on camera):** the dataset is small and local
> (30 tracks); the evaluation compares against the recommender’s own scoring
> objective, not human listener satisfaction. Present the prototype as a
> feasibility demonstration.

---

## Before you record (setup checklist)

- [ ] Open a terminal in the project: `cd "<path>/nexttrack"`.
- [ ] Activate the venv: `source .venv/bin/activate`.
- [ ] Pre-open files in the editor: `app/core/scoring.py`, `app/core/explain.py`, `sample_request.json`.
- [ ] Have two terminal tabs ready (Tab A = server, Tab B = curl/commands).
- [ ] One slide ready: the four-layer architecture diagram (F1) + request flow (F2).
- [ ] Screen resolution ≥ 1280×720; increase terminal font size for readability.
- [ ] Close notifications; clear the terminal before each segment.
- [ ] Recommended tools (macOS): QuickTime Player (screen recording) or OBS Studio; export/save as **.mp4** (in QuickTime, File → Export As; if it produces .mov, convert to .mp4).

---

## Timeline (target ~4:30)

### 0:00–0:25 — Title & one-line pitch
- **Screen:** Title slide — "NextTrack: A Music Recommendation API" + your name/module.
- **Say:** "Hi, I'm [name]. This is NextTrack, a stateless, explainable music recommendation API for my final-year project, *Project Idea 2*. It recommends the next track to play using only the data in each request — no user accounts and no tracking."
- **Commands:** none.

### 0:25–0:55 — Motivation & approach
- **Screen:** Same slide or a short bullet slide (problem → approach).
- **Say:** "Most recommenders build long-term user profiles, which raises privacy concerns. NextTrack instead takes the listening history and preferences inside the request, scores the available tracks with explainable content-based rules, and returns the best next track with a reason. Nothing is stored between requests."
- **Commands:** none.

### 0:55–1:25 — Architecture
- **Screen:** Architecture diagram (F1) + request-flow (F2).
- **Say:** "The system has four layers: a FastAPI API layer, a recommendation-logic layer with the scoring and ranking, a data layer holding a local track dataset, and a testing layer. A request flows in, is validated, candidates are scored and ranked, and a recommendation comes back as JSON."
- **Commands:** none.

### 1:25–1:55 — Start the API: health + docs
- **Screen:** Tab A then browser.
- **Say:** "Let me start the API. The health endpoint confirms it's running, and FastAPI gives interactive documentation automatically."
- **Commands (Tab A):**
  ```bash
  uvicorn app.main:app --reload --port 8000
  ```
- **Commands (Tab B):**
  ```bash
  curl http://localhost:8000/health
  ```
- **Then:** open `http://localhost:8000/docs` in the browser.
- **Outputs to highlight:** `{"status":"ok","service":"nexttrack","version":"0.1.0"}` and the Swagger UI listing `/health` and `/recommend`.

### 1:55–2:55 — The core demo: `POST /recommend`
- **Screen:** Editor showing `sample_request.json`, then Tab B.
- **Say:** "Here's a request with a short history and some preferences — genre, mood, target tempo, a preferred artist, and the scoring weights. I'll send it to `/recommend`."
- **Commands (Tab B):**
  ```bash
  curl -s -X POST http://localhost:8000/recommend \
    -H "Content-Type: application/json" \
    -d @sample_request.json | python -m json.tool
  ```
- **Outputs to highlight:** the `recommended_track`, the numeric `score`, the
  `score_breakdown` per feature, and especially the `explanation` sentence.
- **Say:** "Notice the explanation: it tells me *why* this track was chosen — it
  matched the genre, mood, artist, and was close to the target tempo. That's the
  explainability goal. The `score_breakdown` shows each feature's contribution."

### 2:55–3:25 — History exclusion + an error case
- **Screen:** Tab B.
- **Say:** "The track in the history is never recommended back. And the API handles errors cleanly — if every candidate is already in the history, it returns a 404 with a clear message."
- **Commands (Tab B):**
  ```bash
  curl -s -o /dev/null -w "HTTP %{http_code}\n" -X POST http://localhost:8000/recommend \
    -H "Content-Type: application/json" \
    -d '{"history":["a1","a2"],"preferences":{},"candidates":[
          {"id":"a1","title":"A","artist":"X","genre":"rock","tempo":120,"mood":"calm","year":2018,"popularity":40},
          {"id":"a2","title":"B","artist":"Y","genre":"rock","tempo":125,"mood":"calm","year":2021,"popularity":70}]}'
  ```
- **Outputs to highlight:** `HTTP 404` (mention the `NO_CANDIDATES` envelope).

### 3:25–3:55 — Automated tests
- **Screen:** Tab B.
- **Say:** "The prototype has 42 automated tests covering the scoring functions, the recommender logic and its edge cases, and the API endpoints."
- **Commands (Tab B):** *(stop the server in Tab A first, or use Tab B)*
  ```bash
  pytest -q
  ```
- **Outputs to highlight:** `42 passed`.

### 3:55–4:25 — Evaluation vs random
- **Screen:** Tab B.
- **Say:** "To show it beats chance, an evaluation script compares the recommender against random selection across five scenarios, with a fixed seed. On average the recommender scores far higher and never repeats a track from the history."
- **Commands (Tab B):**
  ```bash
  python scripts/evaluate.py
  ```
- **Outputs to highlight:** the per-scenario table, the average improvement
  (~+220%), and "History exclusion: PASSED".

### 4:25–4:50 — Honest limitations & roadmap, then close
- **Screen:** Closing slide (bullets) or terminal.
- **Say:** "Two honest caveats: the dataset is small and local — 30 tracks — and the evaluation compares against the system's *own* scoring objective, not human listener satisfaction. So it demonstrates feasibility and that the algorithm reliably maximises its criteria, not that listeners prefer the picks. Future work includes external metadata, fuzzy similarity, and a user study. Thanks for watching."
- **Commands:** none.

---

## Narration-to-requirement mapping (so nothing is missed)

| Requirement | Covered at |
|---|---|
| Motivation | 0:25–0:55 |
| Prototype (API, `/recommend`, scoring, explanation) | 1:25–2:55 |
| History exclusion + error handling | 2:55–3:25 |
| Tests | 3:25–3:55 |
| Evaluation | 3:55–4:25 |
| Limitations (small/local dataset; self-referential evaluation) | 4:25–4:50 |

## Export checklist
- [ ] Length between 3:00 and 5:00 (aim ~4:30).
- [ ] Exported as **.mp4** (convert from .mov if needed).
- [ ] Audio audible; terminal text legible at playback size.
- [ ] Both honesty caveats are spoken aloud.
- [ ] File named clearly, e.g. `NextTrack_demo.mp4`.
