"""Exact prime-prefix residue-covering filtration for PRC."""

from __future__ import annotations

import csv
import statistics
from dataclasses import dataclass
from fractions import Fraction
from functools import cmp_to_key
from pathlib import Path
from typing import Iterable

from .primes import is_prime, primes_up_to

ExactInterval = tuple[Fraction, Fraction]
ExactRawInterval = tuple[int, int, int, int]
MAX_DEFAULT_FILTRATION_K = 7


@dataclass(frozen=True)
class PrimePrefixResidueFiltrationRow:
    """Summary of one exact residue-covering filtration level."""

    k: int
    new_prime: int
    primorial: int
    covered_residue_count: int
    covered_density: float
    inherited_count: int
    birth_count: int
    birth_prev_uncovered_median: float | None
    birth_prev_uncovered_max: float | None
    birth_residues_sample: str


@dataclass(frozen=True)
class PrimePrefixResidueBirthSampleRow:
    """One sampled birth residue in the exact residue-covering filtration."""

    k: int
    new_prime: int
    primorial: int
    residue: int
    previous_prefix_uncovered_measure: float


def prime_prefix_residue_filtration_tables(
    *,
    max_k: int = 7,
    birth_sample_limit: int = 200,
    allow_large_k: bool = False,
) -> tuple[list[PrimePrefixResidueFiltrationRow], list[PrimePrefixResidueBirthSampleRow]]:
    """Return exact summary and birth-sample rows for the residue filtration."""
    if max_k < 1:
        raise ValueError("max_k must be >= 1")
    if max_k > MAX_DEFAULT_FILTRATION_K and not allow_large_k:
        raise ValueError(
            f"max_k>{MAX_DEFAULT_FILTRATION_K} requires allow_large_k=True; "
            "k=8 and higher are primorial-scale scans"
        )
    if birth_sample_limit < 0:
        raise ValueError("birth_sample_limit must be >= 0")

    primes = _first_primes(max_k)
    previous_covered: set[int] = set()
    previous_primorial = 1
    primorial = 1
    summary_rows: list[PrimePrefixResidueFiltrationRow] = []
    birth_sample_rows: list[PrimePrefixResidueBirthSampleRow] = []

    for k, new_prime in enumerate(primes, start=1):
        prefix_primes = primes[:k]
        previous_prefix_primes = primes[: k - 1]
        primorial *= new_prime
        covered: set[int] = set()
        births: list[int] = []
        previous_uncovered_measures: list[float] = []
        birth_sample_count = 0
        inherited_count = 0

        for residue in range(primorial):
            if previous_covered and residue % previous_primorial in previous_covered:
                covered.add(residue)
                inherited_count += 1
                continue
            if residue_is_exactly_covered(residue, prefix_primes):
                covered.add(residue)
                births.append(residue)
                measure = float(residue_uncovered_measure(residue, previous_prefix_primes))
                previous_uncovered_measures.append(measure)
                if birth_sample_count < birth_sample_limit:
                    birth_sample_rows.append(
                        PrimePrefixResidueBirthSampleRow(
                            k=k,
                            new_prime=new_prime,
                            primorial=primorial,
                            residue=residue,
                            previous_prefix_uncovered_measure=measure,
                        )
                    )
                    birth_sample_count += 1

        sample_residues = births[: min(30, birth_sample_limit)]
        summary_rows.append(
            PrimePrefixResidueFiltrationRow(
                k=k,
                new_prime=new_prime,
                primorial=primorial,
                covered_residue_count=len(covered),
                covered_density=len(covered) / primorial,
                inherited_count=inherited_count,
                birth_count=len(births),
                birth_prev_uncovered_median=(
                    statistics.median(previous_uncovered_measures)
                    if previous_uncovered_measures
                    else None
                ),
                birth_prev_uncovered_max=(
                    max(previous_uncovered_measures) if previous_uncovered_measures else None
                ),
                birth_residues_sample=" ".join(str(residue) for residue in sample_residues),
            )
        )
        previous_covered = covered
        previous_primorial = primorial

    return summary_rows, birth_sample_rows


def residue_is_exactly_covered(residue: int, primes: Iterable[int]) -> bool:
    """Return whether the given residue is exactly covered by the prime arcs."""
    prime_values = _validated_prime_list(primes)
    if not prime_values:
        return False
    intervals = [
        interval
        for p in prime_values
        for interval in _exact_raw_arc_intervals_for_residue(residue, p)
    ]
    intervals.sort(key=cmp_to_key(_compare_exact_raw_intervals))
    current_start_num, _, current_end_num, current_end_den = intervals[0]
    for start_num, start_den, end_num, end_den in intervals[1:]:
        if start_num * current_end_den <= current_end_num * start_den:
            if end_num * current_end_den > current_end_num * end_den:
                current_end_num, current_end_den = end_num, end_den
        else:
            return False
    return current_start_num == 0 and current_end_num >= current_end_den


def residue_uncovered_measure(residue: int, primes: Iterable[int]) -> Fraction:
    """Return exact uncovered measure for a residue and prime prefix."""
    return sum(
        (_exact_interval_length(interval) for interval in residue_uncovered_intervals(residue, primes)),
        Fraction(0),
    )


def residue_uncovered_intervals(residue: int, primes: Iterable[int]) -> list[ExactInterval]:
    """Return exact connected uncovered intervals for a residue and prime prefix."""
    covered = residue_covered_intervals(residue, primes)
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


def residue_covered_intervals(residue: int, primes: Iterable[int]) -> list[ExactInterval]:
    """Return exact merged covered intervals for a residue and prime prefix."""
    prime_values = _validated_prime_list(primes)
    intervals = [
        interval
        for p in prime_values
        for interval in _exact_arc_intervals_for_residue(residue, p)
    ]
    return _merge_exact_intervals(intervals)


def _validated_prime_list(primes: Iterable[int]) -> list[int]:
    values = list(primes)
    seen: set[int] = set()
    for p in values:
        if isinstance(p, bool) or not isinstance(p, int) or p < 2 or not is_prime(p):
            raise ValueError("primes must contain distinct prime integers >= 2")
        if p in seen:
            raise ValueError("primes must contain distinct prime integers >= 2")
        seen.add(p)
    return values


def write_prime_prefix_residue_filtration_csv(
    rows: Iterable[PrimePrefixResidueFiltrationRow],
    output_path: str | Path,
) -> None:
    """Write exact residue-filtration summary rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixResidueFiltrationRow)


def write_prime_prefix_residue_birth_samples_csv(
    rows: Iterable[PrimePrefixResidueBirthSampleRow],
    output_path: str | Path,
) -> None:
    """Write exact residue-filtration birth sample rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixResidueBirthSampleRow)


def _first_primes(count: int) -> list[int]:
    limit = 32
    while True:
        primes = primes_up_to(limit)
        if len(primes) >= count:
            return primes[:count]
        limit *= 2


def _exact_arc_intervals_for_residue(residue: int, p: int) -> list[ExactInterval]:
    remainder = residue % p
    center = Fraction(remainder, p)
    radius = Fraction(1, 2 * p)
    start = center - radius
    end = center + radius
    one = Fraction(1)
    if start < 0:
        return [(Fraction(0), end), (one + start, one)]
    if end > one:
        return [(Fraction(0), end - one), (start, one)]
    return [(start, end)]


def _exact_raw_arc_intervals_for_residue(residue: int, p: int) -> list[ExactRawInterval]:
    remainder = residue % p
    denominator = 2 * p
    start = 2 * remainder - 1
    end = 2 * remainder + 1
    if start < 0:
        return [(0, 1, end, denominator), (denominator + start, denominator, 1, 1)]
    if end > denominator:
        return [(0, 1, end - denominator, denominator), (start, denominator, 1, 1)]
    return [(start, denominator, end, denominator)]


def _compare_exact_raw_intervals(left: ExactRawInterval, right: ExactRawInterval) -> int:
    left_start_num, left_start_den, left_end_num, left_end_den = left
    right_start_num, right_start_den, right_end_num, right_end_den = right
    start_delta = left_start_num * right_start_den - right_start_num * left_start_den
    if start_delta < 0:
        return -1
    if start_delta > 0:
        return 1

    end_delta = left_end_num * right_end_den - right_end_num * left_end_den
    if end_delta < 0:
        return -1
    if end_delta > 0:
        return 1
    return 0


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


def _exact_interval_length(interval: ExactInterval) -> Fraction:
    start, end = interval
    if end >= start:
        return end - start
    return Fraction(1) - start + end


def _write_dataclass_csv(
    rows: Iterable[object],
    output_path: str | Path,
    row_type: type[object],
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(row_type.__dataclass_fields__.keys())  # type: ignore[attr-defined]
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
