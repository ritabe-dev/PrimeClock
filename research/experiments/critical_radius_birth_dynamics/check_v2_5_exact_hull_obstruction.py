#!/usr/bin/env python3
"""Verify source-only PRC v2.5 exact hull obstruction diagnostics."""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

from v2_5_exact_hull_obstruction import (
    DEFAULT_EXACT_HULL_OBSTRUCTION_FAMILY_CSV,
    DEFAULT_EXACT_HULL_OBSTRUCTION_SUMMARY_CSV,
    build_exact_hull_obstruction_family_rows,
    build_exact_hull_obstruction_summary_rows,
    hull_obstruction_signature,
    read_exact_hull_obstruction_family_csv,
    read_exact_hull_obstruction_summary_csv,
    write_exact_hull_obstruction_artifacts,
)

DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_5_exact_hull_obstruction_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.5 exact hull obstruction diagnostics.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument("--update-data", action="store_true")
    args = parser.parse_args()

    if args.update_data:
        write_exact_hull_obstruction_artifacts()

    family_rows = read_exact_hull_obstruction_family_csv(
        DEFAULT_EXACT_HULL_OBSTRUCTION_FAMILY_CSV
    )
    summary_rows = read_exact_hull_obstruction_summary_csv(
        DEFAULT_EXACT_HULL_OBSTRUCTION_SUMMARY_CSV
    )
    checks = verification_rows(family_rows, summary_rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_5_exact_hull_obstruction: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(family_rows, summary_rows):
    return [
        check_family_rows_recompute(family_rows),
        check_summary_rows_recompute(summary_rows, family_rows),
        check_historical_hull_obstruction_counts(summary_rows),
        check_no_multi_component_close(family_rows),
        check_exact_fraction_fields(family_rows),
        check_b8_checked_close_single_gap(summary_rows),
    ]


def check_family_rows_recompute(rows):
    expected = build_exact_hull_obstruction_family_rows()
    return compare_rows(
        "exact_hull_obstruction_family_rows_match_recomputed",
        rows,
        expected,
    )


def check_summary_rows_recompute(summary_rows, family_rows):
    expected = build_exact_hull_obstruction_summary_rows(family_rows)
    return compare_rows(
        "exact_hull_obstruction_summary_rows_match_recomputed",
        summary_rows,
        expected,
    )


def check_historical_hull_obstruction_counts(rows):
    by_scope = {row.scope: row for row in rows}
    expected_multi = {
        "B4_to_B5_full": 65,
        "B5_to_B6_full": 913,
        "B6_to_B7_full": 13785,
    }
    failed = 0
    for scope, expected in expected_multi.items():
        row = by_scope.get(scope)
        failed += int(row is None)
        if row is None:
            continue
        failed += int(row.multi_component_family_count != expected)
        failed += int(row.hull_obstructed_multi_count != expected)
        failed += int(row.status != "checked_hull_obstruction")
    return check_bool(
        "exact_hull_obstruction_multi_component_counts",
        failed == 0,
        total=len(expected_multi) * 3,
        failed=failed,
    )


def check_no_multi_component_close(rows):
    multi_rows = [row for row in rows if row.old_component_count > 1]
    close_rows = [row for row in rows if row.close_lift_count > 0]
    failed = sum(row.close_lift_count > 0 for row in multi_rows)
    failed += sum(row.old_component_count != 1 for row in close_rows)
    return check_bool(
        "exact_hull_obstruction_close_rows_have_single_gap_precursor",
        failed == 0,
        total=len(multi_rows) + len(close_rows),
        failed=failed,
    )


def check_exact_fraction_fields(rows):
    failed = sum(
        "." in row.min_covering_hull_length or "." in row.new_arc_width
        for row in rows
    )
    return check_bool(
        "exact_hull_obstruction_fraction_fields_are_exact",
        failed == 0,
        total=len(rows),
        failed=failed,
    )


def check_b8_checked_close_single_gap(rows):
    failed = sum(row.b8_checked_close_single_gap_count != 32 for row in rows)
    return check_bool(
        "exact_hull_obstruction_b8_checked_close_single_gap",
        failed == 0,
        total=len(rows),
        failed=failed,
    )


def compare_rows(name: str, committed_rows, recomputed_rows):
    committed = [hull_obstruction_signature(row) for row in committed_rows]
    recomputed = [hull_obstruction_signature(row) for row in recomputed_rows]
    mismatches = sum(left != right for left, right in zip(committed, recomputed))
    mismatches += abs(len(committed) - len(recomputed))
    return check_bool(
        name,
        committed == recomputed,
        total=max(len(committed), len(recomputed)),
        failed=mismatches,
    )


def check_bool(name: str, passed: bool, *, total: int, failed: int):
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
