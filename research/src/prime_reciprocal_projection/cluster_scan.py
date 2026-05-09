"""Two-stage PRC complete-covering cluster scan."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .covering import exact_is_completely_covered, uncovered_measure
from .covering_metrics import random_arc_baseline
from .primes import primes_up_to
from .projection import validate_n


@dataclass(frozen=True)
class ClusterSeedRow:
    """One coarse float-scan seed."""

    n: int
    uncovered_measure: float
    baseline_ratio: float


@dataclass(frozen=True)
class ClusterScanRow:
    """One local cluster summary row."""

    center: int
    seed_uncovered_measure: float | None
    seed_baseline_ratio: float | None
    radius: int
    window_start: int
    window_stop: int
    window_size: int
    float_zero_count: int
    exact_complete_count: int
    float_positive_exact_count: int
    d_r: float
    min_uncovered_measure: float
    median_uncovered_measure: float
    median_baseline_ratio: float
    max_uncovered_measure: float
    certified_values: str


@dataclass(frozen=True)
class ClusterSensitivityRow:
    """One sensitivity summary across seed threshold and window radius."""

    ratio_threshold: float
    radius: int
    seed_count: int
    exact_complete_memberships: int
    unique_exact_complete_count: int
    d_r_min: float
    d_r_median: float
    d_r_mean: float
    d_r_max: float
    top_center: int | None
    top_exact_count: int | None
    top_d_r: float | None


def discover_seed_values(
    *,
    start: int,
    stop: int,
    count: int,
    ratio_threshold: float = 0.05,
) -> list[int]:
    """Find broad candidate seed values from a log-spaced float scan."""
    return [
        row.n
        for row in discover_seed_rows(
            start=start,
            stop=stop,
            count=count,
            ratio_threshold=ratio_threshold,
        )
    ]


def discover_seed_rows(
    *,
    start: int,
    stop: int,
    count: int,
    ratio_threshold: float = 0.05,
) -> list[ClusterSeedRow]:
    """Find broad candidate seed rows from a log-spaced float scan."""
    ns = _log_grid(start, stop, count)
    prime_pool = primes_up_to(stop)
    seeds: list[ClusterSeedRow] = []
    for n in ns:
        measure = uncovered_measure(n, primes=prime_pool)
        baseline = random_arc_baseline(n, primes=prime_pool)
        ratio = measure / baseline if baseline > 0 else math.inf
        if measure == 0.0 or ratio <= ratio_threshold:
            seeds.append(ClusterSeedRow(n=n, uncovered_measure=measure, baseline_ratio=ratio))
    return seeds


def scan_cluster_window(
    center: int,
    *,
    radius: int = 250,
    seed_uncovered_measure: float | None = None,
    seed_baseline_ratio: float | None = None,
    exact_cache: dict[int, bool] | None = None,
) -> ClusterScanRow:
    """Scan one local window and certify exact complete-covering candidates."""
    center = validate_n(center)
    if radius < 0:
        raise ValueError("radius must be >= 0")
    start = max(2, center - radius)
    stop = center + radius
    prime_pool = primes_up_to(stop)

    measures: list[float] = []
    ratios: list[float] = []
    float_zero_candidates: list[int] = []
    exact_values: list[int] = []
    float_zero_values: set[int] = set()
    for n in range(start, stop + 1):
        measure = uncovered_measure(n, primes=prime_pool)
        baseline = random_arc_baseline(n, primes=prime_pool)
        ratio = measure / baseline if baseline > 0 else math.inf
        measures.append(measure)
        ratios.append(ratio)
        if measure == 0.0:
            float_zero_candidates.append(n)
            float_zero_values.add(n)
        if exact_cache is not None and n in exact_cache:
            is_exact_complete = exact_cache[n]
        else:
            is_exact_complete = exact_is_completely_covered(n, primes=prime_pool)
            if exact_cache is not None:
                exact_cache[n] = is_exact_complete
        if is_exact_complete:
            exact_values.append(n)

    window_size = stop - start + 1
    float_positive_exact_count = sum(1 for value in exact_values if value not in float_zero_values)
    return ClusterScanRow(
        center=center,
        seed_uncovered_measure=seed_uncovered_measure,
        seed_baseline_ratio=seed_baseline_ratio,
        radius=radius,
        window_start=start,
        window_stop=stop,
        window_size=window_size,
        float_zero_count=len(float_zero_candidates),
        exact_complete_count=len(exact_values),
        float_positive_exact_count=float_positive_exact_count,
        d_r=len(exact_values) / window_size,
        min_uncovered_measure=min(measures),
        median_uncovered_measure=_median(measures),
        median_baseline_ratio=_median(ratios),
        max_uncovered_measure=max(measures),
        certified_values=" ".join(str(value) for value in exact_values),
    )


def scan_cluster_table(
    centers: Sequence[int | ClusterSeedRow],
    *,
    radius: int = 250,
    exact_cache: dict[int, bool] | None = None,
) -> list[ClusterScanRow]:
    """Scan and certify cluster windows around each center."""
    rows: list[ClusterScanRow] = []
    for center in centers:
        if isinstance(center, ClusterSeedRow):
            rows.append(
                scan_cluster_window(
                    center.n,
                    radius=radius,
                    seed_uncovered_measure=center.uncovered_measure,
                    seed_baseline_ratio=center.baseline_ratio,
                    exact_cache=exact_cache,
                )
            )
        else:
            rows.append(scan_cluster_window(center, radius=radius, exact_cache=exact_cache))
    return rows


def cluster_sensitivity_table(
    *,
    start: int,
    stop: int,
    count: int,
    ratio_thresholds: Sequence[float],
    radii: Sequence[int],
) -> list[ClusterSensitivityRow]:
    """Compute D_R sensitivity summaries for thresholds and radii."""
    if not ratio_thresholds:
        raise ValueError("ratio_thresholds must not be empty")
    if not radii:
        raise ValueError("radii must not be empty")
    for threshold in ratio_thresholds:
        if threshold < 0:
            raise ValueError("ratio thresholds must be >= 0")
    for radius in radii:
        if radius < 0:
            raise ValueError("radii must be >= 0")

    max_threshold = max(ratio_thresholds)
    seeds = discover_seed_rows(
        start=start,
        stop=stop,
        count=count,
        ratio_threshold=max_threshold,
    )

    rows: list[ClusterSensitivityRow] = []
    exact_cache: dict[int, bool] = {}
    for radius in sorted(set(radii)):
        scanned = scan_cluster_table(seeds, radius=radius, exact_cache=exact_cache)
        scanned_by_center = {row.center: row for row in scanned}
        for threshold in sorted(set(ratio_thresholds)):
            eligible_seeds = [
                seed
                for seed in seeds
                if seed.uncovered_measure == 0.0 or seed.baseline_ratio <= threshold
            ]
            eligible_rows = [scanned_by_center[seed.n] for seed in eligible_seeds]
            rows.append(_summarize_sensitivity(threshold, radius, eligible_rows))
    return rows


def write_cluster_scan_csv(rows: list[ClusterScanRow], output_path: str | Path) -> None:
    """Write cluster scan rows as CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(ClusterScanRow.__dataclass_fields__.keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    field: "" if (value := getattr(row, field)) is None else value
                    for field in fieldnames
                }
            )


def write_cluster_sensitivity_csv(
    rows: list[ClusterSensitivityRow], output_path: str | Path
) -> None:
    """Write D_R sensitivity rows as CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(ClusterSensitivityRow.__dataclass_fields__.keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    field: "" if (value := getattr(row, field)) is None else value
                    for field in fieldnames
                }
            )


def read_cluster_scan_csv(input_path: str | Path) -> list[ClusterScanRow]:
    """Read cluster scan rows from CSV."""
    path = Path(input_path)
    with path.open(encoding="utf-8", newline="") as handle:
        return [_cluster_scan_row_from_csv(row) for row in csv.DictReader(handle)]


def unique_certified_values(rows: list[ClusterScanRow]) -> list[int]:
    """Return sorted unique exact complete-covering values from cluster rows."""
    values: set[int] = set()
    for row in rows:
        values.update(int(value) for value in row.certified_values.split() if value)
    return sorted(values)


def _summarize_sensitivity(
    threshold: float,
    radius: int,
    rows: list[ClusterScanRow],
) -> ClusterSensitivityRow:
    if not rows:
        return ClusterSensitivityRow(
            ratio_threshold=threshold,
            radius=radius,
            seed_count=0,
            exact_complete_memberships=0,
            unique_exact_complete_count=0,
            d_r_min=0.0,
            d_r_median=0.0,
            d_r_mean=0.0,
            d_r_max=0.0,
            top_center=None,
            top_exact_count=None,
            top_d_r=None,
        )
    densities = [row.d_r for row in rows]
    top = max(rows, key=lambda row: row.d_r)
    return ClusterSensitivityRow(
        ratio_threshold=threshold,
        radius=radius,
        seed_count=len(rows),
        exact_complete_memberships=sum(row.exact_complete_count for row in rows),
        unique_exact_complete_count=len(unique_certified_values(rows)),
        d_r_min=min(densities),
        d_r_median=_median(densities),
        d_r_mean=sum(densities) / len(densities),
        d_r_max=max(densities),
        top_center=top.center,
        top_exact_count=top.exact_complete_count,
        top_d_r=top.d_r,
    )


def _cluster_scan_row_from_csv(row: dict[str, str]) -> ClusterScanRow:
    return ClusterScanRow(
        center=int(row["center"]),
        seed_uncovered_measure=_optional_float(row.get("seed_uncovered_measure", "")),
        seed_baseline_ratio=_optional_float(row.get("seed_baseline_ratio", "")),
        radius=int(row["radius"]),
        window_start=int(row["window_start"]),
        window_stop=int(row["window_stop"]),
        window_size=int(row["window_size"]),
        float_zero_count=int(row["float_zero_count"]),
        exact_complete_count=int(row["exact_complete_count"]),
        float_positive_exact_count=int(row.get("float_positive_exact_count", "0")),
        d_r=float(row["d_r"]),
        min_uncovered_measure=float(row["min_uncovered_measure"]),
        median_uncovered_measure=float(row["median_uncovered_measure"]),
        median_baseline_ratio=float(row["median_baseline_ratio"]),
        max_uncovered_measure=float(row["max_uncovered_measure"]),
        certified_values=row["certified_values"],
    )


def _optional_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _log_grid(start: int, stop: int, count: int) -> list[int]:
    if start < 2:
        raise ValueError("start must be >= 2")
    if stop < start:
        raise ValueError("stop must be >= start")
    if count < 2:
        raise ValueError("count must be >= 2")
    log_start = math.log(start)
    log_stop = math.log(stop)
    values = {
        int(round(math.exp(log_start + (log_stop - log_start) * index / (count - 1))))
        for index in range(count)
    }
    return sorted(values)


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0
