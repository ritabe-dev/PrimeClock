#!/usr/bin/env python3
"""Verify source-only PRC v2.4 Gate R decision artifacts."""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

from v2_4_gate_r_decision import (
    DEFAULT_ARITHMETIC_STRATUM_BIAS_CSV,
    DEFAULT_GATE_R_DECISION_TABLE_CSV,
    build_arithmetic_stratum_bias_rows,
    build_gate_r_decision_rows,
    read_arithmetic_stratum_bias_csv,
    read_gate_r_decision_table_csv,
    row_signature,
    write_gate_r_decision_artifacts,
)

DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_4_gate_r_decision_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.4 Gate R decision artifacts.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument(
        "--update-data",
        action="store_true",
        help="regenerate committed source-only Gate R decision CSVs",
    )
    args = parser.parse_args()

    if args.update_data:
        write_gate_r_decision_artifacts()

    decision_rows = read_gate_r_decision_table_csv(DEFAULT_GATE_R_DECISION_TABLE_CSV)
    arithmetic_rows = read_arithmetic_stratum_bias_csv(DEFAULT_ARITHMETIC_STRATUM_BIAS_CSV)
    checks = verification_rows(decision_rows, arithmetic_rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_4_gate_r_decision: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(decision_rows, arithmetic_rows) -> list[dict[str, str]]:
    candidates = {row.candidate: row for row in decision_rows}
    headline_keep = [
        row
        for row in decision_rows
        if row.role == "headline theorem candidate" and row.decision == "keep"
    ]
    return [
        compare_recomputed_rows(
            "gate_r_decision_rows_match_recomputed",
            decision_rows,
            build_gate_r_decision_rows(arithmetic_rows),
        ),
        compare_recomputed_rows(
            "arithmetic_stratum_rows_match_recomputed",
            arithmetic_rows,
            build_arithmetic_stratum_bias_rows(),
        ),
        check_bool(
            "gate_r_decision_has_five_candidates",
            len(decision_rows) == 5
            and set(candidates)
            == {
                "capacity + phase gate",
                "signed phase-margin separation theorem",
                "sibling itinerary divergence",
                "width-normalized k2 r=3 lineage survival bias",
                "reflection-paired final remainder bias",
            },
            total=5,
            failed=0 if len(decision_rows) == 5 else abs(len(decision_rows) - 5),
        ),
        check_bool(
            "capacity_phase_is_not_headline_keep",
            candidates["capacity + phase gate"].decision == "weak"
            and candidates["capacity + phase gate"].role == "foundation",
            total=1,
            failed=0
            if candidates["capacity + phase gate"].decision == "weak"
            and candidates["capacity + phase gate"].role == "foundation"
            else 1,
        ),
        check_bool(
            "signed_phase_margin_separation_is_headline_keep",
            candidates["signed phase-margin separation theorem"].decision == "keep"
            and candidates["signed phase-margin separation theorem"].role
            == "headline theorem candidate"
            and candidates["signed phase-margin separation theorem"].checker_backed_score == 5,
            total=1,
            failed=0
            if candidates["signed phase-margin separation theorem"].decision == "keep"
            and candidates["signed phase-margin separation theorem"].role
            == "headline theorem candidate"
            and candidates["signed phase-margin separation theorem"].checker_backed_score == 5
            else 1,
        ),
        check_bool(
            "arithmetic_biases_are_refinements",
            candidates["width-normalized k2 r=3 lineage survival bias"].decision == "support"
            and candidates["width-normalized k2 r=3 lineage survival bias"].role
            == "arithmetic refinement"
            and candidates["reflection-paired final remainder bias"].decision == "support"
            and candidates["reflection-paired final remainder bias"].role == "arithmetic refinement",
            total=2,
            failed=0
            if candidates["width-normalized k2 r=3 lineage survival bias"].decision
            == "support"
            and candidates["width-normalized k2 r=3 lineage survival bias"].role
            == "arithmetic refinement"
            and candidates["reflection-paired final remainder bias"].decision == "support"
            and candidates["reflection-paired final remainder bias"].role
            == "arithmetic refinement"
            else 1,
        ),
        check_arithmetic_capacity_conditioning(arithmetic_rows),
        check_reflection_pair_bias(arithmetic_rows),
        check_bool(
            "headline_candidates_keep_or_gate_r_remains_continue",
            len(headline_keep) >= 1,
            total=2,
            failed=0 if len(headline_keep) >= 1 else 1,
        ),
    ]


def check_arithmetic_capacity_conditioning(rows) -> dict[str, str]:
    top_capacity = _top_parent_gcd(rows, "capacity")
    top_capacity_nonclose = _top_parent_gcd(rows, "capacity_nonclose")
    top_close = _top_parent_gcd(rows, "close")
    k2_width_r3 = _row_for(
        rows,
        "k2_width_normalized_lineage_survival",
        "all",
        "birth_lineage",
        "r=3",
    )
    k2_capacity_r2 = _row_for(
        rows,
        "k2_capacity_conditioned_survival",
        "all",
        "capacity",
        "r=2",
    )
    k2_capacity_r3 = _row_for(
        rows,
        "k2_capacity_conditioned_survival",
        "all",
        "capacity",
        "r=3",
    )
    k2_capacity_r4 = _row_for(
        rows,
        "k2_capacity_conditioned_survival",
        "all",
        "capacity",
        "r=4",
    )
    gcd_one_close = [
        row
        for row in rows
        if row.diagnostic == "parent_gcd_capacity_conditioned"
        and row.population == "close"
        and row.stratum == "gcd=1"
    ]
    passed = (
        top_capacity == "gcd=2"
        and top_capacity_nonclose == "gcd=2"
        and top_close == "gcd=3"
        and k2_width_r3.family_count == 556
        and k2_width_r3.close_rate == "14456/5775"
        and k2_capacity_r2.close_rate == "103/1112"
        and k2_capacity_r3.close_rate == "278/475"
        and k2_capacity_r4.close_rate == "103/1112"
        and not gcd_one_close
    )
    failed = 0 if passed else 1
    return check_bool("k2_width_and_capacity_conditioning", passed, total=9, failed=failed)


def check_reflection_pair_bias(rows) -> dict[str, str]:
    top_pairs = {
        scope: _top_reflection_pair(rows, scope)
        for scope in ("B4_to_B5_full", "B5_to_B6_full", "B6_to_B7_full")
    }
    b7_cross = [
        row
        for row in rows
        if row.diagnostic == "close_child_gcd_reflection_pair_crosstab"
        and row.scope == "B6_to_B7_full"
    ]
    top_b7_cross = max(b7_cross, key=lambda row: row.family_count)
    passed = (
        top_pairs["B4_to_B5_full"] == "3/8"
        and top_pairs["B5_to_B6_full"] == "3/10"
        and top_pairs["B6_to_B7_full"] == "4/13"
        and top_b7_cross.stratum == "gcd=3;pair=4/13"
    )
    failed = 0 if passed else 1
    return check_bool("reflection_pair_bias", passed, total=4, failed=failed)


def compare_recomputed_rows(name: str, committed_rows, recomputed_rows) -> dict[str, str]:
    committed = [row_signature(row) for row in committed_rows]
    recomputed = [row_signature(row) for row in recomputed_rows]
    mismatches = sum(left != right for left, right in zip(committed, recomputed))
    mismatches += abs(len(committed) - len(recomputed))
    return check_bool(
        name,
        committed == recomputed,
        total=max(len(committed), len(recomputed)),
        failed=mismatches,
    )


def _top_parent_gcd(rows, population: str) -> str:
    subset = [
        row
        for row in rows
        if row.diagnostic == "parent_gcd_capacity_conditioned"
        and row.scope == "all"
        and row.population == population
        and row.stratum != "empty"
    ]
    return max(subset, key=lambda row: row.family_count).stratum


def _top_reflection_pair(rows, scope: str) -> str:
    subset = [
        row
        for row in rows
        if row.diagnostic == "close_reflection_pair_by_scope"
        and row.scope == scope
        and row.population == "close"
    ]
    return max(subset, key=lambda row: row.family_count).stratum


def _row_for(rows, diagnostic: str, scope: str, population: str, stratum: str):
    for row in rows:
        if (
            row.diagnostic == diagnostic
            and row.scope == scope
            and row.population == population
            and row.stratum == stratum
        ):
            return row
    raise AssertionError(f"missing row: {diagnostic} {scope} {population} {stratum}")


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
