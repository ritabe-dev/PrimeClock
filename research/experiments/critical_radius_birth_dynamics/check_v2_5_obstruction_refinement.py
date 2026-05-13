#!/usr/bin/env python3
"""Verify source-only PRC v2.5 refined obstruction diagnostics."""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

from v2_5_obstruction_refinement import (
    DEFAULT_OBSTRUCTION_BUCKET_SUMMARY_CSV,
    DEFAULT_REFINED_OBSTRUCTION_CLASSES_CSV,
    OBSTRUCTION_NONE,
    build_obstruction_bucket_summary_rows,
    build_refined_obstruction_rows,
    obstruction_refinement_signature,
    read_obstruction_bucket_summary_csv,
    read_refined_obstruction_csv,
    write_obstruction_refinement_artifacts,
)
from v2_5_residual_dynamics import read_residual_state_transition_csv

DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_5_obstruction_refinement_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.5 refined obstruction diagnostics.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument("--update-data", action="store_true")
    args = parser.parse_args()

    if args.update_data:
        write_obstruction_refinement_artifacts()

    rows = read_refined_obstruction_csv(DEFAULT_REFINED_OBSTRUCTION_CLASSES_CSV)
    summary_rows = read_obstruction_bucket_summary_csv(DEFAULT_OBSTRUCTION_BUCKET_SUMMARY_CSV)
    checks = verification_rows(rows, summary_rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_5_obstruction_refinement: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(rows, summary_rows) -> list[dict[str, str]]:
    transition_rows = read_residual_state_transition_csv()
    nonclose_rows = [row for row in rows if row.refined_obstruction != OBSTRUCTION_NONE]
    classified = [
        row for row in nonclose_rows if row.refined_obstruction != "unclassified"
    ]
    return [
        compare_recomputed_rows(
            "refined_obstruction_rows_match_recomputed",
            rows,
            build_refined_obstruction_rows(transition_rows=transition_rows),
        ),
        compare_recomputed_rows(
            "obstruction_bucket_summary_rows_match_recomputed",
            summary_rows,
            build_obstruction_bucket_summary_rows(rows),
        ),
        check_bool(
            "refined_obstruction_close_rows_clean",
            all(row.refined_obstruction == OBSTRUCTION_NONE for row in rows if row.lineage_role == "close"),
            total=sum(row.lineage_role == "close" for row in rows),
            failed=sum(
                row.refined_obstruction != OBSTRUCTION_NONE
                for row in rows
                if row.lineage_role == "close"
            ),
        ),
        check_bool(
            "refined_obstruction_coverage_above_70_percent",
            len(classified) * 10 >= len(nonclose_rows) * 7,
            total=len(nonclose_rows),
            failed=max(len(nonclose_rows) - len(classified), 0),
        ),
        check_bool(
            "refined_obstruction_uses_multiple_buckets",
            len({row.refined_obstruction for row in nonclose_rows}) >= 3,
            total=len(nonclose_rows),
            failed=0 if len({row.refined_obstruction for row in nonclose_rows}) >= 3 else 1,
        ),
    ]


def compare_recomputed_rows(name: str, committed_rows, recomputed_rows):
    committed = [obstruction_refinement_signature(row) for row in committed_rows]
    recomputed = [obstruction_refinement_signature(row) for row in recomputed_rows]
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
