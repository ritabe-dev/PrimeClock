#!/usr/bin/env python3
"""Verify the internal PRC v2.3 critical-radius/birth-dynamics candidate.

This checker is intentionally scoped to the internal experiment. It reuses the
exact experiment helpers, recomputes the promoted finite candidate rows, and
checks that the committed CSV artifacts still match the theorem-note draft.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import fields
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from tools import (
    BirthDynamicsRow,
    BirthDynamicsSummaryRow,
    BirthThresholdCrossingRow,
    CriticalRadiusNearMissRow,
    CriticalRadiusRow,
    CriticalRadiusSummaryRow,
    ExactInterval,
    NearMissBirthParentRow,
    NearMissGapGeometryRow,
    birth_dynamics_rows,
    birth_dynamics_summary_rows,
    birth_threshold_crossing_rows,
    classify_birth_containment,
    critical_radius_near_miss_rows,
    critical_radius_rows,
    critical_radius_summary_rows,
    exact_arc_intervals_for_residue,
    near_miss_birth_parent_rows,
    near_miss_gap_geometry_rows,
    parse_fraction,
    prime_prefix_residue_full_rows,
    residue_is_exactly_covered,
)


EXPERIMENT_DIR = Path(__file__).resolve().parent
DATA_DIR = EXPERIMENT_DIR / "data"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify PRC v2.3 internal candidate CSVs.",
    )
    parser.add_argument(
        "--out",
        default=DATA_DIR / "prc_v2_3_candidate_verification_v0_1.csv",
        help="verification summary CSV path",
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="print phase progress messages to stderr",
    )
    args = parser.parse_args()

    rows = verification_rows(progress=args.progress)
    write_checks(rows, args.out)
    failed = sum(int(row["failed"]) for row in rows)
    print(
        "check_v2_3_candidate: "
        f"checks={len(rows)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def log_progress(enabled: bool, message: str) -> None:
    if enabled:
        print(f"[check_candidate] {message}", file=sys.stderr)


def verification_rows(*, progress: bool = False) -> list[dict[str, str]]:
    log_progress(progress, "computing critical-radius rows")
    radius_rows = critical_radius_rows(min_k=4, max_k=5)
    radius_summary_rows = critical_radius_summary_rows(radius_rows)
    near_miss_rows = critical_radius_near_miss_rows(radius_rows, limit_per_k=20)
    near_miss_parent_rows = near_miss_birth_parent_rows(near_miss_rows)
    near_miss_gap_rows = near_miss_gap_geometry_rows(near_miss_rows)

    log_progress(progress, "computing prime-prefix full rows through k=7")
    full_rows = prime_prefix_residue_full_rows(max_k=7, allow_large_k=True)

    log_progress(progress, "computing birth-dynamics rows")
    birth_rows = birth_dynamics_rows(min_k=5, max_k=7, full_rows=full_rows)
    birth_summary_rows = birth_dynamics_summary_rows(birth_rows)

    log_progress(progress, "computing birth threshold-crossing rows")
    crossing_rows = birth_threshold_crossing_rows(
        min_k=5,
        max_k=7,
        full_rows=full_rows,
        birth_rows=birth_rows,
    )

    log_progress(progress, "checking generated rows against committed CSVs")
    checks: list[dict[str, str]] = []
    checks.append(check_c4_level_set(radius_rows))
    checks.append(check_c5_level_set_matches_exact_coverage(radius_rows))
    checks.append(check_spectrum_status_counts(radius_summary_rows))
    checks.append(
        check_csv_exact(
            "critical_radius_rows_csv_exact",
            DATA_DIR / "prc_prime_prefix_critical_radius_k4_k5_v0_1.csv",
            radius_rows,
            CriticalRadiusRow,
        )
    )
    checks.append(
        check_csv_exact(
            "critical_radius_summary_csv_exact",
            DATA_DIR / "prc_prime_prefix_critical_radius_summary_v0_1.csv",
            radius_summary_rows,
            CriticalRadiusSummaryRow,
        )
    )
    checks.append(
        check_csv_exact(
            "critical_radius_near_misses_csv_exact",
            DATA_DIR / "prc_prime_prefix_critical_radius_near_misses_k4_k5_v0_1.csv",
            near_miss_rows,
            CriticalRadiusNearMissRow,
        )
    )
    checks.append(
        check_csv_exact(
            "near_miss_parent_overlap_csv_exact",
            DATA_DIR / "prc_prime_prefix_near_miss_birth_parent_overlap_k4_k6_v0_1.csv",
            near_miss_parent_rows,
            NearMissBirthParentRow,
        )
    )
    checks.append(
        check_csv_exact(
            "near_miss_gap_geometry_csv_exact",
            DATA_DIR / "prc_prime_prefix_near_miss_gap_geometry_k4_k5_v0_1.csv",
            near_miss_gap_rows,
            NearMissGapGeometryRow,
        )
    )
    checks.append(check_birth_candidate_claims(birth_rows, crossing_rows))
    checks.append(check_unique_strict_single_gap_remainders(birth_rows))
    checks.append(
        check_csv_exact(
            "birth_threshold_crossing_csv_exact",
            DATA_DIR / "prc_prime_prefix_birth_threshold_crossing_k5_k7_v0_1.csv",
            crossing_rows,
            BirthThresholdCrossingRow,
        )
    )
    checks.append(
        check_csv_exact(
            "birth_dynamics_rows_csv_exact",
            DATA_DIR / "prc_prime_prefix_birth_dynamics_k5_k7_v0_1.csv",
            birth_rows,
            BirthDynamicsRow,
        )
    )
    checks.append(
        check_csv_exact(
            "birth_dynamics_summary_csv_exact",
            DATA_DIR / "prc_prime_prefix_birth_dynamics_summary_v0_1.csv",
            birth_summary_rows,
            BirthDynamicsSummaryRow,
        )
    )
    return checks


def check_c4_level_set(rows: Iterable[CriticalRadiusRow]) -> dict[str, str]:
    covered = {
        row.residue
        for row in rows
        if row.k == 4 and parse_fraction(row.lambda_fraction) <= Fraction(1, 2)
    }
    return check("critical_radius_c4_level_set_exact", 1, int(covered == {2, 208}))


def check_c5_level_set_matches_exact_coverage(
    rows: Iterable[CriticalRadiusRow],
) -> dict[str, str]:
    level_set = {
        row.residue
        for row in rows
        if row.k == 5 and parse_fraction(row.lambda_fraction) <= Fraction(1, 2)
    }
    exact_covered = {
        row.residue
        for row in rows
        if row.k == 5 and residue_is_exactly_covered(row.residue, [2, 3, 5, 7, 11])
    }
    checks = [
        len(level_set) == 36,
        level_set == exact_covered,
    ]
    return check(
        "critical_radius_c5_level_set_matches_exact_coverage",
        len(checks),
        sum(checks),
    )


def check_spectrum_status_counts(
    rows: Iterable[CriticalRadiusSummaryRow],
) -> dict[str, str]:
    expected = {
        4: ("0", "2", "208", "5/9"),
        5: ("2", "34", "2274", "7/13"),
    }
    passed = 0
    for row in rows:
        actual = (
            str(row.robust_covered_count),
            str(row.endpoint_covered_count),
            str(row.uncovered_count),
            row.nearest_uncovered_lambda_fraction,
        )
        passed += actual == expected.get(row.k)
    return check("critical_radius_summary_claims_exact", len(expected), passed)


def check_birth_candidate_claims(
    birth_rows: Iterable[BirthDynamicsRow],
    crossing_rows: Iterable[BirthThresholdCrossingRow],
) -> dict[str, str]:
    birth_rows_list = list(birth_rows)
    crossing_rows_list = list(crossing_rows)
    checks = [
        sum(row.k == 5 for row in birth_rows_list) == 14,
        sum(row.k == 6 for row in birth_rows_list) == 42,
        sum(row.k == 7 for row in birth_rows_list) == 714,
        {row.birth_type for row in birth_rows_list} == {"strict_single_gap_birth"},
        all(row.previous_open_gap_count == 1 for row in birth_rows_list),
        all(not row.uses_endpoint_touching for row in birth_rows_list),
        len(crossing_rows_list) == len(birth_rows_list),
        all(parse_fraction(row.parent_lambda_fraction) > Fraction(1, 2) for row in crossing_rows_list),
        all(parse_fraction(row.current_lambda_fraction) <= Fraction(1, 2) for row in crossing_rows_list),
    ]
    return check(
        "birth_dynamics_b5_b6_b7_strict_single_gap_exact",
        len(checks),
        sum(checks),
    )


def check_unique_strict_single_gap_remainders(
    birth_rows: Iterable[BirthDynamicsRow],
) -> dict[str, str]:
    """Check that each birth parent has exactly one strict q-remainder."""
    rows = list(birth_rows)
    rows_by_parent: dict[tuple[int, int], list[BirthDynamicsRow]] = {}
    for row in rows:
        rows_by_parent.setdefault((row.k, row.parent_residue_mod_previous), []).append(row)

    checks: list[bool] = [
        len(group) == 1
        for group in rows_by_parent.values()
    ]
    checks.extend(
        len([row for row in rows if row.k == k]) == len(
            {
                row.parent_residue_mod_previous
                for row in rows
                if row.k == k
            }
        )
        for k in [5, 6, 7]
    )

    for row in rows:
        previous_gaps = parse_intervals(row.previous_open_gap_boundary_endpoints)
        valid_remainders = []
        for remainder in range(row.new_prime):
            try:
                containment = classify_birth_containment(
                    previous_gaps,
                    exact_arc_intervals_for_residue(remainder, row.new_prime),
                )
            except ValueError:
                continue
            if containment.margin > 0:
                valid_remainders.append(remainder)
        checks.append(valid_remainders == [row.new_prime_remainder])
        checks.append(row.birth_type == "strict_single_gap_birth")
        checks.append(row.previous_open_gap_count == 1)
        checks.append(not row.uses_endpoint_touching)

    return check(
        "birth_dynamics_b5_b6_b7_unique_strict_single_gap_remainders",
        len(checks),
        sum(checks),
    )


def parse_intervals(value: str) -> list[ExactInterval]:
    intervals: list[ExactInterval] = []
    if not value:
        return intervals
    for item in value.split(";"):
        start, end = item.split("-", 1)
        intervals.append((parse_fraction(start), parse_fraction(end)))
    return intervals


def check_csv_exact(
    name: str,
    csv_path: Path,
    expected_rows: Iterable[object],
    row_type: type,
) -> dict[str, str]:
    expected = [dataclass_row(row, row_type) for row in expected_rows]
    actual = read_csv(csv_path)
    if len(actual) != len(expected):
        return check(name, max(len(actual), len(expected)), 0)

    expected_keys = sorted(tuple(row.items()) for row in expected)
    actual_keys = sorted(tuple(row.items()) for row in actual)
    passed = sum(left == right for left, right in zip(expected_keys, actual_keys))
    return check(name, len(expected_keys), passed)


def dataclass_row(row: object, row_type: type) -> dict[str, str]:
    return {
        field.name: str(getattr(row, field.name))
        for field in fields(row_type)
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_checks(rows: Iterable[dict[str, str]], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["check_name", "total", "passed", "failed", "status"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def check(name: str, total: int, passed: int) -> dict[str, str]:
    failed = total - passed
    return {
        "check_name": name,
        "total": str(total),
        "passed": str(passed),
        "failed": str(failed),
        "status": "pass" if failed == 0 else "fail",
    }


if __name__ == "__main__":
    raise SystemExit(main())
