#!/usr/bin/env python3
"""Verify source-only PRC v2.5 prefix-only grammar diagnostics."""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

from v2_5_prefix_grammar import (
    DEFAULT_PREFIX_GRAMMAR_ENRICHMENT_CSV,
    DEFAULT_PREFIX_LINEAGE_GRAMMAR_CSV,
    build_prefix_grammar_enrichment_rows,
    build_prefix_lineage_grammar_rows,
    prefix_grammar_signature,
    read_prefix_grammar_enrichment_csv,
    read_prefix_lineage_grammar_csv,
    write_prefix_grammar_artifacts,
)
from v2_5_residual_dynamics import read_residual_state_transition_csv

DEFAULT_OUT = (
    Path(tempfile.gettempdir()) / "prc_v2_5_prefix_grammar_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.5 prefix-only grammar diagnostics.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    parser.add_argument("--update-data", action="store_true")
    args = parser.parse_args()

    if args.update_data:
        write_prefix_grammar_artifacts()

    grammar_rows = read_prefix_lineage_grammar_csv(DEFAULT_PREFIX_LINEAGE_GRAMMAR_CSV)
    enrichment_rows = read_prefix_grammar_enrichment_csv(
        DEFAULT_PREFIX_GRAMMAR_ENRICHMENT_CSV
    )
    checks = verification_rows(grammar_rows, enrichment_rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_5_prefix_grammar: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(grammar_rows, enrichment_rows) -> list[dict[str, str]]:
    transition_rows = read_residual_state_transition_csv()
    return [
        compare_recomputed_rows(
            "prefix_grammar_rows_match_recomputed",
            grammar_rows,
            build_prefix_lineage_grammar_rows(transition_rows),
        ),
        compare_recomputed_rows(
            "prefix_grammar_enrichment_rows_match_recomputed",
            enrichment_rows,
            build_prefix_grammar_enrichment_rows(transition_rows),
        ),
        check_bool(
            "prefix_grammar_excludes_terminal_close_label",
            all("close" not in row.prefix_transition_sequence.split(">") for row in grammar_rows),
            total=len(grammar_rows),
            failed=sum("close" in row.prefix_transition_sequence.split(">") for row in grammar_rows),
        ),
        check_bool(
            "prefix_grammar_has_enrichment_signal",
            any(row.enrichment_ratio != "0" and row.enrichment_ratio != "1" for row in enrichment_rows),
            total=len(enrichment_rows),
            failed=0
            if any(row.enrichment_ratio != "0" and row.enrichment_ratio != "1" for row in enrichment_rows)
            else 1,
        ),
    ]


def compare_recomputed_rows(name: str, committed_rows, recomputed_rows):
    committed = [prefix_grammar_signature(row) for row in committed_rows]
    recomputed = [prefix_grammar_signature(row) for row in recomputed_rows]
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
