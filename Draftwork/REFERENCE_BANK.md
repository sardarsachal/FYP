# NextTrack — Reference Bank

A working bank of academic and technical sources for the preliminary report.
Harvard style. **No page numbers, DOIs, venues, or access dates have been
invented.** Where a detail is uncertain it is marked `[VERIFY]` — confirm it
against the real source before submission.

> How to use: each entry lists the reference, the report section(s) it
> supports, why it is relevant, the specific claim it can back up, and its
> verification status. Citations in-text should be `(Author, Year)`.

---

## A. Recommender systems (foundations)

### A1. Adomavicius & Tuzhilin (2005)
- **Reference:** Adomavicius, G. and Tuzhilin, A. (2005) ‘Toward the next generation of recommender systems: a survey of the state-of-the-art and possible extensions’, *IEEE Transactions on Knowledge and Data Engineering* `[VERIFY volume/issue/pages/DOI]`.
- **Supports:** 2.1; 1.1.
- **Relevance:** Canonical survey establishing the content-based / collaborative / hybrid taxonomy.
- **Claim it supports:** Recommender systems are commonly categorised into content-based, collaborative, and hybrid approaches.
- **Status:** `[VERIFY volume/issue/pages/DOI]`.

### A2. Ricci, Rokach & Shapira (eds.) — Recommender Systems Handbook
- **Reference:** Ricci, F., Rokach, L. and Shapira, B. (eds.) (`[VERIFY year/edition]`) *Recommender Systems Handbook*. `[VERIFY publisher/city]`.
- **Supports:** 2.1; 2.8.
- **Relevance:** Standard reference handbook; useful for definitions and evaluation framing.
- **Claim it supports:** General definitions of recommendation tasks and evaluation methodology.
- **Status:** `[VERIFY year/edition/publisher]` (1st 2011 / 2nd 2015 / 3rd 2022 — confirm which you cite).

---

## B. Music recommender systems

### B1. Schedl, Knees, McFee, Bogdanov & Kaminskas (2015) — Music Recommender Systems
- **Reference:** Schedl, M., Knees, P., McFee, B., Bogdanov, D. and Kaminskas, M. (2015) ‘Music Recommender Systems’, in Ricci, F., Rokach, L. and Shapira, B. (eds.) *Recommender Systems Handbook*. `[VERIFY edition/pages/publisher]`.
- **Supports:** 2.2; 1.1; 3.1.
- **Relevance:** Authoritative chapter on the specifics of music RS (catalogue scale, sequential listening, context).
- **Claim it supports:** Music recommendation differs from general RS due to short items, sequential/consumption-style listening, and contextual factors.
- **Status:** `[VERIFY edition/pages]`.

### B2. Celma (2010) — Music Recommendation and Discovery
- **Reference:** Celma, Ò. (2010) *Music Recommendation and Discovery: The Long Tail, Long Fail, and Long Play in the Digital Music Space*. `[VERIFY publisher/city/ISBN]`.
- **Supports:** 2.2; 2.8.
- **Relevance:** Foundational monograph on music discovery, the long tail, and evaluation pitfalls.
- **Claim it supports:** Music discovery faces popularity bias and long-tail challenges; accuracy alone is an insufficient measure of a good recommender.
- **Status:** `[VERIFY publisher/ISBN]`.

### B3. Schedl, Zamani, Chen, Deldjoo & Elahi (2018) — Challenges and visions
- **Reference:** Schedl, M., Zamani, H., Chen, C.-W., Deldjoo, Y. and Elahi, M. (2018) ‘Current challenges and visions in music recommender systems research’ `[VERIFY journal (IJMIR?)/volume/pages/DOI]`.
- **Supports:** 2.2; 2.9; 4.7.
- **Relevance:** Sets out open problems: cold start, evaluation, context, beyond-accuracy goals.
- **Claim it supports:** Key open challenges in music RS include cold start, meaningful evaluation, and context-awareness.
- **Status:** `[VERIFY journal/volume/pages/DOI]`.

### B4. Kaminskas & Ricci (2012) — Contextual music IR and recommendation
- **Reference:** Kaminskas, M. and Ricci, F. (2012) ‘Contextual music information retrieval and recommendation: state of the art and challenges’ `[VERIFY journal/volume/pages/DOI]`.
- **Supports:** 2.7; 2.2.
- **Relevance:** Reviews context-aware music recommendation.
- **Claim it supports:** Context (e.g. activity, mood) is an important signal in music recommendation; motivates request-supplied preference parameters.
- **Status:** `[VERIFY journal/volume/pages/DOI]`.

---

## C. Content-based recommendation

### C1. Deldjoo, Schedl & Knees (2021/2024) — Content-driven music recommendation
- **Reference:** Deldjoo, Y., Schedl, M. and Knees, P. (`[VERIFY year]`) ‘Content-driven music recommendation: `[VERIFY exact subtitle]`’ `[VERIFY venue/volume/pages/DOI]`.
- **Supports:** 2.3; 3.6; 4.3.
- **Relevance:** Survey of content-driven approaches using audio/metadata features.
- **Claim it supports:** Content-based music recommendation uses item features (metadata and/or audio descriptors) to compute similarity, avoiding reliance on user interaction histories.
- **Status:** `[VERIFY year/exact title/venue]` — there are related works by these authors; confirm the precise one.

### C2. Pazzani & Billsus (2007) — Content-based recommendation systems
- **Reference:** Pazzani, M.J. and Billsus, D. (2007) ‘Content-based recommendation systems’, in *The Adaptive Web* `[VERIFY editors/pages/publisher]`.
- **Supports:** 2.3; 3.6.
- **Relevance:** Classic treatment of content-based filtering mechanics.
- **Claim it supports:** Content-based methods recommend items similar to those a user has shown interest in, based on item attributes.
- **Status:** `[VERIFY pages/publisher]`.

### C3. Lops, de Gemmis & Semeraro (2011) — Content-based RS: state of the art
- **Reference:** Lops, P., de Gemmis, M. and Semeraro, G. (2011) ‘Content-based recommender systems: state of the art and trends’, in *Recommender Systems Handbook* `[VERIFY edition/pages]`.
- **Supports:** 2.3.
- **Relevance:** Survey of content-based techniques and their trade-offs.
- **Claim it supports:** Content-based systems handle new items well but can suffer from over-specialisation/limited novelty.
- **Status:** `[VERIFY edition/pages]`.

---

## D. Collaborative filtering

### D1. Koren, Bell & Volinsky (2009) — Matrix factorization
- **Reference:** Koren, Y., Bell, R. and Volinsky, C. (2009) ‘Matrix factorization techniques for recommender systems’, *Computer* `[VERIFY volume/issue/pages/DOI]`.
- **Supports:** 2.4.
- **Relevance:** Representative, widely cited CF technique.
- **Claim it supports:** Collaborative filtering learns from user–item interaction patterns rather than item content.
- **Status:** `[VERIFY volume/issue/pages/DOI]`.

### D2. Schein, Popescul, Ungar & Pennock (2002) — Cold-start
- **Reference:** Schein, A.I., Popescul, A., Ungar, L.H. and Pennock, D.M. (2002) ‘Methods and metrics for cold-start recommendations’ `[VERIFY venue/pages/DOI]`.
- **Supports:** 2.4; 2.9.
- **Relevance:** Defines and addresses the cold-start problem.
- **Claim it supports:** CF struggles with cold start (new users/items lacking interaction data) — a limitation a content-based, request-driven design avoids.
- **Status:** `[VERIFY venue/pages/DOI]`.

---

## E. Hybrid recommender systems

### E1. Burke (2002) — Hybrid recommender systems
- **Reference:** Burke, R. (2002) ‘Hybrid recommender systems: survey and experiments’, *User Modeling and User-Adapted Interaction* `[VERIFY volume/issue/pages/DOI]`.
- **Supports:** 2.5; 4.7.
- **Relevance:** Defines hybridisation strategies combining CB and CF.
- **Claim it supports:** Hybrid systems combine paradigms to mitigate individual weaknesses; a natural future extension of NextTrack.
- **Status:** `[VERIFY volume/issue/pages/DOI]`.

---

## F. Explainable recommendation

### F1. Tintarev & Masthoff — Explanations in recommender systems
- **Reference:** Tintarev, N. and Masthoff, J. (`[VERIFY year: 2007 conf / 2011 handbook chapter / 2015 2nd-ed chapter]`) ‘`[VERIFY exact title]`’ `[VERIFY venue/pages]`.
- **Supports:** 2.6; 3.6; 4.4.
- **Relevance:** Foundational work on the aims and evaluation of explanations (transparency, trust, persuasiveness, satisfaction).
- **Claim it supports:** Explanations serve goals such as transparency and trust; NextTrack’s per-recommendation explanation targets transparency.
- **Status:** `[VERIFY which publication]` — multiple related works exist; pick and verify the exact one.

### F2. Zhang & Chen (2020) — Explainable recommendation: a survey
- **Reference:** Zhang, Y. and Chen, X. (2020) ‘Explainable recommendation: a survey and new perspectives’ `[VERIFY venue/volume/pages/DOI]`.
- **Supports:** 2.6.
- **Relevance:** Broad modern survey of explainable recommendation.
- **Claim it supports:** Explainability is an active research goal; approaches range from feature-based to model-based explanations.
- **Status:** `[VERIFY venue/volume/pages/DOI]`.

---

## G. Contextual / session-based recommendation & privacy

### G1. Adomavicius & Tuzhilin (2011) — Context-aware recommender systems
- **Reference:** Adomavicius, G. and Tuzhilin, A. (2011) ‘Context-aware recommender systems’, in *Recommender Systems Handbook* `[VERIFY edition/pages]`.
- **Supports:** 2.7; 3.1.
- **Relevance:** Frames context as a first-class input to recommendation.
- **Claim it supports:** Supplying contextual parameters at request time is an established context-aware strategy.
- **Status:** `[VERIFY edition/pages]`.

### G2. Quadrana, Cremonesi & Jannach (2018) — Sequence-aware recommendation
- **Reference:** Quadrana, M., Cremonesi, P. and Jannach, D. (2018) ‘Sequence-aware recommender systems’, *ACM Computing Surveys* `[VERIFY volume/issue/pages/DOI]`.
- **Supports:** 2.7; 3.6.
- **Relevance:** Surveys session/sequence-based recommendation that uses recent interactions rather than long-term profiles.
- **Claim it supports:** Session/sequence-based recommendation can operate without persistent user profiles — aligning with NextTrack’s stateless design.
- **Status:** `[VERIFY volume/issue/pages/DOI]`.

### G3. Privacy in recommender systems `[VERIFY source]`
- **Reference:** `[VERIFY — e.g. a recommender-systems privacy survey such as Friedman, Knijnenburg et al., or a GDPR-data-minimisation reference]`.
- **Supports:** 2.7; 1.1.
- **Relevance:** Grounds the privacy motivation (data minimisation, avoiding profiling).
- **Claim it supports:** Reducing stored personal data lowers privacy risk; a stateless design supports data minimisation.
- **Status:** `[VERIFY — choose a credible source; do not cite GDPR articles loosely]`.

---

## H. Evaluation of recommender systems

### H1. Herlocker, Konstan, Terveen & Riedl (2004) — Evaluating CF
- **Reference:** Herlocker, J.L., Konstan, J.A., Terveen, L.G. and Riedl, J.T. (2004) ‘Evaluating collaborative filtering recommender systems’, *ACM Transactions on Information Systems* `[VERIFY volume/issue/pages/DOI]`.
- **Supports:** 2.8; 3.7; 4.6.
- **Relevance:** Foundational on offline evaluation metrics and their limits.
- **Claim it supports:** Offline accuracy metrics are standard but do not fully capture user satisfaction — supports the honesty caveat about the evaluation script.
- **Status:** `[VERIFY volume/issue/pages/DOI]`.

### H2. McNee, Riedl & Konstan (2006) — Accuracy is not enough
- **Reference:** McNee, S.M., Riedl, J. and Konstan, J.A. (2006) ‘Being accurate is not enough: how accuracy metrics have hurt recommender systems’ `[VERIFY venue/pages/DOI]`.
- **Supports:** 2.8; 4.7.
- **Relevance:** Argues for beyond-accuracy evaluation (novelty, diversity, satisfaction).
- **Claim it supports:** Accuracy/score metrics alone are insufficient; user-centred evaluation is needed — directly supports the evaluation limitation.
- **Status:** `[VERIFY venue/pages/DOI]`.

---

## I. REST API design and technical documentation

### I1. Fielding (2000) — REST
- **Reference:** Fielding, R.T. (2000) *Architectural Styles and the Design of Network-based Software Architectures*. PhD thesis, University of California, Irvine. `[VERIFY exact wording/availability]`.
- **Supports:** 3.3; 3.4.
- **Relevance:** Origin of the REST architectural style.
- **Claim it supports:** REST principles (statelessness, uniform interface) underpin the API design; statelessness aligns with the project’s privacy stance.
- **Status:** `[VERIFY]`.

### I2. FastAPI documentation
- **Reference:** Ramírez, S. (`[VERIFY year]`) *FastAPI Documentation*. Available at: `[VERIFY URL]` (Accessed: `[VERIFY date]`).
- **Supports:** 3.3; 3.4; 4.1.
- **Relevance:** Primary documentation for the web framework used.
- **Claim it supports:** FastAPI provides automatic request validation and interactive API documentation.
- **Status:** `[VERIFY year/URL/access date]` — cite as software documentation.

### I3. Pydantic documentation
- **Reference:** *Pydantic Documentation* (`[VERIFY version/year]`). Available at: `[VERIFY URL]` (Accessed: `[VERIFY date]`).
- **Supports:** 3.4; 3.5; 4.1.
- **Relevance:** Documentation for the validation library used in the schemas.
- **Claim it supports:** Schema-based validation enforces data types and constraints at the API boundary.
- **Status:** `[VERIFY version/URL/access date]`.

---

## Verification checklist (do before submission)
- [ ] Confirm every `[VERIFY]` detail against the real source.
- [ ] Confirm the **exact** Deldjoo, Schedl & Knees content-based survey (title/year/venue).
- [ ] Confirm **which** Tintarev & Masthoff publication you cite.
- [ ] Confirm the **edition** of *Recommender Systems Handbook* used (1st/2nd/3rd) and matching page ranges for chapters B1, C3, G1.
- [ ] Choose and verify a credible **privacy** source (G3) — do not cite GDPR text loosely.
- [ ] Ensure consistent Harvard formatting and alphabetical reference list.
- [ ] Remove any source you do not actually cite in-text.
