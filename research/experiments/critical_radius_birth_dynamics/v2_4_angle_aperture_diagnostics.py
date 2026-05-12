"""Source-only helpers for PRC v2.4 angle/aperture diagnostics."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from tools import (
    birth_dynamics_rows,
    classify_birth_containment,
    exact_arc_intervals_for_residue,
    first_primes,
    format_fraction,
    format_intervals,
    interval_length,
    primorial,
    residue_uncovered_intervals,
    residue_uncovered_measure,
)
from v2_4_residual_genealogy import read_birth_residual_genealogy_csv
from v2_4_transition_pilot import circular_components

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_K2_GAP_WIDTH_BIAS_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_k2_gap_width_bias_v0_1.csv"
)
DEFAULT_LINEAGE_MEASURE_BIAS_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_lineage_measure_bias_v0_1.csv"
)
DEFAULT_FINAL_APERTURE_MARGINS_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_final_aperture_margins_v0_1.csv"
)
DEFAULT_Q_GRID_BIRTH_PHASE_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_q_grid_birth_phase_histogram_v0_1.csv"
)
DEFAULT_INCREMENTAL_GRID_PHASE_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_incremental_grid_phase_histogram_v0_1.csv"
)
DEFAULT_BIRTH_POTENTIAL_SCORE_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_birth_potential_score_v0_1.csv"
)
DEFAULT_BIRTH_POTENTIAL_CORRELATION_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_birth_potential_score_correlation_v0_1.csv"
)

TARGET_SECTORS: tuple[tuple[Fraction, Fraction], ...] = (
    (Fraction(1, 6), Fraction(1, 4)),
    (Fraction(3, 4), Fraction(5, 6)),
)


@dataclass(frozen=True)
class K2GapWidthBiasRow:
    residue_mod_6: int
    residual_gap_endpoints: str
    residual_width: str
    covered_width: str
    zero_point_in_residual: bool
    birth_lineage_count: int
    expected_uniform_count: str
    expected_residual_weighted_count: str
    expected_covered_weighted_count: str
    expected_inverse_width_weighted_count: str
    observed_over_uniform: str
    observed_over_residual_weighted: str
    observed_over_covered_weighted: str
    observed_over_inverse_width_weighted: str


@dataclass(frozen=True)
class LineageMeasureBiasRow:
    layer_k: int
    population: str
    row_count: int
    average_residual_measure: str
    zero_point_blank_count: int
    zero_point_blank_fraction: str
    target_sector_residual_measure_average: str
    target_sector_share_of_residual: str


@dataclass(frozen=True)
class FinalApertureMarginRow:
    birth_k: int
    birth_residue: int
    parent_residue: int
    new_prime: int
    new_prime_remainder: int
    prefinal_gap_count: int
    prefinal_gap_endpoints: str
    prefinal_gap_width: str
    new_arc_width: str
    aperture_margin: str
    containment_margin: str


@dataclass(frozen=True)
class QGridBirthPhaseRow:
    birth_k: int
    new_prime: int
    new_prime_remainder: int
    center_fraction: str
    center_degrees: str
    birth_count: int
    reflected_remainder: int
    reflected_birth_count: int
    reflection_pair_count: int


@dataclass(frozen=True)
class IncrementalGridPhaseRow:
    birth_k: int
    layer_k: int
    new_prime: int
    new_prime_remainder: int
    center_fraction: str
    center_degrees: str
    transition_label: str
    row_count: int
    reflected_remainder: int
    reflected_row_count: int
    reflection_pair_count: int


@dataclass(frozen=True)
class BirthPotentialScoreRow:
    layer_k: int
    model: str
    residue: int
    occurrence_probability: str
    residual_width: str
    model_weight: str
    normalized_expected_count: str
    observed_birth_lineage_count: int
    observed_over_expected: str


@dataclass(frozen=True)
class BirthPotentialCorrelationRow:
    layer_k: int
    model: str
    pearson_correlation: str
    spearman_correlation: str
    mean_absolute_error: str
    note: str


def build_k2_gap_width_bias_rows() -> list[K2GapWidthBiasRow]:
    """Return width-corrected k=2 diagnostics for future birth lineages."""
    birth_lineage_counts = {residue: 0 for residue in range(6)}
    for row in read_birth_residual_genealogy_csv():
        if row.layer_k == 2:
            birth_lineage_counts[row.layer_residue] += 1
    total_birth_lineages = sum(birth_lineage_counts.values())
    widths = {
        residue: residue_uncovered_measure(residue, [2, 3])
        for residue in range(6)
    }
    covered_widths = {residue: Fraction(1) - width for residue, width in widths.items()}
    inverse_widths = {residue: Fraction(1, 1) / width for residue, width in widths.items()}
    uniform_denominator = Fraction(6)
    residual_weight_total = sum(widths.values(), Fraction(0))
    covered_weight_total = sum(covered_widths.values(), Fraction(0))
    inverse_weight_total = sum(inverse_widths.values(), Fraction(0))

    rows: list[K2GapWidthBiasRow] = []
    for residue in range(6):
        observed = Fraction(birth_lineage_counts[residue])
        expected_uniform = Fraction(total_birth_lineages, 1) / uniform_denominator
        expected_residual = (
            Fraction(total_birth_lineages) * widths[residue] / residual_weight_total
        )
        expected_covered = (
            Fraction(total_birth_lineages)
            * covered_widths[residue]
            / covered_weight_total
        )
        expected_inverse = (
            Fraction(total_birth_lineages)
            * inverse_widths[residue]
            / inverse_weight_total
        )
        rows.append(
            K2GapWidthBiasRow(
                residue_mod_6=residue,
                residual_gap_endpoints=format_intervals(
                    residue_uncovered_intervals(residue, [2, 3])
                ),
                residual_width=format_fraction(widths[residue]),
                covered_width=format_fraction(covered_widths[residue]),
                zero_point_in_residual=_point_in_any_gap(
                    Fraction(0),
                    residue_uncovered_intervals(residue, [2, 3]),
                ),
                birth_lineage_count=birth_lineage_counts[residue],
                expected_uniform_count=format_fraction(expected_uniform),
                expected_residual_weighted_count=format_fraction(expected_residual),
                expected_covered_weighted_count=format_fraction(expected_covered),
                expected_inverse_width_weighted_count=format_fraction(expected_inverse),
                observed_over_uniform=format_fraction(_safe_ratio(observed, expected_uniform)),
                observed_over_residual_weighted=format_fraction(
                    _safe_ratio(observed, expected_residual)
                ),
                observed_over_covered_weighted=format_fraction(
                    _safe_ratio(observed, expected_covered)
                ),
                observed_over_inverse_width_weighted=format_fraction(
                    _safe_ratio(observed, expected_inverse)
                ),
            )
        )
    return rows


def build_lineage_measure_bias_rows(max_k: int = 4) -> list[LineageMeasureBiasRow]:
    """Compare all residues with future-birth lineages by layer."""
    genealogy_rows = read_birth_residual_genealogy_csv()
    rows: list[LineageMeasureBiasRow] = []
    for layer_k in range(1, max_k + 1):
        primes = first_primes(layer_k)
        modulus = primorial(primes)
        all_residue_rows = [
            (
                residue_uncovered_intervals(residue, primes),
                residue_uncovered_measure(residue, primes),
            )
            for residue in range(modulus)
        ]
        rows.append(
            _lineage_measure_row(
                layer_k=layer_k,
                population="all_residues",
                gap_measure_pairs=all_residue_rows,
            )
        )
        birth_layer_rows = [
            row for row in genealogy_rows if row.layer_k == layer_k
        ]
        rows.append(
            _lineage_measure_row(
                layer_k=layer_k,
                population="birth_lineage",
                gap_measure_pairs=[
                    (
                        residue_uncovered_intervals(row.layer_residue, primes),
                        Fraction(row.uncovered_measure_fraction),
                    )
                    for row in birth_layer_rows
                ],
            )
        )
    return rows


def build_final_aperture_margin_rows() -> list[FinalApertureMarginRow]:
    """Return final birth-layer aperture margins for checked B5/B6/B7 births."""
    rows: list[FinalApertureMarginRow] = []
    for birth_row in birth_dynamics_rows(min_k=5, max_k=7):
        parent_primes = first_primes(birth_row.k - 1)
        gaps = residue_uncovered_intervals(
            birth_row.parent_residue_mod_previous,
            parent_primes,
        )
        arcs = exact_arc_intervals_for_residue(birth_row.residue, birth_row.new_prime)
        gap_width = sum(interval_length(gap) for gap in gaps)
        arc_width = sum(interval_length(arc) for arc in arcs)
        containment = classify_birth_containment(gaps, arcs)
        rows.append(
            FinalApertureMarginRow(
                birth_k=birth_row.k,
                birth_residue=birth_row.residue,
                parent_residue=birth_row.parent_residue_mod_previous,
                new_prime=birth_row.new_prime,
                new_prime_remainder=birth_row.new_prime_remainder,
                prefinal_gap_count=len(circular_components(gaps)),
                prefinal_gap_endpoints=format_intervals(gaps),
                prefinal_gap_width=format_fraction(gap_width),
                new_arc_width=format_fraction(arc_width),
                aperture_margin=format_fraction(arc_width - gap_width),
                containment_margin=format_fraction(containment.margin),
            )
        )
    return rows


def build_q_grid_birth_phase_rows() -> list[QGridBirthPhaseRow]:
    """Return final-birth q-grid center histograms for checked B5/B6/B7 rows."""
    rows: list[QGridBirthPhaseRow] = []
    for birth_k in (5, 6, 7):
        birth_rows = birth_dynamics_rows(min_k=birth_k, max_k=birth_k)
        new_prime = birth_rows[0].new_prime
        counts = {
            remainder: sum(
                row.new_prime_remainder == remainder for row in birth_rows
            )
            for remainder in range(new_prime)
        }
        for remainder, count in counts.items():
            if count == 0:
                continue
            reflected = (-remainder) % new_prime
            center = Fraction(remainder, new_prime)
            rows.append(
                QGridBirthPhaseRow(
                    birth_k=birth_k,
                    new_prime=new_prime,
                    new_prime_remainder=remainder,
                    center_fraction=format_fraction(center),
                    center_degrees=format_fraction(center * 360),
                    birth_count=count,
                    reflected_remainder=reflected,
                    reflected_birth_count=counts[reflected],
                    reflection_pair_count=count + counts[reflected],
                )
            )
    return rows


def build_incremental_grid_phase_rows() -> list[IncrementalGridPhaseRow]:
    """Return layer-by-layer new-prime grid center histograms."""
    genealogy_rows = read_birth_residual_genealogy_csv()
    counts = {
        (row.birth_k, row.layer_k, row.layer_residue % row.layer_prime, row.transition_label): 0
        for row in genealogy_rows
    }
    for row in genealogy_rows:
        key = (
            row.birth_k,
            row.layer_k,
            row.layer_residue % row.layer_prime,
            row.transition_label,
        )
        counts[key] += 1
    totals_by_layer_transition = {
        (birth_k, layer_k, transition): {
            remainder: count
            for (bk, lk, remainder, label), count in counts.items()
            if bk == birth_k and lk == layer_k and label == transition
        }
        for birth_k, layer_k, _, transition in counts
    }
    rows: list[IncrementalGridPhaseRow] = []
    for (birth_k, layer_k, remainder, transition_label), count in sorted(counts.items()):
        if count == 0:
            continue
        new_prime = first_primes(layer_k)[-1]
        reflected = (-remainder) % new_prime
        reflected_count = totals_by_layer_transition[
            (birth_k, layer_k, transition_label)
        ].get(reflected, 0)
        center = Fraction(remainder, new_prime)
        rows.append(
            IncrementalGridPhaseRow(
                birth_k=birth_k,
                layer_k=layer_k,
                new_prime=new_prime,
                new_prime_remainder=remainder,
                center_fraction=format_fraction(center),
                center_degrees=format_fraction(center * 360),
                transition_label=transition_label,
                row_count=count,
                reflected_remainder=reflected,
                reflected_row_count=reflected_count,
                reflection_pair_count=count + reflected_count,
            )
        )
    return rows


def build_birth_potential_score_rows(layer_k: int = 2) -> list[BirthPotentialScoreRow]:
    """Return simple width-based potential-score models for one early layer.

    These rows are hypothesis diagnostics. They compare width-based candidate
    scores with observed future-birth lineage counts without asserting that the
    best score is the sole cause of later births.
    """
    primes = first_primes(layer_k)
    modulus = primorial(primes)
    occurrence = Fraction(1, modulus)
    observed_counts = {residue: 0 for residue in range(modulus)}
    for row in read_birth_residual_genealogy_csv():
        if row.layer_k == layer_k:
            observed_counts[row.layer_residue] += 1
    residual_widths = {
        residue: residue_uncovered_measure(residue, primes)
        for residue in range(modulus)
    }
    model_weights = {
        "uniform": {
            residue: occurrence for residue in range(modulus)
        },
        "residual_width": {
            residue: occurrence * residual_widths[residue]
            for residue in range(modulus)
        },
        "covered_width": {
            residue: occurrence * (Fraction(1) - residual_widths[residue])
            for residue in range(modulus)
        },
        "inverse_width": {
            residue: occurrence / residual_widths[residue]
            for residue in range(modulus)
        },
    }
    total_observed = sum(observed_counts.values())
    rows: list[BirthPotentialScoreRow] = []
    for model_name, weights in model_weights.items():
        total_weight = sum(weights.values(), Fraction(0))
        for residue in range(modulus):
            expected = Fraction(total_observed) * weights[residue] / total_weight
            observed = observed_counts[residue]
            rows.append(
                BirthPotentialScoreRow(
                    layer_k=layer_k,
                    model=model_name,
                    residue=residue,
                    occurrence_probability=format_fraction(occurrence),
                    residual_width=format_fraction(residual_widths[residue]),
                    model_weight=format_fraction(weights[residue]),
                    normalized_expected_count=format_fraction(expected),
                    observed_birth_lineage_count=observed,
                    observed_over_expected=format_fraction(
                        _safe_ratio(Fraction(observed), expected)
                    ),
                )
            )
    return rows


def build_birth_potential_correlation_rows(
    score_rows: Iterable[BirthPotentialScoreRow] | None = None,
) -> list[BirthPotentialCorrelationRow]:
    """Return correlations between potential-score models and observed counts."""
    if score_rows is None:
        score_rows = build_birth_potential_score_rows()
    rows_by_model: dict[str, list[BirthPotentialScoreRow]] = {}
    for row in score_rows:
        rows_by_model.setdefault(row.model, []).append(row)
    rows: list[BirthPotentialCorrelationRow] = []
    for model, model_rows in sorted(rows_by_model.items()):
        ordered = sorted(model_rows, key=lambda row: row.residue)
        expected = [float(Fraction(row.normalized_expected_count)) for row in ordered]
        observed = [float(row.observed_birth_lineage_count) for row in ordered]
        mae = sum(abs(left - right) for left, right in zip(expected, observed)) / len(
            expected
        )
        rows.append(
            BirthPotentialCorrelationRow(
                layer_k=ordered[0].layer_k,
                model=model,
                pearson_correlation=_format_float(_pearson(expected, observed)),
                spearman_correlation=_format_float(_spearman(expected, observed)),
                mean_absolute_error=_format_float(mae),
                note="hypothesis diagnostic; does not exclude other mechanisms",
            )
        )
    return rows


def read_k2_gap_width_bias_csv(
    path: str | Path = DEFAULT_K2_GAP_WIDTH_BIAS_CSV,
) -> list[K2GapWidthBiasRow]:
    return _read_dataclass_csv(path, K2GapWidthBiasRow)


def read_lineage_measure_bias_csv(
    path: str | Path = DEFAULT_LINEAGE_MEASURE_BIAS_CSV,
) -> list[LineageMeasureBiasRow]:
    return _read_dataclass_csv(path, LineageMeasureBiasRow)


def read_final_aperture_margin_csv(
    path: str | Path = DEFAULT_FINAL_APERTURE_MARGINS_CSV,
) -> list[FinalApertureMarginRow]:
    return _read_dataclass_csv(path, FinalApertureMarginRow)


def read_q_grid_birth_phase_csv(
    path: str | Path = DEFAULT_Q_GRID_BIRTH_PHASE_CSV,
) -> list[QGridBirthPhaseRow]:
    return _read_dataclass_csv(path, QGridBirthPhaseRow)


def read_incremental_grid_phase_csv(
    path: str | Path = DEFAULT_INCREMENTAL_GRID_PHASE_CSV,
) -> list[IncrementalGridPhaseRow]:
    return _read_dataclass_csv(path, IncrementalGridPhaseRow)


def read_birth_potential_score_csv(
    path: str | Path = DEFAULT_BIRTH_POTENTIAL_SCORE_CSV,
) -> list[BirthPotentialScoreRow]:
    return _read_dataclass_csv(path, BirthPotentialScoreRow)


def read_birth_potential_correlation_csv(
    path: str | Path = DEFAULT_BIRTH_POTENTIAL_CORRELATION_CSV,
) -> list[BirthPotentialCorrelationRow]:
    return _read_dataclass_csv(path, BirthPotentialCorrelationRow)


def write_angle_aperture_diagnostic_csvs(
    *,
    k2_path: str | Path = DEFAULT_K2_GAP_WIDTH_BIAS_CSV,
    measure_path: str | Path = DEFAULT_LINEAGE_MEASURE_BIAS_CSV,
    aperture_path: str | Path = DEFAULT_FINAL_APERTURE_MARGINS_CSV,
    q_grid_path: str | Path = DEFAULT_Q_GRID_BIRTH_PHASE_CSV,
    incremental_grid_path: str | Path = DEFAULT_INCREMENTAL_GRID_PHASE_CSV,
    potential_path: str | Path = DEFAULT_BIRTH_POTENTIAL_SCORE_CSV,
    potential_correlation_path: str | Path = DEFAULT_BIRTH_POTENTIAL_CORRELATION_CSV,
) -> None:
    potential_rows = build_birth_potential_score_rows()
    write_dataclass_csv(build_k2_gap_width_bias_rows(), k2_path, K2GapWidthBiasRow)
    write_dataclass_csv(
        build_lineage_measure_bias_rows(),
        measure_path,
        LineageMeasureBiasRow,
    )
    write_dataclass_csv(
        build_final_aperture_margin_rows(),
        aperture_path,
        FinalApertureMarginRow,
    )
    write_dataclass_csv(
        build_q_grid_birth_phase_rows(),
        q_grid_path,
        QGridBirthPhaseRow,
    )
    write_dataclass_csv(
        build_incremental_grid_phase_rows(),
        incremental_grid_path,
        IncrementalGridPhaseRow,
    )
    write_dataclass_csv(
        potential_rows,
        potential_path,
        BirthPotentialScoreRow,
    )
    write_dataclass_csv(
        build_birth_potential_correlation_rows(potential_rows),
        potential_correlation_path,
        BirthPotentialCorrelationRow,
    )


def row_signature(row: object) -> tuple[object, ...]:
    return tuple(getattr(row, field) for field in row.__dataclass_fields__)


def write_dataclass_csv(rows: Iterable[object], output_path: str | Path, row_type: type) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(row_type.__dataclass_fields__.keys())
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def _lineage_measure_row(
    *,
    layer_k: int,
    population: str,
    gap_measure_pairs: list[tuple[list[tuple[Fraction, Fraction]], Fraction]],
) -> LineageMeasureBiasRow:
    row_count = len(gap_measure_pairs)
    total_measure = sum(measure for _, measure in gap_measure_pairs)
    zero_blank_count = sum(
        _point_in_any_gap(Fraction(0), gaps) for gaps, _ in gap_measure_pairs
    )
    target_measure = sum(
        _sector_overlap_measure(gaps, TARGET_SECTORS)
        for gaps, _ in gap_measure_pairs
    )
    average_measure = total_measure / row_count
    average_target_measure = target_measure / row_count
    return LineageMeasureBiasRow(
        layer_k=layer_k,
        population=population,
        row_count=row_count,
        average_residual_measure=format_fraction(average_measure),
        zero_point_blank_count=zero_blank_count,
        zero_point_blank_fraction=format_fraction(Fraction(zero_blank_count, row_count)),
        target_sector_residual_measure_average=format_fraction(average_target_measure),
        target_sector_share_of_residual=format_fraction(
            _safe_ratio(average_target_measure, average_measure)
        ),
    )


def _read_dataclass_csv(path: str | Path, row_type: type):
    bool_fields = {
        "zero_point_in_residual",
    }
    int_fields = {
        "residue_mod_6",
        "residue",
        "birth_lineage_count",
        "layer_k",
        "row_count",
        "zero_point_blank_count",
        "birth_k",
        "birth_residue",
        "parent_residue",
        "new_prime",
        "new_prime_remainder",
        "prefinal_gap_count",
        "new_prime",
        "new_prime_remainder",
        "birth_count",
        "observed_birth_lineage_count",
        "reflected_remainder",
        "reflected_birth_count",
        "reflected_row_count",
        "reflection_pair_count",
        "layer_k",
        "row_count",
    }
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for raw_row in csv.DictReader(handle):
            values = dict(raw_row)
            for field in bool_fields:
                if field in values:
                    values[field] = values[field] == "True"
            for field in int_fields:
                if field in values:
                    values[field] = int(values[field])
            rows.append(row_type(**values))
    return rows


def _sector_overlap_measure(
    gaps: Iterable[tuple[Fraction, Fraction]],
    sectors: Iterable[tuple[Fraction, Fraction]],
) -> Fraction:
    total = Fraction(0)
    gap_pieces = [piece for gap in gaps for piece in _split_interval(gap)]
    sector_pieces = [piece for sector in sectors for piece in _split_interval(sector)]
    for gap_start, gap_end in gap_pieces:
        for sector_start, sector_end in sector_pieces:
            start = max(gap_start, sector_start)
            end = min(gap_end, sector_end)
            if end > start:
                total += end - start
    return total


def _point_in_any_gap(
    point: Fraction,
    gaps: Iterable[tuple[Fraction, Fraction]],
) -> bool:
    return any(_point_in_interval(point, gap) for gap in gaps)


def _point_in_interval(point: Fraction, interval: tuple[Fraction, Fraction]) -> bool:
    start, end = interval
    if start <= end:
        return start <= point <= end
    return point >= start or point <= end


def _split_interval(
    interval: tuple[Fraction, Fraction],
) -> list[tuple[Fraction, Fraction]]:
    start, end = interval
    if end >= start:
        return [(start, end)]
    return [(start, Fraction(1)), (Fraction(0), end)]


def _safe_ratio(numerator: Fraction, denominator: Fraction) -> Fraction:
    if denominator == 0:
        return Fraction(0)
    return numerator / denominator


def _pearson(left: list[float], right: list[float]) -> float:
    mean_left = sum(left) / len(left)
    mean_right = sum(right) / len(right)
    numerator = sum(
        (left_value - mean_left) * (right_value - mean_right)
        for left_value, right_value in zip(left, right)
    )
    left_norm = sum((value - mean_left) ** 2 for value in left) ** 0.5
    right_norm = sum((value - mean_right) ** 2 for value in right) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def _spearman(left: list[float], right: list[float]) -> float:
    return _pearson(_ranks(left), _ranks(right))


def _ranks(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(indexed):
        end = index + 1
        while end < len(indexed) and indexed[end][1] == indexed[index][1]:
            end += 1
        rank = (index + 1 + end) / 2
        for original_index, _ in indexed[index:end]:
            ranks[original_index] = rank
        index = end
    return ranks


def _format_float(value: float) -> str:
    return f"{value:.6f}"
