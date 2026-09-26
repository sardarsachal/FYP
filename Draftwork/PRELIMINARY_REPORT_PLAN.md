# NextTrack — Preliminary Report Plan

A section-by-section blueprint for the four-chapter preliminary report.
Word targets use the **safer** ranges (not the chapter maximums). Keep a
running per-chapter count; figures, tables, captions, and references are
excluded from the 6000-word total.

| Chapter | Max (brief) | Safer target |
|---|---|---|
| 1 Introduction | 1000 | **750–850** |
| 2 Literature Review | 2500 | **2000–2200** |
| 3 Design | 2000 | **1500–1700** |
| 4 Feature Prototype | 1500 | **1100–1300** |
| **Total** | **6000** | **≈ 5350–6050 → trim to ≤ 6000** |

Reference keys (e.g. `A1`, `F1`) refer to entries in `REFERENCE_BANK.md`.
Figure keys (`F1`–`F11`) refer to the figures list at the bottom of this file.

---

## Chapter 1 — Introduction  (target 750–850)

| § | Subheading | Words | References | Figures | Prototype files |
|---|---|---|---|---|---|
| 1.1 | Project concept and motivation | 200–230 | A1, B1, G3 | — | `README.md` |
| 1.2 | Problem statement (the next-track problem; privacy/statelessness) | 120–150 | G2, G3 | — | `README.md` |
| 1.3 | Aims and objectives | 150–170 | — | — | `README.md` |
| 1.4 | Project template: *Project Idea 2 — NextTrack* | 60–80 | — | — | — |
| 1.5 | Scope and contributions (feasibility prototype; small local dataset) | 120–150 | — | — | `app/data/tracks.json` |
| 1.6 | Report structure | 60–80 | — | — | — |

**Notes:** State plainly that this is a feasibility-demonstrating prototype on a
small, local 30-track dataset. Give 3–4 concrete objectives. Name the template
exactly once and clearly.

---

## Chapter 2 — Literature Review  (target 2000–2200)

| § | Subheading | Words | References | Figures | Prototype files |
|---|---|---|---|---|---|
| 2.1 | Recommender systems: foundations & taxonomy | 220–250 | A1, A2 | — | — |
| 2.2 | Music recommender systems: characteristics & challenges | 260–300 | B1, B2, B3, B4 | — | — |
| 2.3 | Content-based recommendation | 280–320 | C1, C2, C3 | — | `app/core/scoring.py` |
| 2.4 | Collaborative filtering & its limits (cold start, data needs) | 220–250 | D1, D2 | — | — |
| 2.5 | Hybrid recommender systems | 150–180 | E1 | — | — |
| 2.6 | Explainable recommendation | 240–270 | F1, F2 | — | `app/core/explain.py` |
| 2.7 | Contextual / session-based recommendation & privacy | 240–270 | G1, G2, G3, B4 | — | `app/api/routes.py` |
| 2.8 | Evaluation of recommender systems | 220–250 | H1, H2, B2 | — | `scripts/evaluate.py` |
| 2.9 | Synthesis and research gap | 130–160 | A1, B3, F1, G2 | — | — |

**Notes:** General → specific. Each paragraph cites *and interprets*. The CF
subsection should connect cold-start/data-accumulation to the privacy stance.
The synthesis names the gap NextTrack addresses: lightweight, explainable,
privacy-preserving, content-based, stateless recommendation. This is the
largest chapter — spend the budget here.

---

## Chapter 3 — Design  (target 1500–1700)

| § | Subheading | Words | References | Figures | Prototype files |
|---|---|---|---|---|---|
| 3.1 | Domain and target users | 150–180 | B1, G1 | — | `README.md` |
| 3.2 | Requirements (functional / non-functional, MoSCoW) | 170–200 | — | — | `README.md` |
| 3.3 | System architecture (four layers) | 220–260 | I1, I2 | F1, F2 | `app/main.py`, `app/api/routes.py` |
| 3.4 | API design (endpoints, contract, error model) | 220–260 | I1, I2, I3 | F2, F7, F8 | `app/api/routes.py`, `app/models/schemas.py` |
| 3.5 | Data model (track schema, dataset) | 150–180 | I3 | F3 | `app/data/tracks.json`, `app/data/loader.py`, `app/models/schemas.py` |
| 3.6 | Recommendation algorithm (scoring, exclusion, tie-break, explanation) | 280–320 | C1, C2, F1, G2 | F4 | `app/config.py`, `app/core/scoring.py`, `app/core/recommender.py`, `app/core/explain.py` |
| 3.7 | Testing and evaluation plan | 150–180 | H1, H2 | F9, F10 | `tests/*.py`, `scripts/evaluate.py` |
| 3.8 | Workplan, feasibility, and risks | 120–150 | — | — | — |

**Notes:** Lean on diagrams/tables (F1–F4) to save words. State the exact
tie-break order (score → popularity → year → id) and the default weights
(genre 0.40, artist 0.20, tempo 0.20, mood 0.10, popularity 0.10) with
`TEMPO_RANGE_BPM = 60`. Be honest in 3.8 about the small dataset and the
deliberate exclusion of external APIs at this stage.

---

## Chapter 4 — Feature Prototype  (target 1100–1300)

| § | Subheading | Words | References | Figures | Prototype files |
|---|---|---|---|---|---|
| 4.1 | Prototype overview & stack | 130–160 | I2, I3 | F5, F6 | `README.md`, `app/main.py` |
| 4.2 | `POST /recommend` walkthrough | 180–210 | — | F7 | `app/api/routes.py`, `sample_request.json` |
| 4.3 | Scoring & history exclusion in practice | 180–210 | C1 | F7 | `app/core/scoring.py`, `app/core/recommender.py`, `app/config.py` |
| 4.4 | Explanation output (explainability) | 130–160 | F1 | F7 | `app/core/explain.py` |
| 4.5 | Automated testing (42 tests) | 150–180 | — | F9 | `tests/test_scoring.py`, `tests/test_recommender.py`, `tests/test_api.py` |
| 4.6 | Evaluation script & results | 160–190 | H1, H2 | F10, F11 | `scripts/evaluate.py` |
| 4.7 | Critical assessment: what works, limits, improvements | 170–200 | B3, E1, H2, D2 | — | — |

**Notes (honesty guardrails — mandatory):**
- Frame as **feasibility demonstration**, not production readiness.
- State the dataset is **small (30 tracks) and local**.
- State the evaluation compares against the **recommender’s own scoring
  objective**, not human listener satisfaction; it shows the algorithm reliably
  maximises its stated criteria and never repeats history, not that listeners
  prefer the picks.
- Do not present future work (hybrid, external metadata, user study) as if
  already implemented.

---

## Figures / screenshots referenced above

| Key | Figure | Section(s) | Type |
|---|---|---|---|
| F1 | Four-layer architecture diagram | 3.3 | Diagram |
| F2 | Request-flow sequence for `/recommend` | 3.3, 3.4 | Diagram |
| F3 | Data-model table (8 fields) | 3.5 | Table |
| F4 | Scoring-weights table + formula | 3.6 | Table/equation |
| F5 | Swagger UI at `/docs` | 4.1 | Screenshot |
| F6 | `curl /health` response | 4.1 | Screenshot |
| F7 | `POST /recommend` request + JSON response (with `explanation`) | 4.2–4.4 | Screenshot |
| F8 | 404 (all-in-history) and 400 (negative weights) errors | 3.4 | Screenshot |
| F9 | `pytest -q` showing 42 passed | 3.7, 4.5 | Screenshot |
| F10 | `python scripts/evaluate.py` table + summary | 3.7, 4.6 | Screenshot |
| F11 | Optional bar chart: Rec vs Random per scenario | 4.6 | Chart |

## Drafting order (recommended)
1. Chapter 1 (momentum) → 2. Chapter 3 (you know the system) →
3. Chapter 4 (evidence-led) → 4. Chapter 2 (most source-heavy, do with the
   verified reference bank to hand). Re-check total word count after each.
