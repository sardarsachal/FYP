"""
Tests for scripts/analyze_feedback.py.

The numbers this script prints are the ones quoted in the evaluation chapter,
so its statistics are checked against hand-computed values rather than against
whatever it happens to produce. A silent arithmetic error here would propagate
straight into the report.

The script is a standalone file rather than an importable package, so it is
loaded by path.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = PROJECT_ROOT / "scripts" / "analyze_feedback.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("analyze_feedback", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


analyze = _load_module()


# --- summary statistics ---------------------------------------------------

def test_mean_of_known_values():
    assert analyze._mean([1, 2, 3, 4, 5]) == 3.0
    assert analyze._mean([4, 4, 4]) == 4.0


def test_mean_of_empty_is_zero_not_a_crash():
    """Called before any ratings exist in a condition."""
    assert analyze._mean([]) == 0.0


def test_stdev_matches_the_sample_formula():
    """Sample sd (n-1 denominator) of [2,4,4,4,5,5,7,9] is exactly 2.138..."""
    values = [2, 4, 4, 4, 5, 5, 7, 9]
    assert analyze._stdev(values) == pytest.approx(2.13809, abs=1e-5)


def test_stdev_of_identical_values_is_zero():
    assert analyze._stdev([3, 3, 3, 3]) == 0.0


def test_stdev_needs_two_values():
    assert analyze._stdev([4]) == 0.0
    assert analyze._stdev([]) == 0.0


def test_histogram_counts_every_bucket():
    ratings = [1, 1, 3, 5, 5, 5]
    assert analyze._histogram(ratings) == "1:2  2:0  3:1  4:0  5:3"


def test_histogram_of_no_ratings_is_all_zero():
    assert analyze._histogram([]) == "1:0  2:0  3:0  4:0  5:0"


# --- record loading -------------------------------------------------------

def _write(path, records):
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n",
                    encoding="utf-8")


def test_load_records_reads_json_lines(tmp_path):
    path = tmp_path / "f.jsonl"
    _write(path, [{"rating": 5, "mode": "baseline"},
                  {"rating": 3, "mode": "session_aware"}])

    records = analyze.load_records(path)

    assert len(records) == 2
    assert records[0]["rating"] == 5


def test_load_records_skips_blank_and_corrupt_lines(tmp_path):
    """A half-written final line must not lose the whole study file."""
    path = tmp_path / "f.jsonl"
    path.write_text(
        '{"rating": 5, "mode": "baseline"}\n'
        "\n"
        '{"rating": 4, "mode": "sessi\n'          # truncated
        '{"rating": 2, "mode": "session_aware"}\n',
        encoding="utf-8",
    )

    records = analyze.load_records(path)

    assert [r["rating"] for r in records] == [5, 2]


def test_missing_file_exits_cleanly(tmp_path):
    """Running the analysis before collecting should explain itself, not crash."""
    with pytest.raises(SystemExit) as exit_info:
        analyze.load_records(tmp_path / "does-not-exist.jsonl")
    assert exit_info.value.code == 0


# --- end-to-end aggregation ----------------------------------------------

def test_reported_means_and_effect_are_correct(tmp_path, monkeypatch, capsys):
    """
    Session-aware [5,4,5,4] -> mean 4.50; baseline [2,3,1,2] -> mean 2.00;
    effect = +2.50. These are the shapes of number that reach the report.
    """
    path = tmp_path / "f.jsonl"
    records = (
        [{"session_id": "s1", "rating": r, "mode": "session_aware",
          "participant": "P1"} for r in (5, 4, 5, 4)]
        + [{"session_id": "s1", "rating": r, "mode": "baseline",
            "participant": "P1"} for r in (2, 3, 1, 2)]
    )
    _write(path, records)

    monkeypatch.setattr(sys, "argv", ["analyze_feedback.py", "--file", str(path)])
    analyze.main()
    out = capsys.readouterr().out

    assert "Total ratings   : 8" in out
    assert "4.50" in out            # session-aware mean
    assert "2.00" in out            # baseline mean
    assert "+2.50" in out           # the A/B effect


def test_one_sided_data_does_not_report_an_effect(tmp_path, monkeypatch, capsys):
    """With no baseline ratings there is nothing to compare; say so."""
    path = tmp_path / "f.jsonl"
    _write(path, [{"session_id": "s1", "rating": 5,
                   "mode": "session_aware", "participant": "P1"}])

    monkeypatch.setattr(sys, "argv", ["analyze_feedback.py", "--file", str(path)])
    analyze.main()
    out = capsys.readouterr().out

    assert "Need ratings in BOTH conditions" in out
    assert "Effect:" not in out
