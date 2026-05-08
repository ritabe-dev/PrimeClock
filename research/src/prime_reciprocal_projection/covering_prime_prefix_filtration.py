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
MAX_DEFAULT_FULL_EXPORT_K = 6


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


@dataclass(frozen=True)
class PrimePrefixResidueFullRow:
    """One covered residue classified as inherited or newly born."""

    k: int
    new_prime: int
    primorial: int
    residue: int
    residue_mod_previous: int | None
    status: str
    reflection_residue: int
    previous_prefix_uncovered_measure: float | None


@dataclass(frozen=True)
class PrimePrefixBirthWitnessRow:
    """Proof-oriented witness for one birth residue."""

    k: int
    new_prime: int
    primorial: int
    residue: int
    residue_mod_previous: int | None
    reflection_residue: int
    previous_uncovered_interval_count: int
    previous_prefix_uncovered_measure: float
    previous_uncovered_intervals: str
    new_prime_arc_intervals: str
    uses_endpoint_touching: bool


@dataclass(frozen=True)
class PrimePrefixExclusionWitnessRow:
    """Gap witness for a residue that is not covered at a prefix level."""

    k: int
    new_prime: int
    primorial: int
    residue: int
    reflection_residue: int
    uncovered_interval_count: int
    uncovered_measure: float
    first_uncovered_interval: str
    uncovered_intervals: str


@dataclass(frozen=True)
class PrimePrefixBirthClassificationRow:
    """Template-oriented classification for one birth residue."""

    k: int
    new_prime: int
    primorial: int
    residue: int
    reflection_residue: int
    reflection_pair_min: int
    reflection_pair_max: int
    parent_residue_mod_previous: int
    previous_uncovered_interval_count: int
    previous_prefix_uncovered_measure: float
    previous_uncovered_intervals: str
    new_prime_remainder: int
    new_prime_arc_intervals: str
    uses_endpoint_touching: bool


def prime_prefix_residue_filtration_tables(
    *,
    max_k: int = 7,
    birth_sample_limit: int = 200,
    allow_large_k: bool = False,
) -> tuple[list[PrimePrefixResidueFiltrationRow], list[PrimePrefixResidueBirthSampleRow]]:
    """Return exact summary and birth-sample rows for the residue filtration."""
    summary_rows, birth_sample_rows, _ = prime_prefix_residue_filtration_data(
        max_k=max_k,
        birth_sample_limit=birth_sample_limit,
        allow_large_k=allow_large_k,
    )
    return summary_rows, birth_sample_rows


def prime_prefix_residue_full_rows(
    *,
    max_k: int = 5,
    allow_large_k: bool = False,
) -> list[PrimePrefixResidueFullRow]:
    """Return all covered residues through max_k with inherited/birth status."""
    _validate_small_export_k(max_k, allow_large_k=allow_large_k)
    summary_rows, _, covered_sets = prime_prefix_residue_filtration_data(
        max_k=max_k,
        birth_sample_limit=0,
        allow_large_k=allow_large_k,
    )
    primes = _first_primes(max_k)
    rows: list[PrimePrefixResidueFullRow] = []
    for index, summary in enumerate(summary_rows):
        previous_covered = covered_sets[index - 1] if index > 0 else set()
        previous_primorial = summary_rows[index - 1].primorial if index > 0 else 1
        previous_primes = primes[:index]
        for residue in sorted(covered_sets[index]):
            inherited = bool(previous_covered) and residue % previous_primorial in previous_covered
            previous_measure = (
                None
                if inherited
                else float(residue_uncovered_measure(residue, previous_primes))
            )
            rows.append(
                PrimePrefixResidueFullRow(
                    k=summary.k,
                    new_prime=summary.new_prime,
                    primorial=summary.primorial,
                    residue=residue,
                    residue_mod_previous=(
                        residue % previous_primorial if index > 0 else None
                    ),
                    status="inherited" if inherited else "birth",
                    reflection_residue=(-residue) % summary.primorial,
                    previous_prefix_uncovered_measure=previous_measure,
                )
            )
    return rows


def prime_prefix_birth_witness_rows(
    *,
    k: int = 5,
    allow_large_k: bool = False,
) -> list[PrimePrefixBirthWitnessRow]:
    """Return rational interval witnesses for birth residues at one level."""
    _validate_small_export_k(k, allow_large_k=allow_large_k)
    full_rows = [
        row
        for row in prime_prefix_residue_full_rows(max_k=k, allow_large_k=allow_large_k)
        if row.k == k and row.status == "birth"
    ]
    primes = _first_primes(k)
    previous_primes = primes[:-1]
    new_prime = primes[-1]
    previous_primorial = 1
    for p in previous_primes:
        previous_primorial *= p

    rows: list[PrimePrefixBirthWitnessRow] = []
    for row in full_rows:
        previous_gaps = residue_uncovered_intervals(row.residue, previous_primes)
        new_arc_intervals = _exact_arc_intervals_for_residue(row.residue, new_prime)
        rows.append(
            PrimePrefixBirthWitnessRow(
                k=row.k,
                new_prime=row.new_prime,
                primorial=row.primorial,
                residue=row.residue,
                residue_mod_previous=(
                    row.residue % previous_primorial if previous_primes else None
                ),
                reflection_residue=row.reflection_residue,
                previous_uncovered_interval_count=len(previous_gaps),
                previous_prefix_uncovered_measure=float(
                    residue_uncovered_measure(row.residue, previous_primes)
                ),
                previous_uncovered_intervals=_format_intervals(previous_gaps),
                new_prime_arc_intervals=_format_intervals(new_arc_intervals),
                uses_endpoint_touching=_uses_endpoint_touching(
                    previous_gaps,
                    new_arc_intervals,
                ),
            )
        )
    return rows


def prime_prefix_exclusion_witness_rows(
    *,
    k: int = 4,
    allow_large_k: bool = False,
) -> list[PrimePrefixExclusionWitnessRow]:
    """Return gap witnesses for residues not covered at one prefix level."""
    _validate_small_export_k(k, allow_large_k=allow_large_k)
    primes = _first_primes(k)
    primorial = _primorial(primes)
    covered = {
        row.residue
        for row in prime_prefix_residue_full_rows(max_k=k, allow_large_k=allow_large_k)
        if row.k == k
    }
    rows: list[PrimePrefixExclusionWitnessRow] = []
    for residue in range(primorial):
        if residue in covered:
            continue
        gaps = residue_uncovered_intervals(residue, primes)
        rows.append(
            PrimePrefixExclusionWitnessRow(
                k=k,
                new_prime=primes[-1],
                primorial=primorial,
                residue=residue,
                reflection_residue=(-residue) % primorial,
                uncovered_interval_count=len(gaps),
                uncovered_measure=float(residue_uncovered_measure(residue, primes)),
                first_uncovered_interval=_format_intervals(gaps[:1]),
                uncovered_intervals=_format_intervals(gaps),
            )
        )
    return rows


def prime_prefix_birth_classification_rows(
    *,
    k: int = 5,
    allow_large_k: bool = False,
) -> list[PrimePrefixBirthClassificationRow]:
    """Return template-oriented classifications for birth residues."""
    witness_rows = prime_prefix_birth_witness_rows(k=k, allow_large_k=allow_large_k)
    rows: list[PrimePrefixBirthClassificationRow] = []
    for row in witness_rows:
        pair_min = min(row.residue, row.reflection_residue)
        pair_max = max(row.residue, row.reflection_residue)
        rows.append(
            PrimePrefixBirthClassificationRow(
                k=row.k,
                new_prime=row.new_prime,
                primorial=row.primorial,
                residue=row.residue,
                reflection_residue=row.reflection_residue,
                reflection_pair_min=pair_min,
                reflection_pair_max=pair_max,
                parent_residue_mod_previous=row.residue_mod_previous or 0,
                previous_uncovered_interval_count=row.previous_uncovered_interval_count,
                previous_prefix_uncovered_measure=row.previous_prefix_uncovered_measure,
                previous_uncovered_intervals=row.previous_uncovered_intervals,
                new_prime_remainder=row.residue % row.new_prime,
                new_prime_arc_intervals=row.new_prime_arc_intervals,
                uses_endpoint_touching=row.uses_endpoint_touching,
            )
        )
    return rows


def prime_prefix_residue_filtration_data(
    *,
    max_k: int = 7,
    birth_sample_limit: int = 200,
    allow_large_k: bool = False,
) -> tuple[
    list[PrimePrefixResidueFiltrationRow],
    list[PrimePrefixResidueBirthSampleRow],
    list[set[int]],
]:
    """Return exact filtration rows, birth samples, and covered residue sets."""
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
    covered_sets: list[set[int]] = []

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
        covered_sets.append(covered)
        previous_primorial = primorial

    return summary_rows, birth_sample_rows, covered_sets


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


def write_prime_prefix_residue_full_csv(
    rows: Iterable[PrimePrefixResidueFullRow],
    output_path: str | Path,
) -> None:
    """Write all covered residue rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixResidueFullRow)


def write_prime_prefix_birth_witness_csv(
    rows: Iterable[PrimePrefixBirthWitnessRow],
    output_path: str | Path,
) -> None:
    """Write birth witness rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixBirthWitnessRow)


def write_prime_prefix_exclusion_witness_csv(
    rows: Iterable[PrimePrefixExclusionWitnessRow],
    output_path: str | Path,
) -> None:
    """Write exclusion witness rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixExclusionWitnessRow)


def write_prime_prefix_birth_classification_csv(
    rows: Iterable[PrimePrefixBirthClassificationRow],
    output_path: str | Path,
) -> None:
    """Write birth classification rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixBirthClassificationRow)


def _validate_small_export_k(max_k: int, *, allow_large_k: bool) -> None:
    if max_k < 1:
        raise ValueError("max_k must be >= 1")
    if max_k > MAX_DEFAULT_FULL_EXPORT_K and not allow_large_k:
        raise ValueError(
            f"max_k>{MAX_DEFAULT_FULL_EXPORT_K} requires allow_large_k=True; "
            "full exports are proof-oriented small-k artifacts"
        )


def _first_primes(count: int) -> list[int]:
    limit = 32
    while True:
        primes = primes_up_to(limit)
        if len(primes) >= count:
            return primes[:count]
        limit *= 2


def _primorial(primes: Iterable[int]) -> int:
    value = 1
    for p in primes:
        value *= p
    return value


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


def _format_fraction(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _format_intervals(intervals: Iterable[ExactInterval]) -> str:
    return ";".join(
        f"{_format_fraction(start)}-{_format_fraction(end)}"
        for start, end in intervals
    )


def _split_interval(interval: ExactInterval) -> list[ExactInterval]:
    start, end = interval
    one = Fraction(1)
    if end >= start:
        return [(start, end)]
    return [(start, one), (Fraction(0), end)]


def _uses_endpoint_touching(
    previous_gaps: Iterable[ExactInterval],
    new_arc_intervals: Iterable[ExactInterval],
) -> bool:
    arc_segments = [
        segment
        for interval in new_arc_intervals
        for segment in _split_interval(interval)
    ]
    for gap in previous_gaps:
        for gap_start, gap_end in _split_interval(gap):
            for arc_start, arc_end in arc_segments:
                if arc_start <= gap_start and gap_end <= arc_end:
                    if gap_start == arc_start or gap_end == arc_end:
                        return True
                    break
            else:
                raise ValueError("birth gap is not contained in the new prime arc")
    return False


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
