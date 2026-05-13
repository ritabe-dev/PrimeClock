#!/usr/bin/env python3
"""Verify source-only PRC v2.5 residual dynamics artifacts."""

from __future__ import annotations

import argparse
import csv
import tempfile
from fractions import Fraction
from pathlib import Path

from v2_5_residual_dynamics import (
    DEFAULT_RESIDUAL_LINEAGE_SUMMARY_CSV,
    DEFAULT_RESIDUAL_STATE_TRANSITIONS_CSV,
    LINEAGE_CAPACITY_NONCLOSE,
    LINEAGE_CLOSE,
    LINEAGE_NEAR_MISS,
    build_residual_lineage_summary_rows,
    build_residual_state_transition_rows,
    read_residual_lineage_summary_csv,
    read_residual_state_transition_csv,
    row_signature,
    write_residual_dynamics_artifacts,
)

DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_5_residual_dynamics_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.5 residual dynamics artifacts.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument(
        "--update-data",
        action="store_true",
        help="regenerate committed source-only v2.5 residual dynamics CSVs",
    )
    args = parser.parse_args()

    if args.update_data:
        write_residual_dynamics_artifacts()

    rows = read_residual_state_transition_csv(DEFAULT_RESIDUAL_STATE_TRANSITIONS_CSV)
    summary_rows = read_residual_lineage_summary_csv(DEFAULT_RESIDUAL_LINEAGE_SUMMARY_CSV)
    checks = verification_rows(rows, summary_rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_5_residual_dynamics: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(rows, summary_rows) -> list[dict[str, str]]:
    recomputed_rows = build_residual_state_transition_rows()
    final_rows = [row for row in rows if row.layer_k == _child_k_from_scope(row.scope)]
    final_row_keys = {(row.lineage_id, row.layer_k) for row in final_rows}
    close_rows = [row for row in final_rows if row.lineage_role == LINEAGE_CLOSE]
    capacity_nonclose = [
        row for row in final_rows if row.lineage_role == LINEAGE_CAPACITY_NONCLOSE
    ]
    near_miss = [row for row in final_rows if row.lineage_role == LINEAGE_NEAR_MISS]
    labels = {"start", "miss", "trim", "split", "partial_close", "close"}
    return [
        compare_recomputed_rows(
            "residual_state_rows_match_recomputed",
            rows,
            recomputed_rows,
        ),
        compare_recomputed_rows(
            "residual_lineage_summary_rows_match_recomputed",
            summary_rows,
            build_residual_lineage_summary_rows(rows),
        ),
        check_bool(
            "residual_dynamics_final_close_count",
            len(close_rows) == 770 and all(row.is_close and row.is_birth for row in close_rows),
            total=770,
            failed=abs(len(close_rows) - 770)
            + sum(not (row.is_close and row.is_birth) for row in close_rows),
        ),
        check_bool(
            "residual_dynamics_capacity_nonclose_present",
            len(capacity_nonclose) > 0
            and all(row.capacity_pass and not row.is_close for row in capacity_nonclose),
            total=len(capacity_nonclose),
            failed=sum(not row.capacity_pass or row.is_close for row in capacity_nonclose),
        ),
        check_bool(
            "residual_dynamics_near_miss_present",
            len(near_miss) > 0 and all(not row.is_close for row in near_miss),
            total=len(near_miss),
            failed=sum(row.is_close for row in near_miss),
        ),
        check_bool(
            "residual_dynamics_exact_fraction_text",
            all("." not in row.total_residual_measure for row in rows)
            and all("." not in row.max_component_width for row in rows)
            and all("." not in row.phase_margin for row in final_rows),
            total=len(rows),
            failed=sum(
                "." in row.total_residual_measure
                or "." in row.max_component_width
                or ("." in row.phase_margin if (row.lineage_id, row.layer_k) in final_row_keys else False)
                for row in rows
            ),
        ),
        check_bool(
            "residual_dynamics_one_primary_label_per_row",
            all(row.transition_label in labels for row in rows),
            total=len(rows),
            failed=sum(row.transition_label not in labels for row in rows),
        ),
        check_bool(
            "residual_dynamics_positive_phase_selects_close",
            all(Fraction(row.phase_margin) > 0 for row in close_rows)
            and all(
                not row.phase_margin or Fraction(row.phase_margin) <= 0
                for row in final_rows
                if not row.is_close
            ),
            total=len(final_rows),
            failed=sum(Fraction(row.phase_margin) <= 0 for row in close_rows)
            + sum(
                bool(row.phase_margin) and Fraction(row.phase_margin) > 0
                for row in final_rows
                if not row.is_close
            ),
        ),
    ]


def compare_recomputed_rows(name: str, committed_rows, recomputed_rows) -> dict[str, str]:
    committed = [row_signature(row) for row in committed_rows]
    recomputed = [row_signature(row) for row in recomputed_rows]
    mismatches = sum(left != right for left, right in zip(committed, recomputed))
    mismatches += abs(len(committed) - len(recomputed))
    return check_bool(
        name,
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


def _child_k_from_scope(scope: str) -> int:
    if scope.startswith("B5"):
        return 5
    if scope.startswith("B6"):
        return 6
    if scope.startswith("B7"):
        return 7
    raise ValueError(f"unsupported scope: {scope}")


if __name__ == "__main__":
    raise SystemExit(main())
