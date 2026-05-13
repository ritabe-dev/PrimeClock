#!/usr/bin/env python3
"""Verify source-only PRC v2.5 lineage grammar artifacts."""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

from v2_5_lineage_grammar import (
    DEFAULT_LINEAGE_GRAMMAR_CSV,
    build_lineage_grammar_rows,
    grammar_signature,
    read_lineage_grammar_csv,
    write_lineage_grammar_csv,
)
from v2_5_residual_dynamics import read_residual_state_transition_csv

DEFAULT_OUT = (
    Path(tempfile.gettempdir()) / "prc_v2_5_lineage_grammar_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.5 lineage grammar artifacts.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument(
        "--update-data",
        action="store_true",
        help="regenerate committed source-only v2.5 lineage grammar CSV",
    )
    args = parser.parse_args()

    if args.update_data:
        write_lineage_grammar_csv()

    rows = read_lineage_grammar_csv(DEFAULT_LINEAGE_GRAMMAR_CSV)
    checks = verification_rows(rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_5_lineage_grammar: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(rows) -> list[dict[str, str]]:
    transition_rows = read_residual_state_transition_csv()
    recomputed_rows = build_lineage_grammar_rows(transition_rows)
    roles = {row.lineage_role for row in rows}
    return [
        compare_recomputed_rows(rows, recomputed_rows),
        check_bool(
            "lineage_grammar_close_and_nonclose_roles_present",
            {"close", "nonclose", "near_miss", "capacity_nonclose"}.issubset(roles),
            total=4,
            failed=len({"close", "nonclose", "near_miss", "capacity_nonclose"} - roles),
        ),
        check_bool(
            "lineage_grammar_has_dominant_and_rare_patterns",
            any(row.diagnostic_role == "dominant" for row in rows)
            and any(row.diagnostic_role == "rare" for row in rows),
            total=len(rows),
            failed=0
            if any(row.diagnostic_role == "dominant" for row in rows)
            and any(row.diagnostic_role == "rare" for row in rows)
            else 1,
        ),
        check_bool(
            "lineage_grammar_counts_match_final_lineages",
            sum(row.lineage_count for row in rows)
            == len({row.lineage_id for row in transition_rows}),
            total=len(rows),
            failed=0
            if sum(row.lineage_count for row in rows)
            == len({row.lineage_id for row in transition_rows})
            else 1,
        ),
    ]


def compare_recomputed_rows(committed_rows, recomputed_rows) -> dict[str, str]:
    committed = [grammar_signature(row) for row in committed_rows]
    recomputed = [grammar_signature(row) for row in recomputed_rows]
    mismatches = sum(left != right for left, right in zip(committed, recomputed))
    mismatches += abs(len(committed) - len(recomputed))
    return check_bool(
        "lineage_grammar_rows_match_recomputed",
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
