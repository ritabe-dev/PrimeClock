#!/usr/bin/env python3
"""Verify source-only PRC v2.5 B8 control calibration."""

from __future__ import annotations

import argparse
import csv
import tempfile
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

from v2_5_b8_control_calibration import (
    DEFAULT_B8_CONTROL_CALIBRATION_SUMMARY_CSV,
    DEFAULT_B8_CONTROL_OVERLAP_AUDIT_CSV,
    DEFAULT_B8_MATCHED_NONBIRTH_CONTROLS_CSV,
    DEFAULT_B8_SIBLING_NONBIRTH_CONTROLS_CSV,
    build_b8_control_calibration_summary_rows,
    build_b8_control_overlap_audit_rows,
    build_b8_matched_nonbirth_control_rows,
    build_b8_sibling_control_rows,
    control_calibration_signature,
    read_b8_control_calibration_summary_csv,
    read_b8_control_overlap_audit_csv,
    read_b8_matched_nonbirth_control_csv,
    read_b8_sibling_control_csv,
    write_b8_control_calibration_artifacts,
)

DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_5_b8_control_calibration_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.5 B8 control calibration.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument("--update-data", action="store_true")
    args = parser.parse_args()

    if args.update_data:
        write_b8_control_calibration_artifacts()

    sibling_rows = read_b8_sibling_control_csv(DEFAULT_B8_SIBLING_NONBIRTH_CONTROLS_CSV)
    matched_rows = read_b8_matched_nonbirth_control_csv(
        DEFAULT_B8_MATCHED_NONBIRTH_CONTROLS_CSV
    )
    overlap_rows = read_b8_control_overlap_audit_csv(
        DEFAULT_B8_CONTROL_OVERLAP_AUDIT_CSV
    )
    summary_rows = read_b8_control_calibration_summary_csv(
        DEFAULT_B8_CONTROL_CALIBRATION_SUMMARY_CSV
    )
    checks = verification_rows(sibling_rows, matched_rows, overlap_rows, summary_rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_5_b8_control_calibration: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(sibling_rows, matched_rows, overlap_rows, summary_rows):
    return [
        check_sibling_rows_recompute(sibling_rows),
        check_sibling_family_lifts(sibling_rows),
        check_sibling_phase_separation(sibling_rows),
        check_sibling_exact_birth_audit(sibling_rows),
        check_matched_rows_recompute(matched_rows),
        check_matched_nonbirth_controls(matched_rows),
        check_k8_sample_overlap_calibration(overlap_rows),
        check_summary_matches_rows(sibling_rows, matched_rows, overlap_rows, summary_rows),
    ]


def check_sibling_rows_recompute(rows):
    expected = build_b8_sibling_control_rows()
    committed = [control_calibration_signature(row) for row in rows]
    recomputed = [control_calibration_signature(row) for row in expected]
    mismatches = sum(left != right for left, right in zip(committed, recomputed))
    mismatches += abs(len(committed) - len(recomputed))
    return check_bool(
        "b8_control_sibling_rows_match_recompute",
        committed == recomputed,
        total=max(len(committed), len(recomputed)),
        failed=mismatches,
    )


def check_sibling_family_lifts(rows):
    by_parent: dict[int, list[object]] = defaultdict(list)
    for row in rows:
        by_parent[row.parent_residue].append(row)
    failed = 0
    for parent_rows in by_parent.values():
        role_counts = Counter(row.sibling_role for row in parent_rows)
        if len(parent_rows) != 19:
            failed += 1
        if role_counts["birth_close"] != 1:
            failed += 1
        if role_counts["sibling_nonbirth"] != 18:
            failed += 1
    return check_bool(
        "b8_control_sibling_family_has_one_birth_and_18_nonbirth",
        len(by_parent) == 32 and failed == 0,
        total=len(by_parent),
        failed=failed + (0 if len(by_parent) == 32 else 1),
    )


def check_sibling_phase_separation(rows):
    failed = 0
    for row in rows:
        margin = Fraction(row.phase_margin)
        if row.sibling_role == "birth_close":
            failed += int(
                not (
                    margin > 0
                    and row.transition_label == "close"
                    and row.phase_rank == 1
                )
            )
        else:
            failed += int(
                not (
                    margin <= 0
                    and row.transition_label != "close"
                    and not row.child_covered_exact
                )
            )
    return check_bool(
        "b8_control_sibling_phase_separates_birth_from_siblings",
        failed == 0,
        total=len(rows),
        failed=failed,
    )


def check_sibling_exact_birth_audit(rows):
    failed = 0
    for row in rows:
        if not (row.parent_uncovered_exact and row.child_projects_to_parent):
            failed += 1
        if row.sibling_role == "birth_close":
            failed += int(
                not (
                    row.child_covered_exact
                    and row.exact_b8_birth
                    and row.parent_gap_count_exact == 1
                    and row.child_gap_count_exact == 0
                )
            )
        else:
            failed += int(row.child_covered_exact or row.exact_b8_birth)
    return check_bool(
        "b8_control_sibling_exact_birth_audit",
        failed == 0,
        total=len(rows),
        failed=failed,
    )


def check_matched_rows_recompute(rows):
    expected = build_b8_matched_nonbirth_control_rows()
    committed = [control_calibration_signature(row) for row in rows]
    recomputed = [control_calibration_signature(row) for row in expected]
    mismatches = sum(left != right for left, right in zip(committed, recomputed))
    mismatches += abs(len(committed) - len(recomputed))
    return check_bool(
        "b8_control_matched_rows_match_recompute",
        committed == recomputed,
        total=max(len(committed), len(recomputed)),
        failed=mismatches,
    )


def check_matched_nonbirth_controls(rows):
    failed = 0
    for row in rows:
        failed += int(not row.control_capacity_pass)
        failed += int(Fraction(row.control_phase_margin) > 0)
        failed += int(row.control_transition_label == "close")
        failed += int(not row.control_parent_uncovered_exact)
        failed += int(row.control_child_covered_exact)
        failed += int(row.control_exact_b8_birth)
    measure_buckets = {row.control_parent_residual_measure for row in rows}
    reflection_buckets = {row.control_reflection_orbit for row in rows}
    passed = (
        len(rows) >= 64
        and failed == 0
        and len(measure_buckets) > 1
        and len(reflection_buckets) > 1
    )
    return check_bool(
        "b8_control_matched_nonbirth_controls_are_capacity_comparable",
        passed,
        total=len(rows),
        failed=failed
        + (0 if len(rows) >= 64 else 1)
        + (0 if len(measure_buckets) > 1 else 1)
        + (0 if len(reflection_buckets) > 1 else 1),
    )


def check_k8_sample_overlap_calibration(rows):
    expected = build_b8_control_overlap_audit_rows()
    committed = [control_calibration_signature(row) for row in rows]
    recomputed = [control_calibration_signature(row) for row in expected]
    overlap = sum(row.in_aperture_orbit_32 for row in rows)
    failed = sum(left != right for left, right in zip(committed, recomputed))
    failed += abs(len(committed) - len(recomputed))
    failed += sum(row.calibration_role != "sample_overlap_only_not_recall" for row in rows)
    passed = len(rows) == 200 and committed == recomputed and overlap >= 0
    return check_bool(
        "b8_control_k8_sample_overlap_is_calibration_only",
        passed,
        total=max(len(committed), len(recomputed)),
        failed=failed + (0 if len(rows) == 200 else 1),
    )


def check_summary_matches_rows(sibling_rows, matched_rows, overlap_rows, summary_rows):
    expected = build_b8_control_calibration_summary_rows(
        sibling_rows=sibling_rows,
        matched_rows=matched_rows,
        overlap_rows=overlap_rows,
    )
    committed = [control_calibration_signature(row) for row in summary_rows]
    recomputed = [control_calibration_signature(row) for row in expected]
    failed = sum(left != right for left, right in zip(committed, recomputed))
    failed += abs(len(committed) - len(recomputed))
    return check_bool(
        "b8_control_summary_matches_rows",
        committed == recomputed,
        total=max(len(committed), len(recomputed)),
        failed=failed,
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
