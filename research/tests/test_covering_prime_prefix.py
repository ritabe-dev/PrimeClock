import csv
import math
from pathlib import Path

import pytest

from prime_reciprocal_projection.cli import main
from prime_reciprocal_projection.covering import uncovered_measure
from prime_reciprocal_projection.covering_prime_prefix import (
    PrimePrefixProfileRow,
    prime_prefix_profile_rows,
    write_prime_prefix_profile_csv,
)


def test_prime_prefix_uncovered_measure_is_nonincreasing():
    rows = prime_prefix_profile_rows([1000])
    measures = [row.uncovered_measure for row in rows]
    assert all(0.0 <= measure <= 1.0 for measure in measures)
    assert all(later <= earlier + 1e-12 for earlier, later in zip(measures, measures[1:]))


def test_prime_prefix_final_row_matches_full_covering_measure():
    rows = prime_prefix_profile_rows([30])
    final = rows[-1]
    assert final.p_prefix == 29
    assert final.uncovered_measure == pytest.approx(uncovered_measure(30), abs=1e-12)


def test_prime_prefix_baselines_match_small_hand_calculation():
    rows = {row.p_prefix: row for row in prime_prefix_profile_rows([30])}
    row = rows[5]
    expected_width = 1 / 2 + 1 / 3 + 1 / 5
    expected_product = (1 - 1 / 2) * (1 - 1 / 3) * (1 - 1 / 5)
    assert row.prime_index == 3
    assert row.prefix_width_sum == pytest.approx(expected_width)
    assert row.poisson_prefix_baseline == pytest.approx(math.exp(-expected_width))
    assert row.product_prefix_baseline == pytest.approx(expected_product)
    assert row.baseline_delta == pytest.approx(row.uncovered_measure - expected_product)


def test_prime_prefix_omits_checkpoints_above_n():
    rows = prime_prefix_profile_rows([30], checkpoints=[2, 3, 31])
    assert [row.p_prefix for row in rows] == [2, 3]


def test_prime_prefix_gap_quantiles_are_ordered():
    rows = prime_prefix_profile_rows([1000])
    for row in rows:
        assert row.gap_p50 <= row.gap_p90 <= row.gap_p99
        assert 0.0 <= row.top_gap_share <= 1.0


def test_write_prime_prefix_profile_csv_header_and_nan_blank(tmp_path: Path):
    row = PrimePrefixProfileRow(
        n=10,
        p_prefix=7,
        prime_index=4,
        prefix_width_sum=1.0,
        poisson_prefix_baseline=0.36,
        product_prefix_baseline=0.0,
        uncovered_measure=0.0,
        uncovered_over_product_baseline=math.nan,
        baseline_delta=0.0,
        log_uncovered_minus_log_product_baseline=math.nan,
        component_count=0,
        max_gap=0.0,
        gap_p50=0.0,
        gap_p90=0.0,
        gap_p99=0.0,
        top_gap_share=0.0,
        numeric_complete_prefix=True,
    )
    output = tmp_path / "prime-prefix.csv"
    write_prime_prefix_profile_csv([row], output)
    lines = output.read_text(encoding="utf-8").splitlines()
    assert lines[0] == (
        "n,p_prefix,prime_index,prefix_width_sum,poisson_prefix_baseline,"
        "product_prefix_baseline,uncovered_measure,uncovered_over_product_baseline,"
        "baseline_delta,log_uncovered_minus_log_product_baseline,component_count,"
        "max_gap,gap_p50,gap_p90,gap_p99,top_gap_share,numeric_complete_prefix"
    )
    parsed = list(csv.DictReader(output.open(encoding="utf-8")))
    assert parsed[0]["uncovered_over_product_baseline"] == ""
    assert parsed[0]["log_uncovered_minus_log_product_baseline"] == ""


def test_covering_prime_prefix_profile_cli_writes_csv(tmp_path: Path):
    output = tmp_path / "prime-prefix-cli.csv"
    assert (
        main(
            [
                "covering-prime-prefix-profile",
                "--n",
                "30",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 11
    assert lines[0].startswith("n,p_prefix,prime_index,prefix_width_sum")
