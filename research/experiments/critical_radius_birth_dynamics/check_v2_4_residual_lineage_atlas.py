#!/usr/bin/env python3
"""Verify source-only PRC v2.4 exact residual lineage atlas artifacts."""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

from v2_4_residual_lineage_atlas import (
    DEFAULT_LINEAGE_BIRTH_VS_NONBIRTH_FIGURE,
    DEFAULT_LINEAGE_CAPACITY_CONTROLS_FIGURE,
    DEFAULT_RESIDUAL_LINEAGE_ATLAS_CSV,
    DEFAULT_RESIDUAL_LINEAGE_ATLAS_SUMMARY_CSV,
    build_residual_lineage_atlas_rows,
    build_residual_lineage_atlas_summary_rows,
    read_residual_lineage_atlas_csv,
    read_residual_lineage_atlas_summary_csv,
    row_signature,
    write_residual_lineage_atlas_artifacts,
)


DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_4_residual_lineage_atlas_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.4 exact residual lineage atlas.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument(
        "--update-data",
        action="store_true",
        help="regenerate committed source-only atlas CSVs and figures",
    )
    args = parser.parse_args()

    if args.update_data:
        write_residual_lineage_atlas_artifacts()

    rows = read_residual_lineage_atlas_csv(DEFAULT_RESIDUAL_LINEAGE_ATLAS_CSV)
    summary_rows = read_residual_lineage_atlas_summary_csv(
        DEFAULT_RESIDUAL_LINEAGE_ATLAS_SUMMARY_CSV
    )
    recomputed_rows = build_residual_lineage_atlas_rows()
    checks = verification_rows(rows, summary_rows, recomputed_rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_4_residual_lineage_atlas: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(rows, summary_rows, recomputed_rows):
    summary = {(row.metric, row.scope): row for row in summary_rows}
    final_rows = [row for row in rows if row.layer_k == _child_k_from_scope(row.scope)]
    sibling_final = [
        row for row in final_rows if row.control_group == "birth_parent_sibling"
    ]
    capacity_final = [
        row for row in final_rows if row.control_group == "capacity_nonclose_control"
    ]
    return [
        compare_recomputed_rows(rows, recomputed_rows),
        compare_recomputed_rows(
            summary_rows,
            build_residual_lineage_atlas_summary_rows(rows),
            name="lineage_atlas_summary_rows_match_recomputed",
        ),
        check_bool(
            "lineage_atlas_birth_and_nonbirth_siblings_present",
            sum(row.is_birth for row in sibling_final) == 770
            and sum(not row.is_birth for row in sibling_final) == 12068,
            total=len(sibling_final),
            failed=0
            if sum(row.is_birth for row in sibling_final) == 770
            and sum(not row.is_birth for row in sibling_final) == 12068
            else 1,
        ),
        check_bool(
            "lineage_atlas_final_close_matches_birth",
            all(row.is_close for row in sibling_final if row.is_birth)
            and all(not row.is_close for row in final_rows if not row.is_birth),
            total=len(final_rows),
            failed=sum(not row.is_close for row in sibling_final if row.is_birth)
            + sum(row.is_close for row in final_rows if not row.is_birth),
        ),
        check_bool(
            "lineage_atlas_capacity_nonclose_controls_present",
            len(capacity_final) == 40498
            and all(row.is_capacity_satisfied for row in capacity_final)
            and all(not row.is_close for row in capacity_final),
            total=40498,
            failed=abs(len(capacity_final) - 40498)
            + sum(not row.is_capacity_satisfied for row in capacity_final)
            + sum(row.is_close for row in capacity_final),
        ),
        check_bool(
            "lineage_atlas_capacity_gate_is_not_sufficient",
            summary[("capacity_gate_close_families", "all")].value == "770"
            and summary[("capacity_gate_nonclose_families", "all")].value == "2430",
            total=2,
            failed=(
                summary[("capacity_gate_close_families", "all")].value != "770"
            )
            + (
                summary[("capacity_gate_nonclose_families", "all")].value != "2430"
            ),
        ),
        check_bool(
            "lineage_atlas_uses_exact_fraction_text",
            all("." not in row.uncovered_measure for row in rows)
            and all("." not in row.component_endpoints for row in rows),
            total=len(rows),
            failed=sum(
                "." in row.uncovered_measure or "." in row.component_endpoints
                for row in rows
            ),
        ),
        check_figure_exists(DEFAULT_LINEAGE_BIRTH_VS_NONBIRTH_FIGURE),
        check_figure_exists(DEFAULT_LINEAGE_CAPACITY_CONTROLS_FIGURE),
    ]


def compare_recomputed_rows(
    committed_rows,
    recomputed_rows,
    *,
    name: str = "lineage_atlas_rows_match_recomputed",
):
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


def _child_k_from_scope(scope: str) -> int:
    if scope.startswith("B5"):
        return 5
    if scope.startswith("B6"):
        return 6
    if scope.startswith("B7"):
        return 7
    raise ValueError(f"unsupported atlas scope: {scope}")


if __name__ == "__main__":
    raise SystemExit(main())
