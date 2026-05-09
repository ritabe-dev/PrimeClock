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


def test_b5_threshold_crossing_rows_connect_parent_and_child_radius():
    rows = tools.birth_threshold_crossing_rows(k=5)

    assert len(rows) == 14
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
