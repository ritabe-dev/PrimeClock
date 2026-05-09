"""CSV metrics for Prime Reciprocal Covering experiments."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from .covering import covering_summary
from .primes import primes_up_to
from .projection import validate_n


@dataclass(frozen=True)
class CoveringRow:
    """One PRC covering summary row for a fixed N."""

    n: int
    prime_count: int
    uncovered_measure: float
    uncovered_measure_times_log_n: float
    random_arc_baseline: float
    poisson_arc_baseline: float
    product_arc_baseline: float
    max_uncovered_gap: float
    complete_scale_1_over_n: bool
    complete_scale_1_over_pi_n: bool
    complete_numeric_1e_9: bool
    branch1_uncovered_measure: float
    branch1_max_uncovered_gap: float
    branch1_exposed_gap_estimate: float
    gap_fill_ratio: float | None
    gap_fill_drop: float
    uncovered_component_count: int
    gap_p50: float
    gap_p90: float
    gap_p99: float


def random_arc_baseline(n: int, primes: list[int] | None = None) -> float:
    """Return the legacy Poisson arc uncovered-measure baseline."""
    return poisson_arc_baseline(n, primes=primes)


def poisson_arc_baseline(n: int, primes: list[int] | None = None) -> float:
    """Return ``exp(-sum 1/p)``, the Poissonized random-arc approximation."""
    n = validate_n(n)
    prime_values = primes_up_to(n) if primes is None else [p for p in primes if p <= n]
    harmonic_prime_width = sum(1.0 / p for p in prime_values)
    return math.exp(-harmonic_prime_width)


def product_arc_baseline(n: int, primes: list[int] | None = None) -> float:
    """Return ``prod(1 - 1/p)``, the fixed-point random-arc baseline."""
    n = validate_n(n)
    prime_values = primes_up_to(n) if primes is None else [p for p in primes if p <= n]
    baseline = 1.0
    for p in prime_values:
        baseline *= 1.0 - 1.0 / p
    return baseline


def branch1_exposed_gap_estimate(n: int, primes: list[int] | None = None) -> float:
    """Return the largest circular branch-1 transformed exposed-gap estimate."""
    n = validate_n(n)
    prime_values = primes_up_to(n) if primes is None else [p for p in primes if p <= n]
    branch1_primes = [p for p in prime_values if n // p == 1]
    if len(branch1_primes) < 2:
        return 0.0
    estimates = []
    arc_data = sorted(
        ((n / p - 1.0, 1.0 / (2.0 * p)) for p in branch1_primes),
        key=lambda item: item[0],
    )
    for index, (center, radius) in enumerate(arc_data):
        next_center, next_radius = arc_data[(index + 1) % len(arc_data)]
        transformed_gap = next_center - center
        if index == len(arc_data) - 1:
            transformed_gap += 1.0
        exposed = transformed_gap - radius - next_radius
        estimates.append(max(0.0, exposed))
    return max(estimates, default=0.0)


def covering_row(n: int, primes: list[int] | None = None) -> CoveringRow:
    """Compute PRC covering metrics for one integer N."""
    summary = covering_summary(n, primes=primes)
    poisson_baseline = poisson_arc_baseline(n, primes=primes)
    product_baseline = product_arc_baseline(n, primes=primes)
    return CoveringRow(
        n=summary.n,
        prime_count=summary.prime_count,
        uncovered_measure=summary.uncovered_measure,
        uncovered_measure_times_log_n=summary.uncovered_measure * math.log(summary.n),
        random_arc_baseline=poisson_baseline,
        poisson_arc_baseline=poisson_baseline,
        product_arc_baseline=product_baseline,
        max_uncovered_gap=summary.max_uncovered_gap,
        complete_scale_1_over_n=summary.complete_scale_1_over_n,
        complete_scale_1_over_pi_n=summary.complete_scale_1_over_pi_n,
        complete_numeric_1e_9=summary.complete_numeric_1e_9,
        branch1_uncovered_measure=summary.branch1_uncovered_measure,
        branch1_max_uncovered_gap=summary.branch1_max_uncovered_gap,
        branch1_exposed_gap_estimate=branch1_exposed_gap_estimate(summary.n, primes=primes),
        gap_fill_ratio=summary.gap_fill_ratio,
        gap_fill_drop=summary.gap_fill_drop,
        uncovered_component_count=summary.uncovered_component_count,
        gap_p50=summary.gap_p50,
        gap_p90=summary.gap_p90,
        gap_p99=summary.gap_p99,
    )


def covering_table(ns: list[int]) -> list[CoveringRow]:
    """Compute PRC covering rows for a list of N values."""
    if not ns:
        return []
    prime_pool = primes_up_to(max(ns))
    return [covering_row(n, primes=prime_pool) for n in ns]


def write_covering_csv(rows: list[CoveringRow], output_path: str | Path) -> None:
    """Write PRC covering rows as CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(CoveringRow.__dataclass_fields__.keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    field: "" if (value := getattr(row, field)) is None else value
                    for field in fieldnames
                }
            )
