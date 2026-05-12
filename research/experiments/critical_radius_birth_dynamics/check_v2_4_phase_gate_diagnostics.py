#!/usr/bin/env python3
"""Verify source-only PRC v2.4 independent phase-gate diagnostics."""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

from v2_4_phase_gate_diagnostics import (
    DEFAULT_PHASE_GATE_FAMILY_SUMMARY_CSV,
    DEFAULT_PHASE_GATE_LIFT_DIAGNOSTICS_CSV,
    DEFAULT_PHASE_GATE_MARGIN_RANK_FIGURE,
    build_phase_gate_family_summary_rows,
    build_phase_gate_lift_diagnostic_rows,
    read_phase_gate_family_summary_csv,
    read_phase_gate_lift_diagnostics_csv,
    row_signature,
    write_phase_gate_artifacts,
)

DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_4_phase_gate_diagnostics_verification_v0_1.csv"
)
EXPECTED_LIFT_ROWS = 533690
EXPECTED_FAMILIES = 32002
EXPECTED_CLOSE_FAMILIES = 770
EXPECTED_CAPACITY_NONCLOSE_FAMILIES = 2430


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.4 independent phase-gate diagnostics.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument(
        "--update-data",
        action="store_true",
        help="regenerate committed source-only phase-gate CSVs and figure",
    )
    args = parser.parse_args()

    if args.update_data:
        write_phase_gate_artifacts()

    lift_rows = read_phase_gate_lift_diagnostics_csv(DEFAULT_PHASE_GATE_LIFT_DIAGNOSTICS_CSV)
    family_rows = read_phase_gate_family_summary_csv(DEFAULT_PHASE_GATE_FAMILY_SUMMARY_CSV)
    checks = verification_rows(lift_rows, family_rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_4_phase_gate_diagnostics: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(lift_rows, family_rows) -> list[dict[str, str]]:
    recomputed_lift_rows = build_phase_gate_lift_diagnostic_rows()
    close_rows = [row for row in lift_rows if row.is_close]
    nonclose_rows = [row for row in lift_rows if not row.is_close]
    close_families = [row for row in family_rows if row.close_lift_count > 0]
    capacity_nonclose_families = [
        row
        for row in family_rows
        if row.capacity_pass and row.close_lift_count == 0
    ]
    return [
        compare_recomputed_rows(
            "phase_gate_lift_rows_match_recomputed",
            lift_rows,
            recomputed_lift_rows,
        ),
        compare_recomputed_rows(
            "phase_gate_family_rows_match_recomputed",
            family_rows,
            build_phase_gate_family_summary_rows(lift_rows),
        ),
        check_bool(
            "phase_gate_row_counts",
            len(lift_rows) == EXPECTED_LIFT_ROWS
            and len(family_rows) == EXPECTED_FAMILIES,
            total=EXPECTED_LIFT_ROWS + EXPECTED_FAMILIES,
            failed=abs(len(lift_rows) - EXPECTED_LIFT_ROWS)
            + abs(len(family_rows) - EXPECTED_FAMILIES),
        ),
        check_bool(
            "all_close_rows_pass_capacity_and_phase",
            all(row.capacity_pass and row.phase_pass for row in close_rows),
            total=len(close_rows),
            failed=sum(not (row.capacity_pass and row.phase_pass) for row in close_rows),
        ),
        check_bool(
            "nonbirth_close_rows_zero",
            all(not (row.is_close and not row.is_birth) for row in lift_rows),
            total=len(lift_rows),
            failed=sum(row.is_close and not row.is_birth for row in lift_rows),
        ),
        check_bool(
            "capacity_nonclose_families_have_no_phase_pass",
            len(capacity_nonclose_families) == EXPECTED_CAPACITY_NONCLOSE_FAMILIES
            and all(row.phase_pass_count == 0 for row in capacity_nonclose_families),
            total=EXPECTED_CAPACITY_NONCLOSE_FAMILIES,
            failed=abs(len(capacity_nonclose_families) - EXPECTED_CAPACITY_NONCLOSE_FAMILIES)
            + sum(row.phase_pass_count != 0 for row in capacity_nonclose_families),
        ),
        check_bool(
            "close_capable_families_phase_pass_equals_close",
            len(close_families) == EXPECTED_CLOSE_FAMILIES
            and all(
                row.phase_pass_count == row.close_lift_count == row.birth_lift_count == 1
                and row.phase_pass_remainders == row.close_remainders
                for row in close_families
            ),
            total=EXPECTED_CLOSE_FAMILIES,
            failed=abs(len(close_families) - EXPECTED_CLOSE_FAMILIES)
            + sum(
                not (
                    row.phase_pass_count == row.close_lift_count == row.birth_lift_count == 1
                    and row.phase_pass_remainders == row.close_remainders
                )
                for row in close_families
            ),
        ),
        check_bool(
            "close_lifts_are_top_phase_margin_rank",
            all(row.phase_rank_desc == 1 for row in close_rows),
            total=len(close_rows),
            failed=sum(row.phase_rank_desc != 1 for row in close_rows),
        ),
        check_bool(
            "nonclose_rows_do_not_phase_pass",
            all(not row.phase_pass for row in nonclose_rows),
            total=len(nonclose_rows),
            failed=sum(row.phase_pass for row in nonclose_rows),
        ),
        check_bool(
            "phase_margins_are_exact_fraction_text",
            all("." not in row.phase_margin for row in lift_rows)
            and all("." not in row.best_phase_margin for row in family_rows),
            total=len(lift_rows) + len(family_rows),
            failed=sum("." in row.phase_margin for row in lift_rows)
            + sum("." in row.best_phase_margin for row in family_rows),
        ),
        check_figure_exists(DEFAULT_PHASE_GATE_MARGIN_RANK_FIGURE),
    ]


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


def check_figure_exists(path: Path) -> dict[str, str]:
    passed = path.exists() and path.stat().st_size > 1000
    return check_bool(
        f"{path.stem}_exists",
        passed,
        total=1,
        failed=0 if passed else 1,
    )


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
