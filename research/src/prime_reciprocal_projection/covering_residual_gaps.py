"""Residual gap diagnostics after a fixed PRC branch prefix."""

from __future__ import annotations

import csv
import math
import random
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


@dataclass(frozen=True)
class ResidualGapCountTestRow:
    """v0.7 paired test summary for residual gap count."""

    control_role: str
    metric: str
    pair_count: int
    non_tie_pair_count: int
    complete_smaller_count: int
    complete_larger_count: int
    tie_count: int
    complete_smaller_rate_all_pairs: float
    complete_smaller_rate_non_tie: float
    median_delta: float
    mean_delta: float
    sign_test_p_two_sided: float
    bh_q_value: float
    bootstrap_median_delta_ci_low: float
    bootstrap_median_delta_ci_high: float
    bootstrap_iterations: int
    bootstrap_seed: int


@dataclass(frozen=True)
class ResidualGapSecondaryDirectionRow:
    """Direction-only summary for secondary residual gap metrics."""

    control_role: str
    metric: str
    pair_count: int
    complete_smaller_count: int
    complete_larger_count: int
    tie_count: int
    median_delta: float
    complete_smaller_rate_all_pairs: float


@dataclass(frozen=True)
class SeedClusterAuditRow:
    """Seed-level cluster assignment for v0.8 audits."""

    seed_n: int
    bin_index: int
    cluster_id: str
    cluster_start_n: int
    cluster_stop_n: int
    cluster_size: int
    cluster_radius: int
    nearest_seed_distance: int | None
    local_mod6_delta: float | None
    band_mod6_delta: float | None
    band_ordinary_delta: float | None


@dataclass(frozen=True)
class ClusterLevelGapCountDirectionRow:
    """Cluster-level sign direction for one control role and metric."""

    control_role: str
    metric: str
    cluster_count: int
    cluster_non_tie_count: int
    complete_smaller_cluster_count: int
    complete_larger_cluster_count: int
    tie_cluster_count: int
    complete_smaller_cluster_rate: float
    median_cluster_delta: float
    sign_test_p_two_sided: float


@dataclass(frozen=True)
class ControlReuseDetailRow:
    """Control reuse detail for v0.8 audits."""

    control_role: str
    control_n: int
    reuse_count: int
    reused: bool
    seed_ns: str
    cluster_ids: str


PAIRED_DELTA_METRICS = (
    "residual_top_gap_share",
    "residual_gap_max",
    "residual_gap_p90",
    "residual_gap_entropy",
    "residual_gap_count",
    "residual_uncovered_measure",
)
PRIMARY_COUNT_METRIC = "residual_gap_count"
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


def residual_gap_count_test_rows(
    rows: list[ResidualGapPairDeltaRow],
    *,
    bootstrap_iterations: int = 10000,
    bootstrap_seed: int = 1729,
) -> list[ResidualGapCountTestRow]:
    """Return v0.7 exact sign-test and bootstrap summaries for gap count."""
    if bootstrap_iterations < 1:
        raise ValueError("bootstrap_iterations must be >= 1")

    pending: list[dict[str, float | int | str]] = []
    p_values: list[float] = []
    for role in CONTROL_ROLES:
        values = [
            row.delta_complete_minus_control
            for row in rows
            if row.control_role == role and row.metric == PRIMARY_COUNT_METRIC
        ]
        if not values:
            continue
        smaller = sum(1 for value in values if value < 0)
        larger = sum(1 for value in values if value > 0)
        ties = len(values) - smaller - larger
        non_tie = smaller + larger
        p_value = exact_two_sided_sign_test_p(smaller, non_tie)
        ci_low, ci_high = bootstrap_median_delta_ci(
            values,
            iterations=bootstrap_iterations,
            seed=bootstrap_seed + CONTROL_ROLES.index(role),
        )
        p_values.append(p_value)
        pending.append(
            {
                "control_role": role,
                "metric": PRIMARY_COUNT_METRIC,
                "pair_count": len(values),
                "non_tie_pair_count": non_tie,
                "complete_smaller_count": smaller,
                "complete_larger_count": larger,
                "tie_count": ties,
                "complete_smaller_rate_all_pairs": smaller / len(values),
                "complete_smaller_rate_non_tie": smaller / non_tie if non_tie else 0.0,
                "median_delta": median(values),
                "mean_delta": sum(values) / len(values),
                "sign_test_p_two_sided": p_value,
                "bootstrap_median_delta_ci_low": ci_low,
                "bootstrap_median_delta_ci_high": ci_high,
                "bootstrap_iterations": bootstrap_iterations,
                "bootstrap_seed": bootstrap_seed,
            }
        )

    q_values = benjamini_hochberg_q_values(p_values)
    return [
        ResidualGapCountTestRow(
            control_role=str(row["control_role"]),
            metric=str(row["metric"]),
            pair_count=int(row["pair_count"]),
            non_tie_pair_count=int(row["non_tie_pair_count"]),
            complete_smaller_count=int(row["complete_smaller_count"]),
            complete_larger_count=int(row["complete_larger_count"]),
            tie_count=int(row["tie_count"]),
            complete_smaller_rate_all_pairs=float(row["complete_smaller_rate_all_pairs"]),
            complete_smaller_rate_non_tie=float(row["complete_smaller_rate_non_tie"]),
            median_delta=float(row["median_delta"]),
            mean_delta=float(row["mean_delta"]),
            sign_test_p_two_sided=float(row["sign_test_p_two_sided"]),
            bh_q_value=q_value,
            bootstrap_median_delta_ci_low=float(row["bootstrap_median_delta_ci_low"]),
            bootstrap_median_delta_ci_high=float(row["bootstrap_median_delta_ci_high"]),
            bootstrap_iterations=int(row["bootstrap_iterations"]),
            bootstrap_seed=int(row["bootstrap_seed"]),
        )
        for row, q_value in zip(pending, q_values)
    ]


def residual_gap_secondary_direction_rows(
    rows: list[ResidualGapPairDeltaRow],
) -> list[ResidualGapSecondaryDirectionRow]:
    """Return direction-only summaries for every v0.6 residual metric."""
    summaries: list[ResidualGapSecondaryDirectionRow] = []
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
                ResidualGapSecondaryDirectionRow(
                    control_role=control_role,
                    metric=metric,
                    pair_count=len(values),
                    complete_smaller_count=smaller,
                    complete_larger_count=larger,
                    tie_count=ties,
                    median_delta=median(values),
                    complete_smaller_rate_all_pairs=smaller / len(values),
                )
            )
    return summaries


def seed_cluster_audit_rows(
    manifest_rows: list[CohortManifestRow],
    delta_rows: list[ResidualGapPairDeltaRow],
    *,
    metric: str = PRIMARY_COUNT_METRIC,
    cluster_radius: int = 250,
) -> list[SeedClusterAuditRow]:
    """Assign eligible complete seeds to connected clusters within each bin."""
    if cluster_radius < 0:
        raise ValueError("cluster_radius must be >= 0")
    seed_bins = {
        row.seed_n: row.bin_index
        for row in manifest_rows
        if row.cohort_role == "complete" and row.eligible and row.n is not None
    }
    seeds = sorted({row.seed_n for row in delta_rows if row.metric == metric and row.seed_n in seed_bins})
    deltas_by_seed_role = {
        (row.seed_n, row.control_role): row.delta_complete_minus_control
        for row in delta_rows
        if row.metric == metric
    }
    clusters = _seed_clusters(seeds, seed_bins, cluster_radius=cluster_radius)
    rows: list[SeedClusterAuditRow] = []
    for cluster_id, cluster in clusters:
        cluster_start = min(cluster)
        cluster_stop = max(cluster)
        for seed in cluster:
            distances = [abs(seed - other) for other in cluster if other != seed]
            rows.append(
                SeedClusterAuditRow(
                    seed_n=seed,
                    bin_index=seed_bins[seed],
                    cluster_id=cluster_id,
                    cluster_start_n=cluster_start,
                    cluster_stop_n=cluster_stop,
                    cluster_size=len(cluster),
                    cluster_radius=cluster_radius,
                    nearest_seed_distance=min(distances) if distances else None,
                    local_mod6_delta=deltas_by_seed_role.get((seed, "local_mod6_control")),
                    band_mod6_delta=deltas_by_seed_role.get((seed, "band_mod6_control")),
                    band_ordinary_delta=deltas_by_seed_role.get((seed, "band_ordinary_control")),
                )
            )
    return sorted(rows, key=lambda row: (row.bin_index, row.cluster_start_n, row.seed_n))


def cluster_level_gap_count_direction_rows(
    cluster_rows: list[SeedClusterAuditRow],
    *,
    metric: str = PRIMARY_COUNT_METRIC,
) -> list[ClusterLevelGapCountDirectionRow]:
    """Summarize median cluster deltas by control role."""
    summaries: list[ClusterLevelGapCountDirectionRow] = []
    for control_role, field_name in (
        ("local_mod6_control", "local_mod6_delta"),
        ("band_mod6_control", "band_mod6_delta"),
        ("band_ordinary_control", "band_ordinary_delta"),
    ):
        values_by_cluster: dict[str, list[float]] = {}
        for row in cluster_rows:
            value = getattr(row, field_name)
            if value is None:
                continue
            values_by_cluster.setdefault(row.cluster_id, []).append(float(value))
        cluster_deltas = [median(values) for _, values in sorted(values_by_cluster.items()) if values]
        if not cluster_deltas:
            continue
        smaller = sum(1 for value in cluster_deltas if value < 0)
        larger = sum(1 for value in cluster_deltas if value > 0)
        ties = len(cluster_deltas) - smaller - larger
        non_tie = smaller + larger
        summaries.append(
            ClusterLevelGapCountDirectionRow(
                control_role=control_role,
                metric=metric,
                cluster_count=len(cluster_deltas),
                cluster_non_tie_count=non_tie,
                complete_smaller_cluster_count=smaller,
                complete_larger_cluster_count=larger,
                tie_cluster_count=ties,
                complete_smaller_cluster_rate=smaller / non_tie if non_tie else 0.0,
                median_cluster_delta=median(cluster_deltas),
                sign_test_p_two_sided=exact_two_sided_sign_test_p(smaller, non_tie),
            )
        )
    return summaries


def control_reuse_detail_rows(
    delta_rows: list[ResidualGapPairDeltaRow],
    cluster_rows: list[SeedClusterAuditRow],
    *,
    metric: str = PRIMARY_COUNT_METRIC,
) -> list[ControlReuseDetailRow]:
    """Return per-control reuse details with seed and cluster membership."""
    cluster_by_seed = {row.seed_n: row.cluster_id for row in cluster_rows}
    rows: list[ControlReuseDetailRow] = []
    for role in CONTROL_ROLES:
        seeds_by_control: dict[int, list[int]] = {}
        for row in delta_rows:
            if row.metric == metric and row.control_role == role and row.seed_n in cluster_by_seed:
                seeds_by_control.setdefault(row.control_n, []).append(row.seed_n)
        for control_n, seed_ns in sorted(seeds_by_control.items()):
            ordered_seeds = sorted(seed_ns)
            cluster_ids = sorted({cluster_by_seed[seed] for seed in ordered_seeds})
            rows.append(
                ControlReuseDetailRow(
                    control_role=role,
                    control_n=control_n,
                    reuse_count=len(ordered_seeds),
                    reused=len(ordered_seeds) > 1,
                    seed_ns=";".join(str(seed) for seed in ordered_seeds),
                    cluster_ids=";".join(cluster_ids),
                )
            )
    return rows


def write_seed_cluster_audit_csv(rows: list[SeedClusterAuditRow], output_path: str | Path) -> None:
    """Write seed cluster audit rows as CSV."""
    _write_dataclass_csv(rows, output_path, list(SeedClusterAuditRow.__dataclass_fields__))


def write_cluster_level_gap_count_direction_csv(
    rows: list[ClusterLevelGapCountDirectionRow],
    output_path: str | Path,
) -> None:
    """Write cluster-level direction rows as CSV."""
    _write_dataclass_csv(
        rows,
        output_path,
        list(ClusterLevelGapCountDirectionRow.__dataclass_fields__),
    )


def write_control_reuse_detail_csv(
    rows: list[ControlReuseDetailRow],
    output_path: str | Path,
) -> None:
    """Write control reuse detail rows as CSV."""
    _write_dataclass_csv(rows, output_path, list(ControlReuseDetailRow.__dataclass_fields__))


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


def read_residual_gap_pair_delta_csv(path: str | Path) -> list[ResidualGapPairDeltaRow]:
    """Read paired residual gap delta rows from CSV."""
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return [_residual_gap_pair_delta_row_from_csv(row) for row in csv.DictReader(handle)]


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


def write_residual_gap_count_test_csv(
    rows: list[ResidualGapCountTestRow],
    output_path: str | Path,
) -> None:
    """Write v0.7 residual gap count test rows as CSV."""
    _write_dataclass_csv(rows, output_path, list(ResidualGapCountTestRow.__dataclass_fields__))


def write_residual_gap_secondary_direction_csv(
    rows: list[ResidualGapSecondaryDirectionRow],
    output_path: str | Path,
) -> None:
    """Write secondary direction summaries as CSV."""
    _write_dataclass_csv(
        rows,
        output_path,
        list(ResidualGapSecondaryDirectionRow.__dataclass_fields__),
    )


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


def exact_two_sided_sign_test_p(success_count: int, trial_count: int) -> float:
    """Return the exact two-sided sign-test p-value under p=0.5."""
    if trial_count < 0:
        raise ValueError("trial_count must be non-negative")
    if not 0 <= success_count <= trial_count:
        raise ValueError("success_count must satisfy 0 <= success_count <= trial_count")
    if trial_count == 0:
        return 1.0
    lower_tail = sum(math.comb(trial_count, k) for k in range(0, success_count + 1))
    upper_tail = sum(math.comb(trial_count, k) for k in range(success_count, trial_count + 1))
    return min(1.0, 2.0 * min(lower_tail, upper_tail) / (2**trial_count))


def benjamini_hochberg_q_values(p_values: list[float]) -> list[float]:
    """Return Benjamini-Hochberg adjusted q-values in original order."""
    count = len(p_values)
    if count == 0:
        return []
    indexed = sorted(enumerate(p_values), key=lambda item: item[1])
    adjusted = [1.0] * count
    running = 1.0
    for rank_from_end, (index, p_value) in enumerate(reversed(indexed), start=1):
        rank = count - rank_from_end + 1
        running = min(running, p_value * count / rank)
        adjusted[index] = min(1.0, running)
    return adjusted


def bootstrap_median_delta_ci(
    values: list[float],
    *,
    iterations: int = 10000,
    seed: int = 1729,
) -> tuple[float, float]:
    """Return a deterministic percentile 95% CI for the median paired delta."""
    if not values:
        raise ValueError("values must not be empty")
    if iterations < 1:
        raise ValueError("iterations must be >= 1")
    rng = random.Random(seed)
    sample_size = len(values)
    bootstrapped = [
        median([values[rng.randrange(sample_size)] for _ in range(sample_size)])
        for _ in range(iterations)
    ]
    bootstrapped.sort()
    low_index = max(0, math.ceil(0.025 * iterations) - 1)
    high_index = min(iterations - 1, math.ceil(0.975 * iterations) - 1)
    return bootstrapped[low_index], bootstrapped[high_index]


def _seed_clusters(
    seeds: list[int],
    seed_bins: dict[int, int],
    *,
    cluster_radius: int,
) -> list[tuple[str, list[int]]]:
    clusters: list[tuple[str, list[int]]] = []
    cluster_index_by_bin: dict[int, int] = {}
    for bin_index in sorted({seed_bins[seed] for seed in seeds}):
        bin_seeds = sorted(seed for seed in seeds if seed_bins[seed] == bin_index)
        active: list[int] = []
        for seed in bin_seeds:
            if not active or seed - active[-1] <= cluster_radius:
                active.append(seed)
            else:
                cluster_number = cluster_index_by_bin.get(bin_index, 0) + 1
                cluster_index_by_bin[bin_index] = cluster_number
                clusters.append((f"bin{bin_index}_cluster{cluster_number}", active))
                active = [seed]
        if active:
            cluster_number = cluster_index_by_bin.get(bin_index, 0) + 1
            cluster_index_by_bin[bin_index] = cluster_number
            clusters.append((f"bin{bin_index}_cluster{cluster_number}", active))
    return clusters


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


def _residual_gap_pair_delta_row_from_csv(row: dict[str, str]) -> ResidualGapPairDeltaRow:
    return ResidualGapPairDeltaRow(
        seed_n=int(row["seed_n"]),
        control_role=row["control_role"],
        metric=row["metric"],
        complete_n=int(row["complete_n"]),
        control_n=int(row["control_n"]),
        complete_value=float(row["complete_value"]),
        control_value=float(row["control_value"]),
        delta_complete_minus_control=float(row["delta_complete_minus_control"]),
    )


def _write_dataclass_csv(rows: list[object], output_path: str | Path, fieldnames: list[str]) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})
