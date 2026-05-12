#!/usr/bin/env python3
"""Verify source-only PRC v2.4 angle/aperture diagnostics."""

from __future__ import annotations

import argparse
import csv
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path

from v2_4_angle_aperture_diagnostics import (
    DEFAULT_FINAL_APERTURE_MARGINS_CSV,
    DEFAULT_K2_GAP_WIDTH_BIAS_CSV,
    DEFAULT_LINEAGE_MEASURE_BIAS_CSV,
    build_final_aperture_margin_rows,
    build_birth_potential_correlation_rows,
    build_birth_potential_score_rows,
    build_incremental_grid_phase_rows,
    build_k2_gap_width_bias_rows,
    build_lineage_measure_bias_rows,
    build_q_grid_birth_phase_rows,
    read_final_aperture_margin_csv,
    read_birth_potential_correlation_csv,
    read_birth_potential_score_csv,
    read_incremental_grid_phase_csv,
    read_k2_gap_width_bias_csv,
    read_lineage_measure_bias_csv,
    read_q_grid_birth_phase_csv,
    row_signature,
    write_angle_aperture_diagnostic_csvs,
)


DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_4_angle_aperture_diagnostics_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.4 angle/aperture diagnostics.",
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_OUT,
        type=Path,
        help="verification summary CSV path",
    )
    parser.add_argument(
        "--update-data",
        action="store_true",
        help="regenerate committed source-only diagnostic CSVs",
    )
    args = parser.parse_args()

    if args.update_data:
        write_angle_aperture_diagnostic_csvs()

    checks = verification_rows()
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_4_angle_aperture_diagnostics: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows() -> list[dict[str, str]]:
    k2_rows = read_k2_gap_width_bias_csv(DEFAULT_K2_GAP_WIDTH_BIAS_CSV)
    measure_rows = read_lineage_measure_bias_csv(DEFAULT_LINEAGE_MEASURE_BIAS_CSV)
    aperture_rows = read_final_aperture_margin_csv(DEFAULT_FINAL_APERTURE_MARGINS_CSV)
    q_grid_rows = read_q_grid_birth_phase_csv()
    incremental_grid_rows = read_incremental_grid_phase_csv()
    potential_rows = read_birth_potential_score_csv()
    potential_correlation_rows = read_birth_potential_correlation_csv()
    return [
        compare_recomputed_rows(
            "k2_gap_width_bias_rows_match_recomputed",
            k2_rows,
            build_k2_gap_width_bias_rows(),
        ),
        compare_recomputed_rows(
            "lineage_measure_bias_rows_match_recomputed",
            measure_rows,
            build_lineage_measure_bias_rows(),
        ),
        compare_recomputed_rows(
            "final_aperture_margin_rows_match_recomputed",
            aperture_rows,
            build_final_aperture_margin_rows(),
        ),
        compare_recomputed_rows(
            "q_grid_birth_phase_rows_match_recomputed",
            q_grid_rows,
            build_q_grid_birth_phase_rows(),
        ),
        compare_recomputed_rows(
            "incremental_grid_phase_rows_match_recomputed",
            incremental_grid_rows,
            build_incremental_grid_phase_rows(),
        ),
        compare_recomputed_rows(
            "birth_potential_score_rows_match_recomputed",
            potential_rows,
            build_birth_potential_score_rows(),
        ),
        compare_recomputed_rows(
            "birth_potential_correlation_rows_match_recomputed",
            potential_correlation_rows,
            build_birth_potential_correlation_rows(potential_rows),
        ),
        check_k2_width_bias(k2_rows),
        check_lineage_measure_bias(measure_rows),
        check_final_aperture_margins(aperture_rows),
        check_q_grid_birth_phase(q_grid_rows),
        check_incremental_grid_phase(incremental_grid_rows),
        check_birth_potential_score(potential_rows, potential_correlation_rows),
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


def check_k2_width_bias(rows) -> dict[str, str]:
    by_residue = {row.residue_mod_6: row for row in rows}
    passed = (
        len(rows) == 6
        and by_residue[3].residual_width == "1/6"
        and by_residue[3].birth_lineage_count == 556
        and by_residue[3].observed_over_residual_weighted == "3336/385"
        and not by_residue[3].zero_point_in_residual
        and by_residue[1].zero_point_in_residual
        and by_residue[5].zero_point_in_residual
    )
    failed = 0 if passed else 1
    return check_bool("k2_narrow_gap_enrichment", passed, total=7, failed=failed)


def check_lineage_measure_bias(rows) -> dict[str, str]:
    by_key = {(row.layer_k, row.population): row for row in rows}
    passed = (
        len(rows) == 8
        and by_key[(2, "all_residues")].average_residual_measure == "1/3"
        and by_key[(2, "birth_lineage")].average_residual_measure == "59/308"
        and by_key[(2, "birth_lineage")].zero_point_blank_fraction == "4/385"
        and by_key[(4, "all_residues")].average_residual_measure == "8/35"
        and by_key[(4, "birth_lineage")].average_residual_measure == "2441/40425"
    )
    failed = 0 if passed else 1
    return check_bool("lineage_measure_bias_expected_values", passed, total=6, failed=failed)


def check_final_aperture_margins(rows) -> dict[str, str]:
    by_birth_k = Counter(row.birth_k for row in rows)
    margins = [Fraction(row.aperture_margin) for row in rows]
    containment_margins = [Fraction(row.containment_margin) for row in rows]
    width_by_birth_k = {
        birth_k: Counter(
            row.prefinal_gap_width for row in rows if row.birth_k == birth_k
        )
        for birth_k in (5, 6, 7)
    }
    passed = (
        len(rows) == 770
        and by_birth_k == Counter({5: 14, 6: 42, 7: 714})
        and all(row.prefinal_gap_count == 1 for row in rows)
        and all(margin > 0 for margin in margins)
        and all(margin > 0 for margin in containment_margins)
        and width_by_birth_k[5] == Counter({"1/20": 12, "1/21": 2})
        and width_by_birth_k[6]["1/28"] == 18
        and width_by_birth_k[7]["1/28"] == 224
    )
    failed = 0 if passed else 1
    return check_bool("final_aperture_margins_positive", passed, total=8, failed=failed)


def check_q_grid_birth_phase(rows) -> dict[str, str]:
    by_key = {
        (row.birth_k, row.new_prime_remainder): row for row in rows
    }
    passed = (
        len(rows) == 24
        and by_key[(5, 3)].birth_count == 6
        and by_key[(5, 8)].birth_count == 6
        and by_key[(6, 3)].birth_count == 16
        and by_key[(6, 10)].birth_count == 16
        and by_key[(7, 4)].birth_count == 199
        and by_key[(7, 13)].birth_count == 199
        and by_key[(7, 4)].center_degrees == "1440/17"
        and by_key[(7, 13)].center_degrees == "4680/17"
    )
    failed = 0 if passed else 1
    return check_bool("q_grid_birth_phase_histogram", passed, total=9, failed=failed)


def check_incremental_grid_phase(rows) -> dict[str, str]:
    by_key = {
        (row.birth_k, row.layer_k, row.new_prime_remainder, row.transition_label): row
        for row in rows
    }
    passed = (
        len(rows) == 169
        and by_key[(7, 2, 0, "split")].row_count == 522
        and by_key[(6, 2, 0, "split")].row_count == 32
        and by_key[(5, 2, 0, "split")].row_count == 2
        and by_key[(7, 3, 1, "partial_close")].row_count == 252
        and by_key[(7, 3, 4, "partial_close")].row_count == 252
        and by_key[(7, 7, 4, "close")].row_count == 199
        and by_key[(7, 7, 13, "close")].row_count == 199
    )
    failed = 0 if passed else 1
    return check_bool("incremental_grid_phase_histogram", passed, total=8, failed=failed)


def check_birth_potential_score(score_rows, correlation_rows) -> dict[str, str]:
    by_key = {
        (row.model, row.residue): row for row in score_rows
    }
    by_model = {row.model: row for row in correlation_rows}
    passed = (
        len(score_rows) == 24
        and len(correlation_rows) == 4
        and by_key[("inverse_width", 3)].normalized_expected_count == "5775/26"
        and by_key[("inverse_width", 3)].observed_birth_lineage_count == 556
        and by_key[("inverse_width", 3)].observed_over_expected == "14456/5775"
        and float(by_model["inverse_width"].pearson_correlation)
        > float(by_model["uniform"].pearson_correlation)
        and float(by_model["inverse_width"].mean_absolute_error)
        < float(by_model["uniform"].mean_absolute_error)
        and by_model["inverse_width"].note
        == "hypothesis diagnostic; does not exclude other mechanisms"
    )
    failed = 0 if passed else 1
    return check_bool("birth_potential_score_model_comparison", passed, total=8, failed=failed)


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
