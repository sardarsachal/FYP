# Chapter 1: Introduction

## 1.1 Concept and Motivation

Digital music distribution has fundamentally altered how humans consume audio content. Modern commercial streaming platforms—such as Spotify, Apple Music, and YouTube Music—manage music libraries encompassing over 100 million tracks. To help users navigate these vast catalogs, platforms rely heavily on automated Music Recommendation Systems (MRSs) and automated playlist continuation generators. However, the architectural paradigm underpinning virtually all commercial recommender engines is built around persistent user tracking, centralized profiling, and long-term behavioral logging.

While stateful recommendation models driven by deep collaborative filtering and implicit feedback tracking yield high predictive precision, they introduce significant systemic issues:

**Privacy Invasiveness and Surveillance Concerns:** Stateful recommendation engines require continuous logging of explicit interactions (e.g., likes, skips, replays) and implicit signals (e.g., timestamped listening events, device identifiers, geolocation data). Storing these behavioral footprints on centralized cloud servers exposes sensitive psychological and personal data to potential data breaches, unauthorized cross-platform profiling, and intrusive commercial exploitation.

**Account Context Pollution and Profile Corruption:** Stateful user profiling assumes that a single user account maps to one unique listener with static or slowly evolving tastes. In practice, accounts are frequently shared across household members, co-workers, or ambient environments (e.g., playing children's lullabies, party background music, or gym playlists). These temporary listening sessions pollute the user's primary profile, resulting in inaccurate future recommendations.

**The Cold-Start Problem and Friction for Ephemeral Listeners:** Stateful recommendation engines degrade significantly when evaluating new users or unauthenticated listeners who lack sufficient historical interaction logs. Ephemeral listeners seeking immediate session-based continuity without creating an account or consenting to persistent tracking are routinely subjected to generic, top-chart recommendations.

NextTrack addresses these limitations by replacing user-centric stateful profiling with a stateless, session-centric orchestration architecture. NextTrack is a RESTful API that computes the single best "next track" based strictly on the parameters supplied within an individual HTTP POST request. By accepting a short sequence of recent track identifiers, optional preference constraints, and candidate metadata in the request body, NextTrack evaluates track transitions in real time. The system retains zero state on the server, guarantees that no user logs or profiles are persisted, and ensures complete privacy while providing contextually aware recommendations.

## 1.2 Problem Statement

The primary challenge addressed in this project is designing an API that delivers contextually accurate, smooth music transitions without maintaining user profiles or tracking session logs. Stateless recommendation introduces distinct algorithmic constraints:

**Absence of User History:** The recommendation engine cannot access long-term interaction matrices, historical user-item ratings, or global collaborative filtering vectors.

**Inference from Minimal Data:** The algorithm must infer immediate musical context—such as stylistic flow, tempo progression, and emotional mood—from a limited sequence of track identifiers.

**Real-Time Performance:** Because preference processing and candidate scoring must occur dynamically within a single HTTP request lifecycle, computational complexity must remain strictly bounded to guarantee low-latency API responses.

## 1.3 Project Template and Scope

This project falls under the RESTful Web API, Music Information Retrieval (MIR), and Interactive Web Application project template. The scope encompasses the design, implementation, and evaluation of a software system comprising:

**A Stateless RESTful Backend:** Built using Python and FastAPI, adhering to OpenAPI standards and implementing custom scoring modules.

**A Hybrid Content-Graph Scoring Engine:** Combining metadata filtering (genre, mood, tempo), normalized attribute distance functions, and an offline artist similarity graph derived from Last.fm data.

**An Explainable Decision Pipeline:** Generating natural-language explanations alongside detailed sub-score breakdowns for every recommended track to ensure transparency.

**An Interactive Frontend Demonstration Interface:** A single-page application (SPA) featuring an embedded audio/video player (via YouTube IFrame integration) that allows users to test session flows, adjust preference weights, and review scoring diagnostics in real time.

## 1.4 Report Structure

The remainder of this report is organized as follows:

- **Chapter 2 (Literature Review):** Critically examines classical and modern recommendation paradigms in MIR, contextualizing stateless session-aware design against privacy-preserving frameworks.
- **Chapter 3 (Design):** Details the system architecture, component interactions, mathematical formalisms of the scoring functions, and weight distribution rationale.
- **Chapter 4 (Implementation):** Outlines the backend and frontend code structures, key algorithms (e.g., session inference, diversity sampling), and interface designs.
- **Chapter 5 (Evaluation):** Presents automated unit-testing results and offline evaluations of recommendation quality—a comparison against a random baseline, a weight-sensitivity analysis, and a session-aware-versus-baseline A/B on session coherence—together with the design and current status of a user study.
- **Chapter 6 (Conclusion):** Summarizes the project achievements, reflects on architectural trade-offs, and proposes future enhancements.

---

# Chapter 2: Literature Review

## 2.1 Overview of Recommender Systems in Music Information Retrieval (MIR)

Music Information Retrieval (MIR) is an interdisciplinary domain combining computer science, signal processing, musicology, and cognitive psychology. Recommender systems represent one of the most commercially significant applications of MIR. The primary objective of a Music Recommendation System (MRS) is to select audio tracks from a large catalog that align with user preferences, current listening context, or active session flow.

Unlike e-commerce recommenders—where items (e.g., books, appliances) are purchased infrequently and consumed over extended periods—music consumption exhibits distinct behavioral traits:

- **Short Duration and Sequential Consumption:** Tracks typically last between 2 and 5 minutes, meaning users consume dozens of items per session.
- **Repetition and Satiation:** Users frequently re-listen to familiar tracks, though overexposure leads to temporary satiation.
- **Context Sensitivity:** Musical choice is strongly influenced by concurrent activities (e.g., studying, exercising, commuting), time of day, and emotional state.
- **Passive Listening:** Music is often consumed in a "lean-back" mode where automated sequence generation directly determines the user experience.

To model these dynamics, researchers have explored three main algorithmic paradigms: Collaborative Filtering (CF), Content-Based Filtering (CBF), and Context-Aware / Session-Based Recommender Systems.

## 2.2 Collaborative Filtering and Matrix Factorization

Collaborative Filtering (CF) remains the dominant strategy in large-scale commercial recommenders. CF algorithms predict user interest by identifying historical consumption patterns shared across large user populations.

**User-Based and Item-Based Collaborative Filtering.** Early CF systems operated on explicit user-item rating matrices `R ∈ R^(U×I)`, where `U` represents the set of users and `I` the set of items. In memory-based CF, recommendations are generated by computing similarity metrics (e.g., Cosine Similarity or Pearson Correlation) across user vectors or item vectors:

```
sim_cosine(u, v) = (u · v) / (‖u‖₂ · ‖v‖₂)
```

In implicit feedback settings—where explicit 1–5 star ratings are rare—interactions are modeled as binary indicators (listened / not listened) weighted by confidence values derived from play counts, skip rates, or listening duration.

**Model-Based Techniques and Matrix Factorization.** To handle matrix sparsity, model-based techniques decompose the interaction matrix into low-rank latent feature spaces. Matrix Factorization models, such as Singular Value Decomposition (SVD) and Implicit Alternating Least Squares (iALS), project users and items into a shared latent space `R^k` (where `k ≪ min(|U|, |I|)`):

```
r̂(u,i) = p_uᵀ · q_i
```

where `p_u ∈ R^k` represents user `u`'s latent preferences and `q_i ∈ R^k` represents item `i`'s attributes.

**Critical Limitations of CF in Privacy-Preserving Contexts.** While CF captures nuanced preference patterns without requiring item metadata, it presents fundamental drawbacks for privacy-conscious system design:

- **Mandatory Behavioral Tracking:** CF requires persistent storage of user interaction histories (`R`) on central servers to construct user latent vectors (`p_u`).
- **Cold-Start Sensitivity:** CF cannot evaluate new items lacking interaction histories or unauthenticated users lacking historical logs.
- **Popularity Bias and the Long Tail:** As demonstrated by Celma (2010), CF algorithms concentrate recommendations within high-popularity items, suppressing niche or independent artists in the "long tail".

## 2.3 Content-Based Filtering (CBF) and Audio Feature Processing

Content-Based Filtering (CBF) bypasses user interaction matrices by making recommendations based on item properties. In MIR, CBF approaches analyze two primary data modalities: high-level editorial metadata and low-level acoustic signal features.

**High-Level Semantic Metadata.** Editorial metadata includes discrete categorical tags such as genre, mood, sub-genre, release year, record label, and artist country of origin. These descriptors provide clear human-interpretable categories for filtering and scoring. However, traditional metadata suffers from vocabulary inconsistency, incomplete coverage, and subjective tagging discrepancies across databases (e.g., MusicBrainz vs. Spotify Web API).

**Low-Level Acoustic Signal Processing.** To eliminate manual tagging dependencies, audio-based CBF extracts physical features directly from raw audio signals:

- **Timbral Features:** Mel-Frequency Cepstral Coefficients (MFCCs) capture spectral envelope characteristics, summarizing instrument timbres.
- **Rhythmic Features:** Tempo estimation (BPM detection) and onset detection energy curves quantify rhythmic density and tempo transitions.
- **Harmonic Features:** Chromagram analysis maps audio energy across the 12 semitone pitch classes, facilitating key and chord progression matching.

**Limitations of Pure CBF.** Although CBF is inherently immune to the cold-start problem and does not require persistent user tracking, pure CBF models exhibit critical weaknesses:

- **Filter Bubbles and Lack of Serendipity:** CBF models tend to recommend tracks that are acoustically or metadata-identical to input items, limiting novelty.
- **Semantic Gap:** Low-level acoustic features (e.g., MFCCs) do not always correlate with high-level human perception of mood, culture, or genre context; early work by Whitman & Ellis (2004) explored the use of non-content information such as metadata and text to complement audio features.

## 2.4 Session-Based and Sequence-Aware Recommendation Systems

Session-Based Recommender Systems (SBRS) represent a paradigm shift in recommendation research. Rather than modeling static, long-term user profiles, SBRS focus on predicting the next item based on an active sequence of interaction events within a discrete time window.

**Theoretical Framework.** Quadrana et al. (2018) define sequence-aware recommender systems as functions that accept an ordered sequence of user actions `S = (s₁, s₂, …, sₙ)`—where each `sᵢ` represents an interaction event—and compute a ranked list of candidate items for position `sₙ₊₁`. In stateless session setups, the user identifier `u` is either anonymized or intentionally omitted, making the recommendation purely dependent on sequence dynamics.

**Sequential Modeling Methodologies.**

- **Markov Chains (MCs):** Early sequence models used first-order or k-th order Markov Chains to compute state transition probabilities `P(sₙ₊₁ | sₙ)`. While computationally lightweight, MCs struggle with long-range dependencies and state-space explosion when handling large track catalogs.
- **Recurrent Neural Networks (RNNs) and Transformers:** Deep models—such as GRU4Rec and SASRec—use recurrent units or self-attention layers to model complex sequential transitions across long sessions. However, these models require high-performance hardware (GPUs) for inference, making them difficult to deploy as low-latency, lightweight web APIs.
- **Stateless Session Heuristics and Nearest-Neighbors:** Research on session-based recommendation demonstrates that structured heuristics (e.g., session-based k-NN and attribute-continuity matching) can be competitive with deep-learning baselines in domain-specific tasks such as playlist continuation, while maintaining low operational overhead (Jannach, Quadrana and Cremonesi, 2012).

## 2.5 Literature Synthesis and Comparative Analysis

Table 2.1 synthesizes key research literature, evaluating methodologies, key findings, and applicability to privacy-preserving, stateless systems.

**Table 2.1 — Literature synthesis**

| Author / Citation | Core Methodology | Primary Findings / Contributions | Relevance & Limitations for NextTrack |
|---|---|---|---|
| Celma (2010) | Complex-network analysis of music consumption and long-tail structure. | Documented that popularity-driven algorithms over-concentrate on head tracks, suppressing long-tail discovery. | Validates keeping popularity weighted low and using artist similarity to aid discovery without user logs. |
| Whitman & Ellis (2004) | Combining editorial/text metadata with acoustic features. | Explored using non-content (metadata/text) information to complement raw audio features. | Supports NextTrack's metadata-plus-audio hybrid design over a pure raw-audio pipeline. |
| Quadrana, Cremonesi & Jannach (2018) | Survey of sequence-aware and session-based recommendation. | Short-term interaction sequences can provide sufficient context for next-item prediction without user profiles. | Forms the theoretical justification for NextTrack's stateless, request-bound session architecture. |
| Jannach, Quadrana & Cremonesi (2012) | Analysis of session-based recommendation and playlist continuation. | Genre consistency and smooth transitions are important to perceived playlist quality. | Directly informs NextTrack's linear BPM distance function and hard genre-preference logic. |

---

# Chapter 3: Design

## 3.1 System Architecture and Modular Boundaries

NextTrack is designed around modular, decoupled components to ensure separation of concerns, complete backend statelessness, and low-latency HTTP request processing. The backend architecture isolates data loading, data model validation, core scoring logic, and API presentation layers.

**Architectural Components.**

- **API Routing Layer (`app/api/routes.py`):** Acts as the primary interface for external clients. It exposes `GET /health` for service health monitoring, `GET /catalogue` for retrieving candidate track metadata, `POST /recommend` for track selection, and `POST /feedback` for study data collection.
- **Schema & Model Layer (`app/models/schemas.py`):** Utilizes Pydantic models to enforce strict structural and boundary validation on incoming JSON payloads. Rejects malformed requests before execution reaches the core recommender engine.
- **Core Recommender Engine (`app/core/recommender.py`):** Manages candidate pool deduplication, excludes previously played tracks, infers missing context from listening history, applies hard filters, and ranks candidate items.
- **Scoring Logic Layer (`app/core/scoring.py`):** Contains pure, stateless functions that compute normalized feature sub-scores `s_f ∈ [0, 1]`.
- **Artist Graph Similarity Module (`app/core/similarity.py`):** Reads a static, offline JSON graph mapping artists to sets of related artists derived from Last.fm data.
- **Explanation Builder (`app/core/explain.py`):** Maps computed raw scores and session context flags into human-readable, transparent natural-language sentences.

## 3.2 Formal Scoring Model and Equation Formalisms

The total match score `S(c, C)` for a candidate track `c` given an active session context `C` is computed as a weighted sum of normalized feature sub-scores:

```
S(c, C) = Σ_{f ∈ F}  w_f · s_f(c, C)
```

where `F = {genre, artist, tempo, mood, popularity}` represents the evaluated feature set, and `w_f` denotes the weight assigned to feature `f`. Weights are non-negative and strictly normalized to sum to 1.0:

```
w_f ≥ 0   ∀ f ∈ F,     Σ_{f ∈ F} w_f = 1.0
```

**Feature Scoring Functions.**

*1. Genre Score* — categorical exact match against preferred or inferred session genre:

```
s_genre(c, C) = 1.0  if genre_c = genre_C,  else 0.0
```

*2. Mood Score* — categorical exact match against preferred or inferred session mood:

```
s_mood(c, C) = 1.0  if mood_c = mood_C,  else 0.0
```

*3. Linear Tempo Closeness* — quantifies rhythmic compatibility using a linear distance function bounded by `TEMPO_RANGE_BPM = 60` BPM. Exact tempo matches score 1.0, while differences of 60 BPM or greater score 0.0:

```
s_tempo(c, C) = max(0.0, 1.0 − |tempo_c − target_tempo_C| / 60)
```

*4. Popularity Score* — converts continuous popularity values (0–100 integer range) into a normalized score:

```
s_popularity(c) = clamp(popularity_c, 0, 100) / 100.0
```

*5. Artist Affinity Score* — evaluates artist matches across explicit preferences, recent session history (`A_seed`), and the Last.fm similarity graph (`G_sim`):

```
s_artist(c, C) = 1.0   if artist_c ∈ A_seed              (exact affinity)
               = 0.6   else if artist_c ∈ G_sim(A_seed)  (similar affinity)
               = 0.0   otherwise
```

## 3.3 Weight Configuration Rationale

Table 3.1 details the default weight distribution defined in `app/config.py` along with the structural rationale for each weight value.

**Table 3.1 — Default weight distribution and rationale**

| Feature (f) | Default Weight (w_f) | Relative Share | Rationale & Behavioral Impact |
|---|---|---|---|
| Genre | 0.40 | 40% | Genre acts as the primary stylistic anchor; mismatching genres causes immediate perceptual dissonance. |
| Artist | 0.20 | 20% | Rewards direct artist affinity and related artists via similarity-graph matching. |
| Tempo | 0.20 | 20% | Maintains steady rhythmic pace across track transitions. |
| Mood | 0.10 | 10% | Fine-tunes overall emotional alignment (e.g., energetic vs. chill). |
| Popularity | 0.10 | 10% | Serves as a minor tie-breaker favoring recognized tracks without overwhelming niche items. |

## 3.4 Data Models and Validation Contracts

Data interchange is governed by strict Pydantic schemas in `app/models/schemas.py`. Validation parameters are summarized below:

- **Track Model:** Enforces non-empty string constraints on `id`, `title`, `artist`, `genre`, and `mood`. Integrates numerical validation bounds: `tempo ∈ [20, 300]` BPM, `year ∈ [1900, 2100]`, and `popularity ∈ [0, 100]`.
- **Preferences Model:** All attributes (`genre`, `mood`, `target_tempo`, `year_min`, `preferred_artist`, `weights`) are optional. Includes operational control flags: `session_aware` (boolean, defaults to True) and `diversity` (float, bounded to `[0.0, 1.0]`).
- **RecommendRequest:** Encapsulates `history` (list of track ID strings), `preferences` (Preferences object), and optional `candidates` (list of Track objects).
- **RecommendResponse:** Returns the selected `recommended_track`, overall float `score`, dictionary `score_breakdown`, natural-language `explanation` string, and a list of `ranked_alternatives`.

---

# Chapter 4: Implementation

## 4.1 Technology Stack and Package Structure

NextTrack is implemented in Python using modern web application practices.

- **FastAPI Framework:** Selected for asynchronous performance, automated OpenAPI document generation, and native integration with Pydantic validation.
- **Uvicorn ASGI Server:** Provides a lightweight deployment server for handling non-blocking I/O.
- **HTML5 / CSS3 / JavaScript (ES6+):** Powers the single-page application frontend, rendering dynamic score breakdowns and controlling YouTube IFrame playback.

```
nexttrack/
|-- app/
|   |-- api/
|   |   `-- routes.py            # RESTful endpoint definitions
|   |-- core/
|   |   |-- explain.py           # Natural language explanation builder
|   |   |-- recommender.py       # Main recommendation orchestration engine
|   |   |-- scoring.py           # Pure scoring functions
|   |   `-- similarity.py        # Static artist similarity graph loader
|   |-- data/
|   |   |-- artist_similarity.json # Last.fm artist similarity dataset
|   |   |-- loader.py            # Local track dataset loader and validator
|   |   `-- tracks.json          # Bundled track catalog
|   |-- models/
|   |   `-- schemas.py           # Pydantic input/output schemas
|   |-- config.py                # Configuration constants and default weights
|   |-- feedback.py              # Anonymous study feedback logger
|   |-- main.py                  # Application entry point
|   `-- web/
|       `-- index.html           # Single-page web demonstration player
`-- tests/                       # Automated pytest test suites
```

## 4.2 Core Algorithms and Source Code Analysis

**1. Dynamic Session Context Inference.** When users omit explicit preference parameters, NextTrack infers listening context from recent history using `_session_context()` in `app/core/recommender.py`:

```python
def _session_context(history_tracks: list[dict], preferences: Preferences) -> SessionContext:
    """
    Builds the active scoring context from user preferences and session history.
    Explicit preferences take priority. When session_aware is enabled, recent
    history fills in missing preferences and defines artist affinity.
    """
    ctx = SessionContext(
        genre=preferences.genre,
        mood=preferences.mood,
        target_tempo=preferences.target_tempo,
        preferred_artist=preferences.preferred_artist,
    )
    if not getattr(preferences, "session_aware", True) or not history_tracks:
        return ctx

    # Extract recent tracks up to RECENT_HISTORY limit (5 tracks)
    recent = history_tracks[-RECENT_HISTORY:]
    ctx.history_artists = {t["artist"] for t in recent if t.get("artist")}

    # Infer most frequent genre if not explicitly specified
    if ctx.genre is None:
        genres = [t["genre"] for t in recent if t.get("genre")]
        if genres:
            ctx.genre, ctx.genre_inferred = Counter(genres).most_common(1)[0][0], True

    # Infer most frequent mood if not explicitly specified
    if ctx.mood is None:
        moods = [t["mood"] for t in recent if t.get("mood")]
        if moods:
            ctx.mood, ctx.mood_inferred = Counter(moods).most_common(1)[0][0], True

    # Infer target tempo using mean of recent history
    if ctx.target_tempo is None:
        tempos = [t["tempo"] for t in recent if isinstance(t.get("tempo"), int)]
        if tempos:
            ctx.target_tempo, ctx.tempo_inferred = int(round(sum(tempos) / len(tempos))), True

    return ctx
```

**2. Deterministic Candidate Scoring and Sorting.** In `recommend()`, candidate tracks are scored, breakdown dictionaries are constructed, and candidates are sorted deterministically:

```python
# Score candidates against effective session context
scored = []
for track in pool:
    raw = {
        "genre": score_genre(track["genre"], context.genre),
        "artist": score_artist_affinity(
            track["artist"], context.preferred_artist,
            context.history_artists, similar_artists
        ),
        "tempo": score_tempo(track["tempo"], context.target_tempo),
        "mood": score_mood(track["mood"], context.mood),
        "popularity": score_popularity(track["popularity"]),
    }
    breakdown = {f: round(raw[f] * weights[f], 4) for f in SCORING_FEATURES}
    total = round(sum(breakdown.values()), 4)
    scored.append({"track": track, "raw": raw, "breakdown": breakdown, "total": total})

# Deterministic tie-breaking sort: Total Score -> Popularity -> Year -> ID
scored.sort(
    key=lambda s: (
        -s["total"],
        -s["track"]["popularity"],
        -s["track"]["year"],
        s["track"]["id"],
    )
)
```

**3. Score-Weighted Diversity Sampling.** To prevent content-based filter bubbles when `diversity > 0`, `_select_with_diversity()` samples candidates within a dynamic score window:

```python
def _select_with_diversity(scored: list[dict], history: list[str], diversity: float) -> dict:
    """
    Selects a track applying diversity control. Returns the top-ranked item
    if diversity is 0. Otherwise, samples probabilistically from top candidates
    within a window determined by diversity.
    """
    if diversity <= 0 or len(scored) == 1:
        return scored[0]

    best_total = scored[0]["total"]
    threshold = best_total * (1.0 - diversity)

    # Filter candidates within diversity threshold window up to maximum ceiling
    window = [s for s in scored if s["total"] >= threshold][:DIVERSITY_MAX_WINDOW]
    if len(window) == 1:
        return window[0]

    # Seed pseudorandom number generator using request history for reproducibility
    seed_src = "|".join(history or []) + f"|{diversity:.3f}"
    seed = int(hashlib.md5(seed_src.encode()).hexdigest(), 16)
    rng = random.Random(seed)

    # Weighted random choice proportional to candidate total score
    weights = [max(s["total"], 0.0) + 0.01 for s in window]
    return rng.choices(window, weights=weights, k=1)[0]
```

## 4.3 Web Application Interface

The single-page web interface (`app/web/index.html`) demonstrates the API's capabilities through an interactive music player. *(Insert screenshot of the interface.)*

The web client manages session flow through a simple interaction loop:

1. **Catalog Initialization:** Requests catalog tracks and filter vocabularies via `GET /catalogue?playable_only=true`.
2. **Recommendation Request:** As each track finishes playing, the client constructs a `RecommendRequest` containing the played track IDs in `history` and any user-configured controls in `preferences`.
3. **API Processing and Display:** Executes `POST /recommend`, passes the resulting YouTube ID to the player, and updates the UI with the score breakdown and explanation string.

---

# Chapter 5: Evaluation

Correctness and recommendation quality are evaluated separately. All quantitative results reported here are produced by the repository's evaluation script (`scripts/evaluate.py`) with a fixed random seed, and are therefore reproducible.

## 5.1 Automated Testing

Testing follows the layered architecture. Because the scoring and recommendation logic are pure functions (no I/O or global state), they are tested directly with concrete inputs, and the API is tested through FastAPI's in-process test client without a running server. The suite comprises **55 tests** (Table 5.1), all passing on the current build.

**Table 5.1 — Automated test suite**

| Test module | Tests | Coverage |
|---|---|---|
| `tests/test_scoring.py` | 22 | Each per-feature sub-score in isolation: match / mismatch / missing preference; the linear tempo decay (half-range and beyond-range cases); popularity normalization; weight normalization summing to one; and rejection of negative and all-zero weights. |
| `tests/test_recommender.py` | 25 | Highest-scoring selection, history exclusion, duplicate-id handling, deterministic tie-breaking, session-aware genre/mood/tempo inference, exact and similar-artist affinity, the diversity control (determinism at 0, reproducibility, variety, continued history exclusion), explicit genre/mood hard-filtering with graceful relaxation, and score-breakdown/explanation integrity. |
| `tests/test_api.py` | 8 | `/health`; `/recommend` with inline candidates and via the bundled dataset; presence of all required response fields; history exclusion; and each error path — 404 (no candidates), 400 (invalid weights), 422 (malformed body). |

These cover the principal edge cases — empty history, omitted or empty candidates, all candidates already in history, missing preferences, duplicate identifiers, invalid weights, and a malformed body. The suite also provides regression protection: it grew from 42 tests at the preliminary stage to 55 as the session-aware, similarity, diversity, and explicit-filtering features were added, with each new feature accompanied by tests that also guard previously working behavior.

## 5.2 Comparison Against a Random Baseline

**Method.** For each of five scenarios, the recommender's chosen-track score is compared against the mean score of `N = 1000` random picks (seed 42) from the same eligible pool — the exact set of tracks the recommender itself scored — so the baseline uses an identical objective and differs only in choosing randomly:

```
score_random  = (1/N) · Σ_{i=1..N}  score(random eligible track_i)
improvement%  = (score_rec − score_random) / score_random × 100
```

**Result.** On the 395-track catalogue the recommender averaged **0.962** against a random average of **0.728**, an average improvement of **+32.3%**, and in every scenario an automated check confirmed that no history track was ever recommended (Table 5.2). This figure should be read in context: because an explicitly chosen genre and mood act as hard filters, the eligible pool from which the random baseline draws consists only of tracks that already match the request — all of which score highly. The baseline is therefore "a random pick among already-relevant tracks", a far harder comparator than "a random pick from the whole catalogue", and outperforming it by roughly a third — purely by ranking the relevant tracks on tempo, popularity, and artist affinity — is a more honest result than a larger figure obtained against an easier baseline. As Section 2 notes, this still measures the scoring objective rather than human satisfaction, which motivates the further criteria below.

**Table 5.2 — Recommender vs random baseline (1000 trials/scenario, seed 42)**

| Scenario | Recommender | Random | Improvement |
|---|---|---|---|
| Energetic rock | 0.962 | 0.738 | +30.4% |
| Calm ambient | 0.956 | 0.700 | +36.6% |
| Happy pop | 0.984 | 0.758 | +29.9% |
| Energetic hiphop | 0.969 | 0.750 | +29.3% |
| Calm jazz | 0.939 | 0.694 | +35.3% |
| **Average** | **0.962** | **0.728** | **+32.3%** |

## 5.3 Weight-Sensitivity Analysis

**Method.** Each feature weight is scaled, one at a time, by {0.5, 0.75, 1.25, 1.5}, re-normalized, and the recommendation recomputed; a *flip* is a change in the top recommendation versus the default. Over all perturbations, `stability` is the fraction that left the top pick unchanged and `influence(f)` is the fraction of feature `f`'s perturbations that flipped it.

**Result.** Over 100 perturbations (five features × four factors × five scenarios) the top recommendation was **stable in 94%** of cases. Perturbing **genre, artist, or mood never changed the pick** (influence 0%), because the strongly weighted preference match survives a ±50% change to any one weight; the pick shifted only on the low-weight tie-breakers — **popularity** (influence 20%) and **tempo** (10%). Both facts support the chosen weights: the dominant features are robustly dominant, and what little sensitivity exists is confined to the features whose role is only to break near-ties. This is the empirical justification for the weights in Table 3.1 — the recommendation does not hinge on their exact values.

## 5.4 Session-Aware vs Baseline (A/B on Session Coherence)

**Method.** The session-aware recommender is compared against an explicit-preferences-only baseline (`session_aware = false`) by simulating one seeded session per genre with no explicit preferences, then measuring **session coherence** on metrics *independent of the recommender's own objective*. For recommendations `r₁…rₙ` from a seed `s`:

```
genre_coherence  = (1/n) · Σ_i [ genre(r_i) = genre(s) ]
mood_coherence   = (1/n) · Σ_i [ mood(r_i)  = mood(s)  ]
artist_affinity  = (1/n) · Σ_i [ artist(r_i) already heard earlier in the session ]
```

**Result (Table 5.3).** With no explicit preferences supplied, the session-aware recommender keeps the session strongly coherent — staying in the seed's genre and mood and returning to heard or related artists — whereas the baseline drifts toward globally popular tracks regardless of context. Because these metrics are defined independently of the recommender's own objective, they constitute a fair test of the extension rather than a circular one, and they isolate the effect cleanly: the two conditions differ only in whether history-based adaptation is enabled.

**Table 5.3 — Session coherence: session-aware vs baseline (one seeded session per genre)**

| Metric | Session-aware | Baseline | Difference |
|---|---|---|---|
| Genre coherence | 100.0% | 8.3% | +91.7 |
| Mood coherence | 90.0% | 36.7% | +53.3 |
| Artist affinity | 53.3% | 0.0% | +53.3 |

## 5.5 User Study (Design and Status)

Because offline metrics cannot establish *perceived* quality, a user-centred evaluation was designed and its apparatus built into the application. In a blind **study mode**, the app randomly assigns the session-aware or baseline method to each recommendation, hides the method (and the explanation and score breakdown, which would otherwise reveal it), and collects a 1–5 relevance rating logged anonymously via `POST /feedback`; the diversity control is held constant across both conditions so it cannot confound the comparison. The planned analysis compares the methods by the difference in mean rating, `Δ = mean(rating | session-aware) − mean(rating | baseline)`, with a Mann–Whitney U test (appropriate for ordinal 1–5 data) at α = 0.05, using `scripts/analyze_feedback.py`. An end-to-end dry run confirmed that ratings are recorded correctly and that the analysis script reports the difference in means and the significance test. **At the time of writing, the study with participants has not yet been run, so no participant results are reported here**; running the study and reporting its results is the primary outstanding item of the evaluation.

## 5.6 Critical Evaluation

**Achievements.** The offline evaluation establishes feasibility and internal validity on three independent fronts: the recommender consistently outperforms a strong random-among-relevant baseline (5.2), is demonstrably robust to the exact values of its parameters (5.3), and its session-aware extension measurably and substantially improves session coherence on metrics external to its own objective (5.4). The convergence of these three results is stronger evidence than any one alone, and the system is backed by a passing 55-test suite.

**Limitations and improvements.** The most important limitation is one of scope: every offline metric measures the system's own objective or a proxy for coherence, none of which is the same as human satisfaction, so the user study (5.5) is the decisive outstanding work. The catalogue, though real and reproducible, is a demonstration scale (395 tracks), only a subset of which is currently playable because of the YouTube Data API's daily quota; at this scale, high genre coherence is easier to achieve than it would be over a very large catalogue. Categorical matching is transparent but coarse ("rock" and "indie rock" do not match), and mood labels derived from audio classifiers are approximate. Two limitations were surfaced *by using the system* and then corrected — content-based over-specialisation (which motivated the diversity control) and an explicit low-weight mood being ignored (which motivated the explicit-preference hard filter) — both now covered by automated tests; notably, the second change is what strengthened the random baseline in Section 5.2. The clear next step, once user-study data is collected, is to use it to learn the feature weights and re-test them.

---

# Chapter 6: Conclusion

## 6.1 Summary of Contributions

This project designed, implemented, and evaluated NextTrack, a privacy-preserving, stateless RESTful music recommendation API. By replacing stateful user profiling with request-bound session inference, NextTrack addresses key privacy, context-pollution, and cold-start challenges in modern music recommendation systems. The core technical contributions of this work include:

- **Stateless API Architecture:** A lightweight backend using FastAPI and Pydantic that computes recommendations dynamically, retaining zero server-side state.
- **Hybrid Scoring Engine:** Combining content-metadata matching, a linear tempo distance function, popularity normalization, and a Last.fm artist-similarity graph into a unified, explainable model.
- **Explainable Output Pipeline:** Generating clear natural-language explanations and sub-score breakdowns for every recommendation to ensure algorithmic transparency.
- **Interactive Demonstration Web Player:** A single-page application integrated with YouTube playback that lets users test real-time session flows and inspect system diagnostics.
- **Multi-Part Evaluation:** Offline evaluation showing the recommender outperforms a strong random-among-relevant baseline (+32.3%), is robust to its exact weights (94% stability), and substantially improves session coherence over an explicit-only baseline (genre 100% vs 8.3%), together with a complete apparatus and protocol for a user study still to be run.

## 6.2 Limitations and Reflection

While NextTrack achieves its core design goals, several architectural trade-offs warrant discussion:

- **Dependence on Input Metadata Quality:** Because NextTrack relies on track attributes from candidate payloads or the local catalog, missing or inaccurate metadata (e.g., wrong tempo tags) directly impacts recommendation precision.
- **Coarse Audio Feature Modeling:** High-level metadata (genre, mood, tempo) does not fully capture fine-grained acoustic properties such as key transitions, harmonic density, or arrangement dynamics.
- **Fixed Similarity Graphs:** The bundled Last.fm artist-similarity graph is static. Dynamic graph updating would require external network calls, potentially increasing API latency.
- **Evaluation Scope:** The perceived-quality user study has not yet been run, so current evidence establishes feasibility and internal validity rather than proven listener satisfaction.

## 6.3 Future Work

Future development can build upon NextTrack's stateless framework in several directions:

- **Run and iterate on the user study:** Collect participant ratings with the built-in apparatus, then use the findings to learn the feature weights and re-test them.
- **Fuzzy and semantic similarity:** Replace exact categorical matching with partial or embedding-based similarity so genuinely related tracks (e.g., "rock" and "indie rock") are treated as related.
- **Client-Side Feature Extraction via WebAssembly (Wasm):** Run lightweight feature extraction (e.g., BPM estimation and key detection) in the user's browser and attach the results to the request, keeping processing local to the device.
- **Harmonic Key Compatibility (Camelot Wheel Matching):** Extend the scoring engine to evaluate harmonic key relationships for smoother melodic transitions between consecutive tracks.
- **Multi-Criteria Context Inference:** Enhance session inference with additional in-request context (e.g., time of day) supplied per request, without storing persistent user profiles.

---

# References

Celma, Ò. (2010). *Music Recommendation and Discovery: The Long Tail, Long Fail, and Long Play in the Digital Music Space*. Springer Berlin Heidelberg. https://doi.org/10.1007/978-3-642-13287-2

Jannach, D., Quadrana, M., & Cremonesi, P. (2012). Session-based recommender systems. In *Recommender Systems Handbook*. Springer.

Quadrana, M., Cremonesi, P., & Jannach, D. (2018). Sequence-aware recommender systems. *ACM Computing Surveys (CSUR)*, 51(4), 1–36. https://doi.org/10.1145/3190616

Whitman, B., & Ellis, D. (2004). Automatic record review generation from metadata and audio. In *Proceedings of the International Society for Music Information Retrieval Conference (ISMIR 2004)*.

<!--
Note: bibliographic details (volume, issue, pages, DOIs, editions, access dates) must be
checked against the original sources before submission. If Chapter 5 cites McNee et al. (2006)
or other works on evaluation, add them here; the fuller, verified reference list is in
HARVARD_REFERENCE_LIST.md.
-->
