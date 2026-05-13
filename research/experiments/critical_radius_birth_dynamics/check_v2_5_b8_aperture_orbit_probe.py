#!/usr/bin/env python3
"""Verify source-only PRC v2.5 B8 aperture-orbit diagnostics."""

from __future__ import annotations

import argparse
import csv
import tempfile
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

from v2_5_b8_aperture_orbit_probe import (
    APERTURE_FRONTIER_GROUP,
    CAPACITY_TOP_GROUP,
    DEFAULT_B8_APERTURE_ORBIT_HEATMAP,
    DEFAULT_B8_APERTURE_ORBIT_PROBE_CSV,
    DEFAULT_B8_APERTURE_ORBIT_SUMMARY_CSV,
    DEFAULT_B8_BIRTH_OVERLAP_AUDIT_CSV,
    DEFAULT_B8_FAILURE_FORENSICS_CSV,
    DEFAULT_B8_PARENT_SELECTION_AUDIT_CSV,
    b8_aperture_orbit_signature,
    build_b8_aperture_orbit_probe_rows,
    read_b8_aperture_orbit_probe_csv,
    read_b8_aperture_orbit_summary_csv,
    read_b8_birth_overlap_audit_csv,
    read_b8_failure_forensics_csv,
    read_b8_parent_selection_audit_csv,
    write_b8_aperture_orbit_artifacts,
)

DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_5_b8_aperture_orbit_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.5 B8 aperture-orbit diagnostics.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument("--update-data", action="store_true")
    args = parser.parse_args()

    if args.update_data:
        write_b8_aperture_orbit_artifacts()

    failure_rows = read_b8_failure_forensics_csv(DEFAULT_B8_FAILURE_FORENSICS_CSV)
    audit_rows = read_b8_parent_selection_audit_csv(DEFAULT_B8_PARENT_SELECTION_AUDIT_CSV)
    probe_rows = read_b8_aperture_orbit_probe_csv(DEFAULT_B8_APERTURE_ORBIT_PROBE_CSV)
    summary_rows = read_b8_aperture_orbit_summary_csv(DEFAULT_B8_APERTURE_ORBIT_SUMMARY_CSV)
    birth_audit_rows = read_b8_birth_overlap_audit_csv(DEFAULT_B8_BIRTH_OVERLAP_AUDIT_CSV)
    checks = verification_rows(
        failure_rows,
        audit_rows,
        probe_rows,
        summary_rows,
        birth_audit_rows,
    )
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_5_b8_aperture_orbit_probe: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(failure_rows, audit_rows, probe_rows, summary_rows, birth_audit_rows):
    return [
        check_capacity_top_negative_baseline(failure_rows),
        check_probe_rows_recompute_from_selected_parents(probe_rows),
        check_every_parent_has_19_lifts(probe_rows),
        check_parent_measure_diversity(probe_rows),
        check_exact_margin_and_tension(probe_rows),
        check_positive_aperture_consistency(probe_rows),
        check_group_labels_present(probe_rows),
        check_hash_and_summary_stability(audit_rows, summary_rows),
        check_b8_close_rows_are_independent_births(probe_rows, birth_audit_rows),
        check_figure_exists(DEFAULT_B8_APERTURE_ORBIT_HEATMAP),
    ]


def check_capacity_top_negative_baseline(rows):
    labels = Counter(row.transition_label for row in rows)
    by_parent: dict[int, list[object]] = defaultdict(list)
    for row in rows:
        by_parent[row.parent_residue].append(row)
    best_margins = {
        parent: max(Fraction(row.phase_margin) for row in parent_rows)
        for parent, parent_rows in by_parent.items()
    }
    passed = (
        len(rows) == 3800
        and len(by_parent) == 200
        and labels["miss"] == 3400
        and labels["trim"] == 400
        and labels["close"] == 0
        and set(best_margins.values()) == {Fraction(-3, 209)}
    )
    failed = 0 if passed else 1
    return check_bool(
        "b8_capacity_top_200_negative_baseline",
        passed,
        total=1,
        failed=failed,
    )


def check_probe_rows_recompute_from_selected_parents(rows):
    parents = [
        parent
        for parent, _rank in sorted(
            {
                row.parent_residue: min(
                    other.parent_rank
                    for other in rows
                    if other.parent_residue == row.parent_residue
                )
                for row in rows
            }.items(),
            key=lambda item: item[1],
        )
    ]
    recomputed = build_b8_aperture_orbit_probe_rows(
        selected=[
            _candidate_stub_from_probe_rows(parent, [row for row in rows if row.parent_residue == parent])
            for parent in parents
        ],
        group_map={
            parent: set(
                group
                for row in rows
                if row.parent_residue == parent
                for group in row.selection_groups.split(";")
                if group
            )
            for parent in parents
        },
    )
    committed = [b8_aperture_orbit_signature(row) for row in rows]
    expected = [b8_aperture_orbit_signature(row) for row in recomputed]
    mismatches = sum(left != right for left, right in zip(committed, expected))
    mismatches += abs(len(committed) - len(expected))
    return check_bool(
        "b8_aperture_orbit_rows_match_selected_parent_recompute",
        committed == expected,
        total=max(len(committed), len(expected)),
        failed=mismatches,
    )


def check_every_parent_has_19_lifts(rows):
    counts = Counter(row.parent_residue for row in rows)
    failed = sum(count != 19 for count in counts.values())
    return check_bool(
        "b8_aperture_orbit_every_parent_has_19_lifts",
        failed == 0,
        total=len(counts),
        failed=failed,
    )


def check_parent_measure_diversity(rows):
    measures = {row.parent_residual_measure for row in rows}
    passed = len(measures) > 1 and measures != {"4/77"}
    return check_bool(
        "b8_aperture_orbit_not_all_measure_4_77",
        passed,
        total=len(measures),
        failed=0 if passed else 1,
    )


def check_exact_margin_and_tension(rows):
    failed = sum("." in row.phase_margin or "." in row.aperture_tension for row in rows)
    return check_bool(
        "b8_aperture_orbit_exact_fraction_fields",
        failed == 0,
        total=len(rows),
        failed=failed,
    )


def check_positive_aperture_consistency(rows):
    positive = [row for row in rows if Fraction(row.aperture_tension) < 0]
    failed = sum(
        not (Fraction(row.phase_margin) > 0 and row.transition_label == "close")
        for row in positive
    )
    return check_bool(
        "b8_aperture_orbit_positive_aperture_implies_close",
        failed == 0,
        total=len(positive),
        failed=failed,
    )


def check_group_labels_present(rows):
    groups = {group for row in rows for group in row.selection_groups.split(";") if group}
    expected = {
        CAPACITY_TOP_GROUP,
        APERTURE_FRONTIER_GROUP,
        "near_zero_margin_200",
        "orbit_diversity_400",
        "hash_control_200",
    }
    missing = expected - groups
    return check_bool(
        "b8_aperture_orbit_selection_groups_present",
        not missing,
        total=len(expected),
        failed=len(missing),
    )


def check_hash_and_summary_stability(audit_rows, summary_rows):
    audit_parents = {row.parent_residue for row in audit_rows}
    all_summary = {
        row.metric: row.value
        for row in summary_rows
        if row.selection_group == "all"
    }
    passed = (
        len(audit_parents) == len(audit_rows)
        and all_summary.get("selected_parent_count") == str(len(audit_rows))
        and int(all_summary.get("probe_row_count", "0")) == len(audit_rows) * 19
    )
    return check_bool(
        "b8_aperture_orbit_summary_matches_audit",
        passed,
        total=1,
        failed=0 if passed else 1,
    )


def check_b8_close_rows_are_independent_births(probe_rows, birth_audit_rows):
    close_rows = [row for row in probe_rows if row.is_close]
    close_keys = {(row.parent_residue, row.child_residue) for row in close_rows}
    audit_keys = {(row.parent_residue, row.child_residue) for row in birth_audit_rows}
    failed = (
        abs(len(close_rows) - len(birth_audit_rows))
        + len(close_keys.symmetric_difference(audit_keys))
        + sum(not row.exact_b8_birth for row in birth_audit_rows)
        + sum(row.parent_gap_count_exact <= 0 for row in birth_audit_rows)
        + sum(row.child_gap_count_exact != 0 for row in birth_audit_rows)
    )
    return check_bool(
        "b8_aperture_orbit_close_rows_are_independent_births",
        failed == 0,
        total=len(close_rows),
        failed=failed,
    )


def check_figure_exists(path: Path):
    passed = path.exists() and path.stat().st_size > 1000
    return check_bool(
        f"{path.stem}_exists",
        passed,
        total=1,
        failed=0 if passed else 1,
    )


def _candidate_stub_from_probe_rows(parent: int, rows):
    first = rows[0]
    best = max(rows, key=lambda row: (Fraction(row.phase_margin), -row.lift_remainder))
    labels = Counter(row.transition_label for row in rows)
    positive = sum(Fraction(row.phase_margin) > 0 for row in rows)

    from v2_5_b8_aperture_orbit_probe import B8ParentCandidate

    return B8ParentCandidate(
        parent_residue=parent,
        parent_component_count=first.parent_component_count,
        parent_residual_measure=first.parent_residual_measure,
        parent_max_component_width=first.parent_max_component_width,
        best_lift_remainder=best.lift_remainder,
        best_child_residue=best.child_residue,
        best_phase_margin=best.phase_margin,
        best_aperture_tension=best.aperture_tension,
        best_transition_label=best.transition_label,
        trim_lift_count=labels["trim"],
        miss_lift_count=labels["miss"],
        close_lift_count=labels["close"],
        positive_margin_lift_count=positive,
        parent_mod210=first.parent_mod210,
        reflection_orbit=first.reflection_orbit,
        width_bucket="recomputed_probe_stub",
        hash_score="recomputed_probe_stub",
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
