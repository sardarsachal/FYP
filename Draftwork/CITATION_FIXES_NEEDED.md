# Citation Fixes Needed — NextTrack Preliminary Report

Audit of every in-text citation found in `finaldraft.pdf`, whether it has a matching
reference in `HARVARD_REFERENCE_LIST.md`, whether the year looks correct, and the
formatting fixes required.

Legend: ✅ = matched / looks correct · ⚠️ = needs attention · ❌ = error.

---

## 1. In-text citation audit

| # | In-text citation (as printed) | Times | Matching reference? | Year correct? | Notes / fix |
|---|---|---|---|---|---|
| 1 | (Adomavicius and Tuzhilin, 2005) | 1 | ✅ | ✅ | trailing space before ")" |
| 2 | (Adomavicius and Tuzhilin, 2011) | 1 | ✅ | ✅ | context-aware; distinct from #1 — good |
| 3 | (Ricci, Rokach and Shapira **2010**) | 1 | ⚠️ | ❌ | **Year likely wrong** → 2011/2015; also missing comma before year |
| 4 | (Schedl et al., 2015) | 3 | ✅ | ⚠️ | confirm 2015 vs 2016 edition of the Handbook chapter |
| 5 | (Schedl et al., 2018) | 2 | ✅ | ✅ | trailing space |
| 6 | (Kaminskas and Ricci, 2012) | 1 | ✅ | ✅ | extracted as "(… Ricci, 2012)"; confirm full author form |
| 7 | Celma (2010) | 2 | ✅ | ✅ | narrative form; fine |
| 8 | (Pazzani and Billsus, 2007) | 4 | ✅ | ✅ | trailing space |
| 9 | (Deldjoo, Schedl and Knees, 2021) | 1 | ⚠️ | ⚠️ | verify year + venue (see reference list) |
| 10 | (Lops, de Gemmis and Semeraro, 2011) | 2 | ✅ | ✅ | trailing space |
| 11 | (Koren, Bell and Volinsky, 2009) | 1 | ✅ | ✅ | trailing space |
| 12 | (Schein et al., 2002) | 1 | ✅ | ✅ | trailing space |
| 13 | (Burke, 2002) | 2 | ✅ | ✅ | also appears as narrative "Burke (2002)" |
| 14 | (Tintarev and Masthoff, 2007) | 3 | ✅ | ⚠️ | confirm which 2007 publication |
| 15 | (Zhang and Chen, 2020) | 1 | ✅ | ✅ | trailing space |
| 16 | (Quadrana, Cremonesi and Jannach, 2018) | 3 | ✅ | ✅ | trailing space |
| 17 | (Fielding, 2000) | 2 | ✅ | ✅ | trailing space |
| 18 | (Herlocker et al., 2004) | 1 | ✅ | ✅ | trailing space |
| 19 | (McNee, Riedl and Konstan, 2006) | 3 | ✅ | ✅ | also narrative "Riedl and Konstan (2006)" — make consistent |
| 20 | (Ramírez **[no year]**) | 2 | ⚠️ | ❌ | **No year** — add year + access date for FastAPI docs |
| 21 | Pydantic (in text, no formal citation) | 2 | ⚠️ | ⚠️ | Mentioned by name; add a proper doc citation + reference |

## 2. Citations with no matching reference (until the list is added)

The report appears to **lack a reference list entirely**, so currently **every** in-text
citation is unmatched in the document. Adding `HARVARD_REFERENCE_LIST.md` resolves this.
After insertion, confirm each of the 21 sources above resolves to exactly one entry.

## 3. References that should be added, removed, or replaced

- **Add:** a formatted Harvard reference list (none present).
- **Add a proper citation/reference for Pydantic** (currently named in prose without a citation) — or, if you prefer not to cite it formally, that is acceptable, but then do not list it.
- **Replace the year** for *Ricci, Rokach and Shapira* (2010 → correct edition year).
- **Add year/access date** for *Ramírez (FastAPI)* and *Pydantic* documentation.
- **Remove nothing else** — no over-listed (uncited) references can exist yet because there is no list; once added, ensure no extra entries beyond the 21 cited sources.

## 4. Formatting fixes (apply across all in-text citations)

1. **Remove the trailing space before the closing parenthesis** — e.g. "(Fielding, 2000 )" → "(Fielding, 2000)". This affects most citations and stems from deleting the old `[VERIFY]` markers.
2. **Add the missing comma** in "(Ricci, Rokach and Shapira 2010)" → "(Ricci, Rokach and Shapira, 2011)".
3. **Make narrative vs parenthetical forms consistent** — e.g. use "(McNee, Riedl and Konstan, 2006)" rather than the truncated "Riedl and Konstan (2006)"; ensure "Burke (2002)" / "(Burke, 2002)" usage is intentional.
4. **Ensure each first author surname matches the reference list exactly** (alphabetical ordering depends on it).
5. **Check Kaminskas and Ricci (2012)** renders with both authors in text (extraction showed only "Ricci, 2012").

## 5. Summary counts

- **Distinct sources cited:** 21
- **Citations needing year/format attention:** 4 high (Ricci 2010; Ramírez no year; Pydantic; Deldjoo 2021) + global trailing-space cleanup.
- **Sources flagged `[NEEDS MANUAL VERIFICATION]` in the reference list:** 6
  (Adomavicius & Tuzhilin 2011; Deldjoo, Schedl & Knees 2021; Lops et al. 2011;
  Ricci, Rokach & Shapira; Schedl et al. 2015; Tintarev & Masthoff 2007) plus the two
  documentation entries (FastAPI, Pydantic) needing access dates.
