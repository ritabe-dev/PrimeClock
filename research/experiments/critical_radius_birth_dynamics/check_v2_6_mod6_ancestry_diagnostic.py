#!/usr/bin/env python3
"""Audit v2.6 mod 6 ancestry diagnostic boundaries."""

from __future__ import annotations

import csv
from pathlib import Path

from check_v2_6_special_point_obstruction import repo_root_from_script


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
DATA_REL = EXPERIMENT_REL / "data"
NOTES_REL = EXPERIMENT_REL / "notes"

NOTE_REL = NOTES_REL / "prc_v2_6_mod6_ancestry_diagnostic_v0_1.md"
SUMMARY_REL = DATA_REL / "prc_v2_6_mod6_ancestry_summary_v0_1.csv"

REQUIRED_SECTIONS = (
    "## Goal",
    "## k=2 Special Point Suppression",
    "## Mod 6 Gap Geometry",
    "## Checked-Scope Evidence",
    "## Link To Special Point Obstruction",
    "## Diagnostic Decision",
    "## Non-claims",
)
REQUIRED_PHRASES = (
    "source-only v2.6 diagnostic",
    "p=2,3",
    "0 and 1/2",
    "3 mod 6",
    "interior single-gap ancestry",
    "B4->B5 is weak_or_non_supportive",
    "B5->B6 is mod 6 = 3 enriched",
    "B6->B7 is mod 6 = 3 enriched",
    "diagnostic=continue",
    "mod6_theorem=defer",
    "mod6_predictor=reject_for_v2_6_gate_r",
    "public_theorem=defer",
    "no theorem claim",
    "no predictor claim",
    "no public theorem claim",
    "no DOI claim",
    "no GitHub Release claim",
    "no B8 theorem claim",
    "no asymptotic law claim",
)
REQUIRED_ROWS = {
    "B4_to_B5_full": {
        "close_rows": "14",
        "close_mod6_3_count": "2",
        "close_mod6_3_rate": "2/14",
        "decision": "weak_or_non_supportive_mod6_3_signal",
    },
    "B5_to_B6_full": {
        "close_rows": "42",
        "close_mod6_3_count": "32",
        "close_mod6_3_rate": "32/42",
        "decision": "mod6_3_enriched_birth_ancestry_signal",
    },
    "B6_to_B7_full": {
        "close_rows": "714",
        "close_mod6_3_count": "522",
        "close_mod6_3_rate": "522/714",
        "decision": "mod6_3_enriched_birth_ancestry_signal",
    },
}


def require_note(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / NOTE_REL
    if not path.is_file():
        failures.append(f"missing mod 6 ancestry diagnostic note: {NOTE_REL}")
        return
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.replace("`", "").split())
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"mod 6 ancestry note missing section {section}")
    for phrase in REQUIRED_PHRASES:
        normalized_phrase = " ".join(phrase.replace("`", "").split())
        if normalized_phrase not in normalized:
            failures.append(f"mod 6 ancestry note missing phrase {phrase!r}")


def require_summary(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / SUMMARY_REL
    if not path.is_file():
        failures.append(f"missing mod 6 ancestry summary: {SUMMARY_REL}")
        return
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_scope = {row["scope"]: row for row in rows}
    if set(by_scope) != set(REQUIRED_ROWS):
        failures.append(f"unexpected mod 6 ancestry scopes: {sorted(by_scope)}")
        return
    for scope, expected in REQUIRED_ROWS.items():
        row = by_scope[scope]
        for key, value in expected.items():
            if row.get(key) != value:
                failures.append(
                    f"{scope}: expected {key}={value!r}, got {row.get(key)!r}"
                )


def main() -> int:
    repo_root = repo_root_from_script()
    failures: list[str] = []

    require_note(repo_root, failures)
    require_summary(repo_root, failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_6_mod6_ancestry_diagnostic: "
        "checks=7, failed=0, "
        "mod6_theorem=defer, diagnostic=continue"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
