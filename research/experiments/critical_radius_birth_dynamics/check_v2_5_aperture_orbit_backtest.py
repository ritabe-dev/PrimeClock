#!/usr/bin/env python3
"""Verify source-only PRC v2.5 aperture-orbit historical calibration."""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

from v2_5_aperture_orbit_backtest import (
    DEFAULT_APERTURE_ORBIT_BACKTEST_B8_COMPARISON_CSV,
    DEFAULT_APERTURE_ORBIT_BACKTEST_FAMILY_SUMMARY_CSV,
    DEFAULT_APERTURE_ORBIT_BACKTEST_SCOPE_SUMMARY_CSV,
    backtest_signature,
    build_aperture_orbit_backtest_b8_comparison_rows,
    build_aperture_orbit_backtest_family_rows,
    build_aperture_orbit_backtest_scope_rows,
    read_aperture_orbit_backtest_b8_comparison_csv,
    read_aperture_orbit_backtest_family_csv,
    read_aperture_orbit_backtest_scope_csv,
    write_aperture_orbit_backtest_artifacts,
)

DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_5_aperture_orbit_backtest_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.5 aperture-orbit backtest.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument("--update-data", action="store_true")
    args = parser.parse_args()

    if args.update_data:
        write_aperture_orbit_backtest_artifacts()

    family_rows = read_aperture_orbit_backtest_family_csv(
        DEFAULT_APERTURE_ORBIT_BACKTEST_FAMILY_SUMMARY_CSV
    )
    scope_rows = read_aperture_orbit_backtest_scope_csv(
        DEFAULT_APERTURE_ORBIT_BACKTEST_SCOPE_SUMMARY_CSV
    )
    b8_rows = read_aperture_orbit_backtest_b8_comparison_csv(
        DEFAULT_APERTURE_ORBIT_BACKTEST_B8_COMPARISON_CSV
    )
    checks = verification_rows(family_rows, scope_rows, b8_rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_5_aperture_orbit_backtest: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(family_rows, scope_rows, b8_rows):
    return [
        check_family_rows_recompute(family_rows),
        check_scope_rows_recompute(scope_rows, family_rows),
        check_historical_scope_counts(scope_rows),
        check_historical_separator_status(scope_rows),
        check_b8_comparison_rows_recompute(b8_rows),
        check_b8_comparison_separator(b8_rows),
    ]


def check_family_rows_recompute(rows):
    expected = build_aperture_orbit_backtest_family_rows()
    return compare_rows(
        "aperture_orbit_backtest_family_rows_match_recomputed",
        rows,
        expected,
    )


def check_scope_rows_recompute(scope_rows, family_rows):
    expected = build_aperture_orbit_backtest_scope_rows(family_rows=family_rows)
    return compare_rows(
        "aperture_orbit_backtest_scope_rows_match_recomputed",
        scope_rows,
        expected,
    )


def check_historical_scope_counts(rows):
    by_scope = {row.scope: row for row in rows}
    expected_families = {
        "B4_to_B5_full": 208,
        "B5_to_B6_full": 2274,
        "B6_to_B7_full": 29520,
    }
    failed = 0
    for scope, expected in expected_families.items():
        row = by_scope.get(scope)
        failed += int(row is None or row.family_count != expected)
    failed += int(sum(row.close_count for row in rows) != 770)
    failed += int(sum(row.birth_count for row in rows) != 770)
    failed += int(sum(row.capacity_nonclose_families for row in rows) != 2430)
    failed += int(sum(row.nonbirth_close_count for row in rows) != 0)
    return check_bool(
        "aperture_orbit_backtest_historical_counts",
        failed == 0,
        total=len(expected_families) + 4,
        failed=failed,
    )


def check_historical_separator_status(rows):
    failed = 0
    for row in rows:
        failed += int(row.separator_status != "stable_separator")
        failed += int(row.close_phase_rank_1_count != row.close_count)
        failed += int(row.close_positive_margin_count != row.close_count)
        failed += int(row.nonclose_positive_margin_count != 0)
    return check_bool(
        "aperture_orbit_backtest_historical_separator_stable",
        failed == 0,
        total=len(rows) * 4,
        failed=failed,
    )


def check_b8_comparison_rows_recompute(rows):
    expected = build_aperture_orbit_backtest_b8_comparison_rows()
    return compare_rows(
        "aperture_orbit_backtest_b8_comparison_rows_match_recomputed",
        rows,
        expected,
    )


def check_b8_comparison_separator(rows):
    values = {(row.cohort, row.metric): row.value for row in rows}
    expected = {
        ("B8_sibling_control", "birth_close_count"): "32",
        ("B8_sibling_control", "sibling_nonbirth_count"): "576",
        ("B8_sibling_control", "birth_close_positive_margin_count"): "32",
        ("B8_sibling_control", "sibling_nonbirth_positive_margin_count"): "0",
        ("B8_matched_nonbirth_control", "matched_nonbirth_count"): "64",
        ("B8_matched_nonbirth_control", "matched_positive_margin_count"): "0",
        ("B8_sample_calibration", "k8_sample_rows"): "200",
    }
    failed = sum(values.get(key) != expected_value for key, expected_value in expected.items())
    failed += int(int(values.get(("B8_matched_nonbirth_control", "matched_measure_bucket_count"), "0")) <= 1)
    failed += int(int(values.get(("B8_matched_nonbirth_control", "matched_reflection_orbit_count"), "0")) <= 1)
    return check_bool(
        "aperture_orbit_backtest_b8_comparison_stable",
        failed == 0,
        total=len(expected) + 2,
        failed=failed,
    )


def compare_rows(name: str, committed_rows, recomputed_rows):
    committed = [backtest_signature(row) for row in committed_rows]
    recomputed = [backtest_signature(row) for row in recomputed_rows]
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
