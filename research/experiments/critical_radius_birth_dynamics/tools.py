"""Exact helpers for the critical-radius and birth-dynamics sandbox.

This module intentionally lives under ``research/experiments`` instead of the
public package. The v2.2.4 public release remains the stable C4/B5 certificate
artifact; these helpers are the next internal research layer.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

from prime_reciprocal_projection.covering_prime_prefix_filtration import (
    PrimePrefixResidueFullRow,
    prime_prefix_residue_full_rows,
    residue_is_exactly_covered,
    residue_uncovered_intervals,
    residue_uncovered_measure,
)
from prime_reciprocal_projection.primes import primes_up_to

ExactInterval = tuple[Fraction, Fraction]


@dataclass(frozen=True)
class CriticalRadiusRow:
    k: int
    primorial: int
    residue: int
    lambda_fraction: str
    lambda_decimal: float
    status: str
    bottleneck_point: str
    active_primes: str
    active_centers: str
    current_covering_residue: bool


@dataclass(frozen=True)
class CriticalRadiusSummaryRow:
    k: int
    primorial: int
    residue_count: int
    robust_covered_count: int
    endpoint_covered_count: int
    uncovered_count: int
    covered_count: int
    min_lambda_fraction: str
    max_lambda_fraction: str
    distinct_lambda_count: int
    nearest_uncovered_lambda_fraction: str


@dataclass(frozen=True)
class CriticalRadiusNearMissRow:
    k: int
    primorial: int
    near_miss_rank: int
    residue: int
    reflection_residue: int
    lambda_fraction: str
    lambda_minus_half_fraction: str
    bottleneck_point: str
    active_primes: str
    active_centers: str


@dataclass(frozen=True)
class NearMissBirthParentRow:
    k: int
    primorial: int
    near_miss_rank: int
    residue: int
    reflection_residue: int
    lambda_fraction: str
    lambda_minus_half_fraction: str
    next_k: int
    new_prime: int
    birth_lift_count: int
    birth_lift_residues: str
    birth_lift_remainders: str
    child_lambda_fractions: str
    child_statuses: str
    birth_types: str


@dataclass(frozen=True)
class NearMissGapGeometryRow:
    k: int
    primorial: int
    near_miss_rank: int
    residue: int
    lambda_fraction: str
    next_k: int
    new_prime: int
    previous_open_gap_count: int
    previous_uncovered_measure_fraction: str
    max_previous_open_gap_length_fraction: str
    previous_open_gap_boundary_endpoints: str
    containing_remainder_count: int
    containing_remainders: str
    containment_margins: str
    best_containment_margin_fraction: str


@dataclass(frozen=True)
class BirthThresholdCrossingRow:
    k: int
    new_prime: int
    primorial: int
    residue: int
    parent_residue_mod_previous: int
    parent_lambda_fraction: str
    parent_lambda_decimal: float
    current_lambda_fraction: str
    current_lambda_decimal: float
    parent_status: str
    current_status: str
    birth_type: str


@dataclass(frozen=True)
class BirthDynamicsRow:
    k: int
    new_prime: int
    primorial: int
    residue: int
    parent_residue_mod_previous: int
    reflection_residue: int
    birth_type: str
    previous_open_gap_count: int
    previous_uncovered_measure_fraction: str
    previous_open_gap_boundary_endpoints: str
    new_prime_remainder: int
    new_prime_closed_arc_boundary_endpoints: str
    containment_margin_fraction: str
    uses_endpoint_touching: bool


@dataclass(frozen=True)
class BirthDynamicsSummaryRow:
    k: int
    new_prime: int
    primorial: int
    birth_count: int
    strict_single_gap_birth: int
    endpoint_single_gap_birth: int
    strict_multi_gap_birth: int
    endpoint_multi_gap_birth: int
    max_previous_open_gap_count: int
    previous_uncovered_measure_fractions: str


def first_primes(count: int) -> list[int]:
    """Return the first ``count`` primes."""
    if count < 1:
        raise ValueError("count must be >= 1")
    limit = 32
    while True:
        primes = primes_up_to(limit)
        if len(primes) >= count:
            return primes[:count]
        limit *= 2


def primorial(primes: Iterable[int]) -> int:
    value = 1
    for p in primes:
        value *= p
    return value


def center_for_residue(residue: int, p: int) -> Fraction:
    return Fraction(residue % p, p)


def critical_radius_rows(*, min_k: int = 4, max_k: int = 5) -> list[CriticalRadiusRow]:
    """Return exact critical-radius rows for all residues at ``min_k..max_k``."""
    rows: list[CriticalRadiusRow] = []
    for k in range(min_k, max_k + 1):
        primes = first_primes(k)
        modulus = primorial(primes)
        for residue in range(modulus):
            radius, point, active = critical_radius_certificate(residue, primes)
            covered = residue_is_exactly_covered(residue, primes)
            rows.append(
                CriticalRadiusRow(
                    k=k,
                    primorial=modulus,
                    residue=residue,
                    lambda_fraction=format_fraction(radius),
                    lambda_decimal=float(radius),
                    status=critical_radius_status(radius),
                    bottleneck_point=format_fraction(point),
                    active_primes=" ".join(str(p) for p in active),
                    active_centers=" ".join(
                        format_fraction(center_for_residue(residue, p)) for p in active
                    ),
                    current_covering_residue=covered,
                )
            )
    return rows


def critical_radius_summary_rows(
    rows: Iterable[CriticalRadiusRow],
) -> list[CriticalRadiusSummaryRow]:
    grouped: dict[int, list[CriticalRadiusRow]] = {}
    for row in rows:
        grouped.setdefault(row.k, []).append(row)

    summaries: list[CriticalRadiusSummaryRow] = []
    for k, group in sorted(grouped.items()):
        lambda_values = [parse_fraction(row.lambda_fraction) for row in group]
        uncovered_values = [
            parse_fraction(row.lambda_fraction)
            for row in group
            if row.status == "uncovered"
        ]
        robust_count = sum(row.status == "robust_covered" for row in group)
        endpoint_count = sum(row.status == "endpoint_covered" for row in group)
        uncovered_count = sum(row.status == "uncovered" for row in group)
        summaries.append(
            CriticalRadiusSummaryRow(
                k=k,
                primorial=group[0].primorial,
                residue_count=len(group),
                robust_covered_count=robust_count,
                endpoint_covered_count=endpoint_count,
                uncovered_count=uncovered_count,
                covered_count=robust_count + endpoint_count,
                min_lambda_fraction=format_fraction(min(lambda_values)),
                max_lambda_fraction=format_fraction(max(lambda_values)),
                distinct_lambda_count=len(set(lambda_values)),
                nearest_uncovered_lambda_fraction=(
                    format_fraction(min(uncovered_values)) if uncovered_values else ""
                ),
            )
        )
    return summaries


def critical_radius_near_miss_rows(
    rows: Iterable[CriticalRadiusRow],
    *,
    limit_per_k: int = 20,
) -> list[CriticalRadiusNearMissRow]:
    """Return uncovered residues nearest to the covering threshold."""
    if limit_per_k < 1:
        raise ValueError("limit_per_k must be >= 1")

    grouped: dict[int, list[CriticalRadiusRow]] = {}
    for row in rows:
        if row.status == "uncovered":
            grouped.setdefault(row.k, []).append(row)

    threshold = Fraction(1, 2)
    near_misses: list[CriticalRadiusNearMissRow] = []
    for k, group in sorted(grouped.items()):
        ordered = sorted(
            group,
            key=lambda row: (
                parse_fraction(row.lambda_fraction) - threshold,
                row.residue,
            ),
        )
        for rank, row in enumerate(ordered[:limit_per_k], start=1):
            lambda_value = parse_fraction(row.lambda_fraction)
            near_misses.append(
                CriticalRadiusNearMissRow(
                    k=row.k,
                    primorial=row.primorial,
                    near_miss_rank=rank,
                    residue=row.residue,
                    reflection_residue=(-row.residue) % row.primorial,
                    lambda_fraction=row.lambda_fraction,
                    lambda_minus_half_fraction=format_fraction(lambda_value - threshold),
                    bottleneck_point=row.bottleneck_point,
                    active_primes=row.active_primes,
                    active_centers=row.active_centers,
                )
            )
    return near_misses


def near_miss_birth_parent_rows(
    near_miss_rows: Iterable[CriticalRadiusNearMissRow],
) -> list[NearMissBirthParentRow]:
    """Connect near-miss residues to birth lifts at the next prime level."""
    near_misses = list(near_miss_rows)
    if not near_misses:
        return []

    min_next_k = min(row.k for row in near_misses) + 1
    max_next_k = max(row.k for row in near_misses) + 1
    crossing_rows = birth_threshold_crossing_rows(min_k=min_next_k, max_k=max_next_k)
    births_by_parent: dict[tuple[int, int], list[BirthThresholdCrossingRow]] = {}
    for crossing in crossing_rows:
        parent_k = crossing.k - 1
        key = (parent_k, crossing.parent_residue_mod_previous)
        births_by_parent.setdefault(key, []).append(crossing)

    rows: list[NearMissBirthParentRow] = []
    for near_miss in near_misses:
        next_k = near_miss.k + 1
        next_primes = first_primes(next_k)
        new_prime = next_primes[-1]
        matches = sorted(
            births_by_parent.get((near_miss.k, near_miss.residue), []),
            key=lambda row: row.residue,
        )
        rows.append(
            NearMissBirthParentRow(
                k=near_miss.k,
                primorial=near_miss.primorial,
                near_miss_rank=near_miss.near_miss_rank,
                residue=near_miss.residue,
                reflection_residue=near_miss.reflection_residue,
                lambda_fraction=near_miss.lambda_fraction,
                lambda_minus_half_fraction=near_miss.lambda_minus_half_fraction,
                next_k=next_k,
                new_prime=new_prime,
                birth_lift_count=len(matches),
                birth_lift_residues=" ".join(str(row.residue) for row in matches),
                birth_lift_remainders=" ".join(
                    str(row.residue % new_prime) for row in matches
                ),
                child_lambda_fractions=" ".join(row.current_lambda_fraction for row in matches),
                child_statuses=" ".join(row.current_status for row in matches),
                birth_types=" ".join(row.birth_type for row in matches),
            )
        )
    return rows


def near_miss_gap_geometry_rows(
    near_miss_rows: Iterable[CriticalRadiusNearMissRow],
) -> list[NearMissGapGeometryRow]:
    """Return old-gap geometry explaining whether near-misses can birth."""
    rows: list[NearMissGapGeometryRow] = []
    for near_miss in near_miss_rows:
        primes = first_primes(near_miss.k)
        next_primes = first_primes(near_miss.k + 1)
        new_prime = next_primes[-1]
        previous_gaps = residue_uncovered_intervals(near_miss.residue, primes)
        containing_remainders: list[int] = []
        margins: list[Fraction] = []
        for remainder in range(new_prime):
            new_arcs = exact_arc_intervals_for_residue(remainder, new_prime)
            try:
                containment = classify_birth_containment(previous_gaps, new_arcs)
            except ValueError:
                continue
            containing_remainders.append(remainder)
            margins.append(containment.margin)

        rows.append(
            NearMissGapGeometryRow(
                k=near_miss.k,
                primorial=near_miss.primorial,
                near_miss_rank=near_miss.near_miss_rank,
                residue=near_miss.residue,
                lambda_fraction=near_miss.lambda_fraction,
                next_k=near_miss.k + 1,
                new_prime=new_prime,
                previous_open_gap_count=len(previous_gaps),
                previous_uncovered_measure_fraction=format_fraction(
                    residue_uncovered_measure(near_miss.residue, primes)
                ),
                max_previous_open_gap_length_fraction=format_fraction(
                    max(interval_length(gap) for gap in previous_gaps)
                ),
                previous_open_gap_boundary_endpoints=format_intervals(previous_gaps),
                containing_remainder_count=len(containing_remainders),
                containing_remainders=" ".join(str(value) for value in containing_remainders),
                containment_margins=" ".join(format_fraction(value) for value in margins),
                best_containment_margin_fraction=(
                    format_fraction(max(margins)) if margins else ""
                ),
            )
        )
    return rows


def birth_threshold_crossing_rows(
    *,
    min_k: int = 5,
    max_k: int | None = None,
    full_rows: Sequence[PrimePrefixResidueFullRow] | None = None,
    birth_rows: Sequence[BirthDynamicsRow] | None = None,
) -> list[BirthThresholdCrossingRow]:
    """Return how birth layers cross the critical-radius threshold."""
    if max_k is None:
        max_k = min_k
    if min_k < 2:
        raise ValueError("min_k must be >= 2")
    if max_k < min_k:
        raise ValueError("max_k must be >= min_k")

    source_rows = full_rows
    if source_rows is None:
        source_rows = prime_prefix_residue_full_rows(
            max_k=max_k,
            allow_large_k=max_k > 6,
        )
    full_birth_rows = [
        row
        for row in source_rows
        if min_k <= row.k <= max_k and row.status == "birth"
    ]
    source_birth_rows = birth_rows
    if source_birth_rows is None:
        source_birth_rows = birth_dynamics_rows(
            min_k=min_k,
            max_k=max_k,
            full_rows=source_rows,
        )
    birth_types = {
        (row.k, row.residue): row.birth_type
        for row in source_birth_rows
    }

    rows: list[BirthThresholdCrossingRow] = []
    for row in full_birth_rows:
        prefix_primes = first_primes(row.k)
        previous_primes = prefix_primes[:-1]
        new_prime = prefix_primes[-1]
        previous_modulus = primorial(previous_primes)
        modulus = primorial(prefix_primes)
        parent_residue = row.residue % previous_modulus
        parent_lambda = critical_radius_certificate(parent_residue, previous_primes)[0]
        current_lambda = critical_radius_certificate(row.residue, prefix_primes)[0]
        rows.append(
            BirthThresholdCrossingRow(
                k=row.k,
                new_prime=new_prime,
                primorial=modulus,
                residue=row.residue,
                parent_residue_mod_previous=parent_residue,
                parent_lambda_fraction=format_fraction(parent_lambda),
                parent_lambda_decimal=float(parent_lambda),
                current_lambda_fraction=format_fraction(current_lambda),
                current_lambda_decimal=float(current_lambda),
                parent_status=critical_radius_status(parent_lambda),
                current_status=critical_radius_status(current_lambda),
                birth_type=birth_types[(row.k, row.residue)],
            )
        )
    return rows


def critical_radius_certificate(
    residue: int,
    primes: Iterable[int],
) -> tuple[Fraction, Fraction, tuple[int, ...]]:
    """Return ``lambda_k(r)``, a bottleneck point, and active primes.

    The current PRC arcs have radius ``1/(2p)``. With scaled arcs
    ``[c_p-lambda/p, c_p+lambda/p]``, the covering threshold is the maximum of
    ``min_p p*d_T(x,c_p)`` over the circle. We enumerate exact weighted
    bisectors of all lifted center pairs and evaluate the lower envelope.
    """
    prime_values = list(primes)
    if not prime_values:
        raise ValueError("primes must be nonempty")

    centers = [(p, center_for_residue(residue, p)) for p in prime_values]
    candidates: set[Fraction] = {Fraction(0)}
    for _, center in centers:
        candidates.add(center % 1)
        candidates.add((center + Fraction(1, 2)) % 1)
    signs = (-1, 1)
    offsets = (-1, 0, 1)

    for left_index, (left_p, left_center) in enumerate(centers):
        for right_p, right_center in centers[left_index + 1 :]:
            for left_offset in offsets:
                lifted_left = left_center + left_offset
                for right_offset in offsets:
                    lifted_right = right_center + right_offset
                    for left_sign in signs:
                        for right_sign in signs:
                            denominator = left_p * left_sign - right_p * right_sign
                            if denominator == 0:
                                continue
                            numerator = (
                                left_p * left_sign * lifted_left
                                - right_p * right_sign * lifted_right
                            )
                            point = numerator / denominator
                            if not Fraction(0) <= point <= Fraction(1):
                                continue
                            if left_sign * (point - lifted_left) < 0:
                                continue
                            if right_sign * (point - lifted_right) < 0:
                                continue
                            candidates.add(point % 1)

    best_radius = Fraction(-1)
    best_point = Fraction(0)
    best_active: tuple[int, ...] = ()
    for point in sorted(candidates):
        distances = [
            (p * circular_distance(point, center), p)
            for p, center in centers
        ]
        radius = min(value for value, _ in distances)
        active = tuple(sorted(p for value, p in distances if value == radius))
        if radius > best_radius or (radius == best_radius and point < best_point):
            best_radius = radius
            best_point = point
            best_active = active

    return best_radius, best_point, best_active


def critical_radius_status(radius: Fraction) -> str:
    threshold = Fraction(1, 2)
    if radius < threshold:
        return "robust_covered"
    if radius == threshold:
        return "endpoint_covered"
    return "uncovered"


def circular_distance(left: Fraction, right: Fraction) -> Fraction:
    delta = abs((left - right) % 1)
    return min(delta, Fraction(1) - delta)


def birth_dynamics_rows(
    *,
    min_k: int = 5,
    max_k: int = 7,
    full_rows: Sequence[PrimePrefixResidueFullRow] | None = None,
) -> list[BirthDynamicsRow]:
    """Return exact birth-mechanism rows for birth layers ``min_k..max_k``."""
    if full_rows is None:
        full_rows = prime_prefix_residue_full_rows(max_k=max_k, allow_large_k=max_k > 6)
    birth_rows = [
        row
        for row in full_rows
        if min_k <= row.k <= max_k and row.status == "birth"
    ]

    rows: list[BirthDynamicsRow] = []
    for row in birth_rows:
        primes = first_primes(row.k)
        previous_primes = primes[:-1]
        new_prime = primes[-1]
        previous_modulus = primorial(previous_primes)
        previous_gaps = residue_uncovered_intervals(row.residue, previous_primes)
        new_arcs = exact_arc_intervals_for_residue(row.residue, new_prime)
        containment = classify_birth_containment(previous_gaps, new_arcs)
        birth_type = (
            ("endpoint" if containment.uses_endpoint_touching else "strict")
            + ("_single_gap_birth" if len(previous_gaps) == 1 else "_multi_gap_birth")
        )
        rows.append(
            BirthDynamicsRow(
                k=row.k,
                new_prime=new_prime,
                primorial=row.primorial,
                residue=row.residue,
                parent_residue_mod_previous=row.residue % previous_modulus,
                reflection_residue=row.reflection_residue,
                birth_type=birth_type,
                previous_open_gap_count=len(previous_gaps),
                previous_uncovered_measure_fraction=format_fraction(
                    residue_uncovered_measure(row.residue, previous_primes)
                ),
                previous_open_gap_boundary_endpoints=format_intervals(previous_gaps),
                new_prime_remainder=row.residue % new_prime,
                new_prime_closed_arc_boundary_endpoints=format_intervals(new_arcs),
                containment_margin_fraction=format_fraction(containment.margin),
                uses_endpoint_touching=containment.uses_endpoint_touching,
            )
        )
    return rows


def birth_dynamics_summary_rows(rows: Iterable[BirthDynamicsRow]) -> list[BirthDynamicsSummaryRow]:
    grouped: dict[int, list[BirthDynamicsRow]] = {}
    for row in rows:
        grouped.setdefault(row.k, []).append(row)

    summary: list[BirthDynamicsSummaryRow] = []
    for k, group in sorted(grouped.items()):
        counts = {
            "strict_single_gap_birth": 0,
            "endpoint_single_gap_birth": 0,
            "strict_multi_gap_birth": 0,
            "endpoint_multi_gap_birth": 0,
        }
        for row in group:
            counts[row.birth_type] += 1
        measures = sorted({row.previous_uncovered_measure_fraction for row in group})
        summary.append(
            BirthDynamicsSummaryRow(
                k=k,
                new_prime=group[0].new_prime,
                primorial=group[0].primorial,
                birth_count=len(group),
                strict_single_gap_birth=counts["strict_single_gap_birth"],
                endpoint_single_gap_birth=counts["endpoint_single_gap_birth"],
                strict_multi_gap_birth=counts["strict_multi_gap_birth"],
                endpoint_multi_gap_birth=counts["endpoint_multi_gap_birth"],
                max_previous_open_gap_count=max(row.previous_open_gap_count for row in group),
                previous_uncovered_measure_fractions=" ".join(measures),
            )
        )
    return summary


@dataclass(frozen=True)
class BirthContainment:
    margin: Fraction
    uses_endpoint_touching: bool


def classify_birth_containment(
    previous_gaps: Iterable[ExactInterval],
    new_arcs: Iterable[ExactInterval],
) -> BirthContainment:
    """Return exact containment margin of old open gaps in new closed arcs."""
    arc_segments = [segment for interval in new_arcs for segment in split_interval(interval)]
    margins: list[Fraction] = []
    for gap in previous_gaps:
        for gap_segment in split_interval(gap):
            containing = [
                (gap_segment[0] - arc[0], arc[1] - gap_segment[1])
                for arc in arc_segments
                if arc[0] <= gap_segment[0] and gap_segment[1] <= arc[1]
            ]
            if not containing:
                raise ValueError("birth gap is not contained in the new prime arc")
            margins.append(max(min(left_margin, right_margin) for left_margin, right_margin in containing))
    margin = min(margins) if margins else Fraction(0)
    return BirthContainment(margin=margin, uses_endpoint_touching=margin == 0)


def exact_arc_intervals_for_residue(residue: int, p: int) -> list[ExactInterval]:
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


def split_interval(interval: ExactInterval) -> list[ExactInterval]:
    start, end = interval
    if end >= start:
        return [(start, end)]
    return [(start, Fraction(1)), (Fraction(0), end)]


def interval_length(interval: ExactInterval) -> Fraction:
    return sum(end - start for start, end in split_interval(interval))


def format_fraction(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def format_intervals(intervals: Iterable[ExactInterval]) -> str:
    return ";".join(
        f"{format_fraction(start)}-{format_fraction(end)}"
        for start, end in intervals
    )


def write_dataclass_csv(rows: Iterable[object], output_path: str | Path, row_type: type) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(row_type.__dataclass_fields__.keys())  # type: ignore[attr-defined]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def write_critical_radius_csv(rows: Iterable[CriticalRadiusRow], output_path: str | Path) -> None:
    write_dataclass_csv(rows, output_path, CriticalRadiusRow)


def write_critical_radius_summary_csv(
    rows: Iterable[CriticalRadiusSummaryRow],
    output_path: str | Path,
) -> None:
    write_dataclass_csv(rows, output_path, CriticalRadiusSummaryRow)


def write_critical_radius_near_miss_csv(
    rows: Iterable[CriticalRadiusNearMissRow],
    output_path: str | Path,
) -> None:
    write_dataclass_csv(rows, output_path, CriticalRadiusNearMissRow)


def write_near_miss_birth_parent_csv(
    rows: Iterable[NearMissBirthParentRow],
    output_path: str | Path,
) -> None:
    write_dataclass_csv(rows, output_path, NearMissBirthParentRow)


def write_near_miss_gap_geometry_csv(
    rows: Iterable[NearMissGapGeometryRow],
    output_path: str | Path,
) -> None:
    write_dataclass_csv(rows, output_path, NearMissGapGeometryRow)


def write_birth_threshold_crossing_csv(
    rows: Iterable[BirthThresholdCrossingRow],
    output_path: str | Path,
) -> None:
    write_dataclass_csv(rows, output_path, BirthThresholdCrossingRow)


def write_birth_dynamics_csv(rows: Iterable[BirthDynamicsRow], output_path: str | Path) -> None:
    write_dataclass_csv(rows, output_path, BirthDynamicsRow)


def write_birth_dynamics_summary_csv(
    rows: Iterable[BirthDynamicsSummaryRow],
    output_path: str | Path,
) -> None:
    write_dataclass_csv(rows, output_path, BirthDynamicsSummaryRow)
