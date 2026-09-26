# Preliminary Report: NextTrack — A Music Recommendation API

> Four-chapter preliminary report. Word limits: Introduction (max 1000), Literature Review (max 2500), Design (max 2000), Feature Prototype (max 1500); total under 6000 excluding title page, references, appendices, and supporting material.

---

## Chapter 1: Introduction

## 1.1 Project concept and motivation

NextTrack is a music recommendation API: a web service that, given a listener's recent activity and stated preferences, returns a suitable next track to play. Recommender systems have become central to how users navigate large digital catalogues, helping people find relevant items when manual browsing is impractical (Adomavicius and Tuzhilin, 2005 `[VERIFY]`). Music is a particularly demanding domain for such systems, because tracks are short, are consumed in sequences rather than as one-off choices, and are strongly shaped by context and mood (Schedl et al., 2015 `[VERIFY]`). These characteristics make the seemingly simple question — *what should play next?* — a meaningful recommendation problem rather than a trivial lookup.

The motivation for NextTrack is to explore this problem with a deliberately lightweight and transparent design. Many production recommenders depend on accumulating long-term user data to model individual taste, which introduces privacy considerations around profiling and data retention. NextTrack instead investigates whether useful, explainable recommendations can be produced from the information contained in a single request, without storing anything about the user between calls. This emphasis on transparency reflects a wider research interest in explainable recommendation, where systems justify their suggestions to support user understanding and trust (Tintarev and Masthoff, 2007 `[VERIFY]`).

## 1.2 Problem statement

The core problem addressed is the *next-track* recommendation task: selecting one track from a set of available candidates that best continues a listening session, given (i) a short listening history and (ii) user preference parameters such as genre, mood, or tempo. A central design constraint is that the system should be **stateless** — each recommendation must be computed purely from the data supplied in the request, with no persistent user profile. This framing aligns the project with session- and sequence-aware approaches, which generate recommendations from recent interactions rather than long-term personal models (Quadrana, Cremonesi and Jannach, 2018 `[VERIFY]`). The challenge is therefore to define a recommendation strategy that is demonstrably better than random selection, is explainable, and operates entirely within the boundaries of a single stateless request.

## 1.3 Aims and objectives

The overall aim is to design and implement a stateless, explainable, content-based music recommendation API and to demonstrate its feasibility through a working prototype. The specific objectives are:

1. To design a RESTful API that accepts listening history, preferences, and available track data, and returns a recommended next track.
2. To implement an explainable content-based scoring method that ranks candidate tracks by similarity to the user's stated preferences.
3. To exclude tracks already present in the listening history, so recommendations advance the session rather than repeat it.
4. To accompany each recommendation with a human-readable explanation of why the track was selected.
5. To validate the system through automated tests and to evaluate its behaviour against a random-selection baseline.

## 1.4 Project template

This project is undertaken using the supplied project template **Project Idea 2: NextTrack — A Music Recommendation API**, which defines the brief for a request-driven music recommendation service.

## 1.5 Scope and preliminary-stage contribution

The scope of this preliminary stage is a working *feature prototype* that establishes the feasibility of the proposed design rather than a production-ready system. The prototype is implemented as a Python service using the FastAPI framework (Ramírez `[VERIFY]`), which exposes a health-check endpoint and a recommendation endpoint. It draws candidate tracks from a small **local 30-track dataset** described by metadata fields such as genre, artist, tempo, mood, year, and popularity. Recommendations are produced by **weighted content-based scoring**: each candidate receives a score combining per-feature similarities under configurable weights, broadly consistent with content-based recommendation, which derives suggestions from item attributes (Pazzani and Billsus, 2007 `[VERIFY]`). The recommender excludes tracks contained in the listening history, ranks the remainder, applies deterministic tie-breaking, and returns the top candidate together with a score breakdown and a natural-language explanation. The prototype is supported by an automated test suite and an evaluation script that compares the recommender against random selection.

Two limitations are stated plainly. First, the dataset is small and local, so results illustrate the mechanism rather than performance at catalogue scale. Second, the evaluation compares the recommender against random selection using the system's *own* scoring objective; it therefore shows that the method reliably maximises its stated criteria and avoids repeating history, but it makes **no claim about human listener satisfaction**, which would require user-centred study (McNee, Riedl and Konstan, 2006 `[VERIFY]`). Within these bounds, the preliminary-stage contribution is a functioning, transparent, privacy-conscious recommendation API that demonstrates the feasibility of the design and provides a foundation for the fuller system.

## 1.6 Report structure

The remainder of this report is organised as follows. Chapter 2 reviews the relevant literature on recommender systems, music recommendation, content-based, collaborative, and hybrid methods, explainability, contextual and privacy considerations, and evaluation. Chapter 3 presents the design of NextTrack, covering the domain and users, system architecture, API and data model, recommendation algorithm, and the testing and evaluation plan. Chapter 4 describes the implemented feature prototype, presents its testing and evaluation results, and offers an honest assessment of how well it works and how it could be improved.

---

## Chapter 2: Literature Review

## 2.1 Recommender systems: foundations and taxonomy

Recommender systems emerged to address information overload, helping users locate relevant items within catalogues too large to browse manually. The foundational survey by Adomavicius and Tuzhilin (2005) `[VERIFY]` established the now-standard taxonomy that organises recommendation approaches into three families: content-based methods, which recommend items similar to those a user has previously favoured; collaborative filtering, which exploits patterns across many users; and hybrid methods, which combine the two. This taxonomy remains the conceptual backbone of the field and is reflected in standard reference works such as the *Recommender Systems Handbook* (Ricci, Rokach and Shapira `[VERIFY]`).

Each family encodes a different assumption about where recommendation knowledge resides. Content-based methods locate it in the *items* and their attributes; collaborative methods locate it in the *community* of users and their interactions; hybrid methods assume that combining both yields more robust results than either alone. These assumptions carry practical consequences for data requirements, cold-start behaviour, privacy, and explainability — themes that recur throughout this review. NextTrack is positioned deliberately within the content-based family, a choice justified in Section 2.3 and revisited in the synthesis. The remainder of this chapter critically examines each family and the cross-cutting concerns of explainability, statelessness and privacy, and evaluation, relating each to the design decisions described in Chapters 3 and 4.

## 2.2 Music recommender systems

Although music recommendation inherits the general taxonomy, it differs from domains such as film or e-commerce in ways that materially affect design (Schedl et al., 2015 `[VERIFY]`). Music items are short and consumed in rapid succession, so a listener may encounter dozens of recommendations within a single session, in contrast to the occasional, high-commitment choices typical of purchasing a product. Consumption is also sequential: the value of a track depends partly on what preceded it, making the *next-track* decision a meaningful sub-problem rather than an isolated ranking. Furthermore, musical preference is strongly shaped by context — activity, time, and especially mood — which means that the "right" recommendation can vary for the same user from one moment to the next (Kaminskas and Ricci, 2012 `[VERIFY]`).

These characteristics complicate evaluation and design. Celma (2010) `[VERIFY]` highlights the long-tail structure of music catalogues and the resulting popularity bias, whereby a small number of well-known tracks dominate recommendations at the expense of discovery. More recent work surveys the open challenges of the field, including cold start, context-awareness, and the difficulty of meaningful evaluation (Schedl et al., 2018 `[VERIFY]`). For NextTrack, the most relevant implication is that short, sequential, context-sensitive listening lends itself to a request-driven model in which recent history and explicit preferences — including mood and tempo — are supplied at the moment of the request. This framing directly motivates the prototype's input schema and its exclusion of already-played tracks, ensuring recommendations advance the session.

## 2.3 Content-based recommendation

Content-based recommendation derives suggestions from item attributes, recommending items similar to those a user has shown interest in (Pazzani and Billsus, 2007 `[VERIFY]`). In music, these attributes may include editorial metadata such as genre and artist, or descriptors such as tempo and mood, and content-driven approaches increasingly draw on richer audio and metadata features (Deldjoo, Schedl and Knees, 2021 `[VERIFY]`). The principal strengths of content-based methods are well documented (Lops, de Gemmis and Semeraro, 2011 `[VERIFY]`). Because they depend only on item features and a statement of user preference, they handle new items gracefully — a newly added track can be recommended immediately, provided its metadata is known — and they do not require data about other users. They are also comparatively transparent: a recommendation can be explained in terms of the specific attributes that matched.

These methods are not without weaknesses. A recognised limitation is over-specialisation, whereby recommendations remain narrowly similar to past preferences and offer limited novelty or serendipity (Lops, de Gemmis and Semeraro, 2011 `[VERIFY]`). Their quality is also bounded by the richness and accuracy of the available metadata. Despite these caveats, the content-based paradigm aligns closely with NextTrack's goals. Its independence from user-interaction data supports the project's stateless, privacy-conscious design; its transparency supports the natural-language explanation feature; and its tolerance of new items suits a prototype operating over a small, fixed dataset. The prototype's weighted content-based scoring across genre, artist, tempo, mood, and popularity is a direct, if deliberately simple, instantiation of this paradigm. It is acknowledged that the prototype uses exact attribute matching, which is explainable but coarser than the feature-similarity techniques discussed in the content-driven literature.

## 2.4 Collaborative filtering and its limitations

Collaborative filtering (CF) recommends items by learning from the behaviour of many users, typically through neighbourhood methods or latent-factor models such as matrix factorisation (Koren, Bell and Volinsky, 2009 `[VERIFY]`). Its central appeal is that it requires no item metadata and can surface non-obvious associations that content features would miss, which often yields strong accuracy on dense interaction data. For these reasons CF underpins many large-scale commercial systems.

However, CF carries limitations that are directly relevant to NextTrack's design rationale. The most prominent is the cold-start problem: new users and new items lack the interaction data CF depends upon, degrading recommendation quality until sufficient history accumulates (Schein et al., 2002 `[VERIFY]`). By construction, CF also requires the system to *collect and retain* user-interaction histories, which raises privacy and user-profiling concerns, since effective personalisation is predicated on building persistent models of individual behaviour. A related and often-overlooked issue is the shared-account problem: when several listeners use one account, their combined histories blur into a single, inaccurate profile, undermining the assumption that one account corresponds to one set of preferences. These weaknesses are not fatal — they are routinely mitigated in practice — but they illustrate a fundamental tension. CF's strengths are inseparable from its reliance on accumulated personal data. NextTrack's stateless, request-driven model deliberately reduces reliance on stored user profiles, trading the associations CF can capture for the immediacy and cold-start resilience of a content-based approach. The prototype therefore does not implement CF, while recognising it as a candidate for future hybridisation.

## 2.5 Hybrid recommender systems

Hybrid recommender systems combine multiple paradigms to offset the weaknesses of any single approach. Burke (2002) `[VERIFY]` provides an influential survey and taxonomy of hybridisation strategies, including weighted, switching, and feature-combination designs. The motivation is complementary: content-based methods mitigate CF's item cold-start, while CF can introduce the novelty and cross-user discovery that content-based methods tend to lack. In music specifically, hybrid approaches are frequently advocated as a means of balancing accuracy with discovery and of incorporating contextual signals (Schedl et al., 2018 `[VERIFY]`).

Hybrids are not a universal remedy. They increase system complexity, can be harder to explain, and often reintroduce CF's data requirements where a collaborative component is present. For a feasibility prototype prioritising statelessness, transparency, and simplicity, a full hybrid would be premature. NextTrack is consequently scoped as a content-based system, with hybridisation identified as a longer-term extension that the layered architecture could accommodate without disturbing its core. This is an honest acknowledgement that the current design favours clarity and reduced reliance on stored user profiles over the breadth a hybrid might offer.

## 2.6 Explainable recommendation

Explainability has become a significant research theme, motivated by the observation that users benefit not only from accurate recommendations but from understanding *why* an item was suggested. Tintarev and Masthoff (2007) `[VERIFY]` articulate several distinct aims an explanation may serve, including transparency, trust, effectiveness, and user satisfaction, and stress that these aims can require different explanation designs. Subsequent surveys document a broad spectrum of techniques, from feature-based justifications to model-derived explanations (Zhang and Chen, 2020 `[VERIFY]`).

A relevant insight from this literature is that the explanation paradigm should suit the underlying method. Content-based systems are naturally suited to feature-based explanations, because the very attributes that drive a recommendation can be surfaced as its justification. NextTrack exploits this alignment: each recommendation is accompanied by a natural-language explanation citing the matched features — for example, a matching genre or mood, or proximity to a target tempo. This targets the transparency aim identified by Tintarev and Masthoff (2007) `[VERIFY]`. It is important not to overstate this contribution. The prototype's explanations are template-based reflections of the scoring rationale rather than evaluated, user-tested justifications; demonstrating that they genuinely improve trust or satisfaction would require the user study discussed in Section 2.8.

## 2.7 Stateless, session-based, and privacy-conscious recommendation

A growing body of work studies recommendation that relies on recent interactions rather than long-term profiles. Sequence-aware and session-based recommender systems generate suggestions from the current sequence of actions, and can operate without persistent user models (Quadrana, Cremonesi and Jannach, 2018 `[VERIFY]`). This is conceptually close to NextTrack, which treats each request as a self-contained session described by a short history and explicit preferences. The related field of context-aware recommendation similarly argues that contextual parameters should be treated as first-class inputs to the recommendation function (Adomavicius and Tuzhilin, 2011 `[VERIFY]`), which supports NextTrack's decision to accept preference parameters such as mood and tempo directly in the request.

This design also intersects with privacy. By retaining no user data between requests, a stateless service reduces reliance on stored user profiles, although it offers no formal privacy guarantee. From an architectural standpoint, statelessness is additionally a defining constraint of the REST style (Fielding, 2000 `[VERIFY]`), which NextTrack adopts through its FastAPI implementation. The convergence is notable: an architectural principle (REST statelessness), a recommendation strategy (session-based, content-driven), and a privacy posture all point toward the same request-driven design. NextTrack does not claim to resolve privacy concerns in recommendation generally; rather, it explores a design point where reliance on stored user profiles is reduced, at the acknowledged cost of the richer personalisation that persistent profiles enable.

## 2.8 Evaluation of recommender systems

Evaluating recommender systems is itself a substantial research concern. Offline evaluation, which measures performance against historical data or a defined objective, is widely used because it is reproducible and inexpensive (Herlocker et al., 2004 `[VERIFY]`). A common and defensible baseline is comparison against random selection, which establishes whether a method performs better than chance. However, the literature is emphatic that accuracy-style metrics alone are insufficient. McNee, Riedl and Konstan (2006) `[VERIFY]` argue that an exclusive focus on accuracy has, at times, harmed recommender systems by neglecting qualities such as novelty, diversity, and genuine user satisfaction. Celma (2010) `[VERIFY]` similarly warns that high offline accuracy may mask popularity bias and poor discovery.

These cautions frame NextTrack's evaluation honestly. The prototype is assessed by comparing its recommendations against a random baseline across several scenarios, using a fixed seed for reproducibility, with the system's own weighted score as the metric. This demonstrates that the recommender reliably outperforms chance against its stated objective and respects the no-repeat constraint. It does *not* measure human listener satisfaction, and no such claim is made. Consistent with the literature, a user-centred evaluation is identified as necessary future work; the present evaluation establishes feasibility and internal validity, not perceived quality.

## 2.9 Synthesis and relevance to NextTrack

The literature reviewed reveals a consistent set of trade-offs. Collaborative filtering offers powerful cross-user discovery but depends on accumulating personal interaction data, with attendant cold-start, shared-account, and privacy difficulties. Content-based methods sacrifice some discovery but are transparent, resilient to item cold-start, and independent of user data. Hybrids combine strengths at the cost of complexity. Across all paradigms, explanation and rigorous, user-aware evaluation are recognised as important but frequently underdeveloped, and recent work increasingly values session-based and privacy-conscious designs.

NextTrack occupies a coherent point within this landscape. It is **content-based**, exploiting the transparency and cold-start resilience that suit explanation and a fixed dataset; **stateless and session-based**, aligning with REST principles and reducing reliance on stored user profiles by retaining no user data between requests; **explainable**, surfacing the matched attributes behind each recommendation; and **API-focused**, packaging these properties as a reusable service. The gap it addresses is the relative scarcity of lightweight, stateless, explainable, content-based recommendation services suitable as a clear feasibility prototype. The claim is intentionally modest: NextTrack does not solve the open problems of music recommendation, nor does it match the personalisation of data-intensive systems. Operating over a small, local dataset, it demonstrates that a privacy-conscious, explainable, content-based next-track API is feasible, and it provides a principled foundation that the subsequent chapters describe and that future work — richer features, external metadata, fuzzy similarity, hybridisation, and user evaluation — can extend.

---

## Chapter 3: Design

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

---

## Chapter 4: Feature Prototype

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
