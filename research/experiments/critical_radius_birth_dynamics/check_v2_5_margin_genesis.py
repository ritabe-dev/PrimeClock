#!/usr/bin/env python3
"""Verify source-only PRC v2.5 margin genesis diagnostics."""

from __future__ import annotations

import argparse
import csv
import tempfile
from fractions import Fraction
from pathlib import Path

from v2_5_margin_genesis import (
    DEFAULT_CLOSE_NEARMISS_COUNTERFACTUAL_CSV,
    DEFAULT_MARGIN_GENESIS_FIGURE,
    DEFAULT_PREFIX_MARGIN_GENESIS_CSV,
    build_close_nearmiss_counterfactual_rows,
    build_prefix_margin_genesis_rows,
    margin_genesis_signature,
    read_close_nearmiss_counterfactual_csv,
    read_prefix_margin_genesis_csv,
    write_margin_genesis_artifacts,
)
from v2_5_residual_dynamics import read_residual_state_transition_csv

DEFAULT_OUT = (
    Path(tempfile.gettempdir()) / "prc_v2_5_margin_genesis_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.5 margin genesis diagnostics.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument("--update-data", action="store_true")
    args = parser.parse_args()

    if args.update_data:
        write_margin_genesis_artifacts()

    rows = read_prefix_margin_genesis_csv(DEFAULT_PREFIX_MARGIN_GENESIS_CSV)
    counterfactual = read_close_nearmiss_counterfactual_csv(
        DEFAULT_CLOSE_NEARMISS_COUNTERFACTUAL_CSV
    )
    checks = verification_rows(rows, counterfactual)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_5_margin_genesis: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(rows, counterfactual) -> list[dict[str, str]]:
    transition_rows = read_residual_state_transition_csv()
    return [
        compare_recomputed_rows(
            "prefix_margin_genesis_rows_match_recomputed",
            rows,
            build_prefix_margin_genesis_rows(transition_rows=transition_rows),
        ),
        compare_recomputed_rows(
            "close_nearmiss_counterfactual_rows_match_recomputed",
            counterfactual,
            build_close_nearmiss_counterfactual_rows(transition_rows=transition_rows),
        ),
        check_bool(
            "margin_genesis_close_rows_have_positive_margin",
            all(Fraction(row.actual_phase_margin) > 0 for row in rows if row.is_close),
            total=sum(row.is_close for row in rows),
            failed=sum(Fraction(row.actual_phase_margin) <= 0 for row in rows if row.is_close),
        ),
        check_bool(
            "counterfactual_pairs_share_prefix",
            all(row.prefix_sequence_match and row.prefix_component_delta_match for row in counterfactual),
            total=len(counterfactual),
            failed=sum(
                not (row.prefix_sequence_match and row.prefix_component_delta_match)
                for row in counterfactual
            ),
        ),
        check_bool(
            "counterfactual_close_margin_beats_nearmiss",
            all(Fraction(row.margin_gap) > 0 for row in counterfactual),
            total=len(counterfactual),
            failed=sum(Fraction(row.margin_gap) <= 0 for row in counterfactual),
        ),
        check_figure_exists(DEFAULT_MARGIN_GENESIS_FIGURE),
    ]


def compare_recomputed_rows(name: str, committed_rows, recomputed_rows):
    committed = [margin_genesis_signature(row) for row in committed_rows]
    recomputed = [margin_genesis_signature(row) for row in recomputed_rows]
    mismatches = sum(left != right for left, right in zip(committed, recomputed))
    mismatches += abs(len(committed) - len(recomputed))
    return check_bool(
        name,
        committed == recomputed,
        total=max(len(committed), len(recomputed)),
        failed=mismatches,
    )


def check_figure_exists(path: Path):
    passed = path.exists() and path.stat().st_size > 1000
    return check_bool(
        f"{path.stem}_exists",
        passed,
        total=1,
        failed=0 if passed else 1,
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
