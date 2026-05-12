#!/usr/bin/env python3
"""Verify the source-only PRC v2.4 B6 transition sanity probe."""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path
from typing import Sequence

from tools import BirthDynamicsRow, birth_dynamics_rows
from v2_4_transition_pilot import (
    TRANSITION_CLOSE,
    TRANSITION_MISS,
    TRANSITION_PARTIAL_CLOSE,
    TRANSITION_SPLIT,
    TRANSITION_TRIM,
    TransitionProbeRow,
    b6_birth_parent_transition_probe_rows,
    canonical_transition_summary,
    classify_canonical_transition,
    raw_gap_counts_match_intervals,
)


DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_4_b6_sanity_probe_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the source-only PRC v2.4 B6 transition sanity probe.",
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_OUT,
        type=Path,
        help="verification summary CSV path",
    )
    args = parser.parse_args()

    birth_rows = birth_dynamics_rows(min_k=6, max_k=6)
    probe_rows = b6_birth_parent_transition_probe_rows(birth_rows)
    checks = verification_rows(probe_rows, birth_rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_4_b6_sanity_probe: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(
    probe_rows: list[TransitionProbeRow],
    birth_rows: Sequence[BirthDynamicsRow],
) -> list[dict[str, str]]:
    rows_by_parent: dict[int, list[TransitionProbeRow]] = {}
    for row in probe_rows:
        rows_by_parent.setdefault(row.parent_residue, []).append(row)

    taxonomy_counts = canonical_transition_summary(probe_rows)
    close_rows = [
        row for row in probe_rows if classify_canonical_transition(row) == TRANSITION_CLOSE
    ]
    close_keys = {
        (row.parent_residue, row.new_prime_remainder, row.child_residue)
        for row in close_rows
    }
    birth_keys = {
        (row.parent_residue_mod_previous, row.new_prime_remainder, row.residue)
        for row in birth_rows
        if row.k == 6
    }
    return [
        check_bool(
            "b6_probe_row_count",
            len(probe_rows) == 546,
            total=1,
            failed=0 if len(probe_rows) == 546 else 1,
        ),
        check_bool(
            "b6_probe_parent_lifts",
            len(rows_by_parent) == 42
            and all(len(rows) == 13 for rows in rows_by_parent.values()),
            total=42,
            failed=sum(len(rows) != 13 for rows in rows_by_parent.values())
            + (0 if len(rows_by_parent) == 42 else 1),
        ),
        check_bool(
            "b6_probe_close_matches_births",
            close_keys == birth_keys,
            total=len(birth_keys),
            failed=len(close_keys.symmetric_difference(birth_keys)),
        ),
        check_bool(
            "b6_probe_no_non_birth_close",
            all(row.is_b5_birth for row in close_rows),
            total=len(close_rows),
            failed=sum(not row.is_b5_birth for row in close_rows),
        ),
        check_bool(
            "b6_probe_raw_counts_match_recomputed_components",
            all(raw_gap_counts_match_intervals(row) for row in probe_rows),
            total=len(probe_rows),
            failed=sum(not raw_gap_counts_match_intervals(row) for row in probe_rows),
        ),
        check_bool(
            "b6_probe_primary_taxonomy_counts",
            taxonomy_counts[TRANSITION_MISS] == 504
            and taxonomy_counts[TRANSITION_CLOSE] == 42
            and taxonomy_counts[TRANSITION_TRIM] == 0
            and taxonomy_counts[TRANSITION_SPLIT] == 0
            and taxonomy_counts[TRANSITION_PARTIAL_CLOSE] == 0,
            total=5,
            failed=(0 if taxonomy_counts[TRANSITION_MISS] == 504 else 1)
            + (0 if taxonomy_counts[TRANSITION_CLOSE] == 42 else 1)
            + (0 if taxonomy_counts[TRANSITION_TRIM] == 0 else 1)
            + (0 if taxonomy_counts[TRANSITION_SPLIT] == 0 else 1)
            + (0 if taxonomy_counts[TRANSITION_PARTIAL_CLOSE] == 0 else 1),
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
