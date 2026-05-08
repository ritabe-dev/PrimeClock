"""Residual gap diagnostics after a fixed PRC branch prefix."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass, replace
from pathlib import Path

from .covering import exact_is_completely_covered, uncovered_intervals, uncovered_measure
from .covering_branch_fill import _interval_length
from .covering_branch_fill_cohorts import CohortManifestRow, read_cohort_manifest_csv
from .primes import primes_up_to


@dataclass(frozen=True)
class ResidualGapRow:
    """Gap-structure metrics after branches ``1..max_branch``."""

    seed_n: int
    cohort_role: str
    n: int
    bin_index: int
    max_branch: int
    max_possible_branch: int
    prefix_exhausts_all_branches: bool
    seed_analysis_eligible: bool
    full_uncovered_measure: float
    exact_complete: bool
    residual_uncovered_measure: float
    residual_gap_count: int
    residual_gap_max: float
    residual_gap_p50: float
    residual_gap_p90: float
    residual_gap_p99: float
    residual_gap_entropy: float
    residual_top_gap_share: float
    residual_gap_near_zero_count: int


@dataclass(frozen=True)
class ResidualGapPairDeltaRow:
    """Paired complete-minus-control residual gap delta."""

    seed_n: int
    control_role: str
    metric: str
    complete_n: int
    control_n: int
    complete_value: float
    control_value: float
    delta_complete_minus_control: float


@dataclass(frozen=True)
class ResidualGapEffectSummaryRow:
    """Summary of paired residual gap deltas for one control role and metric."""

    control_role: str
    metric: str
    eligible_pair_count: int
    median_delta: float
    complete_smaller_count: int
    complete_larger_count: int
    tie_count: int
    complete_smaller_rate: float


PAIRED_DELTA_METRICS = (
    "residual_top_gap_share",
    "residual_gap_max",
    "residual_gap_p90",
    "residual_gap_entropy",
    "residual_gap_count",
    "residual_uncovered_measure",
)
CONTROL_ROLES = (
    "local_mod6_control",
    "band_mod6_control",
    "band_ordinary_control",
)


def residual_gap_rows_from_manifest_csv(
    manifest_csv: str | Path,
    *,
    summary_csv: str | Path | None = None,
    max_branch: int = 1000,
    near_zero_threshold: float = 1e-6,
) -> list[ResidualGapRow]:
    """Compute residual gap rows from a v0.4 cohort manifest CSV."""
    return residual_gap_rows(
        read_cohort_manifest_csv(manifest_csv),
        summary_rows=read_summary_lookup(summary_csv) if summary_csv else None,
        max_branch=max_branch,
        near_zero_threshold=near_zero_threshold,
    )


def residual_gap_rows(
    manifest_rows: list[CohortManifestRow],
    *,
    summary_rows: dict[tuple[int, str, int], tuple[float, bool]] | None = None,
    max_branch: int = 1000,
    near_zero_threshold: float = 1e-6,
) -> list[ResidualGapRow]:
    """Compute residual gap rows for eligible cohort members."""
    if max_branch < 1:
        raise ValueError("max_branch must be >= 1")
    if near_zero_threshold < 0:
        raise ValueError("near_zero_threshold must be >= 0")

    eligible_rows = [row for row in manifest_rows if row.eligible and row.n is not None]
    if not eligible_rows:
        return []
    prime_pool = primes_up_to(max(row.n for row in eligible_rows if row.n is not None))
    rows: list[ResidualGapRow] = []
    for row in eligible_rows:
        assert row.n is not None
        max_possible_branch = row.n // 2
        prefix_exhausts = max_branch >= max_possible_branch
        prefix_primes = [p for p in prime_pool if p <= row.n and row.n // p <= max_branch]
        gaps = uncovered_intervals(row.n, primes=prefix_primes)
        lengths = sorted(_interval_length(gap) for gap in gaps)
        residual_measure = sum(lengths)
        summary = summary_rows.get((row.seed_n, row.cohort_role, row.n)) if summary_rows else None
        full_measure, exact_complete = (
            summary if summary is not None else (uncovered_measure(row.n), exact_is_completely_covered(row.n))
        )
        rows.append(
            ResidualGapRow(
                seed_n=row.seed_n,
                cohort_role=row.cohort_role,
                n=row.n,
                bin_index=row.bin_index,
                max_branch=max_branch,
                max_possible_branch=max_possible_branch,
                prefix_exhausts_all_branches=prefix_exhausts,
                seed_analysis_eligible=True,
                full_uncovered_measure=full_measure,
                exact_complete=exact_complete,
                residual_uncovered_measure=residual_measure,
                residual_gap_count=len(lengths),
                residual_gap_max=max(lengths, default=0.0),
                residual_gap_p50=gap_quantile(lengths, 0.50),
                residual_gap_p90=gap_quantile(lengths, 0.90),
                residual_gap_p99=gap_quantile(lengths, 0.99),
                residual_gap_entropy=normalized_gap_entropy(lengths),
                residual_top_gap_share=top_gap_share(lengths),
                residual_gap_near_zero_count=sum(1 for length in lengths if length <= near_zero_threshold),
            )
        )
    return mark_seed_analysis_eligibility(rows)


def mark_seed_analysis_eligibility(rows: list[ResidualGapRow]) -> list[ResidualGapRow]:
    """Mark every row in a seed as ineligible if any role exhausts all branches."""
    exhausted_seeds = {row.seed_n for row in rows if row.prefix_exhausts_all_branches}
    return [
        replace(row, seed_analysis_eligible=row.seed_n not in exhausted_seeds)
        for row in rows
    ]


def residual_gap_pair_delta_rows(rows: list[ResidualGapRow]) -> list[ResidualGapPairDeltaRow]:
    """Return complete-minus-control residual gap deltas for eligible seeds."""
    grouped: dict[int, dict[str, ResidualGapRow]] = {}
    for row in rows:
        if not row.seed_analysis_eligible:
            continue
        grouped.setdefault(row.seed_n, {})[row.cohort_role] = row

    deltas: list[ResidualGapPairDeltaRow] = []
    for seed_n in sorted(grouped):
        role_rows = grouped[seed_n]
        complete = role_rows.get("complete")
        if complete is None:
            continue
        for control_role in CONTROL_ROLES:
            control = role_rows.get(control_role)
            if control is None:
                continue
            for metric in PAIRED_DELTA_METRICS:
                complete_value = float(getattr(complete, metric))
                control_value = float(getattr(control, metric))
                deltas.append(
                    ResidualGapPairDeltaRow(
                        seed_n=seed_n,
                        control_role=control_role,
                        metric=metric,
                        complete_n=complete.n,
                        control_n=control.n,
                        complete_value=complete_value,
                        control_value=control_value,
                        delta_complete_minus_control=complete_value - control_value,
                    )
                )
    return deltas


def residual_gap_effect_summary_rows(
    rows: list[ResidualGapPairDeltaRow],
) -> list[ResidualGapEffectSummaryRow]:
    """Summarize paired delta direction by control role and metric."""
    summaries: list[ResidualGapEffectSummaryRow] = []
    for control_role in CONTROL_ROLES:
        for metric in PAIRED_DELTA_METRICS:
            values = [
                row.delta_complete_minus_control
                for row in rows
                if row.control_role == control_role and row.metric == metric
            ]
            if not values:
                continue
            smaller = sum(1 for value in values if value < 0)
            larger = sum(1 for value in values if value > 0)
            ties = len(values) - smaller - larger
            summaries.append(
                ResidualGapEffectSummaryRow(
                    control_role=control_role,
                    metric=metric,
                    eligible_pair_count=len(values),
                    median_delta=median(values),
                    complete_smaller_count=smaller,
                    complete_larger_count=larger,
                    tie_count=ties,
                    complete_smaller_rate=smaller / len(values),
                )
            )
    return summaries


def read_summary_lookup(path: str | Path) -> dict[tuple[int, str, int], tuple[float, bool]]:
    """Read v0.4 cohort summary rows as a lookup by seed, role, and N."""
    lookup: dict[tuple[int, str, int], tuple[float, bool]] = {}
    with Path(path).open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (int(row["seed_n"]), row["cohort_role"], int(row["n"]))
            lookup[key] = (float(row["full_uncovered_measure"]), row["exact_complete"] == "True")
    return lookup


def write_residual_gap_csv(rows: list[ResidualGapRow], output_path: str | Path) -> None:
    """Write residual gap rows as CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(ResidualGapRow.__dataclass_fields__)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def read_residual_gap_csv(path: str | Path) -> list[ResidualGapRow]:
    """Read residual gap rows from CSV."""
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return [_residual_gap_row_from_csv(row) for row in csv.DictReader(handle)]


def write_residual_gap_pair_delta_csv(
    rows: list[ResidualGapPairDeltaRow],
    output_path: str | Path,
) -> None:
    """Write paired residual gap deltas as CSV."""
    _write_dataclass_csv(rows, output_path, list(ResidualGapPairDeltaRow.__dataclass_fields__))


def write_residual_gap_effect_summary_csv(
    rows: list[ResidualGapEffectSummaryRow],
    output_path: str | Path,
) -> None:
    """Write residual gap effect summaries as CSV."""
    _write_dataclass_csv(rows, output_path, list(ResidualGapEffectSummaryRow.__dataclass_fields__))


def gap_quantile(lengths: list[float], q: float) -> float:
    """Return a deterministic nearest-rank quantile from sorted gap lengths."""
    if not 0 <= q <= 1:
        raise ValueError("q must be in [0, 1]")
    if not lengths:
        return 0.0
    index = min(len(lengths) - 1, max(0, math.ceil(q * len(lengths)) - 1))
    return sorted(lengths)[index]


def normalized_gap_entropy(lengths: list[float]) -> float:
    """Return normalized Shannon entropy of positive gap lengths."""
    positive = [length for length in lengths if length > 0]
    total = sum(positive)
    if len(positive) <= 1 or total <= 0:
        return 0.0
    entropy = -sum((length / total) * math.log(length / total) for length in positive)
    return entropy / math.log(len(positive))


def top_gap_share(lengths: list[float]) -> float:
    """Return the largest gap's share of total residual uncovered measure."""
    total = sum(lengths)
    if total <= 0:
        return 0.0
    return max(lengths, default=0.0) / total


def median(values: list[float]) -> float:
    """Return the median of a non-empty list."""
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2


def _residual_gap_row_from_csv(row: dict[str, str]) -> ResidualGapRow:
    return ResidualGapRow(
        seed_n=int(row["seed_n"]),
        cohort_role=row["cohort_role"],
        n=int(row["n"]),
        bin_index=int(row["bin_index"]),
        max_branch=int(row["max_branch"]),
        max_possible_branch=int(row["max_possible_branch"]),
        prefix_exhausts_all_branches=row["prefix_exhausts_all_branches"] == "True",
        seed_analysis_eligible=row["seed_analysis_eligible"] == "True",
        full_uncovered_measure=float(row["full_uncovered_measure"]),
        exact_complete=row["exact_complete"] == "True",
        residual_uncovered_measure=float(row["residual_uncovered_measure"]),
        residual_gap_count=int(row["residual_gap_count"]),
        residual_gap_max=float(row["residual_gap_max"]),
        residual_gap_p50=float(row["residual_gap_p50"]),
        residual_gap_p90=float(row["residual_gap_p90"]),
        residual_gap_p99=float(row["residual_gap_p99"]),
        residual_gap_entropy=float(row["residual_gap_entropy"]),
        residual_top_gap_share=float(row["residual_top_gap_share"]),
        residual_gap_near_zero_count=int(row["residual_gap_near_zero_count"]),
    )


def _write_dataclass_csv(rows: list[object], output_path: str | Path, fieldnames: list[str]) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})
