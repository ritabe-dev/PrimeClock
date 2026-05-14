#!/usr/bin/env python3
"""Audit v2.6 capacity false-positive decomposition."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from check_v2_6_special_point_obstruction import repo_root_from_script


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
DATA_REL = EXPERIMENT_REL / "data"
NOTES_REL = EXPERIMENT_REL / "notes"

PHASE_REL = DATA_REL / "prc_v2_4_phase_gate_lift_diagnostics_v0_1.csv"
SUMMARY_REL = DATA_REL / "prc_v2_6_capacity_false_positive_decomposition_summary_v0_1.csv"
NOTE_REL = NOTES_REL / "prc_v2_6_capacity_false_positive_decomposition_v0_1.md"

SCOPE_ORDER = ("B4_to_B5_full", "B5_to_B6_full", "B6_to_B7_full")
REQUIRED_SECTIONS = (
    "## Goal",
    "## Capacity Is Not A Separator",
    "## False-Positive Decomposition",
    "## Special Remainder Subset",
    "## Ordinary Grid Misalignment",
    "## Link To Single-Gap Containment",
    "## Gate R Decision",
    "## Non-claims",
)
REQUIRED_PHRASES = (
    "source-only v2.6 Gate R diagnostic",
    "capacity is not a separator",
    "capacity=false_positive_filter_only",
    "capacity false positives are single-gap rows",
    "special remainder subset",
    "ordinary non-special q-grid misses",
    "grid_strict_containment_nonclose_rows = 0",
    "q-grid containment sufficient in checked scopes",
    "capacity_false_positive_decomposition=continue",
    "single_gap_grid_containment=continue",
    "public_theorem=defer",
    "no theorem claim",
    "no predictor claim",
    "no public theorem claim",
    "no DOI claim",
    "no GitHub Release claim",
    "no B8 theorem claim",
    "no asymptotic law claim",
)
EXPECTED_ROWS = {
    "B4_to_B5_full": {
        "capacity_nonclose_rows": "294",
        "single_gap_capacity_nonclose_rows": "294",
        "multi_gap_capacity_nonclose_rows": "0",
        "special_remainder_capacity_nonclose_rows": "84",
        "ordinary_grid_miss_capacity_nonclose_rows": "210",
        "grid_strict_containment_nonclose_rows": "0",
        "decision": "capacity_false_positives_are_single_gap_grid_misses",
    },
    "B5_to_B6_full": {
        "capacity_nonclose_rows": "2870",
        "single_gap_capacity_nonclose_rows": "2870",
        "multi_gap_capacity_nonclose_rows": "0",
        "special_remainder_capacity_nonclose_rows": "672",
        "ordinary_grid_miss_capacity_nonclose_rows": "2198",
        "grid_strict_containment_nonclose_rows": "0",
        "decision": "capacity_false_positives_are_single_gap_grid_misses",
    },
    "B6_to_B7_full": {
        "capacity_nonclose_rows": "49402",
        "single_gap_capacity_nonclose_rows": "49402",
        "multi_gap_capacity_nonclose_rows": "0",
        "special_remainder_capacity_nonclose_rows": "8844",
        "ordinary_grid_miss_capacity_nonclose_rows": "40558",
        "grid_strict_containment_nonclose_rows": "0",
        "decision": "capacity_false_positives_are_single_gap_grid_misses",
    },
}


def read_csv(repo_root: Path, relative_path: Path) -> list[dict[str, str]]:
    path = repo_root / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"missing required artifact: {relative_path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def truth(value: str) -> bool:
    return value == "True"


def is_special_remainder(row: dict[str, str]) -> bool:
    q = int(row["new_prime"])
    remainder = int(row["new_prime_remainder"])
    return remainder in {0, (q - 1) // 2, (q + 1) // 2}


def build_summary(phase_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    counters: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "capacity_nonclose_rows": 0,
            "single_gap_capacity_nonclose_rows": 0,
            "multi_gap_capacity_nonclose_rows": 0,
            "special_remainder_capacity_nonclose_rows": 0,
            "ordinary_grid_miss_capacity_nonclose_rows": 0,
            "grid_strict_containment_nonclose_rows": 0,
        }
    )
    for row in phase_rows:
        if not truth(row["capacity_pass"]) or truth(row["is_close"]):
            continue
        counter = counters[row["scope"]]
        special = is_special_remainder(row)
        counter["capacity_nonclose_rows"] += 1
        counter["single_gap_capacity_nonclose_rows"] += int(row["old_component_count"] == "1")
        counter["multi_gap_capacity_nonclose_rows"] += int(row["old_component_count"] != "1")
        counter["special_remainder_capacity_nonclose_rows"] += int(special)
        counter["ordinary_grid_miss_capacity_nonclose_rows"] += int(not special)
        counter["grid_strict_containment_nonclose_rows"] += int(truth(row["phase_pass"]))

    rows: list[dict[str, str]] = []
    for scope in SCOPE_ORDER:
        counter = counters[scope]
        rows.append(
            {
                "scope": scope,
                "capacity_nonclose_rows": str(counter["capacity_nonclose_rows"]),
                "single_gap_capacity_nonclose_rows": str(
                    counter["single_gap_capacity_nonclose_rows"]
                ),
                "multi_gap_capacity_nonclose_rows": str(
                    counter["multi_gap_capacity_nonclose_rows"]
                ),
                "special_remainder_capacity_nonclose_rows": str(
                    counter["special_remainder_capacity_nonclose_rows"]
                ),
                "ordinary_grid_miss_capacity_nonclose_rows": str(
                    counter["ordinary_grid_miss_capacity_nonclose_rows"]
                ),
                "grid_strict_containment_nonclose_rows": str(
                    counter["grid_strict_containment_nonclose_rows"]
                ),
                "decision": "capacity_false_positives_are_single_gap_grid_misses",
            }
        )
    return rows


def require_note(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / NOTE_REL
    if not path.is_file():
        failures.append(f"missing capacity false-positive note: {NOTE_REL}")
        return
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.replace("`", "").split())
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"capacity false-positive note missing section {section}")
    for phrase in REQUIRED_PHRASES:
        normalized_phrase = " ".join(phrase.replace("`", "").split())
        if normalized_phrase not in normalized:
            failures.append(f"capacity false-positive note missing phrase {phrase!r}")


def require_summary(repo_root: Path, failures: list[str]) -> None:
    regenerated = build_summary(read_csv(repo_root, PHASE_REL))
    committed = read_csv(repo_root, SUMMARY_REL)
    if committed != regenerated:
        failures.append(
            "committed capacity false-positive summary differs from regenerated summary"
        )
        return
    by_scope = {row["scope"]: row for row in committed}
    if set(by_scope) != set(EXPECTED_ROWS):
        failures.append(f"unexpected capacity false-positive scopes: {sorted(by_scope)}")
        return
    for scope, expected in EXPECTED_ROWS.items():
        row = by_scope[scope]
        for field, value in expected.items():
            if row.get(field) != value:
                failures.append(
                    f"{scope}: expected {field}={value!r}, got {row.get(field)!r}"
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
        "check_v2_6_capacity_false_positive_decomposition: "
        "checks=8, failed=0, "
        "capacity=false_positive_filter_only, public_theorem=defer"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
