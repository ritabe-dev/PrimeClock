import csv
import hashlib
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from prime_reciprocal_projection.cli import main
from prime_reciprocal_projection.covering_prime_prefix_filtration import (
    PrimePrefixBirthClassificationRow,
    PrimePrefixBirthClassificationV15Row,
    PrimePrefixBirthPairSummaryRow,
    PrimePrefixBirthPairSummaryV15Row,
    PrimePrefixBirthWitnessRow,
    PrimePrefixBirthWitnessV15Row,
    PrimePrefixCertificateVerificationRow,
    PrimePrefixExclusionSummaryRow,
    PrimePrefixExclusionSummaryV15Row,
    PrimePrefixExclusionWitnessRow,
    PrimePrefixExclusionWitnessV16Row,
    PrimePrefixResidueBirthSampleRow,
    PrimePrefixResidueFiltrationRow,
    PrimePrefixResidueFullRow,
    prime_prefix_birth_classification_rows,
    prime_prefix_birth_classification_v15_rows,
    prime_prefix_birth_pair_summary_rows,
    prime_prefix_birth_pair_summary_v15_rows,
    prime_prefix_birth_witness_rows,
    prime_prefix_birth_witness_v15_rows,
    prime_prefix_certificate_verification_rows,
    prime_prefix_exclusion_summary_rows,
    prime_prefix_exclusion_summary_v15_rows,
    prime_prefix_exclusion_witness_rows,
    prime_prefix_exclusion_witness_v16_rows,
    prime_prefix_residue_filtration_tables,
    prime_prefix_residue_full_rows,
    residue_is_exactly_covered,
    residue_uncovered_measure,
    write_prime_prefix_birth_classification_csv,
    write_prime_prefix_birth_classification_v15_csv,
    write_prime_prefix_birth_pair_summary_csv,
    write_prime_prefix_birth_pair_summary_v15_csv,
    write_prime_prefix_birth_witness_csv,
    write_prime_prefix_birth_witness_v15_csv,
    write_prime_prefix_certificate_verification_csv,
    write_prime_prefix_exclusion_summary_csv,
    write_prime_prefix_exclusion_summary_v15_csv,
    write_prime_prefix_exclusion_witness_csv,
    write_prime_prefix_exclusion_witness_v16_csv,
    write_prime_prefix_residue_birth_samples_csv,
    write_prime_prefix_residue_filtration_csv,
    write_prime_prefix_residue_full_csv,
)
from prime_reciprocal_projection.primes import primes_up_to


def _write_verifier_fixture(tmp_path: Path) -> dict[str, Path]:
    paths = {
        "ck_full": tmp_path / "ck_full.csv",
        "c4_witness": tmp_path / "c4_witness.csv",
        "c4_summary": tmp_path / "c4_summary.csv",
        "b5_witness": tmp_path / "b5_witness.csv",
        "b5_classification": tmp_path / "b5_classification.csv",
        "b5_pair": tmp_path / "b5_pair.csv",
    }
    write_prime_prefix_residue_full_csv(
        prime_prefix_residue_full_rows(max_k=5),
        paths["ck_full"],
    )
    write_prime_prefix_exclusion_witness_v16_csv(
        prime_prefix_exclusion_witness_v16_rows(k=4),
        paths["c4_witness"],
    )
    write_prime_prefix_exclusion_summary_v15_csv(
        prime_prefix_exclusion_summary_v15_rows(k=4),
        paths["c4_summary"],
    )
    write_prime_prefix_birth_witness_v15_csv(
        prime_prefix_birth_witness_v15_rows(k=5),
        paths["b5_witness"],
    )
    write_prime_prefix_birth_classification_v15_csv(
        prime_prefix_birth_classification_v15_rows(k=5),
        paths["b5_classification"],
    )
    write_prime_prefix_birth_pair_summary_v15_csv(
        prime_prefix_birth_pair_summary_v15_rows(k=5),
        paths["b5_pair"],
    )
    return paths


def _verification_by_name(paths: dict[str, Path]) -> dict[str, PrimePrefixCertificateVerificationRow]:
    rows = prime_prefix_certificate_verification_rows(
        ck_full_csv=paths["ck_full"],
        c4_exclusion_witness_csv=paths["c4_witness"],
        c4_exclusion_summary_csv=paths["c4_summary"],
        b5_birth_witness_csv=paths["b5_witness"],
        b5_birth_classification_csv=paths["b5_classification"],
        b5_birth_pair_summary_csv=paths["b5_pair"],
    )
    return {row.check_name: row for row in rows}


def _mutate_csv(path: Path, mutate) -> None:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    rows = mutate(rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_residue_exact_coverage_for_first_birth_class():
    assert residue_is_exactly_covered(2, [2, 3, 5, 7])
    assert not residue_is_exactly_covered(0, [2, 3, 5, 7])


def test_prime_prefix_filtration_first_nonempty_level():
    rows, birth_rows = prime_prefix_residue_filtration_tables(max_k=4)
    assert [row.covered_residue_count for row in rows[:3]] == [0, 0, 0]
    assert rows[3].k == 4
    assert rows[3].primorial == 210
    assert rows[3].covered_residue_count == 2
    assert rows[3].birth_count == 2
    assert rows[3].birth_residues_sample == "2 208"
    assert [row.residue for row in birth_rows] == [2, 208]


def test_prime_prefix_filtration_k5_inherited_and_birth_counts():
    rows, _ = prime_prefix_residue_filtration_tables(max_k=5)
    row = rows[-1]
    assert row.k == 5
    assert row.new_prime == 11
    assert row.inherited_count == 22
    assert row.birth_count == 14
    assert row.covered_residue_count == 36


def test_prime_prefix_filtration_k7_regeneration_counts():
    rows, birth_rows = prime_prefix_residue_filtration_tables(
        max_k=7,
        birth_sample_limit=200,
    )
    row = rows[-1]
    assert row.k == 7
    assert row.covered_residue_count == 9384
    assert row.inherited_count == 8670
    assert row.birth_count == 714
    assert len(birth_rows) == 258


def test_prime_prefix_filtration_invariants_hold_through_k7():
    rows, birth_rows = prime_prefix_residue_filtration_tables(
        max_k=7,
        birth_sample_limit=200,
    )
    previous_count = 0
    for row in rows:
        assert row.covered_residue_count == row.inherited_count + row.birth_count
        assert row.inherited_count == previous_count * row.new_prime
        previous_count = row.covered_residue_count

    for birth in birth_rows:
        prefix_primes = primes_up_to(birth.new_prime)
        previous_primes = prefix_primes[:-1]
        assert not residue_is_exactly_covered(birth.residue, previous_primes)
        assert residue_is_exactly_covered(birth.residue, prefix_primes)


def test_prime_prefix_filtration_density_is_monotone_through_k7():
    rows, _ = prime_prefix_residue_filtration_tables(max_k=7)
    previous_density = 0.0
    for row in rows:
        assert row.covered_density >= previous_density
        if row.k > 1:
            assert row.covered_density == pytest.approx(
                previous_density + row.birth_count / row.primorial
            )
        previous_density = row.covered_density


def test_prime_prefix_filtration_rejects_unguarded_large_k():
    with pytest.raises(ValueError, match="primorial-scale"):
        prime_prefix_residue_filtration_tables(max_k=8)


def test_prime_prefix_filtration_rejects_invalid_prime_lists():
    with pytest.raises(ValueError, match="distinct prime"):
        residue_is_exactly_covered(0, [1])
    with pytest.raises(ValueError, match="distinct prime"):
        residue_is_exactly_covered(0, [4])
    with pytest.raises(ValueError, match="distinct prime"):
        residue_is_exactly_covered(0, [2, 2])


def test_prime_prefix_filtration_birth_previous_measure():
    assert residue_uncovered_measure(2, [2, 3, 5]) == Fraction(1, 20)
    rows, birth_rows = prime_prefix_residue_filtration_tables(max_k=4)
    assert rows[-1].birth_prev_uncovered_median == pytest.approx(0.05)
    assert rows[-1].birth_prev_uncovered_max == pytest.approx(0.05)
    assert birth_rows[0].previous_prefix_uncovered_measure == pytest.approx(0.05)


def test_prime_prefix_full_rows_c5_counts_and_reflection():
    rows = prime_prefix_residue_full_rows(max_k=5)
    c4_rows = [row for row in rows if row.k == 4]
    c5_rows = [row for row in rows if row.k == 5]
    c5_residues = {row.residue for row in c5_rows}

    assert [row.residue for row in c4_rows] == [2, 208]
    assert len(c5_rows) == 36
    assert sum(row.status == "inherited" for row in c5_rows) == 22
    assert sum(row.status == "birth" for row in c5_rows) == 14
    assert all(row.reflection_residue in c5_residues for row in c5_rows)


def test_prime_prefix_birth_witness_rows_k5():
    rows = prime_prefix_birth_witness_rows(k=5)
    assert len(rows) == 14
    for row in rows:
        assert row.previous_uncovered_interval_count > 0
        assert row.previous_prefix_uncovered_measure > 0
        assert row.previous_uncovered_intervals
        assert row.new_prime_arc_intervals
        assert not residue_is_exactly_covered(row.residue, [2, 3, 5, 7])
        assert residue_is_exactly_covered(row.residue, [2, 3, 5, 7, 11])


def test_prime_prefix_c4_exclusion_witness_rows():
    rows = prime_prefix_exclusion_witness_rows(k=4)
    residues = {row.residue for row in rows}
    assert len(rows) == 208
    assert 2 not in residues
    assert 208 not in residues
    assert all(row.reflection_residue in residues for row in rows)
    for row in rows:
        assert row.uncovered_interval_count > 0
        assert row.uncovered_measure > 0
        assert row.first_uncovered_interval
        assert row.uncovered_intervals
        assert not residue_is_exactly_covered(row.residue, [2, 3, 5, 7])


def test_prime_prefix_c4_exclusion_witness_v16_rows():
    rows = prime_prefix_exclusion_witness_v16_rows(k=4)
    residues = {row.residue for row in rows}
    assert len(rows) == 208
    assert 2 not in residues
    assert 208 not in residues
    first = rows[0]
    assert first.residue == 0
    assert first.uncovered_measure_fraction == "1/2"
    assert first.first_open_gap_boundary_endpoints == "1/4-3/4"
    assert first.witness_point == "1/2"
    assert first.open_gap_boundary_endpoints == "1/4-3/4"
    for row in rows:
        assert row.open_gap_count > 0
        assert row.uncovered_measure_fraction
        assert row.witness_point
        assert row.first_open_gap_boundary_endpoints
        assert row.open_gap_boundary_endpoints
        assert not residue_is_exactly_covered(row.residue, [2, 3, 5, 7])


def test_prime_prefix_c4_exclusion_summary_rows():
    rows = prime_prefix_exclusion_summary_rows(k=4)
    assert len(rows) == 36
    assert sum(row.residue_count for row in rows) == 208
    assert rows[0].uncovered_interval_count == 1
    assert rows[0].uncovered_measure_fraction == "1/28"
    assert rows[0].residue_count == 2
    max_measure_row = max(rows, key=lambda row: row.uncovered_measure)
    assert max_measure_row.uncovered_measure_fraction == "1/2"
    assert max_measure_row.residue_count == 3


def test_prime_prefix_b5_birth_classification_rows():
    rows = prime_prefix_birth_classification_rows(k=5)
    residues = {row.residue for row in rows}
    pair_keys = {(row.reflection_pair_min, row.reflection_pair_max) for row in rows}
    assert len(rows) == 14
    assert len(pair_keys) == 7
    assert all(row.reflection_residue in residues for row in rows)
    for row in rows:
        assert row.new_prime_remainder == row.residue % 11
        assert row.previous_uncovered_interval_count == 1
        assert row.previous_prefix_uncovered_measure > 0
        assert row.previous_uncovered_intervals
        assert row.new_prime_arc_intervals
        assert not residue_is_exactly_covered(row.residue, [2, 3, 5, 7])
        assert residue_is_exactly_covered(row.residue, [2, 3, 5, 7, 11])


def test_prime_prefix_b5_birth_pair_summary_rows():
    rows = prime_prefix_birth_pair_summary_rows(k=5)
    assert len(rows) == 7
    assert rows[0].reflection_pair_min == 118
    assert rows[0].reflection_pair_max == 2192
    assert rows[0].parent_residue_pair_mod_previous == "118 / 92"
    assert rows[0].previous_uncovered_interval_count_pair == "1 / 1"
    assert rows[0].previous_uncovered_intervals_pair == "7/10-3/4 / 1/4-3/10"
    assert rows[0].new_prime_remainder_pair == "8 / 3"
    assert rows[0].new_prime_arc_intervals_pair == "15/22-17/22 / 5/22-7/22"
    assert rows[0].uses_endpoint_touching_pair == "False / False"


def test_prime_prefix_b5_v15_rows_have_exact_fraction_and_open_gap_fields():
    witness_rows = prime_prefix_birth_witness_v15_rows(k=5)
    classification_rows = prime_prefix_birth_classification_v15_rows(k=5)
    pair_rows = prime_prefix_birth_pair_summary_v15_rows(k=5)

    first_witness = witness_rows[0]
    assert first_witness.previous_prefix_uncovered_measure_fraction == "1/20"
    assert first_witness.previous_open_gap_boundary_endpoints == "7/10-3/4"
    assert first_witness.new_prime_closed_arc_boundary_endpoints == "15/22-17/22"

    first_classification = classification_rows[0]
    assert first_classification.previous_prefix_uncovered_measure_fraction == "1/20"
    assert first_classification.previous_open_gap_count == 1
    assert first_classification.previous_open_gap_boundary_endpoints == "7/10-3/4"

    assert pair_rows[0].previous_prefix_uncovered_measure_fraction_pair == "1/20 / 1/20"
    one_over_21_pair = next(row for row in pair_rows if row.reflection_pair_min == 849)
    assert one_over_21_pair.previous_prefix_uncovered_measure_fraction_pair == "1/21 / 1/21"


def test_prime_prefix_c4_v15_exclusion_summary_has_complete_residue_lists():
    rows = prime_prefix_exclusion_summary_v15_rows(k=4)
    assert len(rows) == 36
    assert sum(row.residue_count for row in rows) == 208
    residues = {
        int(value)
        for row in rows
        for value in row.residues.split()
    }
    assert len(residues) == 208
    assert 2 not in residues
    assert 208 not in residues
    assert rows[0].open_gap_count == 1
    assert rows[0].uncovered_measure_fraction == "1/28"


def test_prime_prefix_full_export_rejects_unguarded_large_k():
    with pytest.raises(ValueError, match="full exports"):
        prime_prefix_residue_full_rows(max_k=7)
    with pytest.raises(ValueError, match="full exports"):
        prime_prefix_birth_witness_rows(k=7)


def test_write_prime_prefix_filtration_csv_headers(tmp_path: Path):
    summary_out = tmp_path / "summary.csv"
    birth_out = tmp_path / "birth.csv"
    write_prime_prefix_residue_filtration_csv(
        [
            PrimePrefixResidueFiltrationRow(
                k=1,
                new_prime=2,
                primorial=2,
                covered_residue_count=0,
                covered_density=0.0,
                inherited_count=0,
                birth_count=0,
                birth_prev_uncovered_median=None,
                birth_prev_uncovered_max=None,
                birth_residues_sample="",
            )
        ],
        summary_out,
    )
    write_prime_prefix_residue_birth_samples_csv(
        [
            PrimePrefixResidueBirthSampleRow(
                k=4,
                new_prime=7,
                primorial=210,
                residue=2,
                previous_prefix_uncovered_measure=0.05,
            )
        ],
        birth_out,
    )
    assert summary_out.read_text(encoding="utf-8").splitlines()[0] == (
        "k,new_prime,primorial,covered_residue_count,covered_density,"
        "inherited_count,birth_count,birth_prev_uncovered_median,"
        "birth_prev_uncovered_max,birth_residues_sample"
    )
    assert birth_out.read_text(encoding="utf-8").splitlines()[0] == (
        "k,new_prime,primorial,residue,previous_prefix_uncovered_measure"
    )


def test_write_prime_prefix_full_and_witness_csv_headers(tmp_path: Path):
    full_out = tmp_path / "full.csv"
    witness_out = tmp_path / "witness.csv"
    exclusion_out = tmp_path / "exclusion.csv"
    exclusion_summary_out = tmp_path / "exclusion_summary.csv"
    classification_out = tmp_path / "classification.csv"
    pair_summary_out = tmp_path / "pair_summary.csv"
    write_prime_prefix_residue_full_csv(
        [
            PrimePrefixResidueFullRow(
                k=4,
                new_prime=7,
                primorial=210,
                residue=2,
                residue_mod_previous=2,
                status="birth",
                reflection_residue=208,
                previous_prefix_uncovered_measure=0.05,
            )
        ],
        full_out,
    )
    write_prime_prefix_birth_witness_csv(
        [
            PrimePrefixBirthWitnessRow(
                k=5,
                new_prime=11,
                primorial=2310,
                residue=118,
                residue_mod_previous=118,
                reflection_residue=2192,
                previous_uncovered_interval_count=1,
                previous_prefix_uncovered_measure=0.01,
                previous_uncovered_intervals="1/2-3/5",
                new_prime_arc_intervals="1/2-3/5",
                uses_endpoint_touching=True,
            )
        ],
        witness_out,
    )
    write_prime_prefix_exclusion_witness_csv(
        [
            PrimePrefixExclusionWitnessRow(
                k=4,
                new_prime=7,
                primorial=210,
                residue=0,
                reflection_residue=0,
                uncovered_interval_count=1,
                uncovered_measure=0.1,
                first_uncovered_interval="1/2-3/5",
                uncovered_intervals="1/2-3/5",
            )
        ],
        exclusion_out,
    )
    write_prime_prefix_exclusion_summary_csv(
        [
            PrimePrefixExclusionSummaryRow(
                k=4,
                new_prime=7,
                primorial=210,
                uncovered_interval_count=1,
                uncovered_measure_fraction="1/10",
                uncovered_measure=0.1,
                residue_count=2,
                residues_sample="1 209",
                first_uncovered_interval_sample="1/2-3/5",
            )
        ],
        exclusion_summary_out,
    )
    write_prime_prefix_birth_classification_csv(
        [
            PrimePrefixBirthClassificationRow(
                k=5,
                new_prime=11,
                primorial=2310,
                residue=118,
                reflection_residue=2192,
                reflection_pair_min=118,
                reflection_pair_max=2192,
                parent_residue_mod_previous=118,
                previous_uncovered_interval_count=1,
                previous_prefix_uncovered_measure=0.05,
                previous_uncovered_intervals="7/10-3/4",
                new_prime_remainder=8,
                new_prime_arc_intervals="15/22-17/22",
                uses_endpoint_touching=False,
            )
        ],
        classification_out,
    )
    write_prime_prefix_birth_pair_summary_csv(
        [
            PrimePrefixBirthPairSummaryRow(
                k=5,
                new_prime=11,
                primorial=2310,
                reflection_pair_min=118,
                reflection_pair_max=2192,
                parent_residue_pair_mod_previous="118 / 92",
                previous_uncovered_interval_count_pair="1 / 1",
                previous_prefix_uncovered_measure_pair="0.05 / 0.05",
                previous_uncovered_intervals_pair="7/10-3/4 / 1/4-3/10",
                new_prime_remainder_pair="8 / 3",
                new_prime_arc_intervals_pair="15/22-17/22 / 5/22-7/22",
                uses_endpoint_touching_pair="False / False",
            )
        ],
        pair_summary_out,
    )
    assert full_out.read_text(encoding="utf-8").splitlines()[0] == (
        "k,new_prime,primorial,residue,residue_mod_previous,status,"
        "reflection_residue,previous_prefix_uncovered_measure"
    )
    assert witness_out.read_text(encoding="utf-8").splitlines()[0] == (
        "k,new_prime,primorial,residue,residue_mod_previous,reflection_residue,"
        "previous_uncovered_interval_count,previous_prefix_uncovered_measure,"
        "previous_uncovered_intervals,new_prime_arc_intervals,uses_endpoint_touching"
    )
    assert exclusion_out.read_text(encoding="utf-8").splitlines()[0] == (
        "k,new_prime,primorial,residue,reflection_residue,"
        "uncovered_interval_count,uncovered_measure,first_uncovered_interval,"
        "uncovered_intervals"
    )
    assert exclusion_summary_out.read_text(encoding="utf-8").splitlines()[0] == (
        "k,new_prime,primorial,uncovered_interval_count,"
        "uncovered_measure_fraction,uncovered_measure,residue_count,"
        "residues_sample,first_uncovered_interval_sample"
    )
    assert classification_out.read_text(encoding="utf-8").splitlines()[0] == (
        "k,new_prime,primorial,residue,reflection_residue,reflection_pair_min,"
        "reflection_pair_max,parent_residue_mod_previous,"
        "previous_uncovered_interval_count,previous_prefix_uncovered_measure,"
        "previous_uncovered_intervals,new_prime_remainder,new_prime_arc_intervals,"
        "uses_endpoint_touching"
    )
    assert pair_summary_out.read_text(encoding="utf-8").splitlines()[0] == (
        "k,new_prime,primorial,reflection_pair_min,reflection_pair_max,"
        "parent_residue_pair_mod_previous,previous_uncovered_interval_count_pair,"
        "previous_prefix_uncovered_measure_pair,previous_uncovered_intervals_pair,"
        "new_prime_remainder_pair,new_prime_arc_intervals_pair,"
        "uses_endpoint_touching_pair"
    )


def test_write_prime_prefix_v15_csv_headers(tmp_path: Path):
    witness_out = tmp_path / "witness_v15.csv"
    classification_out = tmp_path / "classification_v15.csv"
    pair_summary_out = tmp_path / "pair_summary_v15.csv"
    exclusion_witness_out = tmp_path / "exclusion_witness_v16.csv"
    exclusion_summary_out = tmp_path / "exclusion_summary_v15.csv"
    verification_out = tmp_path / "verification.csv"
    write_prime_prefix_birth_witness_v15_csv(
        [
            PrimePrefixBirthWitnessV15Row(
                k=5,
                new_prime=11,
                primorial=2310,
                residue=118,
                residue_mod_previous=118,
                reflection_residue=2192,
                previous_open_gap_count=1,
                previous_prefix_uncovered_measure_fraction="1/20",
                previous_prefix_uncovered_measure=0.05,
                previous_open_gap_boundary_endpoints="7/10-3/4",
                new_prime_closed_arc_boundary_endpoints="15/22-17/22",
                uses_endpoint_touching=False,
            )
        ],
        witness_out,
    )
    write_prime_prefix_birth_classification_v15_csv(
        [
            PrimePrefixBirthClassificationV15Row(
                k=5,
                new_prime=11,
                primorial=2310,
                residue=118,
                reflection_residue=2192,
                reflection_pair_min=118,
                reflection_pair_max=2192,
                parent_residue_mod_previous=118,
                previous_open_gap_count=1,
                previous_prefix_uncovered_measure_fraction="1/20",
                previous_prefix_uncovered_measure=0.05,
                previous_open_gap_boundary_endpoints="7/10-3/4",
                new_prime_remainder=8,
                new_prime_closed_arc_boundary_endpoints="15/22-17/22",
                uses_endpoint_touching=False,
            )
        ],
        classification_out,
    )
    write_prime_prefix_birth_pair_summary_v15_csv(
        [
            PrimePrefixBirthPairSummaryV15Row(
                k=5,
                new_prime=11,
                primorial=2310,
                reflection_pair_min=118,
                reflection_pair_max=2192,
                parent_residue_pair_mod_previous="118 / 92",
                previous_open_gap_count_pair="1 / 1",
                previous_prefix_uncovered_measure_fraction_pair="1/20 / 1/20",
                previous_prefix_uncovered_measure_pair="0.05 / 0.05",
                previous_open_gap_boundary_endpoints_pair="7/10-3/4 / 1/4-3/10",
                new_prime_remainder_pair="8 / 3",
                new_prime_closed_arc_boundary_endpoints_pair=(
                    "15/22-17/22 / 5/22-7/22"
                ),
                uses_endpoint_touching_pair="False / False",
            )
        ],
        pair_summary_out,
    )
    write_prime_prefix_exclusion_summary_v15_csv(
        [
            PrimePrefixExclusionSummaryV15Row(
                k=4,
                new_prime=7,
                primorial=210,
                open_gap_count=1,
                uncovered_measure_fraction="1/28",
                uncovered_measure=1 / 28,
                residue_count=2,
                residues="1 209",
                first_open_gap_boundary_endpoint_sample="1/2-15/28",
            )
        ],
        exclusion_summary_out,
    )
    write_prime_prefix_exclusion_witness_v16_csv(
        [
            PrimePrefixExclusionWitnessV16Row(
                k=4,
                new_prime=7,
                primorial=210,
                residue=0,
                reflection_residue=0,
                open_gap_count=1,
                uncovered_measure_fraction="1/2",
                uncovered_measure=0.5,
                first_open_gap_boundary_endpoints="1/4-3/4",
                witness_point="1/2",
                open_gap_boundary_endpoints="1/4-3/4",
            )
        ],
        exclusion_witness_out,
    )
    write_prime_prefix_certificate_verification_csv(
        [
            PrimePrefixCertificateVerificationRow(
                check_name="example",
                total=1,
                passed=1,
                failed=0,
                status="pass",
            )
        ],
        verification_out,
    )
    assert witness_out.read_text(encoding="utf-8").splitlines()[0] == (
        "k,new_prime,primorial,residue,residue_mod_previous,reflection_residue,"
        "previous_open_gap_count,previous_prefix_uncovered_measure_fraction,"
        "previous_prefix_uncovered_measure,previous_open_gap_boundary_endpoints,"
        "new_prime_closed_arc_boundary_endpoints,uses_endpoint_touching"
    )
    assert classification_out.read_text(encoding="utf-8").splitlines()[0] == (
        "k,new_prime,primorial,residue,reflection_residue,reflection_pair_min,"
        "reflection_pair_max,parent_residue_mod_previous,previous_open_gap_count,"
        "previous_prefix_uncovered_measure_fraction,previous_prefix_uncovered_measure,"
        "previous_open_gap_boundary_endpoints,new_prime_remainder,"
        "new_prime_closed_arc_boundary_endpoints,uses_endpoint_touching"
    )
    assert pair_summary_out.read_text(encoding="utf-8").splitlines()[0] == (
        "k,new_prime,primorial,reflection_pair_min,reflection_pair_max,"
        "parent_residue_pair_mod_previous,previous_open_gap_count_pair,"
        "previous_prefix_uncovered_measure_fraction_pair,"
        "previous_prefix_uncovered_measure_pair,"
        "previous_open_gap_boundary_endpoints_pair,new_prime_remainder_pair,"
        "new_prime_closed_arc_boundary_endpoints_pair,uses_endpoint_touching_pair"
    )
    assert exclusion_summary_out.read_text(encoding="utf-8").splitlines()[0] == (
        "k,new_prime,primorial,open_gap_count,uncovered_measure_fraction,"
        "uncovered_measure,residue_count,residues,"
        "first_open_gap_boundary_endpoint_sample"
    )
    assert exclusion_witness_out.read_text(encoding="utf-8").splitlines()[0] == (
        "k,new_prime,primorial,residue,reflection_residue,open_gap_count,"
        "uncovered_measure_fraction,uncovered_measure,"
        "first_open_gap_boundary_endpoints,witness_point,"
        "open_gap_boundary_endpoints"
    )
    assert verification_out.read_text(encoding="utf-8").splitlines()[0] == (
        "check_name,total,passed,failed,status"
    )


def test_covering_prime_prefix_filtration_cli_writes_csvs(tmp_path: Path):
    summary_out = tmp_path / "summary.csv"
    birth_out = tmp_path / "birth.csv"
    assert (
        main(
            [
                "covering-prime-prefix-filtration",
                "--max-k",
                "4",
                "--summary-out",
                str(summary_out),
                "--birth-samples-out",
                str(birth_out),
            ]
        )
        == 0
    )
    summary_lines = summary_out.read_text(encoding="utf-8").splitlines()
    birth_lines = birth_out.read_text(encoding="utf-8").splitlines()
    assert len(summary_lines) == 5
    assert len(birth_lines) == 3
    assert summary_lines[-1].startswith("4,7,210,2,")


def test_covering_prime_prefix_filtration_full_cli_writes_csv(tmp_path: Path):
    output = tmp_path / "full.csv"
    assert (
        main(
            [
                "covering-prime-prefix-filtration-full",
                "--max-k",
                "5",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 39
    assert lines[0].startswith("k,new_prime,primorial,residue")


def test_covering_prime_prefix_birth_witnesses_cli_writes_csv(tmp_path: Path):
    output = tmp_path / "witness.csv"
    assert (
        main(
            [
                "covering-prime-prefix-birth-witnesses",
                "--k",
                "5",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 15
    assert lines[0].startswith("k,new_prime,primorial,residue")


def test_covering_prime_prefix_exclusion_witnesses_cli_writes_csv(tmp_path: Path):
    output = tmp_path / "exclusion.csv"
    assert (
        main(
            [
                "covering-prime-prefix-exclusion-witnesses",
                "--k",
                "4",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 209
    assert lines[0].startswith("k,new_prime,primorial,residue")


def test_covering_prime_prefix_exclusion_summary_cli_writes_csv(tmp_path: Path):
    output = tmp_path / "summary.csv"
    assert (
        main(
            [
                "covering-prime-prefix-exclusion-summary",
                "--k",
                "4",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 37
    assert lines[0].startswith("k,new_prime,primorial,uncovered_interval_count")


def test_covering_prime_prefix_birth_classification_cli_writes_csv(tmp_path: Path):
    output = tmp_path / "classification.csv"
    assert (
        main(
            [
                "covering-prime-prefix-birth-classification",
                "--k",
                "5",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 15
    assert lines[0].startswith("k,new_prime,primorial,residue")


def test_covering_prime_prefix_birth_pair_summary_cli_writes_csv(tmp_path: Path):
    output = tmp_path / "pair_summary.csv"
    assert (
        main(
            [
                "covering-prime-prefix-birth-pair-summary",
                "--k",
                "5",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 8
    assert lines[0].startswith("k,new_prime,primorial,reflection_pair_min")


def test_covering_prime_prefix_v15_clis_write_csvs(tmp_path: Path):
    witness_out = tmp_path / "witness_v15.csv"
    classification_out = tmp_path / "classification_v15.csv"
    pair_out = tmp_path / "pair_v15.csv"
    exclusion_witness_out = tmp_path / "exclusion_witness_v16.csv"
    exclusion_summary_out = tmp_path / "exclusion_summary_v15.csv"
    assert (
        main(
            [
                "covering-prime-prefix-birth-witnesses-v1-5",
                "--k",
                "5",
                "--out",
                str(witness_out),
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "covering-prime-prefix-birth-classification-v1-5",
                "--k",
                "5",
                "--out",
                str(classification_out),
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "covering-prime-prefix-birth-pair-summary-v1-5",
                "--k",
                "5",
                "--out",
                str(pair_out),
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "covering-prime-prefix-exclusion-witnesses-v1-6",
                "--k",
                "4",
                "--out",
                str(exclusion_witness_out),
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "covering-prime-prefix-exclusion-summary-v1-5",
                "--k",
                "4",
                "--out",
                str(exclusion_summary_out),
            ]
        )
        == 0
    )
    assert len(witness_out.read_text(encoding="utf-8").splitlines()) == 15
    assert len(classification_out.read_text(encoding="utf-8").splitlines()) == 15
    assert len(pair_out.read_text(encoding="utf-8").splitlines()) == 8
    assert len(exclusion_witness_out.read_text(encoding="utf-8").splitlines()) == 209
    assert len(exclusion_summary_out.read_text(encoding="utf-8").splitlines()) == 37


def test_prime_prefix_certificate_verifier_passes_public_csvs(tmp_path: Path):
    paths = _write_verifier_fixture(tmp_path)
    verification_out = tmp_path / "verification.csv"

    rows = prime_prefix_certificate_verification_rows(
        ck_full_csv=paths["ck_full"],
        c4_exclusion_witness_csv=paths["c4_witness"],
        c4_exclusion_summary_csv=paths["c4_summary"],
        b5_birth_witness_csv=paths["b5_witness"],
        b5_birth_classification_csv=paths["b5_classification"],
        b5_birth_pair_summary_csv=paths["b5_pair"],
    )
    write_prime_prefix_certificate_verification_csv(rows, verification_out)

    assert all(row.status == "pass" for row in rows)
    checks = {row.check_name: row for row in rows}
    assert checks["c4_exclusion_rational_witness_point"].passed == 208
    assert checks["c4_exclusion_residue_set_complete"].passed == 208
    assert checks["c4_exclusion_exact_fields"].passed == 208
    assert checks["c4_summary_partitions_witness_rows"].passed == 36
    assert checks["b5_ck_full_c5_rows_complete"].passed == 36
    assert checks["b5_birth_witness_residue_set_complete"].passed == 14
    assert checks["b5_birth_exact_witness_fields"].passed == 14
    assert checks["b5_birth_classification_matches_witnesses"].passed == 14
    assert checks["b5_pair_summary_matches_classification"].passed == 7
    assert verification_out.read_text(encoding="utf-8").splitlines()[0] == (
        "check_name,total,passed,failed,status"
    )


def test_prime_prefix_certificate_verifier_fails_tampered_gap(tmp_path: Path):
    paths = _write_verifier_fixture(tmp_path)

    _mutate_csv(
        paths["b5_witness"],
        lambda rows: [
            {**row, "previous_open_gap_boundary_endpoints": "1/4-3/4"}
            if index == 0
            else row
            for index, row in enumerate(rows)
        ],
    )

    containment = _verification_by_name(paths)[
        "b5_birth_old_open_gap_strictly_inside_new_arc"
    ]
    assert containment.status == "fail"
    assert containment.failed == 1


def test_prime_prefix_certificate_verifier_fails_completeness_tampering(
    tmp_path: Path,
):
    cases = [
        (
            "c4_witness",
            lambda rows: rows[:-1],
            "c4_exclusion_residue_set_complete",
        ),
        (
            "c4_witness",
            lambda rows: [rows[0], *rows],
            "c4_exclusion_residue_set_complete",
        ),
        (
            "c4_summary",
            lambda rows: [
                {**row, "residue_count": "999"}
                if index == 0
                else row
                for index, row in enumerate(rows)
            ],
            "c4_summary_partitions_witness_rows",
        ),
        (
            "c4_witness",
            lambda rows: [
                {**row, "uncovered_measure_fraction": "1/999"}
                if index == 0
                else row
                for index, row in enumerate(rows)
            ],
            "c4_exclusion_exact_fields",
        ),
        (
            "b5_witness",
            lambda rows: rows[:-1],
            "b5_birth_witness_residue_set_complete",
        ),
        (
            "b5_witness",
            lambda rows: [
                {**row, "previous_open_gap_boundary_endpoints": "71/100-18/25"}
                if index == 0
                else row
                for index, row in enumerate(rows)
            ],
            "b5_birth_exact_witness_fields",
        ),
        (
            "b5_witness",
            lambda rows: [
                {**row, "new_prime_closed_arc_boundary_endpoints": "7/10-3/4"}
                if index == 0
                else row
                for index, row in enumerate(rows)
            ],
            "b5_birth_exact_witness_fields",
        ),
        (
            "b5_classification",
            lambda rows: [
                {**row, "parent_residue_mod_previous": "999"}
                if index == 0
                else row
                for index, row in enumerate(rows)
            ],
            "b5_birth_classification_matches_witnesses",
        ),
        (
            "b5_pair",
            lambda rows: [
                {**row, "new_prime_remainder_pair": "9 / 3"}
                if index == 0
                else row
                for index, row in enumerate(rows)
            ],
            "b5_pair_summary_matches_classification",
        ),
    ]

    for file_key, mutate, expected_failed_check in cases:
        paths = _write_verifier_fixture(tmp_path / expected_failed_check)
        _mutate_csv(paths[file_key], mutate)
        check = _verification_by_name(paths)[expected_failed_check]
        assert check.status == "fail", expected_failed_check
        assert check.failed > 0, expected_failed_check


def test_covering_prime_prefix_verify_certificates_cli_writes_csv(tmp_path: Path):
    paths = _write_verifier_fixture(tmp_path)
    verification_out = tmp_path / "verification.csv"
    assert (
        main(
            [
                "covering-prime-prefix-verify-certificates",
                "--ck-full",
                str(paths["ck_full"]),
                "--c4-exclusion-witnesses",
                str(paths["c4_witness"]),
                "--c4-exclusion-summary",
                str(paths["c4_summary"]),
                "--b5-birth-witnesses",
                str(paths["b5_witness"]),
                "--b5-birth-classification",
                str(paths["b5_classification"]),
                "--b5-birth-pair-summary",
                str(paths["b5_pair"]),
                "--out",
                str(verification_out),
            ]
        )
        == 0
    )
    lines = verification_out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 15
    assert all(line.endswith(",pass") for line in lines[1:])


def test_covering_prime_prefix_verify_certificates_cli_fails_tampered_csv(
    tmp_path: Path,
):
    paths = _write_verifier_fixture(tmp_path)
    _mutate_csv(paths["c4_witness"], lambda rows: rows[:-1])
    verification_out = tmp_path / "verification.csv"

    assert (
        main(
            [
                "covering-prime-prefix-verify-certificates",
                "--ck-full",
                str(paths["ck_full"]),
                "--c4-exclusion-witnesses",
                str(paths["c4_witness"]),
                "--c4-exclusion-summary",
                str(paths["c4_summary"]),
                "--b5-birth-witnesses",
                str(paths["b5_witness"]),
                "--b5-birth-classification",
                str(paths["b5_classification"]),
                "--b5-birth-pair-summary",
                str(paths["b5_pair"]),
                "--out",
                str(verification_out),
            ]
        )
        == 1
    )
    rows = {row["check_name"]: row for row in csv.DictReader(verification_out.open())}
    assert rows["c4_exclusion_residue_set_complete"]["status"] == "fail"


def test_covering_prime_prefix_filtration_cli_rejects_large_k_without_flag(tmp_path: Path):
    with pytest.raises(ValueError, match="primorial-scale"):
        main(
            [
                "covering-prime-prefix-filtration",
                "--max-k",
                "8",
                "--summary-out",
                str(tmp_path / "summary.csv"),
                "--birth-samples-out",
                str(tmp_path / "birth.csv"),
            ]
        )


def test_covering_prime_prefix_filtration_cli_regenerates_committed_csvs(tmp_path: Path):
    summary_out = tmp_path / "summary.csv"
    birth_out = tmp_path / "birth.csv"
    assert (
        main(
            [
                "covering-prime-prefix-filtration",
                "--max-k",
                "7",
                "--birth-sample-limit",
                "200",
                "--summary-out",
                str(summary_out),
                "--birth-samples-out",
                str(birth_out),
            ]
        )
        == 0
    )
    assert summary_out.read_bytes() == Path(
        "data/summaries/prc_prime_prefix_residue_covering_filtration_v0_1.csv"
    ).read_bytes()
    assert birth_out.read_bytes() == Path(
        "data/summaries/prc_prime_prefix_residue_covering_birth_samples_v0_1.csv"
    ).read_bytes()


def test_public_finite_theorem_csvs_regenerate_byte_identically(tmp_path: Path):
    summary_out = tmp_path / "filtration.csv"
    birth_samples_out = tmp_path / "birth_samples.csv"
    full_out = tmp_path / "ck_full.csv"
    c4_witness_out = tmp_path / "c4_witness.csv"
    c4_summary_out = tmp_path / "c4_summary.csv"
    b5_witness_out = tmp_path / "b5_witness.csv"
    b5_classification_out = tmp_path / "b5_classification.csv"
    b5_pair_out = tmp_path / "b5_pair.csv"
    verification_out = tmp_path / "verification.csv"

    summary_rows, birth_rows = prime_prefix_residue_filtration_tables(
        max_k=7,
        birth_sample_limit=200,
    )
    write_prime_prefix_residue_filtration_csv(summary_rows, summary_out)
    write_prime_prefix_residue_birth_samples_csv(birth_rows, birth_samples_out)
    write_prime_prefix_residue_full_csv(
        prime_prefix_residue_full_rows(max_k=5),
        full_out,
    )
    write_prime_prefix_exclusion_witness_v16_csv(
        prime_prefix_exclusion_witness_v16_rows(k=4),
        c4_witness_out,
    )
    write_prime_prefix_exclusion_summary_v15_csv(
        prime_prefix_exclusion_summary_v15_rows(k=4),
        c4_summary_out,
    )
    write_prime_prefix_birth_witness_v15_csv(
        prime_prefix_birth_witness_v15_rows(k=5),
        b5_witness_out,
    )
    write_prime_prefix_birth_classification_v15_csv(
        prime_prefix_birth_classification_v15_rows(k=5),
        b5_classification_out,
    )
    write_prime_prefix_birth_pair_summary_v15_csv(
        prime_prefix_birth_pair_summary_v15_rows(k=5),
        b5_pair_out,
    )
    write_prime_prefix_certificate_verification_csv(
        prime_prefix_certificate_verification_rows(
            ck_full_csv=full_out,
            c4_exclusion_witness_csv=c4_witness_out,
            c4_exclusion_summary_csv=c4_summary_out,
            b5_birth_witness_csv=b5_witness_out,
            b5_birth_classification_csv=b5_classification_out,
            b5_birth_pair_summary_csv=b5_pair_out,
        ),
        verification_out,
    )

    expected_paths = {
        summary_out: "data/summaries/prc_prime_prefix_residue_covering_filtration_v0_1.csv",
        birth_samples_out: (
            "data/summaries/"
            "prc_prime_prefix_residue_covering_birth_samples_v0_1.csv"
        ),
        full_out: "data/summaries/prc_prime_prefix_ck_full_v1_1.csv",
        c4_witness_out: (
            "data/summaries/prc_prime_prefix_c4_exclusion_witness_v1_6.csv"
        ),
        c4_summary_out: (
            "data/summaries/prc_prime_prefix_c4_exclusion_summary_v1_5.csv"
        ),
        b5_witness_out: "data/summaries/prc_prime_prefix_birth_witness_v1_5.csv",
        b5_classification_out: (
            "data/summaries/prc_prime_prefix_b5_birth_classification_v1_5.csv"
        ),
        b5_pair_out: (
            "data/summaries/prc_prime_prefix_b5_birth_pair_summary_v1_5.csv"
        ),
        verification_out: (
            "data/summaries/"
            "prc_prime_prefix_certificate_verification_v1_7.csv"
        ),
    }
    for generated_path, committed_path in expected_paths.items():
        assert generated_path.read_bytes() == Path(committed_path).read_bytes()


def test_standalone_prime_prefix_certificate_checker_passes(tmp_path: Path):
    output = tmp_path / "standalone_verification.csv"
    result = subprocess.run(
        [
            sys.executable,
            "certificates/check_prime_prefix_c4_b5.py",
            "--out",
            str(output),
        ],
        check=False,
        cwd=Path(__file__).parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "checks=9, failed=0" in result.stdout
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 10
    assert all(line.endswith(",pass") for line in lines[1:])
    assert output.read_bytes() == Path(
        "data/summaries/prc_prime_prefix_certificate_standalone_verification_v1_8.csv"
    ).read_bytes()


def test_standalone_prime_prefix_certificate_checker_fails_missing_row(
    tmp_path: Path,
):
    paths = _write_verifier_fixture(tmp_path)
    output = tmp_path / "standalone_verification.csv"
    _mutate_csv(paths["c4_witness"], lambda rows: rows[:-1])

    result = subprocess.run(
        [
            sys.executable,
            "certificates/check_prime_prefix_c4_b5.py",
            "--ck-full",
            str(paths["ck_full"]),
            "--c4-exclusion-witnesses",
            str(paths["c4_witness"]),
            "--c4-exclusion-summary",
            str(paths["c4_summary"]),
            "--b5-birth-witnesses",
            str(paths["b5_witness"]),
            "--b5-birth-classification",
            str(paths["b5_classification"]),
            "--b5-birth-pair-summary",
            str(paths["b5_pair"]),
            "--out",
            str(output),
        ],
        check=False,
        cwd=Path(__file__).parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "failed=" in result.stdout
    rows = {row["check_name"]: row for row in csv.DictReader(output.open())}
    assert rows["c4_exclusion_rows_exact"]["status"] == "fail"


def test_public_release_checker_fails_hash_mismatch(tmp_path: Path):
    release_root = tmp_path / "release"
    release_root.mkdir()
    readme = release_root / "README.md"
    readme.write_text(
        "public release bundle\n"
        "finite `C_k/C_4/B_5`\n"
        "not included\n",
        encoding="utf-8",
    )
    digest = hashlib.sha256(readme.read_bytes()).hexdigest()
    (release_root / "SHA256SUMS").write_text(
        f"{digest}  README.md\n",
        encoding="utf-8",
    )

    checker = Path(__file__).parents[2] / "scripts" / "check_public_release.py"
    ok_result = subprocess.run(
        [sys.executable, str(checker), str(release_root)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert ok_result.returncode == 0

    readme.write_text(
        "public release bundle\n"
        "finite `C_k/C_4/B_5`\n"
        "not included\n"
        "changed\n",
        encoding="utf-8",
    )
    failed_result = subprocess.run(
        [sys.executable, str(checker), str(release_root)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert failed_result.returncode == 1
    assert "hash mismatch for README.md" in failed_result.stdout


def test_public_release_checker_rejects_internal_paths(tmp_path: Path):
    release_root = tmp_path / "release"
    release_root.mkdir()
    readme = release_root / "README.md"
    readme.write_text(
        "public release bundle\n"
        "finite `C_k/C_4/B_5`\n"
        "not included\n",
        encoding="utf-8",
    )
    private_note = release_root / "private_notes" / "secret.md"
    private_note.parent.mkdir()
    private_note.write_text("local note\n", encoding="utf-8")
    experiment_file = (
        release_root
        / "research"
        / "experiments"
        / "critical_radius_birth_dynamics"
        / "candidate_bundle_manifest_v0_1.json"
    )
    experiment_file.parent.mkdir(parents=True)
    experiment_file.write_text("{}\n", encoding="utf-8")
    manifest_lines = []
    for path in [readme, private_note, experiment_file]:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_lines.append(f"{digest}  {path.relative_to(release_root).as_posix()}")
    (release_root / "SHA256SUMS").write_text(
        "\n".join(manifest_lines) + "\n",
        encoding="utf-8",
    )

    checker = Path(__file__).parents[2] / "scripts" / "check_public_release.py"
    result = subprocess.run(
        [sys.executable, str(checker), str(release_root)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "private_notes" in result.stdout
    assert "research/experiments" in result.stdout
    assert "candidate_bundle_manifest" in result.stdout


def test_public_release_build_uses_config_default_version(tmp_path: Path):
    repo_root = Path(__file__).parents[2]
    builder = repo_root / "scripts" / "build_public_release.py"

    result = subprocess.run(
        [sys.executable, str(builder), "--out", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert (tmp_path / "PrimeClock-2.2.4").is_dir()
    assert "PrimeClock-2.2.4" in result.stdout


def test_public_release_build_fails_stale_version(tmp_path: Path):
    repo_root = Path(__file__).parents[2]
    builder = repo_root / "scripts" / "build_public_release.py"

    result = subprocess.run(
        [
            sys.executable,
            str(builder),
            "--version",
            "2.2.1",
            "--out",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "does not match release_config public_release" in result.stdout


def test_public_release_version_checker_passes_current_repo():
    repo_root = Path(__file__).parents[2]
    checker = repo_root / "scripts" / "check_release_versions.py"

    result = subprocess.run(
        [sys.executable, str(checker)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "release version check passed: v2.2.4" in result.stdout


def test_public_release_version_checker_rejects_wrong_doi_policy(tmp_path: Path):
    repo_root = Path(__file__).parents[2]
    builder = repo_root / "scripts" / "build_public_release.py"
    checker = repo_root / "scripts" / "check_release_versions.py"

    build_result = subprocess.run(
        [sys.executable, str(builder), "--out", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert build_result.returncode == 0

    bundle_root = tmp_path / "PrimeClock-2.2.4"
    config_path = bundle_root / "release" / "public" / "release_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["doi_policy"] = "version_doi_in_citation"
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(checker), "--repo-root", str(bundle_root)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "doi_policy must be" in result.stderr


def test_public_release_version_checker_passes_generated_bundle(tmp_path: Path):
    repo_root = Path(__file__).parents[2]
    builder = repo_root / "scripts" / "build_public_release.py"

    build_result = subprocess.run(
        [sys.executable, str(builder), "--out", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert build_result.returncode == 0

    bundle_root = tmp_path / "PrimeClock-2.2.4"
    checker = bundle_root / "scripts" / "check_release_versions.py"
    result = subprocess.run(
        [sys.executable, str(checker)],
        check=False,
        capture_output=True,
        text=True,
        cwd=bundle_root,
    )

    assert result.returncode == 0
    assert "release version check passed: v2.2.4" in result.stdout


def test_public_release_version_checker_rejects_old_workflow_actions(tmp_path: Path):
    repo_root = Path(__file__).parents[2]
    builder = repo_root / "scripts" / "build_public_release.py"
    checker = repo_root / "scripts" / "check_release_versions.py"

    build_result = subprocess.run(
        [sys.executable, str(builder), "--out", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert build_result.returncode == 0

    bundle_root = tmp_path / "PrimeClock-2.2.4"
    workflow = bundle_root / ".github" / "workflows" / "verify.yml"
    workflow.write_text(
        workflow.read_text(encoding="utf-8")
        .replace("actions/checkout@v6", "actions/checkout@v4")
        .replace("actions/setup-python@v6", "actions/setup-python@v5"),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(checker), "--repo-root", str(bundle_root)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "actions/checkout@v6" in result.stdout
    assert "actions/setup-python@v6" in result.stdout


def test_publish_public_release_dry_run_does_not_execute_remote_writes(tmp_path: Path):
    repo_root = Path(__file__).parents[2]
    publisher = repo_root / "scripts" / "publish_public_release.py"

    result = subprocess.run(
        [
            sys.executable,
            str(publisher),
            "--public-worktree",
            str(tmp_path / "missing-public-worktree"),
            "--build-parent",
            str(tmp_path / "build"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "mode: dry-run" in result.stdout
    assert "GitHub Release: no" in result.stdout
    assert "Zenodo target: no" in result.stdout
    assert "DRY-RUN:" in result.stdout
    assert "git push origin HEAD:main" in result.stdout
    assert "git tag" not in result.stdout
    assert "gh release create" not in result.stdout


def test_publish_public_release_doi_release_dry_run_creates_release_commands(tmp_path: Path):
    repo_root = Path(__file__).parents[2]
    builder = repo_root / "scripts" / "build_public_release.py"

    build_result = subprocess.run(
        [sys.executable, str(builder), "--out", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert build_result.returncode == 0

    bundle_root = tmp_path / "PrimeClock-2.2.4"
    config_path = bundle_root / "release" / "public" / "release_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["release_kind"] = "doi_release"
    config["zenodo_expected"] = True
    config["allow_github_release"] = True
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    publisher = bundle_root / "scripts" / "publish_public_release.py"
    result = subprocess.run(
        [
            sys.executable,
            str(publisher),
            "--public-worktree",
            str(tmp_path / "missing-public-worktree"),
            "--build-parent",
            str(tmp_path / "build"),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=bundle_root,
    )

    assert result.returncode == 0
    assert "GitHub Release: yes" in result.stdout
    assert "Zenodo target: yes" in result.stdout
    assert "git tag" in result.stdout
    assert "gh release create" in result.stdout
    assert "PrimeClock-2.2.4.zip" in result.stdout


def test_release_version_checker_rejects_top_level_version_doi(tmp_path: Path):
    repo_root = Path(__file__).parents[2]
    builder = repo_root / "scripts" / "build_public_release.py"
    checker = repo_root / "scripts" / "check_release_versions.py"

    build_result = subprocess.run(
        [sys.executable, str(builder), "--out", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert build_result.returncode == 0

    bundle_root = tmp_path / "PrimeClock-2.2.4"
    citation = bundle_root / "CITATION.cff"
    citation.write_text(
        citation.read_text(encoding="utf-8").replace(
            'doi: "10.5281/zenodo.20091722"',
            'doi: "10.5281/zenodo.20096689"',
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(checker), "--repo-root", str(bundle_root)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "CITATION.cff uses version DOI as top-level doi" in result.stdout


def test_finalize_release_doi_rejects_maintenance_sync(tmp_path: Path):
    repo_root = Path(__file__).parents[2]
    finalizer = repo_root / "scripts" / "finalize_release_doi.py"
    html = tmp_path / "zenodo.html"
    html.write_text(
        "concept 10.5281/zenodo.20091722 version 10.5281/zenodo.20096689\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(finalizer), "--html-file", str(html)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "refusing DOI finalization for release_kind=maintenance_sync" in result.stdout


def test_finalize_release_doi_reports_pending_for_doi_release(tmp_path: Path):
    repo_root = Path(__file__).parents[2]
    builder = repo_root / "scripts" / "build_public_release.py"
    finalizer = repo_root / "scripts" / "finalize_release_doi.py"

    build_result = subprocess.run(
        [sys.executable, str(builder), "--out", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert build_result.returncode == 0

    bundle_root = tmp_path / "PrimeClock-2.2.4"
    config_path = bundle_root / "release" / "public" / "release_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["release_kind"] = "doi_release"
    config["zenodo_expected"] = True
    config["allow_github_release"] = True
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    html = tmp_path / "zenodo.html"
    html.write_text("concept DOI only: 10.5281/zenodo.20091722\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(finalizer),
            "--repo-root",
            str(bundle_root),
            "--html-file",
            str(html),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "pending: no Zenodo version DOI found" in result.stdout


def test_finalize_release_doi_detects_version_doi_without_changing_citation(tmp_path: Path):
    repo_root = Path(__file__).parents[2]
    builder = repo_root / "scripts" / "build_public_release.py"
    finalizer = repo_root / "scripts" / "finalize_release_doi.py"

    build_result = subprocess.run(
        [sys.executable, str(builder), "--out", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert build_result.returncode == 0

    bundle_root = tmp_path / "PrimeClock-2.2.4"
    config_path = bundle_root / "release" / "public" / "release_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["release_kind"] = "doi_release"
    config["zenodo_expected"] = True
    config["allow_github_release"] = True
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    html = tmp_path / "zenodo.html"
    html.write_text(
        "concept 10.5281/zenodo.20091722 version 10.5281/zenodo.20096689\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(finalizer),
            "--repo-root",
            str(bundle_root),
            "--html-file",
            str(html),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "version DOI: 10.5281/zenodo.20096689" in result.stdout
    assert "dry-run" in result.stdout

    assert 'doi: "10.5281/zenodo.20091722"' in (bundle_root / "CITATION.cff").read_text(
        encoding="utf-8"
    )
