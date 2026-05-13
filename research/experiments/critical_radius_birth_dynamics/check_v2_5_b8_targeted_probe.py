#!/usr/bin/env python3
"""Verify source-only PRC v2.5 B8 high-potential probe."""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

from v2_5_b8_targeted_probe import (
    DEFAULT_B8_HIGH_POTENTIAL_PROBE_CSV,
    DEFAULT_TOP_PARENT_CAP,
    b8_probe_signature,
    build_b8_high_potential_probe_rows,
    read_b8_high_potential_probe_csv,
    write_b8_high_potential_probe_csv,
)

DEFAULT_OUT = (
    Path(tempfile.gettempdir()) / "prc_v2_5_b8_targeted_probe_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.5 B8 high-potential probe.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument("--update-data", action="store_true")
    args = parser.parse_args()

    if args.update_data:
        write_b8_high_potential_probe_csv()

    rows = read_b8_high_potential_probe_csv(DEFAULT_B8_HIGH_POTENTIAL_PROBE_CSV)
    checks = verification_rows(rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_5_b8_targeted_probe: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(rows) -> list[dict[str, str]]:
    recomputed = build_b8_high_potential_probe_rows()
    parent_count = len({row.parent_residue for row in rows})
    return [
        compare_recomputed_rows(rows, recomputed),
        check_bool(
            "b8_probe_parent_cap_respected",
            parent_count <= DEFAULT_TOP_PARENT_CAP,
            total=DEFAULT_TOP_PARENT_CAP,
            failed=max(parent_count - DEFAULT_TOP_PARENT_CAP, 0),
        ),
        check_bool(
            "b8_probe_has_19_lifts_per_parent",
            len(rows) == parent_count * 19,
            total=parent_count * 19,
            failed=abs(len(rows) - parent_count * 19),
        ),
        check_bool(
            "b8_probe_reports_phase_rank",
            all(1 <= row.phase_rank <= 19 for row in rows),
            total=len(rows),
            failed=sum(not (1 <= row.phase_rank <= 19) for row in rows),
        ),
    ]


def compare_recomputed_rows(committed_rows, recomputed_rows):
    committed = [b8_probe_signature(row) for row in committed_rows]
    recomputed = [b8_probe_signature(row) for row in recomputed_rows]
    mismatches = sum(left != right for left, right in zip(committed, recomputed))
    mismatches += abs(len(committed) - len(recomputed))
    return check_bool(
        "b8_probe_rows_match_recomputed",
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
