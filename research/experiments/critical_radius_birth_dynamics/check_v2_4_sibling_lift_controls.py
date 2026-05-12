#!/usr/bin/env python3
"""Verify source-only PRC v2.4 sibling-lift phase controls."""

from __future__ import annotations

import argparse
import csv
import tempfile
from collections import Counter
from pathlib import Path

from v2_4_nonbirth_controls import (
    DEFAULT_SIBLING_LIFT_CONTROLS_CSV,
    build_sibling_lift_phase_control_rows,
    read_sibling_lift_phase_control_csv,
    row_signature,
    write_dataclass_csv,
    SiblingLiftPhaseControlRow,
)

DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_4_sibling_lift_controls_verification_v0_1.csv"
)
EXPECTED_SCOPE_COUNTS = {
    "B4_to_B5_full": 208,
    "B5_to_B6_full": 2274,
    "B6_to_B7_full": 29520,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.4 sibling-lift controls.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument(
        "--update-data",
        action="store_true",
        help="regenerate committed source-only sibling-lift control CSV",
    )
    args = parser.parse_args()

    if args.update_data:
        write_dataclass_csv(
            build_sibling_lift_phase_control_rows(),
            DEFAULT_SIBLING_LIFT_CONTROLS_CSV,
            SiblingLiftPhaseControlRow,
        )

    rows = read_sibling_lift_phase_control_csv(DEFAULT_SIBLING_LIFT_CONTROLS_CSV)
    checks = verification_rows(rows, build_sibling_lift_phase_control_rows())
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_4_sibling_lift_controls: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(committed_rows, recomputed_rows):
    by_scope = Counter(row.scope for row in committed_rows)
    return [
        compare_recomputed_rows(committed_rows, recomputed_rows),
        check_bool(
            "sibling_control_scope_counts",
            all(by_scope[scope] == count for scope, count in EXPECTED_SCOPE_COUNTS.items()),
            total=sum(EXPECTED_SCOPE_COUNTS.values()),
            failed=sum(
                abs(by_scope[scope] - count)
                for scope, count in EXPECTED_SCOPE_COUNTS.items()
            ),
        ),
        check_bool(
            "sibling_control_close_equals_birth",
            all(row.close_lift_count == row.birth_lift_count for row in committed_rows),
            total=len(committed_rows),
            failed=sum(
                row.close_lift_count != row.birth_lift_count for row in committed_rows
            ),
        ),
        check_bool(
            "sibling_control_nonbirth_close_zero",
            all(row.nonbirth_close_count == 0 for row in committed_rows),
            total=len(committed_rows),
            failed=sum(row.nonbirth_close_count != 0 for row in committed_rows),
        ),
        check_bool(
            "sibling_control_has_birth_and_nonbirth_families",
            sum(row.birth_lift_count > 0 for row in committed_rows) == 770
            and sum(row.birth_lift_count == 0 for row in committed_rows) == 31232,
            total=len(committed_rows),
            failed=0
            if sum(row.birth_lift_count > 0 for row in committed_rows) == 770
            and sum(row.birth_lift_count == 0 for row in committed_rows) == 31232
            else 1,
        ),
    ]


def compare_recomputed_rows(committed_rows, recomputed_rows):
    committed = [row_signature(row) for row in committed_rows]
    recomputed = [row_signature(row) for row in recomputed_rows]
    mismatches = sum(left != right for left, right in zip(committed, recomputed))
    mismatches += abs(len(committed) - len(recomputed))
    return check_bool(
        "sibling_control_rows_match_recomputed",
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
