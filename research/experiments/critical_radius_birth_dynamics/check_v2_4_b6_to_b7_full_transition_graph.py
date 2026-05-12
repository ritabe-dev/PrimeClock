#!/usr/bin/env python3
"""Verify the source-only PRC v2.4 full B6->B7 transition graph."""

from __future__ import annotations

import argparse
import csv
import tempfile
from collections import Counter
from pathlib import Path

from tools import birth_dynamics_rows
from v2_4_transition_pilot import (
    DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV,
    TRANSITION_CLOSE,
    TRANSITION_MISS,
    TRANSITION_PARTIAL_CLOSE,
    TRANSITION_SPLIT,
    TRANSITION_TRIM,
    b6_to_b7_full_transition_rows,
    canonical_transition_summary,
    classify_canonical_transition,
    component_transition_stats,
    raw_gap_counts_match_intervals,
    read_b5_gap_close_transition_pilot_csv,
    transition_row_geometry_signature,
    transition_row_key,
    write_transition_rows_csv,
)

DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_4_b6_to_b7_full_transition_graph_verification_v0_1.csv"
)
EXPECTED_PARENT_COUNT = 29520
EXPECTED_ROW_COUNT = 501840
EXPECTED_LIFTS_PER_PARENT = 17


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.4 B6->B7 full transition graph.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument(
        "--update-data",
        action="store_true",
        help="regenerate the committed source-only B6->B7 full graph CSV",
    )
    args = parser.parse_args()

    birth_rows = birth_dynamics_rows(min_k=7, max_k=7)
    if args.update_data:
        write_transition_rows_csv(
            b6_to_b7_full_transition_rows(birth_rows),
            DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV,
        )

    committed_rows = read_b5_gap_close_transition_pilot_csv(
        DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV
    )
    recomputed_rows = b6_to_b7_full_transition_rows(birth_rows)
    checks = verification_rows(
        committed_rows=committed_rows,
        recomputed_rows=recomputed_rows,
        birth_rows=birth_rows,
    )
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_4_b6_to_b7_full_transition_graph: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(*, committed_rows, recomputed_rows, birth_rows):
    taxonomy = canonical_transition_summary(committed_rows)
    close_rows = [
        row
        for row in committed_rows
        if classify_canonical_transition(row) == TRANSITION_CLOSE
    ]
    birth_keys = {
        (row.parent_residue_mod_previous, row.new_prime_remainder, row.residue)
        for row in birth_rows
    }
    close_keys = {
        (row.parent_residue, row.new_prime_remainder, row.child_residue)
        for row in close_rows
    }
    return [
        compare_recomputed_rows(
            "b6_to_b7_committed_rows_match_recomputed_geometry",
            committed_rows,
            recomputed_rows,
        ),
        check_bool(
            "b6_to_b7_row_count",
            len(committed_rows) == EXPECTED_ROW_COUNT
            and len({row.parent_residue for row in committed_rows})
            == EXPECTED_PARENT_COUNT
            and all_parent_lift_counts(committed_rows, EXPECTED_LIFTS_PER_PARENT),
            total=EXPECTED_PARENT_COUNT,
            failed=parent_lift_failures(committed_rows, EXPECTED_LIFTS_PER_PARENT)
            + (0 if len(committed_rows) == EXPECTED_ROW_COUNT else 1),
        ),
        check_bool(
            "b6_to_b7_close_matches_b7_births",
            close_keys == birth_keys and all(row.is_b5_birth for row in close_rows),
            total=len(birth_keys),
            failed=len(close_keys.symmetric_difference(birth_keys))
            + sum(not row.is_b5_birth for row in close_rows),
        ),
        check_bool(
            "b6_to_b7_nonbirth_close_count",
            sum(not row.is_b5_birth for row in close_rows) == 0,
            total=len(close_rows),
            failed=sum(not row.is_b5_birth for row in close_rows),
        ),
        check_bool(
            "b6_to_b7_primary_taxonomy_is_complete",
            sum(taxonomy[label] for label in taxonomy_labels()) == EXPECTED_ROW_COUNT
            and taxonomy[TRANSITION_CLOSE] == len(birth_rows),
            total=EXPECTED_ROW_COUNT,
            failed=abs(
                EXPECTED_ROW_COUNT
                - sum(taxonomy[label] for label in taxonomy_labels())
            )
            + abs(taxonomy[TRANSITION_CLOSE] - len(birth_rows)),
        ),
        check_bool(
            "b6_to_b7_component_delta_is_consistent",
            sum(component_delta_summary(committed_rows).values()) == EXPECTED_ROW_COUNT,
            total=EXPECTED_ROW_COUNT,
            failed=abs(
                EXPECTED_ROW_COUNT
                - sum(component_delta_summary(committed_rows).values())
            ),
        ),
        check_bool(
            "b6_to_b7_raw_counts_match_recomputed_components",
            all(raw_gap_counts_match_intervals(row) for row in committed_rows),
            total=len(committed_rows),
            failed=sum(
                not raw_gap_counts_match_intervals(row) for row in committed_rows
            ),
        ),
    ]


def compare_recomputed_rows(name: str, committed_rows, recomputed_rows):
    committed_by_key = {transition_row_key(row): row for row in committed_rows}
    recomputed_by_key = {transition_row_key(row): row for row in recomputed_rows}
    missing_keys = set(committed_by_key).symmetric_difference(recomputed_by_key)
    mismatches = [
        key
        for key in sorted(set(committed_by_key) & set(recomputed_by_key))
        if transition_row_geometry_signature(committed_by_key[key])
        != transition_row_geometry_signature(recomputed_by_key[key])
    ]
    return check_bool(
        name,
        not missing_keys and not mismatches,
        total=max(len(committed_rows), len(recomputed_rows)),
        failed=len(missing_keys) + len(mismatches),
    )


def all_parent_lift_counts(rows, expected_lifts: int) -> bool:
    rows_by_parent: dict[int, list[object]] = {}
    for row in rows:
        rows_by_parent.setdefault(row.parent_residue, []).append(row)
    return all(len(group) == expected_lifts for group in rows_by_parent.values())


def parent_lift_failures(rows, expected_lifts: int) -> int:
    rows_by_parent: dict[int, list[object]] = {}
    for row in rows:
        rows_by_parent.setdefault(row.parent_residue, []).append(row)
    return sum(len(group) != expected_lifts for group in rows_by_parent.values())


def component_delta_summary(rows) -> Counter[tuple[str, int]]:
    return Counter(
        (classify_canonical_transition(row), component_transition_stats(row).component_delta)
        for row in rows
    )


def taxonomy_labels() -> tuple[str, ...]:
    return (
        TRANSITION_MISS,
        TRANSITION_TRIM,
        TRANSITION_SPLIT,
        TRANSITION_PARTIAL_CLOSE,
        TRANSITION_CLOSE,
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
