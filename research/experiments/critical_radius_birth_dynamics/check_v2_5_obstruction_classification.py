#!/usr/bin/env python3
"""Verify source-only PRC v2.5 obstruction classification artifacts."""

from __future__ import annotations

import argparse
import csv
import tempfile
from collections import Counter
from pathlib import Path

from v2_5_obstruction_classification import (
    DEFAULT_OBSTRUCTION_CLASSES_CSV,
    OBSTRUCTION_NONE,
    build_obstruction_class_rows,
    obstruction_signature,
    read_obstruction_class_csv,
    write_obstruction_class_csv,
)
from v2_5_residual_dynamics import read_residual_state_transition_csv

DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_5_obstruction_classification_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.5 obstruction classification.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument(
        "--update-data",
        action="store_true",
        help="regenerate committed source-only v2.5 obstruction CSV",
    )
    args = parser.parse_args()

    if args.update_data:
        write_obstruction_class_csv()

    rows = read_obstruction_class_csv(DEFAULT_OBSTRUCTION_CLASSES_CSV)
    checks = verification_rows(rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_5_obstruction_classification: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(rows) -> list[dict[str, str]]:
    transition_rows = read_residual_state_transition_csv()
    recomputed_rows = build_obstruction_class_rows(transition_rows)
    counts = Counter(row.obstruction_class for row in rows)
    close_rows = [row for row in rows if row.is_close]
    nonclose_rows = [row for row in rows if not row.is_close]
    return [
        compare_recomputed_rows(rows, recomputed_rows),
        check_bool(
            "obstruction_close_rows_have_no_obstruction",
            all(row.obstruction_class == OBSTRUCTION_NONE for row in close_rows),
            total=len(close_rows),
            failed=sum(row.obstruction_class != OBSTRUCTION_NONE for row in close_rows),
        ),
        check_bool(
            "obstruction_nonclose_rows_are_classified",
            all(row.obstruction_class != OBSTRUCTION_NONE for row in nonclose_rows),
            total=len(nonclose_rows),
            failed=sum(row.obstruction_class == OBSTRUCTION_NONE for row in nonclose_rows),
        ),
        check_bool(
            "obstruction_phase_and_near_miss_buckets_present",
            counts["phase_obstruction"] > 0 and counts["near_miss_obstruction"] > 0,
            total=2,
            failed=(counts["phase_obstruction"] == 0)
            + (counts["near_miss_obstruction"] == 0),
        ),
        check_bool(
            "obstruction_rows_match_final_lineages",
            len(rows) == len({row.lineage_id for row in transition_rows}),
            total=len(rows),
            failed=abs(len(rows) - len({row.lineage_id for row in transition_rows})),
        ),
    ]


def compare_recomputed_rows(committed_rows, recomputed_rows) -> dict[str, str]:
    committed = [obstruction_signature(row) for row in committed_rows]
    recomputed = [obstruction_signature(row) for row in recomputed_rows]
    mismatches = sum(left != right for left, right in zip(committed, recomputed))
    mismatches += abs(len(committed) - len(recomputed))
    return check_bool(
        "obstruction_rows_match_recomputed",
        committed == recomputed,
        total=max(len(committed), len(recomputed)),
        failed=mismatches,
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
