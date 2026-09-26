# NextTrack user study — facilitator crib sheet

One page to run from. Full protocol: `USER_STUDY_PLAN.md`.

## Before the first participant

```bash
cd nexttrack
.venv/bin/uvicorn app.main:app --port 8000
```

Open **http://localhost:8000** — **not** `127.0.0.1:8000`. YouTube refuses to
play embedded video on a page served from a bare IP, so `127.0.0.1` shows
"Video unavailable" on every track and would waste the session.

Confirm once: a track plays with sound, and Study mode hides the explanation.

## Per participant (~12 min)

**1. Brief & consent — say this:**

> "You'll listen to a series of recommended tracks and rate how well each one
> fits the session you're building. It takes about ten minutes. It's anonymous —
> I'm recording only your ratings, no name or personal details. You can stop at
> any point. Happy to go ahead?"

Wait for a clear yes.

**2. Set up:** tick **Study mode (blind A/B)**, enter the label — `P1`, `P2`, …
(one per participant, in order). The app won't recommend without it.

**3. Warm-up:** one recommendation to show the flow. **Then press Reset** — this
is what keeps the warm-up out of the data.

**4. Main task — two sessions, Reset between them:**

| | Session A | Session B |
|---|---|---|
| Start | any track | a track they like |
| Then | keep pressing **Recommend next** | same |
| Rated tracks | ~5 | ~5 |

Each track: **let it play 20–30 seconds before rating.** This matters — the
pilot was thrown out partly because ratings came 7–16 seconds apart, which the
timestamps make visible to anyone reading the data file.

Ask them to rate how well the track *fits the session*, not whether they like
the song in isolation.

**5. Questionnaire** — fill a row in `study_data/questionnaire.csv`:

| Column | Item (1–5) |
|---|---|
| `q1_fit` | The recommended tracks generally fit the listening session |
| `q2_followon` | The tracks felt like they followed on from what I'd just heard |
| `q3_explanation_clear` | The "why this track" explanation was clear |
| `q4_explanation_trust` | The explanation made me trust the recommendation more |
| `q5_ease` | The app was easy to use |
| `q6_open` | Free text: what worked, what you'd change |

For q3/q4, **turn Study mode off** and take one recommendation so the
explanation is visible, then discuss it.

**6. Debrief:** explain that two methods were being compared — one that adapts to
what they'd just played, one that doesn't — and that the app hid which was which
so their ratings wouldn't be biased.

## Watch out for

- **Don't change any setting mid-study.** The instrument must stay fixed across
  all participants or the data isn't comparable.
- **One label per person.** Don't reuse `P1` for two people; don't leave it blank.
- Don't react to their ratings ("good", "really?") — it biases the next one.
- If a track shows a playback error, press **Skip to next** and carry on; that
  recommendation just isn't rated.

## Progress check (run any time)

```bash
wc -l study_data/feedback.jsonl                      # total ratings so far
.venv/bin/python scripts/analyze_feedback.py         # live summary
```

Target: **5–8 participants, ~10 rated tracks each ≈ 50–80 ratings**, with both
conditions roughly equal (block randomisation handles the balance for you).
