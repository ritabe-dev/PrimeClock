from fractions import Fraction
from pathlib import Path

import pytest

from prime_reciprocal_projection.cli import main
from prime_reciprocal_projection.covering_prime_prefix_filtration import (
    PrimePrefixBirthWitnessRow,
    PrimePrefixResidueBirthSampleRow,
    PrimePrefixResidueFiltrationRow,
    PrimePrefixResidueFullRow,
    prime_prefix_birth_witness_rows,
    prime_prefix_residue_filtration_tables,
    prime_prefix_residue_full_rows,
    residue_is_exactly_covered,
    residue_uncovered_measure,
    write_prime_prefix_birth_witness_csv,
    write_prime_prefix_residue_birth_samples_csv,
    write_prime_prefix_residue_filtration_csv,
    write_prime_prefix_residue_full_csv,
)
from prime_reciprocal_projection.primes import primes_up_to


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
    assert full_out.read_text(encoding="utf-8").splitlines()[0] == (
        "k,new_prime,primorial,residue,residue_mod_previous,status,"
        "reflection_residue,previous_prefix_uncovered_measure"
    )
    assert witness_out.read_text(encoding="utf-8").splitlines()[0] == (
        "k,new_prime,primorial,residue,residue_mod_previous,reflection_residue,"
        "previous_uncovered_interval_count,previous_prefix_uncovered_measure,"
        "previous_uncovered_intervals,new_prime_arc_intervals,uses_endpoint_touching"
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
