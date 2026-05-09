"""Prime-prefix residual profiles for Prime Reciprocal Covering."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .covering import gap_quantile, is_completely_covered_numeric, uncovered_intervals
from .primes import primes_up_to
from .projection import validate_n

DEFAULT_PREFIX_CHECKPOINTS = (
    2,
    3,
    5,
    7,
    11,
    13,
    17,
    19,
    23,
    29,
    31,
    47,
    97,
    199,
    499,
    997,
    1999,
    4999,
    9973,
    19997,
    49999,
    99991,
    199999,
    499979,
    999983,
)


@dataclass(frozen=True)
class PrimePrefixProfileRow:
    """One prime-prefix residual profile row for a fixed ``N`` and prefix ``P``."""

    n: int
    p_prefix: int
    prime_index: int
    prefix_width_sum: float
    poisson_prefix_baseline: float
    product_prefix_baseline: float
    uncovered_measure: float
    uncovered_over_product_baseline: float
    baseline_delta: float
    log_uncovered_minus_log_product_baseline: float
    component_count: int
    max_gap: float
    gap_p50: float
    gap_p90: float
    gap_p99: float
    top_gap_share: float
    numeric_complete_prefix: bool


def prime_prefix_profile_rows(
    ns: Iterable[int],
    *,
    checkpoints: Iterable[int] = DEFAULT_PREFIX_CHECKPOINTS,
    numeric_tolerance: float = 1e-12,
) -> list[PrimePrefixProfileRow]:
    """Return prime-prefix residual profile rows for the given ``N`` values."""
    n_values = sorted({validate_n(n) for n in ns})
    if not n_values:
        return []
    if numeric_tolerance < 0:
        raise ValueError("numeric_tolerance must be >= 0")

    checkpoint_values = _validated_checkpoints(checkpoints)
    prime_pool = primes_up_to(max(n_values))
    rows: list[PrimePrefixProfileRow] = []
    for n in n_values:
        rows.extend(
            _prime_prefix_profile_rows_for_n(
                n,
                prime_pool=prime_pool,
                checkpoints=checkpoint_values,
                numeric_tolerance=numeric_tolerance,
            )
        )
    return rows


def write_prime_prefix_profile_csv(
    rows: Iterable[PrimePrefixProfileRow],
    output_path: str | Path,
) -> None:
    """Write prime-prefix residual profile rows as CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(PrimePrefixProfileRow.__dataclass_fields__.keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _csv_value(getattr(row, field)) for field in fieldnames})


def _prime_prefix_profile_rows_for_n(
    n: int,
    *,
    prime_pool: list[int],
    checkpoints: list[int],
    numeric_tolerance: float,
) -> list[PrimePrefixProfileRow]:
    n_primes = [p for p in prime_pool if p <= n]
    if not n_primes:
        return []

    rows: list[PrimePrefixProfileRow] = []
    prefix_primes: list[int] = []
    next_prime_index = 0
    prefix_width_sum = 0.0
    product_prefix_baseline = 1.0

    for p_prefix in checkpoints:
        if p_prefix > n:
            continue
        while next_prime_index < len(n_primes) and n_primes[next_prime_index] <= p_prefix:
            p = n_primes[next_prime_index]
            prefix_primes.append(p)
            prefix_width_sum += 1.0 / p
            product_prefix_baseline *= 1.0 - 1.0 / p
            next_prime_index += 1
        if not prefix_primes:
            continue
        rows.append(
            prime_prefix_profile_row(
                n,
                p_prefix=p_prefix,
                prefix_primes=prefix_primes,
                prefix_width_sum=prefix_width_sum,
                product_prefix_baseline=product_prefix_baseline,
                numeric_tolerance=numeric_tolerance,
            )
        )
    return rows


def prime_prefix_profile_row(
    n: int,
    *,
    p_prefix: int,
    prefix_primes: list[int],
    prefix_width_sum: float,
    product_prefix_baseline: float,
    numeric_tolerance: float = 1e-12,
) -> PrimePrefixProfileRow:
    """Return one prime-prefix residual profile row."""
    n = validate_n(n)
    gaps = uncovered_intervals(n, primes=prefix_primes)
    gap_lengths = [_interval_length(gap) for gap in gaps]
    uncovered_measure = sum(gap_lengths)
    max_gap = max(gap_lengths, default=0.0)
    poisson_prefix_baseline = math.exp(-prefix_width_sum)
    safe_ratio = _safe_ratio(uncovered_measure, product_prefix_baseline)
    safe_log_delta = _safe_log_delta(uncovered_measure, product_prefix_baseline)
    return PrimePrefixProfileRow(
        n=n,
        p_prefix=p_prefix,
        prime_index=len(prefix_primes),
        prefix_width_sum=prefix_width_sum,
        poisson_prefix_baseline=poisson_prefix_baseline,
        product_prefix_baseline=product_prefix_baseline,
        uncovered_measure=uncovered_measure,
        uncovered_over_product_baseline=safe_ratio,
        baseline_delta=uncovered_measure - product_prefix_baseline,
        log_uncovered_minus_log_product_baseline=safe_log_delta,
        component_count=len(gaps),
        max_gap=max_gap,
        gap_p50=gap_quantile(gaps, 0.50),
        gap_p90=gap_quantile(gaps, 0.90),
        gap_p99=gap_quantile(gaps, 0.99),
        top_gap_share=max_gap / uncovered_measure if uncovered_measure > 0 else 0.0,
        numeric_complete_prefix=is_completely_covered_numeric(
            n,
            primes=prefix_primes,
            tolerance=numeric_tolerance,
        ),
    )


def _validated_checkpoints(checkpoints: Iterable[int]) -> list[int]:
    values = sorted({int(checkpoint) for checkpoint in checkpoints})
    if any(value < 2 for value in values):
        raise ValueError("checkpoints must be >= 2")
    return values


def _interval_length(interval: tuple[float, float]) -> float:
    start, end = interval
    if end >= start:
        return end - start
    return 1.0 - start + end


def _safe_ratio(uncovered_measure: float, product_prefix_baseline: float) -> float:
    if uncovered_measure <= 0.0 or product_prefix_baseline <= 0.0:
        return math.nan
    return uncovered_measure / product_prefix_baseline


def _safe_log_delta(uncovered_measure: float, product_prefix_baseline: float) -> float:
    if uncovered_measure <= 0.0 or product_prefix_baseline <= 0.0:
        return math.nan
    return math.log(uncovered_measure) - math.log(product_prefix_baseline)


def _csv_value(value: object) -> object:
    if isinstance(value, float) and math.isnan(value):
        return ""
    return value
