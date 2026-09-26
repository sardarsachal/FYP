# Chapter 3: Design

## 3.1 Domain and target users

NextTrack operates in the domain of music recommendation, specifically the *next-track* selection task: choosing one track to continue an active listening session. This is a well-established but non-trivial sub-problem of music recommender systems, where items are short, consumed sequentially, and influenced by context such as mood and activity (Schedl et al., 2015 `[VERIFY]`). Rather than modelling long-term taste, NextTrack treats each request as a self-contained decision informed by recent history and explicit preferences, an approach consistent with session- and sequence-aware recommendation (Quadrana, Cremonesi and Jannach, 2018 `[VERIFY]`).

The system has two classes of users. The **direct users** are developers and client applications that integrate the API: they send structured requests and consume JSON responses, and they require a predictable, well-documented, stateless interface. The **indirect users** are listeners, who never interact with the API directly but experience its output through a client application. The design therefore prioritises a clear contract and machine-readable responses for direct users, while ensuring that the recommendation itself, and its accompanying natural-language explanation, are meaningful for the listener's experience.

## 3.2 Requirements

The requirements are summarised in Table 3.1. Functional requirements capture what the service must do; non-functional requirements capture qualities it must exhibit.

**[Table 3.1: Functional and non-functional requirements]**

| Type | Requirement |
|---|---|
| Functional | Accept a request containing listening history, preferences, and optional candidate tracks. |
| Functional | Return a single recommended next track with a total score, a per-feature score breakdown, and a natural-language explanation. |
| Functional | Exclude tracks already present in the listening history. |
| Functional | Provide a health-check endpoint and a recommendation endpoint. |
| Functional | Validate input and return clear, structured error responses. |
| Non-functional | Statelessness: each response depends only on its request; no user data is persisted. |
| Non-functional | Explainability: every recommendation is justified to the user. |
| Non-functional | Determinism: identical inputs yield identical outputs. |
| Non-functional | Testability: the logic is verifiable through automated tests. |
| Non-functional | Simplicity: the design favours a minimal, maintainable prototype. |

Statelessness is both a design principle and a core property of the REST architectural style (Fielding, 2000 `[VERIFY]`), and here it additionally serves the project's privacy-conscious motivation by reducing reliance on stored user profiles.

## 3.3 System architecture

NextTrack is structured into four cooperating layers, shown in Figure 3.1. Separating responsibilities in this way keeps the recommendation logic independent of the web framework and the data source, so each can be tested or replaced in isolation.

**[Figure 3.1: NextTrack system architecture]**

1. **API layer** (`app/api/routes.py`, `app/main.py`) — built on FastAPI (Ramírez `[VERIFY]`). It defines the HTTP endpoints, maps internal results to responses, and translates errors into HTTP status codes.
2. **Validation / schema layer** (`app/models/schemas.py`) — Pydantic models that validate and type-check incoming requests and structure outgoing responses (Pydantic documentation `[VERIFY]`).
3. **Recommendation logic layer** (`app/core/recommender.py`, `scoring.py`, `explain.py`, `config.py`) — the stateless core that scores candidates, excludes history, ranks, and generates explanations.
4. **Data / testing layer** (`app/data/loader.py`, `tracks.json`, `tests/`) — loads and validates the local dataset and exercises all layers through automated tests.

The request flow for a recommendation is shown in Figure 3.2. A client sends a request to `/recommend`; FastAPI and Pydantic validate the body; candidates are taken from the request if supplied, otherwise loaded from the local dataset; the recommender excludes history tracks, scores and ranks the remaining candidates, applies deterministic tie-breaking, and builds a natural-language explanation; the result is serialised as JSON and returned. Because no state is retained, the same request always produces the same response.

**[Figure 3.2: `/recommend` request flow]**

## 3.4 API design

The API exposes two endpoints. `GET /health` is a lightweight liveness check returning a small JSON object with the service status and version. `POST /recommend` is the primary endpoint: it accepts a JSON body containing `history` (a list of track identifiers), `preferences` (optional parameters and weights), and an optional `candidates` list. When `candidates` is omitted, the service falls back to the bundled local dataset, allowing the same endpoint to serve both client-supplied and built-in catalogues.

Error handling is explicit and mapped to appropriate HTTP status codes, returned in a consistent error envelope of the form `{"error": {"code", "message"}}`:

- **422 — validation error:** a malformed body that fails Pydantic validation (handled automatically by the framework).
- **400 — invalid input:** semantically invalid input the schema cannot catch, such as negative scoring weights, raised as a `ValueError` during normalisation.
- **404 — no candidates:** no candidates remain to recommend, for example when every candidate is already in the history.
- **500 — dataset loading error:** the local dataset cannot be loaded or fails validation.

This layered validation — type-level checks at the schema boundary and semantic checks within the logic — keeps the endpoint thin while producing predictable, debuggable responses for direct users.

## 3.5 Data model

Each track is represented by eight metadata fields, summarised in Table 3.2. These fields are the basis for content-based scoring, which derives recommendations from item attributes rather than interaction histories (Pazzani and Billsus, 2007 `[VERIFY]`).

**[Table 3.2: Track data model]**

| Field | Type | Constraint | Role |
|---|---|---|---|
| `id` | string | non-empty, unique | history matching, tie-breaking |
| `title` | string | non-empty | display, explanation |
| `artist` | string | non-empty | artist-match score |
| `genre` | string | non-empty | genre-match score |
| `tempo` | integer | realistic BPM range | tempo-closeness score |
| `mood` | string | non-empty | mood-match score |
| `year` | integer | realistic year range | tie-breaking (recency) |
| `popularity` | integer | 0–100 | popularity score, tie-breaking |

The dataset is a **local 30-track dataset** stored as a JSON file, spanning several genres and moods. It is intentionally small: sufficient to demonstrate the mechanism but not representative of a full catalogue, a limitation revisited in Section 3.8.

## 3.6 Recommendation algorithm

NextTrack uses **weighted content-based scoring**. Each candidate not excluded by the history receives an overall score that is a weighted sum of five per-feature sub-scores, each in the range [0, 1]:

```
score = w_genre·s_genre + w_artist·s_artist + w_tempo·s_tempo
      + w_mood·s_mood  + w_popularity·s_popularity
```

The sub-scores are defined as follows. Genre, artist, and mood are exact matches against the corresponding preference, scoring 1.0 on a match and 0.0 otherwise. Tempo is scored by linear closeness to a target tempo, `max(0, 1 − |tempo − target| / R)`, where `R` is a configurable tempo range (60 BPM in the prototype), so an exact match scores 1.0 and the score decays to 0.0 at the range boundary. Popularity is normalised as `popularity / 100`. The default feature weights are given in Table 3.3 and are **normalised to sum to one** before use; negative weights are rejected, and clients may override the defaults per request.

**[Table 3.3: Scoring features and default weights]**

| Feature | Default weight | Sub-score rule |
|---|---|---|
| genre | 0.40 | exact match → 1.0, else 0.0 |
| artist | 0.20 | exact match → 1.0, else 0.0 |
| tempo | 0.20 | linear closeness within range |
| mood | 0.10 | exact match → 1.0, else 0.0 |
| popularity | 0.10 | popularity / 100 |

History exclusion is applied before scoring: any candidate whose `id` appears in the supplied history is removed, so that tracks already heard are not recommended again. Duplicate candidate identifiers are also removed. Ranking is **deterministic**: candidates are ordered by total score, then by higher popularity, then by more recent year, then by lexicographically smaller `id`. This tie-breaking guarantees reproducible output. Finally, a natural-language explanation is generated from the winning track's matched features (for example, citing a matched genre, mood, or proximity to the target tempo), supporting the system's transparency goal (Tintarev and Masthoff, 2007 `[VERIFY]`).

## 3.7 Testing and evaluation plan

Testing operates at three levels. **Scoring unit tests** verify each sub-score function and weight normalisation, including exact matches, mismatches, missing preferences, tempo decay, and rejection of invalid weights. **Recommender unit tests** verify the assembled logic: selection of the highest-scoring track, history exclusion, duplicate handling, deterministic tie-breaking, the score breakdown, and the presence of an explanation. **API tests**, using FastAPI's test client, verify the endpoints end-to-end, including the success path and each error path (422, 400, 404). Edge cases covered include empty history, omitted or empty candidates, all candidates already in history, missing preferences, duplicate candidate identifiers, and malformed requests.

Evaluation compares the recommender against a random-selection baseline over the local dataset across several realistic scenarios, using a fixed random seed for reproducibility and averaging many random trials per scenario. The metric is the system's own weighted score, so the evaluation demonstrates that the recommender reliably selects higher-scoring tracks than chance and never repeats history. Importantly, this evaluates the **scoring objective, not human listener satisfaction**; meaningful user-centred evaluation would require a separate study, since accuracy-style metrics alone are known to be insufficient measures of recommendation quality (McNee, Riedl and Konstan, 2006 `[VERIFY]`).

## 3.8 Workplan, feasibility, and risks

The design is feasible because the prototype is already implemented and verified against the plan above. Several risks and limitations are acknowledged honestly. The **local 30-track dataset** is small, so behaviour at catalogue scale is untested. Genre, artist, and mood use **exact metadata matching**, which is simple and explainable but cannot capture partial or semantic similarity. **No external metadata sources** (such as streaming or music-database APIs) are integrated at this stage, and **no user study** has been conducted, so claims are limited to the scoring objective. Future work to address these risks includes enriching the dataset from external sources offline, introducing fuzzy or similarity-based matching, exploring hybrid methods that combine content-based and collaborative signals (Burke, 2002 `[VERIFY]`), and conducting a user-centred evaluation. These extensions build naturally on the layered architecture without altering its core design.
