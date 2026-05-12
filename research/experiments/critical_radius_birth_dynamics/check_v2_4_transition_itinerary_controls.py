#!/usr/bin/env python3
"""Verify source-only PRC v2.4 transition itinerary controls."""

from __future__ import annotations

import argparse
import csv
import tempfile
from collections import Counter
from pathlib import Path

from v2_4_nonbirth_controls import (
    DEFAULT_TRANSITION_ITINERARY_CONTROLS_CSV,
    TransitionItineraryControlRow,
    build_transition_itinerary_control_rows,
    read_transition_itinerary_control_csv,
    row_signature,
    write_dataclass_csv,
)

DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_4_transition_itinerary_controls_verification_v0_1.csv"
)
EXPECTED_SCOPE_COUNTS = {
    "B5_birth_parent_siblings": 154,
    "B6_birth_parent_siblings": 546,
    "B7_birth_parent_siblings": 12138,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.4 transition itinerary controls.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument(
        "--update-data",
        action="store_true",
        help="regenerate committed source-only itinerary control CSV",
    )
    args = parser.parse_args()

    if args.update_data:
        write_dataclass_csv(
            build_transition_itinerary_control_rows(),
            DEFAULT_TRANSITION_ITINERARY_CONTROLS_CSV,
            TransitionItineraryControlRow,
        )

    rows = read_transition_itinerary_control_csv(
        DEFAULT_TRANSITION_ITINERARY_CONTROLS_CSV
    )
    checks = verification_rows(rows, build_transition_itinerary_control_rows())
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_4_transition_itinerary_controls: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(committed_rows, recomputed_rows):
    by_scope = Counter(row.scope for row in committed_rows)
    return [
        compare_recomputed_rows(committed_rows, recomputed_rows),
        check_bool(
            "itinerary_control_scope_counts",
            all(by_scope[scope] == count for scope, count in EXPECTED_SCOPE_COUNTS.items()),
            total=sum(EXPECTED_SCOPE_COUNTS.values()),
            failed=sum(
                abs(by_scope[scope] - count)
                for scope, count in EXPECTED_SCOPE_COUNTS.items()
            ),
        ),
        check_bool(
            "itinerary_control_birth_and_nonbirth_rows",
            sum(row.is_birth for row in committed_rows) == 770
            and sum(not row.is_birth for row in committed_rows) == 12068,
            total=len(committed_rows),
            failed=0
            if sum(row.is_birth for row in committed_rows) == 770
            and sum(not row.is_birth for row in committed_rows) == 12068
            else 1,
        ),
        check_bool(
            "itinerary_control_close_equals_birth",
            all(row.is_close == row.is_birth for row in committed_rows),
            total=len(committed_rows),
            failed=sum(row.is_close != row.is_birth for row in committed_rows),
        ),
        check_bool(
            "itinerary_control_has_multiple_nonbirth_sequences",
            len({row.transition_sequence for row in committed_rows if not row.is_birth})
            > 10,
            total=1,
            failed=0
            if len({row.transition_sequence for row in committed_rows if not row.is_birth})
            > 10
            else 1,
        ),
    ]


def compare_recomputed_rows(committed_rows, recomputed_rows):
    committed = [row_signature(row) for row in committed_rows]
    recomputed = [row_signature(row) for row in recomputed_rows]
    mismatches = sum(left != right for left, right in zip(committed, recomputed))
    mismatches += abs(len(committed) - len(recomputed))
    return check_bool(
        "itinerary_control_rows_match_recomputed",
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
