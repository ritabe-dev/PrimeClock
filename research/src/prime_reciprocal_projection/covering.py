"""Prime Reciprocal Covering on the unit circle."""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

from .primes import primes_up_to
from .projection import phi, validate_n

Interval = tuple[float, float]
ExactInterval = tuple[Fraction, Fraction]
ExactRawInterval = tuple[int, int, int, int]


@dataclass(frozen=True)
class PrimeArc:
    """One prime-indexed circular arc in PRC."""

    p: int
    center: float
    radius: float

    @property
    def width(self) -> float:
        """Return the total arc width."""
        return 2.0 * self.radius


@dataclass(frozen=True)
class CoveringSummary:
    """Coverage summary for a fixed integer N."""

    n: int
    prime_count: int
    uncovered_measure: float
    max_uncovered_gap: float
    complete_scale_1_over_n: bool
    complete_scale_1_over_pi_n: bool
    complete_numeric_1e_9: bool
    branch1_uncovered_measure: float
    branch1_max_uncovered_gap: float
    gap_fill_ratio: float | None
    gap_fill_drop: float
    uncovered_component_count: int
    gap_p50: float
    gap_p90: float
    gap_p99: float


def _filtered_primes(n: int, primes: Iterable[int] | None, branch: int | None) -> list[int]:
    if branch is not None and (isinstance(branch, bool) or not isinstance(branch, int)):
        raise TypeError("branch must be an integer or None")
    if branch is not None and branch < 1:
        raise ValueError("branch must be >= 1")

    values = primes_up_to(n) if primes is None else [p for p in primes if p <= n]
    if branch is None:
        return values
    return [p for p in values if n // p == branch]


def prime_arcs(n: int, primes: Iterable[int] | None = None, branch: int | None = None) -> list[PrimeArc]:
    """Return prime-indexed arcs for ``N`` on ``R/Z``.

    Each arc has center ``{N/p}`` and radius ``1/(2p)``. If ``branch`` is an
    integer, only primes with ``floor(N/p) == branch`` are included.
    """
    n = validate_n(n)
    return [PrimeArc(p=p, center=phi(n, p), radius=1.0 / (2.0 * p)) for p in _filtered_primes(n, primes, branch)]


def _arc_intervals(arc: PrimeArc) -> list[Interval]:
    start = arc.center - arc.radius
    end = arc.center + arc.radius
    if arc.width >= 1.0:
        return [(0.0, 1.0)]
    if start < 0.0:
        return [(0.0, end), (1.0 + start, 1.0)]
    if end > 1.0:
        return [(0.0, end - 1.0), (start, 1.0)]
    return [(start, end)]


def merge_circular_intervals(intervals: Iterable[Interval], *, tolerance: float = 0.0) -> list[Interval]:
    """Merge normalized half-open intervals in ``[0, 1)``.

    Touching intervals are merged. ``tolerance`` expands the touching rule but
    does not change returned endpoints.
    """
    if tolerance < 0:
        raise ValueError("tolerance must be >= 0")

    normalized: list[Interval] = []
    for start, end in intervals:
        if start < 0.0 or end < 0.0 or start > 1.0 or end > 1.0:
            raise ValueError("intervals must be normalized to [0, 1]")
        if end < start:
            raise ValueError("interval start must be <= end")
        if math.isclose(start, end, rel_tol=0.0, abs_tol=tolerance):
            continue
        normalized.append((start, end))

    if not normalized:
        return []

    normalized.sort()
    merged: list[Interval] = []
    current_start, current_end = normalized[0]
    for start, end in normalized[1:]:
        if start <= current_end + tolerance:
            current_end = max(current_end, end)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end
    merged.append((current_start, current_end))

    if len(merged) == 1:
        start, end = merged[0]
        if start <= tolerance and end >= 1.0 - tolerance:
            return [(0.0, 1.0)]
    return merged


def covered_intervals(
    n: int,
    primes: Iterable[int] | None = None,
    branch: int | None = None,
    *,
    tolerance: float = 0.0,
) -> list[Interval]:
    """Return merged covered intervals for PRC arcs."""
    arcs = prime_arcs(n, primes=primes, branch=branch)
    intervals = [interval for arc in arcs for interval in _arc_intervals(arc)]
    return merge_circular_intervals(intervals, tolerance=tolerance)


def exact_covered_intervals(
    n: int,
    primes: Iterable[int] | None = None,
    branch: int | None = None,
) -> list[ExactInterval]:
    """Return merged covered intervals using exact rational endpoints."""
    n = validate_n(n)
    intervals = [
        interval
        for p in _filtered_primes(n, primes, branch)
        for interval in _exact_arc_intervals(n, p)
    ]
    return _merge_exact_intervals(intervals)


def uncovered_intervals(
    n: int,
    primes: Iterable[int] | None = None,
    branch: int | None = None,
    *,
    tolerance: float = 0.0,
) -> list[Interval]:
    """Return connected uncovered intervals in ``[0, 1)``."""
    covered = covered_intervals(n, primes=primes, branch=branch, tolerance=tolerance)
    if not covered:
        return [(0.0, 1.0)]
    if len(covered) == 1 and covered[0] == (0.0, 1.0):
        return []

    gaps: list[Interval] = []
    for index, (start, end) in enumerate(covered):
        next_start = covered[(index + 1) % len(covered)][0]
        if index == len(covered) - 1:
            gap_start = end
            gap_end = next_start + 1.0
        else:
            gap_start = end
            gap_end = next_start
        length = gap_end - gap_start
        if length > tolerance:
            gaps.append((gap_start % 1.0, gap_end % 1.0))
    return gaps


def exact_uncovered_intervals(
    n: int,
    primes: Iterable[int] | None = None,
    branch: int | None = None,
) -> list[ExactInterval]:
    """Return exact connected uncovered intervals in ``[0, 1)``."""
    covered = exact_covered_intervals(n, primes=primes, branch=branch)
    if not covered:
        return [(Fraction(0), Fraction(1))]
    if len(covered) == 1 and covered[0] == (Fraction(0), Fraction(1)):
        return []

    one = Fraction(1)
    gaps: list[ExactInterval] = []
    for index, (_, end) in enumerate(covered):
        next_start = covered[(index + 1) % len(covered)][0]
        gap_start = end
        gap_end = next_start + one if index == len(covered) - 1 else next_start
        if gap_end > gap_start:
            gaps.append((gap_start % one, gap_end % one))
    return gaps


def uncovered_measure(
    n: int,
    primes: Iterable[int] | None = None,
    branch: int | None = None,
    *,
    tolerance: float = 0.0,
) -> float:
    """Return ``A(N)``, the total uncovered measure."""
    gaps = uncovered_intervals(n, primes=primes, branch=branch, tolerance=tolerance)
    return sum(_interval_length(gap) for gap in gaps)


def is_completely_covered_numeric(
    n: int,
    primes: Iterable[int] | None = None,
    *,
    tolerance: float = 1e-12,
) -> bool:
    """Return whether floating-point PRC intervals cover the circle.

    This is a fast prefilter, not an exact mathematical certificate. Exact
    claims should still call ``exact_is_completely_covered``.
    """
    covered = covered_intervals(n, primes=primes, tolerance=tolerance)
    return len(covered) == 1 and covered[0] == (0.0, 1.0)


def exact_uncovered_measure(
    n: int,
    primes: Iterable[int] | None = None,
    branch: int | None = None,
) -> Fraction:
    """Return exact ``A(N)`` as a rational number."""
    gaps = exact_uncovered_intervals(n, primes=primes, branch=branch)
    return sum((_exact_interval_length(gap) for gap in gaps), Fraction(0))


def exact_is_completely_covered(n: int, primes: Iterable[int] | None = None) -> bool:
    """Return whether PRC exactly covers the circle for ``N``."""
    n = validate_n(n)
    intervals = [
        interval for p in _filtered_primes(n, primes, None) for interval in _exact_raw_arc_intervals(n, p)
    ]
    if not intervals:
        return False
    intervals.sort(key=lambda interval: interval[0] / interval[1])
    current_start_num, current_start_den, current_end_num, current_end_den = intervals[0]
    for start_num, start_den, end_num, end_den in intervals[1:]:
        if start_num * current_end_den <= current_end_num * start_den:
            if end_num * current_end_den > current_end_num * end_den:
                current_end_num, current_end_den = end_num, end_den
        else:
            return False
    return current_start_num == 0 and current_end_num >= current_end_den


def max_uncovered_gap(
    n: int,
    primes: Iterable[int] | None = None,
    branch: int | None = None,
    *,
    tolerance: float = 0.0,
) -> float:
    """Return ``G(N)``, the largest connected uncovered gap."""
    gaps = uncovered_intervals(n, primes=primes, branch=branch, tolerance=tolerance)
    return max((_interval_length(gap) for gap in gaps), default=0.0)


def gap_quantile(gaps: Iterable[Interval], quantile: float) -> float:
    """Return a linear-interpolated quantile of uncovered gap lengths."""
    if not 0.0 <= quantile <= 1.0:
        raise ValueError("quantile must be in [0, 1]")
    values = sorted(_interval_length(gap) for gap in gaps)
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    position = quantile * (len(values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]
    weight = position - lower
    return values[lower] * (1.0 - weight) + values[upper] * weight


def covering_summary(
    n: int,
    *,
    primes: Iterable[int] | None = None,
    epsilon_numeric: float = 1e-9,
) -> CoveringSummary:
    """Return PRC covering metrics for one integer ``N``."""
    n = validate_n(n)
    if epsilon_numeric < 0:
        raise ValueError("epsilon_numeric must be >= 0")
    prime_values = primes_up_to(n) if primes is None else [p for p in primes if p <= n]
    prime_count = len(prime_values)

    gaps = uncovered_intervals(n, primes=prime_values)
    measure = sum(_interval_length(gap) for gap in gaps)
    max_gap = max((_interval_length(gap) for gap in gaps), default=0.0)

    branch1_gaps = uncovered_intervals(n, primes=prime_values, branch=1)
    branch1_measure = sum(_interval_length(gap) for gap in branch1_gaps)
    branch1_max_gap = max((_interval_length(gap) for gap in branch1_gaps), default=0.0)
    gap_fill_ratio = max_gap / branch1_max_gap if branch1_max_gap > 0 else None

    return CoveringSummary(
        n=n,
        prime_count=prime_count,
        uncovered_measure=measure,
        max_uncovered_gap=max_gap,
        complete_scale_1_over_n=measure < 1.0 / n,
        complete_scale_1_over_pi_n=measure < 1.0 / prime_count,
        complete_numeric_1e_9=measure < epsilon_numeric,
        branch1_uncovered_measure=branch1_measure,
        branch1_max_uncovered_gap=branch1_max_gap,
        gap_fill_ratio=gap_fill_ratio,
        gap_fill_drop=branch1_max_gap - max_gap,
        uncovered_component_count=len(gaps),
        gap_p50=gap_quantile(gaps, 0.50),
        gap_p90=gap_quantile(gaps, 0.90),
        gap_p99=gap_quantile(gaps, 0.99),
    )


def _interval_length(interval: Interval) -> float:
    start, end = interval
    if end >= start:
        return end - start
    return 1.0 - start + end


def _exact_interval_length(interval: ExactInterval) -> Fraction:
    start, end = interval
    if end >= start:
        return end - start
    return Fraction(1) - start + end


def _exact_arc_intervals(n: int, p: int) -> list[ExactInterval]:
    center = Fraction(n % p, p)
    radius = Fraction(1, 2 * p)
    start = center - radius
    end = center + radius
    one = Fraction(1)
    if start < 0:
        return [(Fraction(0), end), (one + start, one)]
    if end > one:
        return [(Fraction(0), end - one), (start, one)]
    return [(start, end)]


def _exact_raw_arc_intervals(n: int, p: int) -> list[ExactRawInterval]:
    remainder = n % p
    denominator = 2 * p
    start = 2 * remainder - 1
    end = 2 * remainder + 1
    if start < 0:
        return [(0, 1, end, denominator), (denominator + start, denominator, 1, 1)]
    if end > denominator:
        return [(0, 1, end - denominator, denominator), (start, denominator, 1, 1)]
    return [(start, denominator, end, denominator)]


def _merge_exact_intervals(intervals: Iterable[ExactInterval]) -> list[ExactInterval]:
    normalized = [(start, end) for start, end in intervals if start != end]
    if not normalized:
        return []
    normalized.sort()
    merged: list[ExactInterval] = []
    current_start, current_end = normalized[0]
    for start, end in normalized[1:]:
        if start <= current_end:
            current_end = max(current_end, end)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end
    merged.append((current_start, current_end))
    if len(merged) == 1 and merged[0] == (Fraction(0), Fraction(1)):
        return [(Fraction(0), Fraction(1))]
    return merged
