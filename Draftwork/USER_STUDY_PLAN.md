# NextTrack — User Study Plan

A small, controlled study to evaluate whether NextTrack's recommendations are
useful to real listeners, and specifically whether the **session-aware**
recommender is preferred over the **explicit-preferences-only baseline**. The
design also sets up the iteration the brief rewards: a change informed by the
findings, which is then itself re-tested.

---

## 1. Objectives and hypotheses

**Objective.** Move the evaluation beyond the system's own scoring objective
(which only shows the recommender maximises its stated criteria) to a
**user-centred** measure of perceived recommendation quality, as the literature
argues is necessary (McNee, Riedl & Konstan, 2006).

**Primary hypothesis (H1).** Listeners rate tracks from the *session-aware*
recommender higher in relevance than tracks from the *baseline* recommender.

**Secondary questions.**
- (H2) Do listeners find the natural-language **explanations** helpful and
  trustworthy?
- (H3) Is the web app easy to use (basic usability)?

---

## 2. Design

- **Within-subjects, blind A/B.** Every participant experiences both conditions.
- **Independent variable:** recommendation method — `session_aware` vs
  `baseline` — assigned **randomly per recommendation** by the app's study mode.
- **Blinding:** in study mode the app **hides the explanation and score
  breakdown**, so participants cannot infer which method produced a track. The
  method is recorded silently with each rating.
- **Controlled comparison:** in study mode the app sends **no explicit
  preferences**, and the **diversity control is held constant** (0.3) across
  both conditions, so the *only* difference between conditions is the
  history-based adaptation being tested. (Diversity is fixed rather than zero so
  the experience is not monotonous, which would otherwise depress all ratings
  and mask the effect.)
- **Dependent variable:** a 1–5 relevance rating ("How well did this track fit
  your session?") given after each recommendation.

---

## 3. Participants

- **5–8 participants** (sufficient to detect a moderate effect in a coursework
  study and consistent with small-scale HCI evaluation practice).
- Recruited by convenience (peers/family); any adult who listens to music.
- **No personal data collected.** Each browser session gets a random,
  anonymous `session_id`; an optional facilitator label (e.g. "P3") is used
  only to group a participant's ratings. No names, emails, or accounts.

---

## 4. Materials

- The NextTrack web app running locally (`uvicorn app.main:app`), opened at
  <http://localhost:8000>, with **Study mode (blind A/B)** enabled.
- Full-length playback via the embedded YouTube player.
- Ratings are logged to `study_data/feedback.jsonl` and analysed with
  `scripts/analyze_feedback.py`.
- A short **post-session questionnaire** (Section 7).

---

## 5. Procedure (per participant, ~10–15 min)

1. **Brief & consent (verbal).** Explain: you'll listen to short stretches of
   recommended tracks and rate how well each fits the session; participation is
   voluntary and anonymous; you may stop at any time. Confirm agreement.
2. **Set-up.** Facilitator enables Study mode and enters the participant label
   (P1, P2, …).
3. **Warm-up (not rated).** One recommendation to show the flow and the player.
   Reset the session afterwards.
4. **Main task.** The participant builds a listening session: press
   **Recommend next**, listen for ~20–30 seconds, then give a **1–5 rating**.
   Repeat for **~10–12 tracks**, so both methods are sampled several times.
5. **Questionnaire.** The participant answers the short questionnaire (Section 7),
   including one item where the explanation is shown (study mode off) so they can
   comment on its usefulness.
6. **Debrief.** Explain the two methods that were being compared.

---

## 6. Tasks / scenarios

To vary context, ask each participant to run **two short sessions**, resetting
between them:
- **Session A — "background listening":** start from any track, just keep
  pressing Recommend next.
- **Session B — a chosen vibe:** the participant plays one track they like, then
  continues the session from there.

This exercises the history-based adaptation from different starting points.

---

## 7. Post-session questionnaire (1–5 Likert unless noted)

1. The recommended tracks generally fit the listening session. *(overall)*
2. The tracks felt like they followed on from what I had just heard.
3. *(explanation shown)* The "why this track" explanation was clear.
4. *(explanation shown)* The explanation made me trust the recommendation more.
5. The app was easy to use.
6. Open text: what worked well, and what would you change?

---

## 8. Analysis plan

Run `python scripts/analyze_feedback.py`. Report:
- **n and mean rating per method**, and the **difference in means** (the A/B
  effect on H1).
- **Rating distributions** (1–5 histogram) per method.
- A **Mann–Whitney U test** (non-parametric, appropriate for ordinal 1–5 data)
  on session-aware vs baseline ratings; report U and p (α = 0.05).
- Questionnaire items summarised as means; open-text responses themed.

---

## 9. Iteration and re-test (the key step)

The study is designed to **drive a change that is then re-tested**:

1. From the ratings and comments, identify the biggest weakness (candidate
   examples: over-repetition of one artist; too much popularity bias; genre
   "lock-in" so the session never explores).
2. Make **one targeted modification** (e.g. add a light **diversity/novelty**
   control, or cap artist repetition, or lower the popularity weight).
3. Re-run a **shorter A/B** (modified vs previous session-aware) with a few
   participants to check the change actually improved perceived quality — and
   report whether it did, even if the result is negative.

This closes the loop the brief describes as *"modifications based on user
testing, which are themselves tested."*

---

## 10. Threats to validity (state honestly in the report)

- **Small, convenience sample** → results are indicative, not generalisable.
- **Short dataset (122 tracks)** → limited room to explore; genre coherence may
  be easier than at catalogue scale.
- **Facilitator presence** may bias ratings upward (demand characteristics);
  blinding the method mitigates bias *between conditions*.
- **30-second listening windows** approximate, not full, listening behaviour.
- Ratings are **relative to the session**, not absolute musical quality.
