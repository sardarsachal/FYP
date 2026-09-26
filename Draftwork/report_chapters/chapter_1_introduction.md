# Chapter 1: Introduction

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
