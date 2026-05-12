#!/usr/bin/env python3
"""Verify source-only PRC v2.4 transition graph probes."""

from __future__ import annotations

import argparse
import csv
import tempfile
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

from tools import BirthDynamicsRow, birth_dynamics_rows
from v2_4_transition_pilot import (
    DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV,
    DEFAULT_B7_BIRTH_PARENT_TRANSITION_PROBE_CSV,
    TRANSITION_CLOSE,
    TRANSITION_MISS,
    TRANSITION_PARTIAL_CLOSE,
    TRANSITION_SPLIT,
    TRANSITION_TRIM,
    TransitionProbeRow,
    b5_to_b6_full_transition_rows,
    b7_birth_parent_transition_probe_rows,
    canonical_transition_summary,
    classify_canonical_transition,
    component_transition_stats,
    raw_gap_counts_match_intervals,
    read_b5_gap_close_transition_pilot_csv,
    transition_row_geometry_signature,
    transition_row_key,
)


DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_4_transition_graph_probes_verification_v0_1.csv"
)
B7_FULL_GRAPH_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "prc_v2_4_b6_to_b7_full_transition_graph_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.4 transition graph probes.",
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_OUT,
        type=Path,
        help="verification summary CSV path",
    )
    args = parser.parse_args()

    b6_birth_rows = birth_dynamics_rows(min_k=6, max_k=6)
    b7_birth_rows = birth_dynamics_rows(min_k=7, max_k=7)
    b5_to_b6_rows = read_b5_gap_close_transition_pilot_csv(
        DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV
    )
    b7_probe_rows = read_b5_gap_close_transition_pilot_csv(
        DEFAULT_B7_BIRTH_PARENT_TRANSITION_PROBE_CSV
    )
    checks = verification_rows(
        b5_to_b6_rows=b5_to_b6_rows,
        b6_birth_rows=b6_birth_rows,
        b7_probe_rows=b7_probe_rows,
        b7_birth_rows=b7_birth_rows,
    )
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_4_transition_graph_probes: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(
    *,
    b5_to_b6_rows: list[TransitionProbeRow],
    b6_birth_rows: Sequence[BirthDynamicsRow],
    b7_probe_rows: list[TransitionProbeRow],
    b7_birth_rows: Sequence[BirthDynamicsRow],
) -> list[dict[str, str]]:
    recomputed_b5_to_b6 = b5_to_b6_full_transition_rows(b6_birth_rows)
    recomputed_b7_probe = b7_birth_parent_transition_probe_rows(b7_birth_rows)
    b5_to_b6_taxonomy = canonical_transition_summary(b5_to_b6_rows)
    b7_taxonomy = canonical_transition_summary(b7_probe_rows)
    b5_to_b6_delta = component_delta_summary(b5_to_b6_rows)
    b7_delta = component_delta_summary(b7_probe_rows)
    b6_birth_keys = birth_keys(b6_birth_rows, k=6)
    b7_birth_keys = birth_keys(b7_birth_rows, k=7)
    b5_to_b6_close_keys = close_keys(b5_to_b6_rows)
    b7_close_keys = close_keys(b7_probe_rows)
    genealogy_flow = b5_label_to_b6_flow(b5_to_b6_rows)

    return [
        compare_recomputed_rows(
            "b5_to_b6_committed_rows_match_recomputed_geometry",
            b5_to_b6_rows,
            recomputed_b5_to_b6,
        ),
        check_bool(
            "b5_to_b6_row_count",
            len(b5_to_b6_rows) == 29562
            and len({row.parent_residue for row in b5_to_b6_rows}) == 2274
            and all_parent_lift_counts(b5_to_b6_rows, 13),
            total=2274,
            failed=parent_lift_failures(b5_to_b6_rows, 13)
            + (0 if len(b5_to_b6_rows) == 29562 else 1),
        ),
        check_bool(
            "b5_to_b6_primary_taxonomy_counts",
            b5_to_b6_taxonomy[TRANSITION_MISS] == 20442
            and b5_to_b6_taxonomy[TRANSITION_TRIM] == 5610
            and b5_to_b6_taxonomy[TRANSITION_SPLIT] == 3090
            and b5_to_b6_taxonomy[TRANSITION_PARTIAL_CLOSE] == 378
            and b5_to_b6_taxonomy[TRANSITION_CLOSE] == 42,
            total=5,
            failed=(0 if b5_to_b6_taxonomy[TRANSITION_MISS] == 20442 else 1)
            + (0 if b5_to_b6_taxonomy[TRANSITION_TRIM] == 5610 else 1)
            + (0 if b5_to_b6_taxonomy[TRANSITION_SPLIT] == 3090 else 1)
            + (0 if b5_to_b6_taxonomy[TRANSITION_PARTIAL_CLOSE] == 378 else 1)
            + (0 if b5_to_b6_taxonomy[TRANSITION_CLOSE] == 42 else 1),
        ),
        check_bool(
            "b5_to_b6_component_delta_breakdown",
            b5_to_b6_delta[(TRANSITION_MISS, 0)] == 20442
            and b5_to_b6_delta[(TRANSITION_TRIM, 0)] == 5610
            and b5_to_b6_delta[(TRANSITION_SPLIT, 1)] == 3090
            and b5_to_b6_delta[(TRANSITION_PARTIAL_CLOSE, -1)] == 378
            and b5_to_b6_delta[(TRANSITION_CLOSE, -1)] == 42,
            total=5,
            failed=sum(
                [
                    b5_to_b6_delta[(TRANSITION_MISS, 0)] != 20442,
                    b5_to_b6_delta[(TRANSITION_TRIM, 0)] != 5610,
                    b5_to_b6_delta[(TRANSITION_SPLIT, 1)] != 3090,
                    b5_to_b6_delta[(TRANSITION_PARTIAL_CLOSE, -1)] != 378,
                    b5_to_b6_delta[(TRANSITION_CLOSE, -1)] != 42,
                ]
            ),
        ),
        check_bool(
            "b5_to_b6_close_matches_b6_births",
            b5_to_b6_close_keys == b6_birth_keys
            and all(row.is_b5_birth for row in b5_to_b6_rows if is_close(row)),
            total=len(b6_birth_keys),
            failed=len(b5_to_b6_close_keys.symmetric_difference(b6_birth_keys))
            + sum(not row.is_b5_birth for row in b5_to_b6_rows if is_close(row)),
        ),
        check_bool(
            "b5_to_b6_genealogy_flow_close_sources",
            genealogy_flow[(TRANSITION_MISS, 0, TRANSITION_CLOSE, -1, True)] == 18
            and genealogy_flow[(TRANSITION_TRIM, 0, TRANSITION_CLOSE, -1, True)]
            == 24,
            total=2,
            failed=(
                0
                if genealogy_flow[(TRANSITION_MISS, 0, TRANSITION_CLOSE, -1, True)]
                == 18
                else 1
            )
            + (
                0
                if genealogy_flow[
                    (TRANSITION_TRIM, 0, TRANSITION_CLOSE, -1, True)
                ]
                == 24
                else 1
            ),
        ),
        check_bool(
            "b5_to_b6_raw_counts_match_recomputed_components",
            all(raw_gap_counts_match_intervals(row) for row in b5_to_b6_rows),
            total=len(b5_to_b6_rows),
            failed=sum(
                not raw_gap_counts_match_intervals(row) for row in b5_to_b6_rows
            ),
        ),
        compare_recomputed_rows(
            "b7_probe_committed_rows_match_recomputed_geometry",
            b7_probe_rows,
            recomputed_b7_probe,
        ),
        check_bool(
            "b7_probe_row_count",
            len(b7_probe_rows) == 12138
            and len({row.parent_residue for row in b7_probe_rows}) == 714
            and all_parent_lift_counts(b7_probe_rows, 17),
            total=714,
            failed=parent_lift_failures(b7_probe_rows, 17)
            + (0 if len(b7_probe_rows) == 12138 else 1),
        ),
        check_bool(
            "b7_probe_primary_taxonomy_counts",
            b7_taxonomy[TRANSITION_MISS] == 11424
            and b7_taxonomy[TRANSITION_TRIM] == 0
            and b7_taxonomy[TRANSITION_SPLIT] == 0
            and b7_taxonomy[TRANSITION_PARTIAL_CLOSE] == 0
            and b7_taxonomy[TRANSITION_CLOSE] == 714,
            total=5,
            failed=(0 if b7_taxonomy[TRANSITION_MISS] == 11424 else 1)
            + (0 if b7_taxonomy[TRANSITION_TRIM] == 0 else 1)
            + (0 if b7_taxonomy[TRANSITION_SPLIT] == 0 else 1)
            + (0 if b7_taxonomy[TRANSITION_PARTIAL_CLOSE] == 0 else 1)
            + (0 if b7_taxonomy[TRANSITION_CLOSE] == 714 else 1),
        ),
        check_bool(
            "b7_probe_component_delta_breakdown",
            b7_delta[(TRANSITION_MISS, 0)] == 11424
            and b7_delta[(TRANSITION_CLOSE, -1)] == 714,
            total=2,
            failed=(0 if b7_delta[(TRANSITION_MISS, 0)] == 11424 else 1)
            + (0 if b7_delta[(TRANSITION_CLOSE, -1)] == 714 else 1),
        ),
        check_bool(
            "b7_probe_close_matches_b7_births",
            b7_close_keys == b7_birth_keys
            and all(row.is_b5_birth for row in b7_probe_rows if is_close(row)),
            total=len(b7_birth_keys),
            failed=len(b7_close_keys.symmetric_difference(b7_birth_keys))
            + sum(not row.is_b5_birth for row in b7_probe_rows if is_close(row)),
        ),
        check_bool(
            "b7_full_graph_available_as_source_only",
            B7_FULL_GRAPH_PATH.exists(),
            total=1,
            failed=0 if B7_FULL_GRAPH_PATH.exists() else 1,
        ),
    ]


def compare_recomputed_rows(
    name: str,
    committed_rows: list[TransitionProbeRow],
    recomputed_rows: list[TransitionProbeRow],
) -> dict[str, str]:
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


def component_delta_summary(rows: Iterable[TransitionProbeRow]) -> Counter[tuple[str, int]]:
    return Counter(
        (classify_canonical_transition(row), component_transition_stats(row).component_delta)
        for row in rows
    )


def close_keys(rows: Iterable[TransitionProbeRow]) -> set[tuple[int, int, int]]:
    return {
        (row.parent_residue, row.new_prime_remainder, row.child_residue)
        for row in rows
        if is_close(row)
    }


def birth_keys(rows: Sequence[BirthDynamicsRow], *, k: int) -> set[tuple[int, int, int]]:
    return {
        (row.parent_residue_mod_previous, row.new_prime_remainder, row.residue)
        for row in rows
        if row.k == k
    }


def is_close(row: TransitionProbeRow) -> bool:
    return classify_canonical_transition(row) == TRANSITION_CLOSE


def all_parent_lift_counts(rows: list[TransitionProbeRow], expected_lifts: int) -> bool:
    rows_by_parent: dict[int, list[TransitionProbeRow]] = {}
    for row in rows:
        rows_by_parent.setdefault(row.parent_residue, []).append(row)
    return all(len(group) == expected_lifts for group in rows_by_parent.values())


def parent_lift_failures(rows: list[TransitionProbeRow], expected_lifts: int) -> int:
    rows_by_parent: dict[int, list[TransitionProbeRow]] = {}
    for row in rows:
        rows_by_parent.setdefault(row.parent_residue, []).append(row)
    return sum(len(group) != expected_lifts for group in rows_by_parent.values())


def b5_label_to_b6_flow(
    b5_to_b6_rows: Iterable[TransitionProbeRow],
) -> Counter[tuple[str, int, str, int, bool]]:
    b5_rows = {
        row.child_residue: row
        for row in read_b5_gap_close_transition_pilot_csv()
    }
    flow: Counter[tuple[str, int, str, int, bool]] = Counter()
    for row in b5_to_b6_rows:
        parent_row = b5_rows[row.parent_residue]
        parent_stats = component_transition_stats(parent_row)
        row_stats = component_transition_stats(row)
        flow[
            (
                classify_canonical_transition(parent_row),
                parent_stats.component_delta,
                classify_canonical_transition(row),
                row_stats.component_delta,
                row.is_b5_birth,
            )
        ] += 1
    return flow


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
