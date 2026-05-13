#!/usr/bin/env python3
"""Verify source-only PRC v2.5 feature ablation diagnostics."""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

from v2_5_feature_ablation import (
    DEFAULT_FEATURE_ABLATION_CSV,
    DEFAULT_FEATURE_ABLATION_FIGURE,
    build_feature_ablation_rows,
    feature_ablation_signature,
    read_feature_ablation_csv,
    write_feature_ablation_artifacts,
)
from v2_5_residual_dynamics import read_residual_state_transition_csv

DEFAULT_OUT = (
    Path(tempfile.gettempdir()) / "prc_v2_5_feature_ablation_verification_v0_1.csv"
)
EXPECTED_FEATURE_SETS = {
    "width only",
    "capacity only",
    "phase margin only",
    "state features",
    "transition grammar",
    "arithmetic strata",
    "state + grammar",
    "state + grammar + phase margin",
    "state + grammar + phase margin + arithmetic",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.5 feature ablation diagnostics.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument(
        "--update-data",
        action="store_true",
        help="regenerate committed source-only v2.5 feature ablation CSV/figure",
    )
    args = parser.parse_args()

    if args.update_data:
        write_feature_ablation_artifacts()

    rows = read_feature_ablation_csv(DEFAULT_FEATURE_ABLATION_CSV)
    checks = verification_rows(rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_5_feature_ablation: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(rows) -> list[dict[str, str]]:
    transition_rows = read_residual_state_transition_csv()
    recomputed_rows = build_feature_ablation_rows(transition_rows)
    all_scope = {row.feature_set: row for row in rows if row.scope == "all"}
    return [
        compare_recomputed_rows(rows, recomputed_rows),
        check_bool(
            "feature_ablation_expected_feature_sets",
            set(all_scope) == EXPECTED_FEATURE_SETS,
            total=len(EXPECTED_FEATURE_SETS),
            failed=len(EXPECTED_FEATURE_SETS.symmetric_difference(set(all_scope))),
        ),
        check_bool(
            "feature_ablation_phase_margin_beats_width_capacity",
            all_scope["phase margin only"].top_k_hit_rate
            >= all_scope["width only"].top_k_hit_rate
            and all_scope["phase margin only"].top_k_hit_rate
            >= all_scope["capacity only"].top_k_hit_rate,
            total=3,
            failed=0
            if all_scope["phase margin only"].top_k_hit_rate
            >= all_scope["width only"].top_k_hit_rate
            and all_scope["phase margin only"].top_k_hit_rate
            >= all_scope["capacity only"].top_k_hit_rate
            else 1,
        ),
        check_bool(
            "feature_ablation_has_scope_rows",
            len({row.scope for row in rows}) >= 4,
            total=len(rows),
            failed=0 if len({row.scope for row in rows}) >= 4 else 1,
        ),
        check_figure_exists(DEFAULT_FEATURE_ABLATION_FIGURE),
    ]


def compare_recomputed_rows(committed_rows, recomputed_rows) -> dict[str, str]:
    committed = [feature_ablation_signature(row) for row in committed_rows]
    recomputed = [feature_ablation_signature(row) for row in recomputed_rows]
    mismatches = sum(left != right for left, right in zip(committed, recomputed))
    mismatches += abs(len(committed) - len(recomputed))
    return check_bool(
        "feature_ablation_rows_match_recomputed",
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
