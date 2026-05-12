#!/usr/bin/env python3
"""Verify source-only PRC v2.4 theorem-candidate selection note."""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

from v2_4_gate_r_decision import (
    DEFAULT_ARITHMETIC_STRATUM_BIAS_CSV,
    DEFAULT_GATE_R_DECISION_TABLE_CSV,
    read_arithmetic_stratum_bias_csv,
    read_gate_r_decision_table_csv,
)
from v2_4_phase_gate_diagnostics import (
    DEFAULT_PHASE_GATE_FAMILY_SUMMARY_CSV,
    DEFAULT_PHASE_GATE_LIFT_DIAGNOSTICS_CSV,
    read_phase_gate_family_summary_csv,
    read_phase_gate_lift_diagnostics_csv,
)

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_THEOREM_NOTE = (
    EXPERIMENT_DIR / "notes" / "prc_v2_4_theorem_candidate_selection_v0_1.md"
)
DEFAULT_Q_GRID_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_q_grid_birth_phase_histogram_v0_1.csv"
)
DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_4_theorem_candidate_selection_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.4 theorem-candidate selection.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    args = parser.parse_args()

    arithmetic_rows = read_arithmetic_stratum_bias_csv(DEFAULT_ARITHMETIC_STRATUM_BIAS_CSV)
    decision_rows = read_gate_r_decision_table_csv(DEFAULT_GATE_R_DECISION_TABLE_CSV)
    phase_lift_rows = read_phase_gate_lift_diagnostics_csv(DEFAULT_PHASE_GATE_LIFT_DIAGNOSTICS_CSV)
    phase_family_rows = read_phase_gate_family_summary_csv(DEFAULT_PHASE_GATE_FAMILY_SUMMARY_CSV)
    q_rows = read_csv(DEFAULT_Q_GRID_CSV)
    note_text = DEFAULT_THEOREM_NOTE.read_text(encoding="utf-8")
    checks = verification_rows(
        arithmetic_rows,
        decision_rows,
        phase_lift_rows,
        phase_family_rows,
        q_rows,
        note_text,
    )
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_4_theorem_candidate_selection: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(
    arithmetic_rows,
    decision_rows,
    phase_lift_rows,
    phase_family_rows,
    q_rows,
    note_text: str,
):
    return [
        check_phase_gate_cross_layer_counts(phase_family_rows),
        check_phase_gate_exact_separation(phase_lift_rows, phase_family_rows),
        check_selected_theorem_candidate(decision_rows),
        check_b7_reflection_pair_refinement(arithmetic_rows),
        check_b7_gcd_reflection_cross_refinement(arithmetic_rows),
        check_q_grid_pair_refinement(q_rows),
        check_note_content(note_text),
    ]


def check_phase_gate_cross_layer_counts(rows):
    by_scope = {}
    for scope in ("B4_to_B5_full", "B5_to_B6_full", "B6_to_B7_full"):
        scoped = [row for row in rows if row.scope == scope]
        by_scope[scope] = {
            "capacity": sum(row.capacity_pass for row in scoped),
            "capacity_nonclose": sum(row.capacity_pass and row.close_lift_count == 0 for row in scoped),
            "close": sum(row.close_lift_count > 0 for row in scoped),
            "phase": sum(row.phase_pass_count > 0 for row in scoped),
            "birth": sum(row.birth_lift_count > 0 for row in scoped),
        }
    passed = by_scope == {
        "B4_to_B5_full": {
            "capacity": 28,
            "capacity_nonclose": 14,
            "close": 14,
            "phase": 14,
            "birth": 14,
        },
        "B5_to_B6_full": {
            "capacity": 224,
            "capacity_nonclose": 182,
            "close": 42,
            "phase": 42,
            "birth": 42,
        },
        "B6_to_B7_full": {
            "capacity": 2948,
            "capacity_nonclose": 2234,
            "close": 714,
            "phase": 714,
            "birth": 714,
        },
    }
    return check_bool("phase_gate_cross_layer_counts", passed, total=15, failed=0 if passed else 1)


def check_phase_gate_exact_separation(lift_rows, family_rows):
    close_rows = [row for row in lift_rows if row.is_close]
    nonclose_rows = [row for row in lift_rows if not row.is_close]
    capacity_nonclose_families = [
        row for row in family_rows if row.capacity_pass and row.close_lift_count == 0
    ]
    close_families = [row for row in family_rows if row.close_lift_count > 0]
    passed = (
        len(close_rows) == 770
        and all(row.capacity_pass and row.phase_pass for row in close_rows)
        and all(row.phase_rank_desc == 1 for row in close_rows)
        and all(not row.phase_pass for row in nonclose_rows)
        and len(capacity_nonclose_families) == 2430
        and all(row.phase_pass_count == 0 for row in capacity_nonclose_families)
        and len(close_families) == 770
        and all(
            row.phase_pass_count == row.close_lift_count == row.birth_lift_count == 1
            and row.phase_pass_remainders == row.close_remainders
            for row in close_families
        )
    )
    return check_bool("phase_gate_exact_separation", passed, total=8, failed=0 if passed else 1)


def check_selected_theorem_candidate(rows):
    selected = [
        row
        for row in rows
        if row.candidate == "signed phase-margin separation theorem"
    ]
    passed = (
        len(selected) == 1
        and selected[0].role == "headline theorem candidate"
        and selected[0].decision == "keep"
        and "close=770/770" in selected[0].evidence
        and "capacity_nonclose=2430" in selected[0].evidence
        and "phase_pass_nonclose=0" in selected[0].evidence
        and "close_rank_1=770/770" in selected[0].evidence
    )
    return check_bool("selected_theorem_candidate", passed, total=6, failed=0 if passed else 1)


def check_b7_reflection_pair_refinement(rows):
    subset = [
        row
        for row in rows
        if row.diagnostic == "close_reflection_pair_by_scope"
        and row.scope == "B6_to_B7_full"
        and row.population == "close"
    ]
    top = max(subset, key=lambda row: row.family_count)
    pair_imbalances_zero = all("pair_imbalance=0" in row.note for row in subset)
    unique_top = sum(row.family_count == top.family_count for row in subset) == 1
    passed = (
        len(subset) == 7
        and top.stratum == "4/13"
        and top.family_count == 398
        and top.observed_share == "199/357"
        and pair_imbalances_zero
        and unique_top
    )
    return check_bool("b7_reflection_pair_refinement", passed, total=7, failed=0 if passed else 1)


def check_b7_gcd_reflection_cross_refinement(rows):
    subset = [
        row
        for row in rows
        if row.diagnostic == "close_child_gcd_reflection_pair_crosstab"
        and row.scope == "B6_to_B7_full"
    ]
    top = max(subset, key=lambda row: row.family_count)
    unique_top = sum(row.family_count == top.family_count for row in subset) == 1
    passed = (
        top.stratum == "gcd=3;pair=4/13"
        and top.family_count == 316
        and top.observed_share == "158/357"
        and unique_top
    )
    return check_bool("b7_gcd_reflection_cross_refinement", passed, total=4, failed=0 if passed else 1)


def check_q_grid_pair_refinement(rows):
    b7_pair_rows = [
        row
        for row in rows
        if row["birth_k"] == "7"
        and row["new_prime"] == "17"
        and row["new_prime_remainder"] in {"4", "13"}
    ]
    passed = (
        len(b7_pair_rows) == 2
        and {row["birth_count"] for row in b7_pair_rows} == {"199"}
        and {row["reflection_pair_count"] for row in b7_pair_rows} == {"398"}
        and {row["reflected_birth_count"] for row in b7_pair_rows} == {"199"}
    )
    return check_bool("q_grid_reflected_pair_refinement", passed, total=2, failed=0 if passed else 1)


def check_note_content(note_text: str):
    required = [
        "signed phase-margin separation theorem",
        "B4 -> B5: capacity families = 28, close families = 14, phase-pass families = 14",
        "B5 -> B6: capacity families = 224, close families = 42, phase-pass families = 42",
        "B6 -> B7: capacity families = 2948, close families = 714, phase-pass families = 714",
        "all scopes: capacity non-close families = 2430",
        "phase_pass = (_phase_margin(row) > 0)",
        "Kept as refinement: reflected-pair arithmetic concentration.",
        "finite checked B5/B6/B7 source-only evidence",
    ]
    failed = sum(text not in note_text for text in required)
    return check_bool("theorem_note_content", failed == 0, total=len(required), failed=failed)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def check_bool(name: str, passed: bool, *, total: int, failed: int) -> dict[str, str]:
    return {
        "check": name,
        "total": str(total),
        "passed": str(max(total - failed, 0)),
        "failed": str(failed),
        "status": "pass" if passed else "fail",
    }


def write_checks(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["check", "total", "passed", "failed", "status"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
