#!/usr/bin/env python3
"""Verify the source-only PRC v2.4 B5 transition pilot.

This checker is intentionally not a candidate or public-release gate. It audits
the first v2.4 research seed against the v2.3 B5 birth dynamics so the research
line can stay separate from v2.3.0 publication artifacts.
"""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path
from typing import Sequence

from tools import (
    BirthDynamicsRow,
    birth_dynamics_rows,
)
from v2_4_transition_pilot import (
    B5GapCloseTransitionPilotRow,
    TRANSITION_CLOSE,
    TRANSITION_PARTIAL_CLOSE,
    b5_gap_close_transition_pilot_summary,
    classify_canonical_transition,
    prime_zero_obstruction_holds,
    raw_gap_counts_match_intervals,
    read_b5_gap_close_transition_pilot_csv,
    recompute_b5_transition_pilot_rows,
    transition_row_geometry_signature,
    transition_row_key,
)


EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_4_b5_transition_pilot_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the source-only PRC v2.4 B5 transition pilot.",
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_OUT,
        type=Path,
        help="verification summary CSV path",
    )
    args = parser.parse_args()

    rows = read_b5_gap_close_transition_pilot_csv()
    birth_rows = birth_dynamics_rows(min_k=5, max_k=5)
    recomputed_rows = recompute_b5_transition_pilot_rows(birth_rows)
    checks = verification_rows(rows, birth_rows, recomputed_rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_4_b5_transition_pilot: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(
    pilot_rows: list[B5GapCloseTransitionPilotRow],
    birth_rows: Sequence[BirthDynamicsRow],
    recomputed_rows: list[B5GapCloseTransitionPilotRow],
) -> list[dict[str, str]]:
    summary = b5_gap_close_transition_pilot_summary(pilot_rows)
    rows_by_parent: dict[int, list[B5GapCloseTransitionPilotRow]] = {}
    for row in pilot_rows:
        rows_by_parent.setdefault(row.parent_residue, []).append(row)

    pilot_birth_keys = {
        (row.parent_residue, row.new_prime_remainder, row.child_residue)
        for row in pilot_rows
        if row.is_b5_birth
    }
    v2_3_birth_keys = {
        (row.parent_residue_mod_previous, row.new_prime_remainder, row.residue)
        for row in birth_rows
    }
    pilot_by_key = {transition_row_key(row): row for row in pilot_rows}
    recomputed_by_key = {transition_row_key(row): row for row in recomputed_rows}
    missing_keys = set(pilot_by_key).symmetric_difference(recomputed_by_key)
    geometry_mismatches = [
        key
        for key in sorted(set(pilot_by_key) & set(recomputed_by_key))
        if transition_row_geometry_signature(pilot_by_key[key])
        != transition_row_geometry_signature(recomputed_by_key[key])
    ]
    canonical_close_rows = [
        row for row in pilot_rows if classify_canonical_transition(row) == TRANSITION_CLOSE
    ]
    canonical_partial_close_rows = [
        row
        for row in pilot_rows
        if classify_canonical_transition(row) == TRANSITION_PARTIAL_CLOSE
    ]
    return [
        check_bool(
            "pilot_recomputed_rows_match_committed_geometry",
            not missing_keys and not geometry_mismatches,
            total=max(len(pilot_rows), len(recomputed_rows)),
            failed=len(missing_keys) + len(geometry_mismatches),
        ),
        check_bool(
            "pilot_raw_counts_match_recomputed_components",
            all(raw_gap_counts_match_intervals(row) for row in pilot_rows),
            total=len(pilot_rows),
            failed=sum(not raw_gap_counts_match_intervals(row) for row in pilot_rows),
        ),
        check_bool(
            "pilot_row_count",
            summary.total_rows == 2288,
            total=1,
            failed=0 if summary.total_rows == 2288 else 1,
        ),
        check_bool(
            "pilot_parent_lifts",
            summary.parent_count == 208
            and all(len(rows) == 11 for rows in rows_by_parent.values()),
            total=208,
            failed=sum(len(rows) != 11 for rows in rows_by_parent.values())
            + (0 if summary.parent_count == 208 else 1),
        ),
        check_bool(
            "pilot_transition_counts",
            summary.close_count == 14 and summary.not_close_count == 2274,
            total=2,
            failed=(0 if summary.close_count == 14 else 1)
            + (0 if summary.not_close_count == 2274 else 1),
        ),
        check_bool(
            "pilot_birth_rows_are_exact_close_rows",
            summary.birth_count == 14
            and len(canonical_close_rows) == 14
            and summary.birth_remaining_zero_count == 14
            and all(row.is_b5_birth for row in canonical_close_rows),
            total=4,
            failed=(0 if summary.birth_count == 14 else 1)
            + (0 if len(canonical_close_rows) == 14 else 1)
            + (0 if summary.birth_remaining_zero_count == 14 else 1)
            + (0 if all(row.is_b5_birth for row in canonical_close_rows) else 1),
        ),
        check_bool(
            "pilot_b5_birth_alignment_with_v2_3_birth_dynamics",
            pilot_birth_keys == v2_3_birth_keys,
            total=len(v2_3_birth_keys),
            failed=len(pilot_birth_keys.symmetric_difference(v2_3_birth_keys)),
        ),
        check_bool(
            "pilot_primary_taxonomy_counts",
            summary.canonical_close_count == 14
            and summary.canonical_partial_close_count == 22
            and summary.canonical_split_count == 258
            and summary.canonical_trim_count == 474
            and summary.canonical_miss_count == 1520,
            total=5,
            failed=(0 if summary.canonical_close_count == 14 else 1)
            + (0 if summary.canonical_partial_close_count == 22 else 1)
            + (0 if summary.canonical_split_count == 258 else 1)
            + (0 if summary.canonical_trim_count == 474 else 1)
            + (0 if summary.canonical_miss_count == 1520 else 1),
        ),
        check_bool(
            "pilot_close_birth_alignment",
            summary.canonical_close_count == summary.birth_count
            and summary.birth_remaining_zero_count == summary.birth_count,
            total=2,
            failed=(0 if summary.canonical_close_count == summary.birth_count else 1)
            + (
                0
                if summary.birth_remaining_zero_count == summary.birth_count
                else 1
            ),
        ),
        check_bool(
            "pilot_partial_close_two_gap_parents",
            all(row.old_gap_count == 2 for row in canonical_partial_close_rows),
            total=len(canonical_partial_close_rows),
            failed=sum(row.old_gap_count != 2 for row in canonical_partial_close_rows),
        ),
        check_bool(
            "pilot_close_reflection_and_aperture_families",
            summary.close_to_zero_reflection_pair_count == 7
            and summary.close_aperture_family_count == 4,
            total=2,
            failed=(0 if summary.close_to_zero_reflection_pair_count == 7 else 1)
            + (0 if summary.close_aperture_family_count == 4 else 1),
        ),
        check_bool(
            "pilot_prime_zero_obstruction_diagnostic",
            prime_zero_obstruction_holds(11, [2, 3, 5, 7])
            and not prime_zero_obstruction_holds(11, [2, 3, 5, 7, 11])
            and not prime_zero_obstruction_holds(12, [2, 3, 5, 7]),
            total=3,
            failed=sum(
                [
                    not prime_zero_obstruction_holds(11, [2, 3, 5, 7]),
                    prime_zero_obstruction_holds(11, [2, 3, 5, 7, 11]),
                    prime_zero_obstruction_holds(12, [2, 3, 5, 7]),
                ]
            ),
        ),
        check_bool(
            "pilot_trim_split_component_delta_breakdown",
            summary.trim_component_delta_zero_count == 474
            and summary.canonical_split_count == 258
            and summary.split_count == 258,
            total=2,
            failed=(0 if summary.trim_component_delta_zero_count == 474 else 1)
            + (
                0
                if summary.canonical_split_count == 258
                and summary.split_count == 258
                else 1
            ),
        ),
    ]


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
