from fractions import Fraction

import pytest

from prime_reciprocal_projection.covering import (
    covered_intervals,
    covering_summary,
    exact_is_completely_covered,
    exact_uncovered_intervals,
    exact_uncovered_measure,
    max_uncovered_gap,
    merge_circular_intervals,
    prime_arcs,
    uncovered_intervals,
    uncovered_measure,
)
from prime_reciprocal_projection.primes import primes_up_to


def test_prime_arcs_use_phi_center_and_one_over_p_width():
    arcs = prime_arcs(10, primes=[3])
    assert len(arcs) == 1
    assert arcs[0].center == pytest.approx(1 / 3)
    assert arcs[0].radius == pytest.approx(1 / 6)
    assert arcs[0].width == pytest.approx(1 / 3)


def test_wraparound_arc_is_split_for_coverage():
    intervals = covered_intervals(10, primes=[5])
    assert intervals == pytest.approx([(0.0, 0.1), (0.9, 1.0)])
    gaps = uncovered_intervals(10, primes=[5])
    assert gaps == pytest.approx([(0.1, 0.9)])
    assert uncovered_measure(10, primes=[5]) == pytest.approx(0.8)


def test_touching_intervals_merge():
    intervals = merge_circular_intervals([(0.0, 0.25), (0.25, 0.5), (0.75, 1.0)])
    assert intervals == [(0.0, 0.5), (0.75, 1.0)]


def test_full_coverage_has_no_uncovered_intervals():
    merged = merge_circular_intervals([(0.0, 0.25), (0.25, 1.0)])
    assert merged == [(0.0, 1.0)]


def test_empty_custom_prime_set_leaves_full_circle_uncovered():
    assert uncovered_intervals(10, primes=[]) == [(0.0, 1.0)]
    assert uncovered_measure(10, primes=[]) == 1.0
    assert max_uncovered_gap(10, primes=[]) == 1.0


def test_exact_uncovered_measure_matches_float_for_small_oracle():
    assert exact_uncovered_intervals(10, primes=[5])
    assert not exact_is_completely_covered(10, primes=[5])
    assert exact_uncovered_measure(10, primes=[5]) == Fraction(4, 5)
    assert exact_uncovered_measure(10, primes=[3]) == Fraction(2, 3)
    assert uncovered_measure(10, primes=[3]) == pytest.approx(float(exact_uncovered_measure(10, primes=[3])))


def test_exact_uncovered_intervals_use_circular_gap_topology():
    float_gap = uncovered_intervals(10, primes=[3])[0]
    assert float_gap[0] == pytest.approx(0.5)
    assert float_gap[1] == pytest.approx(1 / 6)
    assert exact_uncovered_intervals(10, primes=[3]) == [(Fraction(1, 2), Fraction(1, 6))]
    assert exact_uncovered_measure(10, primes=[3]) == Fraction(2, 3)


def test_covering_bounds_and_branch1_monotonicity():
    for n in [100, 1000]:
        a = uncovered_measure(n)
        g = max_uncovered_gap(n)
        a1 = uncovered_measure(n, branch=1)
        g1 = max_uncovered_gap(n, branch=1)
        assert 0 <= a <= 1
        assert 0 <= g <= a
        assert a <= a1 + 1e-12
        assert g <= g1 + 1e-12


def test_branch_one_matches_primes_between_n_over_two_and_n():
    n = 100
    arcs = prime_arcs(n, branch=1)
    assert arcs
    assert all(n / 2 < arc.p <= n for arc in arcs)
    assert {arc.p for arc in arcs} == {p for p in primes_up_to(n) if n / 2 < p <= n}


def test_covering_summary_has_scale_events_and_gap_quantiles():
    summary = covering_summary(1000)
    assert summary.n == 1000
    assert summary.prime_count == 168
    assert 0 <= summary.uncovered_measure <= 1
    assert 0 <= summary.max_uncovered_gap <= summary.uncovered_measure
    assert summary.gap_p50 <= summary.gap_p90 <= summary.gap_p99


def test_invalid_branch_rejected():
    with pytest.raises(ValueError):
        prime_arcs(10, branch=0)
    with pytest.raises(TypeError):
        prime_arcs(10, branch=1.5)  # type: ignore[arg-type]
