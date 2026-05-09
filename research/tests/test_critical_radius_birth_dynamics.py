from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

from prime_reciprocal_projection.covering_prime_prefix_filtration import (
    residue_is_exactly_covered,
)


EXPERIMENT_DIR = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "critical_radius_birth_dynamics"
)


def _load_tools():
    spec = importlib.util.spec_from_file_location(
        "critical_radius_birth_dynamics_tools",
        EXPERIMENT_DIR / "tools.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tools = _load_tools()


def test_critical_radius_c4_endpoint_residues():
    primes = [2, 3, 5, 7]
    assert tools.critical_radius_certificate(2, primes)[0] == Fraction(1, 2)
    assert tools.critical_radius_certificate(208, primes)[0] == Fraction(1, 2)


def test_critical_radius_level_set_matches_c4():
    primes = [2, 3, 5, 7]
    covered_by_radius = {
        residue
        for residue in range(210)
        if tools.critical_radius_certificate(residue, primes)[0] <= Fraction(1, 2)
    }
    assert covered_by_radius == {2, 208}


def test_critical_radius_level_set_matches_c5_count():
    primes = [2, 3, 5, 7, 11]
    covered_by_radius = {
        residue
        for residue in range(2310)
        if tools.critical_radius_certificate(residue, primes)[0] <= Fraction(1, 2)
    }
    assert len(covered_by_radius) == 36
    assert all(residue_is_exactly_covered(residue, primes) for residue in covered_by_radius)


def test_critical_radius_reflection_invariance_for_k5():
    primes = [2, 3, 5, 7, 11]
    modulus = 2310
    for residue in [0, 2, 118, 849, 1202, 2309]:
        radius = tools.critical_radius_certificate(residue, primes)[0]
        reflected = tools.critical_radius_certificate((-residue) % modulus, primes)[0]
        assert radius == reflected


def test_critical_radius_rows_have_stable_statuses():
    rows = tools.critical_radius_rows(min_k=4, max_k=4)
    assert [row.__dataclass_fields__.keys() for row in rows[:1]]
    assert sum(row.status == "endpoint_covered" for row in rows) == 2
    assert sum(row.current_covering_residue for row in rows) == 2


def test_critical_radius_summary_counts_match_level_sets():
    rows = tools.critical_radius_rows(min_k=4, max_k=5)
    summary = {row.k: row for row in tools.critical_radius_summary_rows(rows)}

    assert summary[4].residue_count == 210
    assert summary[4].covered_count == 2
    assert summary[4].endpoint_covered_count == 2
    assert summary[4].robust_covered_count == 0
    assert summary[4].nearest_uncovered_lambda_fraction

    assert summary[5].residue_count == 2310
    assert summary[5].covered_count == 36
    assert summary[5].covered_count == (
        summary[5].robust_covered_count + summary[5].endpoint_covered_count
    )


def test_critical_radius_near_misses_are_sorted_uncovered_rows():
    rows = tools.critical_radius_rows(min_k=4, max_k=5)
    near_misses = tools.critical_radius_near_miss_rows(rows, limit_per_k=5)
    grouped = {
        k: [row for row in near_misses if row.k == k]
        for k in [4, 5]
    }

    assert {k: len(group) for k, group in grouped.items()} == {4: 5, 5: 5}
    assert grouped[4][0].lambda_fraction == "5/9"
    assert grouped[5][0].lambda_fraction == "7/13"

    for group in grouped.values():
        margins = [Fraction(row.lambda_minus_half_fraction) for row in group]
        assert margins == sorted(margins)
        assert all(margin > 0 for margin in margins)
        assert [row.near_miss_rank for row in group] == list(range(1, len(group) + 1))


def test_near_miss_birth_parent_overlap_links_next_birth_layer():
    radius_rows = tools.critical_radius_rows(min_k=4, max_k=5)
    near_misses = tools.critical_radius_near_miss_rows(radius_rows, limit_per_k=20)
    parent_rows = tools.near_miss_birth_parent_rows(near_misses)
    grouped = {
        k: [row for row in parent_rows if row.k == k]
        for k in [4, 5]
    }

    assert {k: len(group) for k, group in grouped.items()} == {4: 20, 5: 20}
    assert sum(row.birth_lift_count > 0 for row in grouped[4]) == 13
    assert sum(row.birth_lift_count > 0 for row in grouped[5]) == 19

    for row in parent_rows:
        assert row.next_k == row.k + 1
        if row.birth_lift_count:
            residues = row.birth_lift_residues.split()
            remainders = row.birth_lift_remainders.split()
            assert len(residues) == row.birth_lift_count
            assert len(remainders) == row.birth_lift_count
            assert set(row.birth_types.split()) == {"strict_single_gap_birth"}


def test_near_miss_gap_geometry_matches_birth_parent_overlap():
    radius_rows = tools.critical_radius_rows(min_k=4, max_k=5)
    near_misses = tools.critical_radius_near_miss_rows(radius_rows, limit_per_k=20)
    parent_rows = tools.near_miss_birth_parent_rows(near_misses)
    gap_rows = tools.near_miss_gap_geometry_rows(near_misses)

    parent_by_key = {(row.k, row.residue): row for row in parent_rows}
    assert len(gap_rows) == 40
    for row in gap_rows:
        parent = parent_by_key[(row.k, row.residue)]
        assert row.containing_remainder_count == parent.birth_lift_count
        assert row.containing_remainders == parent.birth_lift_remainders
        assert row.previous_open_gap_count >= 1
        assert Fraction(row.previous_uncovered_measure_fraction) > 0
        assert Fraction(row.max_previous_open_gap_length_fraction) > 0
        if row.containing_remainder_count:
            assert row.best_containment_margin_fraction
            assert Fraction(row.best_containment_margin_fraction) > 0


def test_b5_threshold_crossing_rows_connect_parent_and_child_radius():
    rows = tools.birth_threshold_crossing_rows(min_k=5)

    assert len(rows) == 14
    assert {row.birth_type for row in rows} == {"strict_single_gap_birth"}
    for row in rows:
        assert Fraction(row.parent_lambda_fraction) > Fraction(1, 2)
        assert Fraction(row.current_lambda_fraction) <= Fraction(1, 2)
        assert row.parent_status == "uncovered"
        assert row.current_status in {"robust_covered", "endpoint_covered"}


def test_threshold_crossing_rows_cover_b5_b6_b7_births():
    rows = tools.birth_threshold_crossing_rows(min_k=5, max_k=7)
    counts = {k: sum(row.k == k for row in rows) for k in [5, 6, 7]}

    assert counts == {5: 14, 6: 42, 7: 714}
    assert {row.birth_type for row in rows} == {"strict_single_gap_birth"}
    for row in rows:
        assert Fraction(row.parent_lambda_fraction) > Fraction(1, 2)
        assert Fraction(row.current_lambda_fraction) <= Fraction(1, 2)
        assert row.parent_status == "uncovered"
        assert row.current_status in {"robust_covered", "endpoint_covered"}


def test_birth_dynamics_counts_and_summary_through_k7():
    rows = tools.birth_dynamics_rows(min_k=5, max_k=7)
    summary = {row.k: row for row in tools.birth_dynamics_summary_rows(rows)}

    assert summary[5].birth_count == 14
    assert summary[6].birth_count == 42
    assert summary[7].birth_count == 714

    for row in summary.values():
        classified = (
            row.strict_single_gap_birth
            + row.endpoint_single_gap_birth
            + row.strict_multi_gap_birth
            + row.endpoint_multi_gap_birth
        )
        assert classified == row.birth_count


def test_b5_births_are_strict_single_gap_births():
    rows = [row for row in tools.birth_dynamics_rows(min_k=5, max_k=5) if row.k == 5]
    assert len(rows) == 14
    assert {row.birth_type for row in rows} == {"strict_single_gap_birth"}
    assert all(row.previous_open_gap_count == 1 for row in rows)
    assert all(not row.uses_endpoint_touching for row in rows)


def test_integrated_experiment_note_keeps_scope_narrow():
    note = EXPERIMENT_DIR / "notes" / "prc_critical_radius_birth_dynamics_v0_1.md"
    text = note.read_text(encoding="utf-8")

    assert "C_k = { r : lambda_k(r) <= 1/2 }" in text
    assert "B_7: 714 strict single-gap births" in text
    assert "not a general theorem for all levels" in text
    assert "does not claim" in text


def test_near_miss_predictor_note_keeps_gap_geometry_boundary():
    note = EXPERIMENT_DIR / "notes" / "prc_near_miss_birth_predictor_v0_2.md"
    text = note.read_text(encoding="utf-8")

    assert "k=4 near-misses: 13/20 are B_5 birth parents" in text
    assert "k=5 near-misses: 19/20 are B_6 birth parents" in text
    assert "near-miss rank is useful but not sufficient" in text
    assert "near-miss candidate + containing next-prime remainder" in text
    assert "does not claim" in text
