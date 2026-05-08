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
class PrimePrefixExclusionWitnessV16Row:
    """Theorem-oriented exclusion witness with a rational interior point."""

    k: int
    new_prime: int
    primorial: int
    residue: int
    reflection_residue: int
    open_gap_count: int
    uncovered_measure_fraction: str
    uncovered_measure: float
    first_open_gap_boundary_endpoints: str
    witness_point: str
    open_gap_boundary_endpoints: str


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


@dataclass(frozen=True)
class PrimePrefixBirthPairSummaryRow:
    """Reflection-pair summary for birth residues."""

    k: int
    new_prime: int
    primorial: int
    reflection_pair_min: int
    reflection_pair_max: int
    parent_residue_pair_mod_previous: str
    previous_uncovered_interval_count_pair: str
    previous_prefix_uncovered_measure_pair: str
    previous_uncovered_intervals_pair: str
    new_prime_remainder_pair: str
    new_prime_arc_intervals_pair: str
    uses_endpoint_touching_pair: str


@dataclass(frozen=True)
class PrimePrefixExclusionSummaryRow:
    """Compressed exclusion-witness group for one prefix level."""

    k: int
    new_prime: int
    primorial: int
    uncovered_interval_count: int
    uncovered_measure_fraction: str
    uncovered_measure: float
    residue_count: int
    residues_sample: str
    first_uncovered_interval_sample: str


@dataclass(frozen=True)
class PrimePrefixBirthWitnessV15Row:
    """Theorem-oriented birth witness with exact fractions and open-gap wording."""

    k: int
    new_prime: int
    primorial: int
    residue: int
    residue_mod_previous: int | None
    reflection_residue: int
    previous_open_gap_count: int
    previous_prefix_uncovered_measure_fraction: str
    previous_prefix_uncovered_measure: float
    previous_open_gap_boundary_endpoints: str
    new_prime_closed_arc_boundary_endpoints: str
    uses_endpoint_touching: bool


@dataclass(frozen=True)
class PrimePrefixBirthClassificationV15Row:
    """Template classification with exact gap-measure fractions."""

    k: int
    new_prime: int
    primorial: int
    residue: int
    reflection_residue: int
    reflection_pair_min: int
    reflection_pair_max: int
    parent_residue_mod_previous: int
    previous_open_gap_count: int
    previous_prefix_uncovered_measure_fraction: str
    previous_prefix_uncovered_measure: float
    previous_open_gap_boundary_endpoints: str
    new_prime_remainder: int
    new_prime_closed_arc_boundary_endpoints: str
    uses_endpoint_touching: bool


@dataclass(frozen=True)
class PrimePrefixBirthPairSummaryV15Row:
    """Reflection-pair summary with exact fraction pairs."""

    k: int
    new_prime: int
    primorial: int
    reflection_pair_min: int
    reflection_pair_max: int
    parent_residue_pair_mod_previous: str
    previous_open_gap_count_pair: str
    previous_prefix_uncovered_measure_fraction_pair: str
    previous_prefix_uncovered_measure_pair: str
    previous_open_gap_boundary_endpoints_pair: str
    new_prime_remainder_pair: str
    new_prime_closed_arc_boundary_endpoints_pair: str
    uses_endpoint_touching_pair: str


@dataclass(frozen=True)
class PrimePrefixExclusionSummaryV15Row:
    """Compressed C4 exclusion group with complete residue lists."""

    k: int
    new_prime: int
    primorial: int
    open_gap_count: int
    uncovered_measure_fraction: str
    uncovered_measure: float
    residue_count: int
    residues: str
    first_open_gap_boundary_endpoint_sample: str


@dataclass(frozen=True)
class PrimePrefixCertificateVerificationRow:
    """Summary row for independent finite-certificate verification."""

    check_name: str
    total: int
    passed: int
    failed: int
    status: str


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


def prime_prefix_exclusion_witness_v16_rows(
    *,
    k: int = 4,
    allow_large_k: bool = False,
) -> list[PrimePrefixExclusionWitnessV16Row]:
    """Return theorem-oriented gap witnesses with explicit interior points."""
    _validate_small_export_k(k, allow_large_k=allow_large_k)
    primes = _first_primes(k)
    primorial = _primorial(primes)
    covered = {
        row.residue
        for row in prime_prefix_residue_full_rows(max_k=k, allow_large_k=allow_large_k)
        if row.k == k
    }
    rows: list[PrimePrefixExclusionWitnessV16Row] = []
    for residue in range(primorial):
        if residue in covered:
            continue
        gaps = residue_uncovered_intervals(residue, primes)
        measure = residue_uncovered_measure(residue, primes)
        first_gap = gaps[0]
        rows.append(
            PrimePrefixExclusionWitnessV16Row(
                k=k,
                new_prime=primes[-1],
                primorial=primorial,
                residue=residue,
                reflection_residue=(-residue) % primorial,
                open_gap_count=len(gaps),
                uncovered_measure_fraction=_format_fraction(measure),
                uncovered_measure=float(measure),
                first_open_gap_boundary_endpoints=_format_intervals([first_gap]),
                witness_point=_format_fraction(_circular_midpoint(first_gap)),
                open_gap_boundary_endpoints=_format_intervals(gaps),
            )
        )
    return rows


def prime_prefix_exclusion_summary_rows(
    *,
    k: int = 4,
    allow_large_k: bool = False,
) -> list[PrimePrefixExclusionSummaryRow]:
    """Return compressed classes for exclusion witnesses at one prefix level."""
    _validate_small_export_k(k, allow_large_k=allow_large_k)
    primes = _first_primes(k)
    primorial = _primorial(primes)
    groups: dict[tuple[int, Fraction], list[tuple[int, str]]] = {}
    for row in prime_prefix_exclusion_witness_rows(k=k, allow_large_k=allow_large_k):
        exact_measure = residue_uncovered_measure(row.residue, primes)
        groups.setdefault((row.uncovered_interval_count, exact_measure), []).append(
            (row.residue, row.first_uncovered_interval)
        )

    rows: list[PrimePrefixExclusionSummaryRow] = []
    for (gap_count, measure), values in sorted(groups.items(), key=_exclusion_summary_sort_key):
        residues = [residue for residue, _ in values]
        first_intervals = sorted({interval for _, interval in values})
        rows.append(
            PrimePrefixExclusionSummaryRow(
                k=k,
                new_prime=primes[-1],
                primorial=primorial,
                uncovered_interval_count=gap_count,
                uncovered_measure_fraction=_format_fraction(measure),
                uncovered_measure=float(measure),
                residue_count=len(residues),
                residues_sample=" ".join(str(residue) for residue in residues[:20]),
                first_uncovered_interval_sample=" ".join(first_intervals[:8]),
            )
        )
    return rows


def prime_prefix_exclusion_summary_v15_rows(
    *,
    k: int = 4,
    allow_large_k: bool = False,
) -> list[PrimePrefixExclusionSummaryV15Row]:
    """Return theorem-oriented C4 exclusion classes with complete residue lists."""
    _validate_small_export_k(k, allow_large_k=allow_large_k)
    primes = _first_primes(k)
    primorial = _primorial(primes)
    groups: dict[tuple[int, Fraction], list[tuple[int, str]]] = {}
    for row in prime_prefix_exclusion_witness_rows(k=k, allow_large_k=allow_large_k):
        exact_measure = residue_uncovered_measure(row.residue, primes)
        groups.setdefault((row.uncovered_interval_count, exact_measure), []).append(
            (row.residue, row.first_uncovered_interval)
        )

    rows: list[PrimePrefixExclusionSummaryV15Row] = []
    for (gap_count, measure), values in sorted(groups.items(), key=_exclusion_summary_sort_key):
        residues = [residue for residue, _ in values]
        first_intervals = sorted({interval for _, interval in values})
        rows.append(
            PrimePrefixExclusionSummaryV15Row(
                k=k,
                new_prime=primes[-1],
                primorial=primorial,
                open_gap_count=gap_count,
                uncovered_measure_fraction=_format_fraction(measure),
                uncovered_measure=float(measure),
                residue_count=len(residues),
                residues=" ".join(str(residue) for residue in residues),
                first_open_gap_boundary_endpoint_sample=" ".join(first_intervals[:8]),
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


def prime_prefix_birth_witness_v15_rows(
    *,
    k: int = 5,
    allow_large_k: bool = False,
) -> list[PrimePrefixBirthWitnessV15Row]:
    """Return theorem-oriented birth witnesses with exact fraction columns."""
    _validate_small_export_k(k, allow_large_k=allow_large_k)
    full_rows = [
        row
        for row in prime_prefix_residue_full_rows(max_k=k, allow_large_k=allow_large_k)
        if row.k == k and row.status == "birth"
    ]
    primes = _first_primes(k)
    previous_primes = primes[:-1]
    new_prime = primes[-1]
    previous_primorial = _primorial(previous_primes)

    rows: list[PrimePrefixBirthWitnessV15Row] = []
    for row in full_rows:
        previous_gaps = residue_uncovered_intervals(row.residue, previous_primes)
        previous_measure = residue_uncovered_measure(row.residue, previous_primes)
        new_arc_intervals = _exact_arc_intervals_for_residue(row.residue, new_prime)
        rows.append(
            PrimePrefixBirthWitnessV15Row(
                k=row.k,
                new_prime=row.new_prime,
                primorial=row.primorial,
                residue=row.residue,
                residue_mod_previous=(
                    row.residue % previous_primorial if previous_primes else None
                ),
                reflection_residue=row.reflection_residue,
                previous_open_gap_count=len(previous_gaps),
                previous_prefix_uncovered_measure_fraction=_format_fraction(previous_measure),
                previous_prefix_uncovered_measure=float(previous_measure),
                previous_open_gap_boundary_endpoints=_format_intervals(previous_gaps),
                new_prime_closed_arc_boundary_endpoints=_format_intervals(new_arc_intervals),
                uses_endpoint_touching=_uses_endpoint_touching(
                    previous_gaps,
                    new_arc_intervals,
                ),
            )
        )
    return rows


def prime_prefix_birth_classification_v15_rows(
    *,
    k: int = 5,
    allow_large_k: bool = False,
) -> list[PrimePrefixBirthClassificationV15Row]:
    """Return theorem-oriented B5 classifications with exact fraction columns."""
    witness_rows = prime_prefix_birth_witness_v15_rows(k=k, allow_large_k=allow_large_k)
    rows: list[PrimePrefixBirthClassificationV15Row] = []
    for row in witness_rows:
        pair_min = min(row.residue, row.reflection_residue)
        pair_max = max(row.residue, row.reflection_residue)
        rows.append(
            PrimePrefixBirthClassificationV15Row(
                k=row.k,
                new_prime=row.new_prime,
                primorial=row.primorial,
                residue=row.residue,
                reflection_residue=row.reflection_residue,
                reflection_pair_min=pair_min,
                reflection_pair_max=pair_max,
                parent_residue_mod_previous=row.residue_mod_previous or 0,
                previous_open_gap_count=row.previous_open_gap_count,
                previous_prefix_uncovered_measure_fraction=(
                    row.previous_prefix_uncovered_measure_fraction
                ),
                previous_prefix_uncovered_measure=row.previous_prefix_uncovered_measure,
                previous_open_gap_boundary_endpoints=row.previous_open_gap_boundary_endpoints,
                new_prime_remainder=row.residue % row.new_prime,
                new_prime_closed_arc_boundary_endpoints=(
                    row.new_prime_closed_arc_boundary_endpoints
                ),
                uses_endpoint_touching=row.uses_endpoint_touching,
            )
        )
    return rows


def prime_prefix_birth_pair_summary_v15_rows(
    *,
    k: int = 5,
    allow_large_k: bool = False,
) -> list[PrimePrefixBirthPairSummaryV15Row]:
    """Return theorem-oriented B5 reflection-pair summaries."""
    classification_rows = prime_prefix_birth_classification_v15_rows(
        k=k,
        allow_large_k=allow_large_k,
    )
    groups: dict[tuple[int, int], list[PrimePrefixBirthClassificationV15Row]] = {}
    for row in classification_rows:
        key = (row.reflection_pair_min, row.reflection_pair_max)
        groups.setdefault(key, []).append(row)

    rows: list[PrimePrefixBirthPairSummaryV15Row] = []
    for (pair_min, pair_max), group in sorted(groups.items()):
        ordered = sorted(group, key=lambda row: row.residue)
        if len(ordered) != 2:
            raise ValueError(
                "birth pair summary expects two residues per reflection pair; "
                f"got {len(ordered)} for {pair_min}/{pair_max}"
            )
        first = ordered[0]
        rows.append(
            PrimePrefixBirthPairSummaryV15Row(
                k=first.k,
                new_prime=first.new_prime,
                primorial=first.primorial,
                reflection_pair_min=pair_min,
                reflection_pair_max=pair_max,
                parent_residue_pair_mod_previous=_join_pair(
                    [row.parent_residue_mod_previous for row in ordered]
                ),
                previous_open_gap_count_pair=_join_pair(
                    [row.previous_open_gap_count for row in ordered]
                ),
                previous_prefix_uncovered_measure_fraction_pair=_join_pair(
                    [row.previous_prefix_uncovered_measure_fraction for row in ordered]
                ),
                previous_prefix_uncovered_measure_pair=_join_pair(
                    [row.previous_prefix_uncovered_measure for row in ordered]
                ),
                previous_open_gap_boundary_endpoints_pair=_join_pair(
                    [row.previous_open_gap_boundary_endpoints for row in ordered]
                ),
                new_prime_remainder_pair=_join_pair(
                    [row.new_prime_remainder for row in ordered]
                ),
                new_prime_closed_arc_boundary_endpoints_pair=_join_pair(
                    [row.new_prime_closed_arc_boundary_endpoints for row in ordered]
                ),
                uses_endpoint_touching_pair=_join_pair(
                    [row.uses_endpoint_touching for row in ordered]
                ),
            )
        )
    return rows


def prime_prefix_birth_pair_summary_rows(
    *,
    k: int = 5,
    allow_large_k: bool = False,
) -> list[PrimePrefixBirthPairSummaryRow]:
    """Return reflection-pair summaries for birth residues."""
    classification_rows = prime_prefix_birth_classification_rows(
        k=k,
        allow_large_k=allow_large_k,
    )
    groups: dict[tuple[int, int], list[PrimePrefixBirthClassificationRow]] = {}
    for row in classification_rows:
        key = (row.reflection_pair_min, row.reflection_pair_max)
        groups.setdefault(key, []).append(row)

    rows: list[PrimePrefixBirthPairSummaryRow] = []
    for (pair_min, pair_max), group in sorted(groups.items()):
        ordered = sorted(group, key=lambda row: row.residue)
        if len(ordered) != 2:
            raise ValueError(
                "birth pair summary expects two residues per reflection pair; "
                f"got {len(ordered)} for {pair_min}/{pair_max}"
            )
        first = ordered[0]
        rows.append(
            PrimePrefixBirthPairSummaryRow(
                k=first.k,
                new_prime=first.new_prime,
                primorial=first.primorial,
                reflection_pair_min=pair_min,
                reflection_pair_max=pair_max,
                parent_residue_pair_mod_previous=_join_pair(
                    [row.parent_residue_mod_previous for row in ordered]
                ),
                previous_uncovered_interval_count_pair=_join_pair(
                    [row.previous_uncovered_interval_count for row in ordered]
                ),
                previous_prefix_uncovered_measure_pair=_join_pair(
                    [row.previous_prefix_uncovered_measure for row in ordered]
                ),
                previous_uncovered_intervals_pair=_join_pair(
                    [row.previous_uncovered_intervals for row in ordered]
                ),
                new_prime_remainder_pair=_join_pair(
                    [row.new_prime_remainder for row in ordered]
                ),
                new_prime_arc_intervals_pair=_join_pair(
                    [row.new_prime_arc_intervals for row in ordered]
                ),
                uses_endpoint_touching_pair=_join_pair(
                    [row.uses_endpoint_touching for row in ordered]
                ),
            )
        )
    return rows


def prime_prefix_certificate_verification_rows(
    *,
    ck_full_csv: str | Path = "data/summaries/prc_prime_prefix_ck_full_v1_1.csv",
    c4_exclusion_witness_csv: str | Path = (
        "data/summaries/prc_prime_prefix_c4_exclusion_witness_v1_6.csv"
    ),
    b5_birth_witness_csv: str | Path = (
        "data/summaries/prc_prime_prefix_birth_witness_v1_5.csv"
    ),
    b5_birth_pair_summary_csv: str | Path = (
        "data/summaries/prc_prime_prefix_b5_birth_pair_summary_v1_5.csv"
    ),
) -> list[PrimePrefixCertificateVerificationRow]:
    """Verify public C4/B5 certificate CSVs using low-level rational checks."""
    ck_rows = _read_csv_dicts(ck_full_csv)
    c4_exclusion_rows = _read_csv_dicts(c4_exclusion_witness_csv)
    b5_birth_rows = _read_csv_dicts(b5_birth_witness_csv)
    b5_pair_rows = _read_csv_dicts(b5_birth_pair_summary_csv)

    checks: list[PrimePrefixCertificateVerificationRow] = []

    c4_positive_residues = [
        int(row["residue"])
        for row in ck_rows
        if row.get("k") == "4"
    ]
    c4_positive_passed = sum(
        residue in {2, 208} and residue_is_exactly_covered(residue, [2, 3, 5, 7])
        for residue in c4_positive_residues
    )
    checks.append(
        _verification_row(
            "c4_positive_closed_arc_coverage",
            total=2,
            passed=c4_positive_passed if set(c4_positive_residues) == {2, 208} else 0,
        )
    )

    c4_exclusion_passed = 0
    c4_witness_point_passed = 0
    for row in c4_exclusion_rows:
        residue = int(row["residue"])
        intervals = _parse_interval_list(_first_gap_boundary_text(row))
        if intervals and _has_valid_open_gap_witness(residue, [2, 3, 5, 7], intervals[0]):
            c4_exclusion_passed += 1
        if intervals and "witness_point" in row:
            witness_point = _parse_fraction(row["witness_point"])
            if (
                _point_in_open_interval(witness_point, intervals[0])
                and not _point_is_covered_by_closed_arcs(
                    witness_point,
                    residue,
                    [2, 3, 5, 7],
                )
            ):
                c4_witness_point_passed += 1
    checks.append(
        _verification_row(
            "c4_exclusion_open_gap_witness",
            total=len(c4_exclusion_rows),
            passed=c4_exclusion_passed,
        )
    )
    if c4_exclusion_rows and "witness_point" in c4_exclusion_rows[0]:
        checks.append(
            _verification_row(
                "c4_exclusion_rational_witness_point",
                total=len(c4_exclusion_rows),
                passed=c4_witness_point_passed,
            )
        )

    b5_birth_coverage_passed = 0
    b5_gap_containment_passed = 0
    for row in b5_birth_rows:
        residue = int(row["residue"])
        if (
            not residue_is_exactly_covered(residue, [2, 3, 5, 7])
            and residue_is_exactly_covered(residue, [2, 3, 5, 7, 11])
        ):
            b5_birth_coverage_passed += 1
        old_gaps = _parse_interval_list(row["previous_open_gap_boundary_endpoints"])
        new_arcs = _parse_interval_list(row["new_prime_closed_arc_boundary_endpoints"])
        if old_gaps and all(_gap_strictly_inside_closed_arcs(gap, new_arcs) for gap in old_gaps):
            b5_gap_containment_passed += 1
    checks.append(
        _verification_row(
            "b5_birth_previous_uncovered_current_covered",
            total=len(b5_birth_rows),
            passed=b5_birth_coverage_passed,
        )
    )
    checks.append(
        _verification_row(
            "b5_birth_old_open_gap_strictly_inside_new_arc",
            total=len(b5_birth_rows),
            passed=b5_gap_containment_passed,
        )
    )

    b5_reflection_passed = 0
    for row in b5_pair_rows:
        primorial = int(row["primorial"])
        pair_min = int(row["reflection_pair_min"])
        pair_max = int(row["reflection_pair_max"])
        if (-pair_min) % primorial == pair_max and (-pair_max) % primorial == pair_min:
            b5_reflection_passed += 1
    checks.append(
        _verification_row(
            "b5_reflection_pair_fields",
            total=len(b5_pair_rows),
            passed=b5_reflection_passed,
        )
    )

    return checks


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


def write_prime_prefix_exclusion_witness_v16_csv(
    rows: Iterable[PrimePrefixExclusionWitnessV16Row],
    output_path: str | Path,
) -> None:
    """Write theorem-oriented exclusion witness rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixExclusionWitnessV16Row)


def write_prime_prefix_exclusion_summary_csv(
    rows: Iterable[PrimePrefixExclusionSummaryRow],
    output_path: str | Path,
) -> None:
    """Write compressed exclusion summary rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixExclusionSummaryRow)


def write_prime_prefix_exclusion_summary_v15_csv(
    rows: Iterable[PrimePrefixExclusionSummaryV15Row],
    output_path: str | Path,
) -> None:
    """Write theorem-oriented exclusion summary rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixExclusionSummaryV15Row)


def write_prime_prefix_birth_classification_csv(
    rows: Iterable[PrimePrefixBirthClassificationRow],
    output_path: str | Path,
) -> None:
    """Write birth classification rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixBirthClassificationRow)


def write_prime_prefix_birth_pair_summary_csv(
    rows: Iterable[PrimePrefixBirthPairSummaryRow],
    output_path: str | Path,
) -> None:
    """Write birth reflection-pair summary rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixBirthPairSummaryRow)


def write_prime_prefix_birth_witness_v15_csv(
    rows: Iterable[PrimePrefixBirthWitnessV15Row],
    output_path: str | Path,
) -> None:
    """Write theorem-oriented birth witness rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixBirthWitnessV15Row)


def write_prime_prefix_birth_classification_v15_csv(
    rows: Iterable[PrimePrefixBirthClassificationV15Row],
    output_path: str | Path,
) -> None:
    """Write theorem-oriented birth classification rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixBirthClassificationV15Row)


def write_prime_prefix_birth_pair_summary_v15_csv(
    rows: Iterable[PrimePrefixBirthPairSummaryV15Row],
    output_path: str | Path,
) -> None:
    """Write theorem-oriented birth reflection-pair summary rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixBirthPairSummaryV15Row)


def write_prime_prefix_certificate_verification_csv(
    rows: Iterable[PrimePrefixCertificateVerificationRow],
    output_path: str | Path,
) -> None:
    """Write independent certificate verification summary rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixCertificateVerificationRow)


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


def _join_pair(values: Iterable[object]) -> str:
    return " / ".join(str(value) for value in values)


def _primorial(primes: Iterable[int]) -> int:
    value = 1
    for p in primes:
        value *= p
    return value


def _exclusion_summary_sort_key(
    item: tuple[tuple[int, Fraction], list[tuple[int, str]]],
) -> tuple[int, Fraction]:
    (gap_count, measure), _ = item
    return (gap_count, measure)


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


def _read_csv_dicts(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _verification_row(
    check_name: str,
    *,
    total: int,
    passed: int,
) -> PrimePrefixCertificateVerificationRow:
    failed = total - passed
    return PrimePrefixCertificateVerificationRow(
        check_name=check_name,
        total=total,
        passed=passed,
        failed=failed,
        status="pass" if failed == 0 else "fail",
    )


def _parse_fraction(text: str) -> Fraction:
    if "/" in text:
        numerator, denominator = text.split("/", 1)
        return Fraction(int(numerator), int(denominator))
    return Fraction(int(text), 1)


def _parse_interval_list(text: str) -> list[ExactInterval]:
    if not text:
        return []
    intervals: list[ExactInterval] = []
    for item in text.split(";"):
        start, end = item.split("-", 1)
        intervals.append((_parse_fraction(start), _parse_fraction(end)))
    return intervals


def _first_gap_boundary_text(row: dict[str, str]) -> str:
    return row.get("first_open_gap_boundary_endpoints") or row.get("first_uncovered_interval", "")


def _has_valid_open_gap_witness(
    residue: int,
    primes: Iterable[int],
    gap: ExactInterval,
) -> bool:
    if _exact_interval_length(gap) <= 0:
        return False
    witness = _circular_midpoint(gap)
    return not _point_is_covered_by_closed_arcs(witness, residue, primes)


def _circular_midpoint(interval: ExactInterval) -> Fraction:
    start, end = interval
    one = Fraction(1)
    if end >= start:
        return (start + end) / 2
    return ((start + end + one) / 2) % one


def _point_is_covered_by_closed_arcs(
    point: Fraction,
    residue: int,
    primes: Iterable[int],
) -> bool:
    for p in primes:
        if any(_point_in_closed_interval(point, interval) for interval in _exact_arc_intervals_for_residue(residue, p)):
            return True
    return False


def _point_in_closed_interval(point: Fraction, interval: ExactInterval) -> bool:
    return any(start <= point <= end for start, end in _split_interval(interval))


def _point_in_open_interval(point: Fraction, interval: ExactInterval) -> bool:
    return any(start < point < end for start, end in _split_interval(interval))


def _gap_strictly_inside_closed_arcs(
    gap: ExactInterval,
    arc_intervals: Iterable[ExactInterval],
) -> bool:
    arc_segments = [
        segment
        for interval in arc_intervals
        for segment in _split_interval(interval)
    ]
    for gap_segment in _split_interval(gap):
        gap_start, gap_end = gap_segment
        if not any(
            _point_in_open_interval(gap_start, arc_segment)
            and _point_in_open_interval(gap_end, arc_segment)
            for arc_segment in arc_segments
        ):
            return False
    return True


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
