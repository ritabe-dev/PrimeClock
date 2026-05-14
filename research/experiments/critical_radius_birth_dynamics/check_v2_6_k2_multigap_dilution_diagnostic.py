#!/usr/bin/env python3
"""Audit v2.6 k=2 multi-gap dilution diagnostic."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from check_v2_6_special_point_obstruction import repo_root_from_script


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
DATA_REL = EXPERIMENT_REL / "data"
NOTES_REL = EXPERIMENT_REL / "notes"

PHASE_REL = DATA_REL / "prc_v2_4_phase_gate_lift_diagnostics_v0_1.csv"
SUMMARY_REL = DATA_REL / "prc_v2_6_k2_multigap_dilution_summary_v0_1.csv"
NOTE_REL = NOTES_REL / "prc_v2_6_k2_multigap_dilution_diagnostic_v0_1.md"

SCOPE_ORDER = ("B4_to_B5_full", "B5_to_B6_full", "B6_to_B7_full")
REQUIRED_SECTIONS = (
    "## Goal",
    "## B4 Weakness",
    "## Component Dilution Table",
    "## Single-Gap Conditional Close Rate",
    "## Link To Special Point Obstruction",
    "## Diagnostic Decision",
    "## Non-claims",
)
REQUIRED_PHRASES = (
    "source-only v2.6 Gate R diagnostic",
    "k=2 multi-gap dilution",
    "parent_residue % 6",
    "ancestry proxy, not a proven lineage theorem",
    "B4->B5",
    "3 mod 6",
    "35 families",
    "14 single-gap",
    "21 multi-gap",
    "2 close rows",
    "single-gap conditional close rate",
    "diagnostic=continue",
    "k2_multigap_dilution=continue",
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
KEY_EXPECTATIONS = {
    ("B4_to_B5_full", "3"): {
        "families": "35",
        "single_gap_families": "14",
        "multi_gap_families": "21",
        "close_rows": "2",
        "close_rate_all": "2/35",
        "close_rate_given_single_gap": "2/14",
        "decision": "weak_due_to_multigap_dilution_candidate",
    },
    ("B5_to_B6_full", "3"): {
        "families": "383",
        "single_gap_families": "158",
        "multi_gap_families": "225",
        "close_rows": "32",
        "decision": "single_gap_conditioned_enrichment_candidate",
    },
    ("B6_to_B7_full", "3"): {
        "families": "4947",
        "single_gap_families": "2118",
        "multi_gap_families": "2829",
        "close_rows": "522",
        "decision": "single_gap_conditioned_enrichment_candidate",
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


def decision_for(scope: str, mod6: int) -> str:
    if scope == "B4_to_B5_full" and mod6 == 3:
        return "weak_due_to_multigap_dilution_candidate"
    if scope in {"B5_to_B6_full", "B6_to_B7_full"} and mod6 == 3:
        return "single_gap_conditioned_enrichment_candidate"
    if mod6 in {2, 4}:
        return "single_gap_sibling_control"
    return "nonproductive_mod6_control"


def fraction(numerator: int, denominator: int) -> str:
    return f"{numerator}/{denominator}"


def build_summary(phase_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    family_components: dict[tuple[str, int], int] = {}
    close_rows: dict[tuple[str, int], int] = defaultdict(int)

    for row in phase_rows:
        scope = row["scope"]
        parent_residue = int(row["parent_residue"])
        key = (scope, parent_residue)
        old_component_count = int(row["old_component_count"])
        previous = family_components.setdefault(key, old_component_count)
        if previous != old_component_count:
            raise ValueError(f"inconsistent component count for {key}")
        if truth(row["is_close"]):
            close_rows[(scope, parent_residue % 6)] += 1

    grouped: dict[tuple[str, int], dict[str, int]] = defaultdict(
        lambda: {
            "families": 0,
            "single_gap_families": 0,
            "multi_gap_families": 0,
            "close_rows": 0,
        }
    )
    for (scope, parent_residue), old_component_count in family_components.items():
        mod6 = parent_residue % 6
        bucket = grouped[(scope, mod6)]
        bucket["families"] += 1
        if old_component_count == 1:
            bucket["single_gap_families"] += 1
        else:
            bucket["multi_gap_families"] += 1

    for key, count in close_rows.items():
        grouped[key]["close_rows"] = count

    rows: list[dict[str, str]] = []
    for scope in SCOPE_ORDER:
        for mod6 in range(6):
            bucket = grouped[(scope, mod6)]
            families = bucket["families"]
            single_gap = bucket["single_gap_families"]
            close_count = bucket["close_rows"]
            rows.append(
                {
                    "scope": scope,
                    "parent_mod6_proxy": str(mod6),
                    "families": str(families),
                    "single_gap_families": str(single_gap),
                    "multi_gap_families": str(bucket["multi_gap_families"]),
                    "close_rows": str(close_count),
                    "close_rate_all": fraction(close_count, families),
                    "close_rate_given_single_gap": fraction(close_count, single_gap),
                    "decision": decision_for(scope, mod6),
                }
            )
    return rows


def require_note(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / NOTE_REL
    if not path.is_file():
        failures.append(f"missing k=2 multi-gap dilution note: {NOTE_REL}")
        return
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.replace("`", "").split())
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"k=2 dilution note missing section {section}")
    for phrase in REQUIRED_PHRASES:
        normalized_phrase = " ".join(phrase.replace("`", "").split())
        if normalized_phrase not in normalized:
            failures.append(f"k=2 dilution note missing phrase {phrase!r}")


def require_summary(repo_root: Path, failures: list[str]) -> None:
    regenerated = build_summary(read_csv(repo_root, PHASE_REL))
    committed = read_csv(repo_root, SUMMARY_REL)
    if committed != regenerated:
        failures.append("committed k=2 dilution summary differs from regenerated summary")
        return

    by_key = {(row["scope"], row["parent_mod6_proxy"]): row for row in committed}
    expected_keys = {(scope, str(mod6)) for scope in SCOPE_ORDER for mod6 in range(6)}
    if set(by_key) != expected_keys:
        failures.append(f"unexpected k=2 dilution summary keys: {sorted(by_key)}")
        return

    for key, expectations in KEY_EXPECTATIONS.items():
        row = by_key[key]
        for field, expected in expectations.items():
            if row.get(field) != expected:
                failures.append(
                    f"{key}: expected {field}={expected!r}, got {row.get(field)!r}"
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
        "check_v2_6_k2_multigap_dilution_diagnostic: "
        "checks=8, failed=0, "
        "k2_multigap_dilution=continue, mod6_theorem=defer"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
