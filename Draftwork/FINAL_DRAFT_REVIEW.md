# Final Draft Review — `finaldraft.pdf`

Review of the preliminary report **NextTrack — A Music Recommendation API** against the
assignment criteria. Based on extracted text from the 17-page PDF (≈ 5,790 words).
Source code was not modified; the report itself was not rewritten.

> Note on method: PDF text was extracted programmatically. Some observations about
> hyphenation and spacing may be extraction artifacts — these are flagged as
> "verify in the document" rather than asserted as definite errors.

---

## 1. Overall verdict

**ALMOST READY — needs targeted fixes before submission.**

The content, structure, and argument are strong and the report avoids overclaiming.
However, three things must be fixed first: (a) the wrong project-template identifier in
§1.4, (b) the missing figures/screenshots (all are still literal placeholders), and
(c) the apparent absence of a formatted reference list. None require rewriting; they are
correction-and-insertion tasks.

## 2. Strengths

- **Correct four-chapter structure** (Introduction, Literature Review, Design, Feature Prototype), each within its word cap.
- **Clear full-project vs prototype framing.** Chapter 1.5 and Chapter 3 describe the full intended project; Chapter 4 is correctly the prototype-focused chapter.
- **Critical, comparative literature review** (Chapter 2) that contrasts content-based, collaborative, and hybrid methods and links each to the design — not a list of summaries.
- **Design justified by users/domain** (direct developers vs indirect listeners) with explicit requirements, layered architecture, data strategy, technologies, a dated workplan, and a two-scope evaluation strategy.
- **Honest, non-overclaiming tone.** Production readiness, privacy, listener satisfaction, and external-API integration are all explicitly hedged (see §7).
- **Prototype is genuinely evaluated** (random baseline, fixed seed, history-exclusion check) with the correct caveat that it measures the scoring objective, not satisfaction.

## 3. High-priority fixes (before submission)

1. **§1.4 project template is WRONG.** The draft reads *"Project Idea 7.2: NextTrack A Music Recommendation API"*. It must read **"Project Idea 2: NextTrack — A Music Recommendation API"** (correct number, and an em dash before "A"). Chapter 3.1 already has it correct, so this is an internal inconsistency.
2. **All figures are still placeholders.** The literal texts `[Figure 3.1: ...]`, `[Figure 4.1: ...]`, `[Figure 4.2: ...]`, `[Figure 4.3: ...]`, `[Figure 4.4: ...]` remain in the PDF with **no actual image inserted**. Chapter 4 in particular needs real screenshots (Swagger UI, a `/recommend` JSON response, the `42 passed` test output, and the evaluation output) as evidence. Insert the images and remove the square brackets.
3. **No formatted reference list found.** The report cites ~20 sources in text but appears to have no Harvard reference list section. Add the list from `HARVARD_REFERENCE_LIST.md` (and verify each entry).
4. **`Ricci, Rokach and Shapira` is dated "2010".** The *Recommender Systems Handbook* editions are 2011 (1st), 2015 (2nd), and 2022 (3rd) — **2010 is almost certainly wrong**. Correct the year and make it consistent with whichever edition the chapter citations (Schedl et al. 2015; Lops et al. 2011; Adomavicius & Tuzhilin 2011) actually refer to.
5. **FastAPI (Ramírez) citation has no year.** In text it appears as "(Ramírez )" with an empty year. Software documentation needs a year (or "no date") plus a URL and access date — both for FastAPI and Pydantic.

## 4. Medium-priority improvements

- **Table captions are wrapped in literal brackets** — `[Table 3.1: ...]`, `[Table 3.2: ...]`, `[Table 3.3: ...]`. The tables themselves exist and have content, but remove the `[ ]` and format as proper captions (e.g. "Table 3.1: User and domain requirements").
- **Trailing space before closing parenthesis** in in-text citations, e.g. "(Adomavicius and Tuzhilin, 2005 )". Remove the space → "(… 2005)". This is a side-effect of deleting the old `[VERIFY]` markers.
- **Verify hyphenation in the document.** The extracted text shows hyphens missing in key terms — "content based" (×31), "request driven" (×9), "natural language explanation" (×10), "30 track". This may be a PDF-extraction artifact, but **check the actual document** that these read "content-based", "request-driven", "natural-language explanation", and "local 30-track dataset" consistently.
- **Em dash in the title/template.** Ensure "NextTrack — A Music Recommendation API" uses the em dash consistently (the §1.4 instance is missing it).

## 5. Formatting issues

- Missing reference list (see High-priority #3).
- Figure placeholders not rendered (High-priority #2).
- Bracketed table captions (Medium).
- Citation trailing spaces (Medium).
- Confirm front matter (title page, table of contents) and that figures/tables/references are excluded from the 6,000-word count per the brief.

## 6. Figure / table issues

| Item | Status | Action |
|---|---|---|
| Figure 3.1 (architecture) | Placeholder text only | Insert architecture diagram; remove brackets |
| Figure 4.1 (Swagger UI) | Placeholder text only | Insert screenshot |
| Figure 4.2 (`/recommend` JSON) | Placeholder text only | Insert screenshot |
| Figure 4.3 (42 tests passed) | Placeholder text only | Insert screenshot |
| Figure 4.4 (evaluation output) | Placeholder text only | Insert screenshot |
| Table 3.1 (requirements) | Present, bracketed caption | De-bracket caption |
| Table 3.2 (weights) | Present, bracketed caption | De-bracket caption |
| Table 3.3 (workplan) | Present, bracketed caption | De-bracket caption |

All figures/tables are referenced in the text (e.g. "shown in Figure 3.1", "summarised in Table 3.1"), which is good — only the artwork and caption formatting are missing.

## 7. Overclaiming risks

**Low — the report is appropriately cautious.** Verified in the text:
- *Production readiness:* "…rather than a production ready system." ✅ hedged.
- *Privacy:* "…it offers no formal privacy guarantee." ✅ hedged.
- *Listener satisfaction:* "…no claim about human listener satisfaction…" ✅ hedged.
- *External APIs:* external sources (MusicBrainz/Spotify/Wikidata) are described as planned/future and "not part of the preliminary prototype." ✅ hedged.

No changes required here — keep this wording.

## 8. Word count concerns

- **Total ≈ 5,790 words** (extracted, including headings, tables, and placeholder text) — under the 6,000 cap.
- Approx per chapter (from the source drafts): Ch1 ≈ 879, Ch2 ≈ 2,060, Ch3 ≈ 1,567, Ch4 ≈ 1,263 — **all within their individual maxima**.
- Margin is comfortable. Note the brief excludes title page, references, appendices, figures, and supporting material, so adding the reference list and figures will **not** push you over.

## 9. Final submission checklist

- [ ] Fix §1.4 to "Project Idea 2: NextTrack — A Music Recommendation API" (em dash included).
- [ ] Insert real images for Figures 3.1 and 4.1–4.4; delete the `[ ]` placeholder brackets.
- [ ] Add the Harvard reference list (from `HARVARD_REFERENCE_LIST.md`) and verify every entry.
- [ ] Correct the "Ricci, Rokach and Shapira 2010" year; align Handbook edition across citations.
- [ ] Add year + URL + access date to FastAPI (Ramírez) and Pydantic doc references.
- [ ] De-bracket table captions (Tables 3.1–3.3).
- [ ] Remove trailing spaces before ")" in in-text citations.
- [ ] Confirm hyphenation of key terms in the actual document.
- [ ] Confirm every in-text citation has a matching reference and vice-versa (see `CITATION_FIXES_NEEDED.md`).
- [ ] Add/confirm title page and table of contents.
- [ ] Re-export to PDF and re-check the word count and that figures render.
