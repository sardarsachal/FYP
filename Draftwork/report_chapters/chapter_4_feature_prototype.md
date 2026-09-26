# Chapter 4: Feature Prototype

## 4.1 Prototype overview and goals

The implemented feature prototype is a working, stateless music recommendation service that realises the design presented in Chapter 3. It is built in Python using the FastAPI framework (Ramírez `[VERIFY]`) and exposes two HTTP endpoints: a health check and the recommendation endpoint. The goal of the prototype is to demonstrate the *feasibility* of the proposed approach end-to-end — from receiving a structured request, through weighted content-based scoring, to returning a justified recommendation — rather than to deliver a production system. Accordingly, it operates over a small local dataset and is supported by automated tests and a reproducible evaluation script.

The central technical feature is the `POST /recommend` endpoint. It embodies the project's core contribution: producing a suitable next track from the information contained in a single request, without storing any user data between calls. The `GET /health` endpoint is a supporting feature that confirms the service is running and reports its version, which is useful both for manual testing and for integration. Figure 4.1 shows both endpoints in the automatically generated interactive documentation.

**[Figure 4.1: Swagger UI showing `/health` and `/recommend`]**

## 4.2 Implemented API behaviour

The `/recommend` endpoint accepts a JSON request body with three parts: a `history` list of previously played track identifiers; a `preferences` object containing optional parameters such as genre, mood, target tempo, preferred artist, and scoring weights; and an optional `candidates` list of tracks to choose from. These inputs are validated at the API boundary by Pydantic schemas, so malformed requests are rejected before any recommendation logic runs.

A key convenience of the implementation is candidate fallback. When the `candidates` field is omitted or null, the prototype loads its bundled **local 30-track dataset** and uses those as the candidate pool. The same endpoint therefore serves two modes: clients may supply their own catalogue inline, or rely on the built-in dataset. This keeps the API flexible while allowing the prototype to be demonstrated without any external data. Successful requests return a structured JSON response containing the recommended track, a numeric score, a per-feature score breakdown, a natural-language explanation, and a ranked list of alternatives (Figure 4.2). Error conditions are returned with appropriate status codes and a consistent error envelope, as described in Chapter 3.

**[Figure 4.2: Successful `/recommend` JSON response]**

## 4.3 Recommendation logic in the prototype

Internally, the recommender executes the pipeline designed in Section 3.6. It first removes any duplicate candidate identifiers and then **excludes every track whose identifier appears in the listening history**, so a previously played track is never returned within the same session. Each remaining candidate is then scored as a weighted sum of five content-based sub-scores — genre, artist, tempo, mood, and popularity — using weights normalised to sum to one. This content-based strategy derives recommendations from item attributes rather than accumulated user interactions (Pazzani and Billsus, 2007 `[VERIFY]`). Candidates are ranked by total score, with **deterministic tie-breaking** by popularity, then year, then identifier, so identical inputs always yield identical outputs. Finally, the prototype constructs a natural-language explanation from the winning track's matched features, directly supporting the transparency goal of explainable recommendation (Tintarev and Masthoff, 2007 `[VERIFY]`).

A concrete, verified example illustrates the behaviour. Given a request with history `["t02"]` and preferences specifying genre `rock`, mood `energetic`, and a target tempo of `130`, the prototype recommends **"Wildfire" by The Hours** with a total score of **0.7453**. The accompanying natural-language explanation states that the track was chosen because it matches the preferred genre (rock), matches the energetic mood, is close to the target tempo, and is a popular track. The score breakdown attributes the result across the individual features, and the previously played track `t02` is correctly absent from the results. This single example demonstrates the full chain — validation, history exclusion, weighted scoring, ranking, and explanation — operating as designed.

## 4.4 Testing evidence

The prototype is supported by an automated test suite of **42 tests**, organised by layer and run with `pytest`. These comprise **22 scoring tests**, **12 recommender tests**, and **8 API tests** (Figure 4.3).

- The **scoring tests** verify each sub-score function in isolation, including exact matches, mismatches, missing preferences, the linear decay of the tempo score, popularity normalisation, weight normalisation summing to one, and rejection of negative or all-zero weights.
- The **recommender tests** verify the assembled logic: selection of the highest-scoring candidate, exclusion of history tracks, safe handling of duplicate identifiers, deterministic tie-breaking, the presence of the expected score-breakdown keys, a non-empty explanation, and correctly ordered alternatives.
- The **API tests**, using FastAPI's test client, verify the endpoints end-to-end, covering the health check, successful recommendations with inline candidates and via the local dataset, the presence of all required response fields, history exclusion, and each error path (404 for no candidates, 400 for invalid weights, and 422 for a malformed body).

Together these tests cover the principal edge cases identified in the design — empty history, omitted or empty candidates, all candidates already in history, missing preferences, duplicate identifiers, and invalid input — providing evidence that the implemented behaviour matches the specification.

**[Figure 4.3: Test output showing 42 tests passed]**

## 4.5 Evaluation results

To assess whether the recommender performs better than chance, an evaluation script compares it against random selection over the local dataset across **five realistic scenarios** (for example, energetic rock and calm jazz). For each scenario, the recommender's chosen track is compared against the average of **1000 random selections** drawn from the same eligible pool, using a **fixed random seed** for reproducibility (Figure 4.4).

Across the scenarios, the recommender achieves an **average score of approximately 0.762**, compared with an **average random score of approximately 0.239**, an **average improvement of about +220%**. In every scenario, an automated check confirms that the recommender never recommends a track present in the listening history; this **history-exclusion check passed** throughout. These results provide quantitative evidence that the recommender reliably selects higher-scoring tracks than random choice and respects the no-repeat constraint.

This evaluation must be interpreted carefully. It measures performance against the **system's own weighted scoring objective**, not human listener satisfaction. It therefore demonstrates that the algorithm consistently and reproducibly maximises its stated criteria, but it does **not** establish that listeners would prefer these recommendations, since accuracy-style metrics alone are known to be insufficient indicators of recommendation quality (McNee, Riedl and Konstan, 2006 `[VERIFY]`).

**[Figure 4.4: Evaluation script output comparing recommender against random]**

## 4.6 Critical assessment and future improvements

The prototype successfully demonstrates the intended feature: a stateless, explainable, content-based recommendation API that is implemented, tested, and evaluated. Its strengths are a clean layered design, deterministic and reproducible behaviour, transparent explanations, and evidence that the implemented behaviour matches the specification through automated tests.

Its limitations are stated honestly. The **local 30-track dataset** is small, so behaviour at catalogue scale is untested. Scoring relies on **exact metadata matching** for genre, artist, and mood, which is explainable but cannot capture partial or semantic similarity. The **evaluation uses the system's own scoring objective**, and **no human listener study** has yet been conducted, so no claim is made about user satisfaction. Finally, **no external music-metadata source** is integrated at this stage.

These limitations define a clear path for future work: enlarging the dataset; enriching metadata from external sources offline; introducing fuzzy or semantic similarity in place of exact matching; conducting a user-centred evaluation; and, in the longer term, exploring hybrid recommendation that combines content-based and collaborative signals (Burke, 2002 `[VERIFY]`). Each extension builds on the existing architecture without disturbing its core design, confirming that the prototype provides a sound foundation for the full system.
