"""
Analyse the user-study ratings collected via the web app's study mode.

Reads study_data/feedback.jsonl (anonymous 1-5 relevance ratings, each tagged
with the method used) and reports, for the session-aware recommender vs the
explicit-only baseline:

  - number of ratings and mean rating per method,
  - the difference in means (the A/B effect),
  - a distribution of ratings per method,
  - a Mann-Whitney U test (a non-parametric significance check suitable for
    ordinal 1-5 ratings) when SciPy is available; otherwise the effect size and
    counts are still reported.

Run from the project root:

    python scripts/analyze_feedback.py
    python scripts/analyze_feedback.py --file study_data/feedback.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FILE = PROJECT_ROOT / "study_data" / "feedback.jsonl"


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        print(f"No feedback file at {path}.")
        print("Run the app in study mode and collect some ratings first.")
        sys.exit(0)
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _stdev(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def _histogram(ratings: list[int]) -> str:
    counts = {n: ratings.count(n) for n in range(1, 6)}
    return "  ".join(f"{n}:{counts[n]}" for n in range(1, 6))


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyse NextTrack study ratings.")
    parser.add_argument("--file", default=str(DEFAULT_FILE),
                        help="Path to feedback.jsonl")
    args = parser.parse_args()

    records = load_records(Path(args.file))
    aware = [r["rating"] for r in records if r.get("mode") == "session_aware"]
    base = [r["rating"] for r in records if r.get("mode") == "baseline"]
    participants = {r.get("participant") for r in records if r.get("participant")}
    sessions = {r.get("session_id") for r in records if r.get("session_id")}

    print("NextTrack user-study results")
    print("============================")
    print(f"Total ratings   : {len(records)}")
    print(f"Sessions        : {len(sessions)}")
    print(f"Participants     : {len(participants)}"
          + (f" ({', '.join(sorted(p for p in participants))})" if participants else ""))
    print()

    header = f"{'Method':<16} {'n':>4} {'mean':>6} {'sd':>6}   ratings 1..5"
    print(header)
    print("-" * len(header))
    for label, xs in (("Session-aware", aware), ("Baseline", base)):
        print(f"{label:<16} {len(xs):>4} {_mean(xs):>6.2f} {_stdev(xs):>6.2f}   "
              f"{_histogram(xs)}")

    if aware and base:
        diff = _mean(aware) - _mean(base)
        print(f"\nEffect: session-aware rated {diff:+.2f} points vs baseline "
              f"(on a 1-5 scale).")
        _significance(aware, base)
    else:
        print("\nNeed ratings in BOTH conditions to compare. Collect more in "
              "study mode.")

    _per_participant(records)
    _design_checks(records)


def _per_participant(records: list[dict]) -> None:
    """Per-participant means, so the effect can be shown not to rest on one person."""
    labelled = [r for r in records if r.get("participant")]
    if not labelled:
        return
    print("\nPer participant")
    print("---------------")
    header = f"{'P':<8} {'n':>4}  {'aware':>6} {'base':>6}  {'diff':>6}"
    print(header)
    for label in sorted({r["participant"] for r in labelled}):
        rows = [r for r in labelled if r["participant"] == label]
        a = [r["rating"] for r in rows if r.get("mode") == "session_aware"]
        b = [r["rating"] for r in rows if r.get("mode") == "baseline"]
        diff = (_mean(a) - _mean(b)) if (a and b) else 0.0
        print(f"{label:<8} {len(rows):>4}  {_mean(a):>6.2f} {_mean(b):>6.2f}  "
              f"{diff:>+6.2f}")


def _design_checks(records: list[dict]) -> None:
    """Validity checks readable straight off the collected data.

    Two things a reader of the raw file can verify independently, so it is
    better to report them than to leave them to be discovered: whether the
    blind A/B assignment actually came out balanced, and whether the pacing is
    consistent with the protocol's 20-30s listening window. Ratings logged a
    few seconds apart cannot have followed a listen, and the timestamps make
    that visible to anyone.
    """
    from datetime import datetime

    print("\nDesign checks")
    print("-------------")
    sessions = {r.get("session_id") for r in records if r.get("session_id")}
    print(f"Distinct sessions        : {len(sessions)}")

    labelled = [r for r in records if r.get("participant")]
    unlabelled = len(records) - len(labelled)
    if unlabelled:
        print(f"Unattributable ratings   : {unlabelled}  "
              f"(no participant label - cannot be used)")

    for label in sorted({r["participant"] for r in labelled}):
        rows = [r for r in labelled if r["participant"] == label]
        n_a = sum(1 for r in rows if r.get("mode") == "session_aware")
        n_b = sum(1 for r in rows if r.get("mode") == "baseline")
        # A warm-up or a skipped recommendation consumes an assignment without
        # producing a rating, so the *rated* counts can differ by more than one
        # even when assignment was correct. Only a wide gap is worth a flag.
        flag = "" if abs(n_a - n_b) <= 2 else "   <-- check assignment"
        print(f"  {label}: assignment {n_a} aware / {n_b} baseline{flag}")

    stamps = sorted(datetime.fromisoformat(r["timestamp"])
                    for r in records if r.get("timestamp"))
    if len(stamps) > 1:
        gaps = [(stamps[i + 1] - stamps[i]).total_seconds()
                for i in range(len(stamps) - 1)]
        gaps = [g for g in gaps if g >= 0]
        ordered = sorted(gaps)
        median = ordered[len(ordered) // 2]
        too_fast = sum(1 for g in gaps if g < 20)
        print(f"Median gap between ratings: {median:.1f}s")
        print(f"Gaps under 20s            : {too_fast}/{len(gaps)}", end="")
        if too_fast > len(gaps) / 2:
            print("   <-- too fast to have listened; pacing does not match the protocol")
        else:
            print("   (consistent with a 20-30s listen)")


def _significance(aware: list[int], base: list[int]) -> None:
    """Report a Mann-Whitney U test if SciPy is present (optional dependency)."""
    try:
        from scipy.stats import mannwhitneyu
    except Exception:
        print("(Install scipy for a Mann-Whitney U significance test; the mean "
              "difference and counts above still describe the effect.)")
        return
    if len(aware) < 3 or len(base) < 3:
        print("(Too few ratings per group for a meaningful significance test.)")
        return
    stat, p = mannwhitneyu(aware, base, alternative="two-sided")
    verdict = "statistically significant" if p < 0.05 else "not yet significant"
    print(f"Mann-Whitney U = {stat:.1f}, p = {p:.4f} — {verdict} at α = 0.05.")


if __name__ == "__main__":
    main()
