#!/usr/bin/env python3
"""Verify source-only PRC v2.4 early residual genealogy rows."""

from __future__ import annotations

import argparse
import csv
import tempfile
from collections import Counter
from pathlib import Path

from tools import birth_dynamics_rows
from v2_4_residual_genealogy import (
    DEFAULT_BIRTH_RESIDUAL_GENEALOGY_CSV,
    TRANSITION_CLOSE,
    build_birth_residual_genealogy_rows,
    close_transition_count,
    final_birth_rows,
    genealogy_layer_summary,
    genealogy_row_key,
    genealogy_row_signature,
    genealogy_transition_summary,
    non_coprime_birth_count,
    prefinal_rows,
    read_birth_residual_genealogy_csv,
)


DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_4_birth_residual_genealogy_verification_v0_1.csv"
)

EXPECTED_LAYER_SUMMARY = {
    (5, 1, "start"): 14,
    (5, 2, "split"): 2,
    (5, 2, "trim"): 12,
    (5, 3, "partial_close"): 2,
    (5, 3, "trim"): 12,
    (5, 4, "miss"): 12,
    (5, 4, "trim"): 2,
    (5, 5, "close"): 14,
    (6, 1, "start"): 42,
    (6, 2, "split"): 32,
    (6, 2, "trim"): 10,
    (6, 3, "miss"): 6,
    (6, 3, "partial_close"): 32,
    (6, 3, "trim"): 4,
    (6, 4, "miss"): 10,
    (6, 4, "trim"): 32,
    (6, 5, "miss"): 18,
    (6, 5, "trim"): 24,
    (6, 6, "close"): 42,
    (7, 1, "start"): 714,
    (7, 2, "split"): 522,
    (7, 2, "trim"): 192,
    (7, 3, "miss"): 36,
    (7, 3, "partial_close"): 504,
    (7, 3, "split"): 6,
    (7, 3, "trim"): 168,
    (7, 4, "miss"): 340,
    (7, 4, "partial_close"): 2,
    (7, 4, "trim"): 372,
    (7, 5, "miss"): 464,
    (7, 5, "partial_close"): 6,
    (7, 5, "split"): 4,
    (7, 5, "trim"): 240,
    (7, 6, "miss"): 408,
    (7, 6, "partial_close"): 20,
    (7, 6, "trim"): 286,
    (7, 7, "close"): 714,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.4 early residual genealogy rows.",
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_OUT,
        type=Path,
        help="verification summary CSV path",
    )
    args = parser.parse_args()

    committed_rows = read_birth_residual_genealogy_csv(
        DEFAULT_BIRTH_RESIDUAL_GENEALOGY_CSV
    )
    recomputed_rows = build_birth_residual_genealogy_rows(
        birth_dynamics_rows(min_k=5, max_k=7)
    )
    checks = verification_rows(committed_rows, recomputed_rows)
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_4_birth_residual_genealogy: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(committed_rows, recomputed_rows) -> list[dict[str, str]]:
    final_rows = final_birth_rows(committed_rows)
    before_final = prefinal_rows(committed_rows)
    expected_birth_keys = {
        (row.k, row.residue)
        for row in birth_dynamics_rows(min_k=5, max_k=7)
    }
    final_birth_keys = {(row.birth_k, row.birth_residue) for row in final_rows}
    layer_failures = lineage_layer_failures(committed_rows)
    transition_counts = genealogy_transition_summary(committed_rows)
    layer_counts = genealogy_layer_summary(committed_rows)
    expected_transition_counts = Counter(
        {
            "start": 770,
            "miss": 1294,
            "trim": 1354,
            "split": 566,
            "partial_close": 566,
            "close": 770,
        }
    )
    return [
        compare_recomputed_rows(committed_rows, recomputed_rows),
        check_bool(
            "genealogy_row_count",
            len(committed_rows) == 5320,
            total=1,
            failed=0 if len(committed_rows) == 5320 else 1,
        ),
        check_bool(
            "genealogy_birth_rows_represented",
            final_birth_keys == expected_birth_keys and len(final_rows) == 770,
            total=len(expected_birth_keys),
            failed=len(final_birth_keys.symmetric_difference(expected_birth_keys))
            + (0 if len(final_rows) == 770 else 1),
        ),
        check_bool(
            "genealogy_layers_are_complete",
            not layer_failures,
            total=770,
            failed=layer_failures,
        ),
        check_bool(
            "genealogy_final_layer_closes",
            all(row.transition_label == TRANSITION_CLOSE for row in final_rows)
            and all(row.is_zero_residual_state for row in final_rows)
            and close_transition_count(committed_rows) == 770,
            total=770,
            failed=sum(row.transition_label != TRANSITION_CLOSE for row in final_rows)
            + sum(not row.is_zero_residual_state for row in final_rows)
            + (0 if close_transition_count(committed_rows) == 770 else 1),
        ),
        check_bool(
            "genealogy_prefinal_layers_remain_uncovered",
            all(row.residual_component_count > 0 for row in before_final)
            and not any(row.is_zero_residual_state for row in before_final),
            total=len(before_final),
            failed=sum(row.residual_component_count == 0 for row in before_final)
            + sum(row.is_zero_residual_state for row in before_final),
        ),
        check_bool(
            "genealogy_transition_counts",
            transition_counts == expected_transition_counts,
            total=len(expected_transition_counts),
            failed=sum(
                transition_counts[label] != expected_count
                for label, expected_count in expected_transition_counts.items()
            ),
        ),
        check_bool(
            "genealogy_layer_transition_counts",
            layer_counts == Counter(EXPECTED_LAYER_SUMMARY),
            total=len(EXPECTED_LAYER_SUMMARY),
            failed=sum(
                layer_counts[key] != value
                for key, value in EXPECTED_LAYER_SUMMARY.items()
            )
            + sum(key not in EXPECTED_LAYER_SUMMARY for key in layer_counts),
        ),
        check_bool(
            "genealogy_origin_and_zero_center_diagnostics",
            sum(row.origin_component_present for row in committed_rows) == 576
            and sum(row.zero_center_available for row in committed_rows) == 4744
            and non_coprime_birth_count(committed_rows) == 770
            and sum(row.birth_new_prime_remainder == 0 for row in final_rows) == 0,
            total=4,
            failed=(0 if sum(row.origin_component_present for row in committed_rows) == 576 else 1)
            + (0 if sum(row.zero_center_available for row in committed_rows) == 4744 else 1)
            + (0 if non_coprime_birth_count(committed_rows) == 770 else 1)
            + (0 if sum(row.birth_new_prime_remainder == 0 for row in final_rows) == 0 else 1),
        ),
    ]


def compare_recomputed_rows(committed_rows, recomputed_rows) -> dict[str, str]:
    committed_by_key = {genealogy_row_key(row): row for row in committed_rows}
    recomputed_by_key = {genealogy_row_key(row): row for row in recomputed_rows}
    missing_keys = set(committed_by_key).symmetric_difference(recomputed_by_key)
    mismatches = [
        key
        for key in sorted(set(committed_by_key) & set(recomputed_by_key))
        if genealogy_row_signature(committed_by_key[key])
        != genealogy_row_signature(recomputed_by_key[key])
    ]
    return check_bool(
        "genealogy_committed_rows_match_recomputed_rows",
        not missing_keys and not mismatches,
        total=max(len(committed_rows), len(recomputed_rows)),
        failed=len(missing_keys) + len(mismatches),
    )


def lineage_layer_failures(rows) -> int:
    layers_by_birth: dict[tuple[int, int], set[int]] = {}
    for row in rows:
        layers_by_birth.setdefault((row.birth_k, row.birth_residue), set()).add(
            row.layer_k
        )
    return sum(
        layers != set(range(1, birth_k + 1))
        for (birth_k, _), layers in layers_by_birth.items()
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
