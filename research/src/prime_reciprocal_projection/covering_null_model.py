"""Structure-preserving null models for PRC branch-prefix diagnostics."""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from pathlib import Path

from .covering import merge_circular_intervals
from .covering_branch_fill_cohorts import CohortManifestRow
from .covering_residual_gaps import ResidualGapRow, gap_quantile, median
from .primes import primes_up_to


@dataclass(frozen=True)
class NullArcTemplate:
    """One preserved arc width in a branch-wise null model."""

    branch: int
    p: int
    radius: float

    @property
    def width(self) -> float:
        return 2.0 * self.radius


@dataclass(frozen=True)
class BranchUniformNullRow:
    """Per-observation branch-uniform null summary."""

    seed_n: int
    cohort_role: str
    n: int
    model: str
    iterations: int
    observed_residual_gap_count: int
    null_gap_count_mean: float
    null_gap_count_p05: float
    null_gap_count_p50: float
    null_gap_count_p95: float
    observed_percentile: float
    observed_less_than_null_rate: float


@dataclass(frozen=True)
class BranchUniformNullSummaryRow:
    """Cohort-level branch-uniform null summary."""

    cohort_role: str
    eligible_row_count: int
    median_observed_percentile: float
    median_observed_less_than_null_rate: float
    rows_below_null_p05: int
    rows_above_null_p95: int


BRANCH_UNIFORM_MODEL = "branch_uniform"
COHORT_ROLE_ORDER = (
    "complete",
    "local_mod6_control",
    "band_mod6_control",
    "band_ordinary_control",
)


def branch_uniform_arc_template(n: int, *, max_branch: int = 1000) -> list[NullArcTemplate]:
    """Return the branch and width template preserved by the null model."""
    if max_branch < 1:
        raise ValueError("max_branch must be >= 1")
    return [
        NullArcTemplate(branch=n // p, p=p, radius=1.0 / (2.0 * p))
        for p in primes_up_to(n)
        if n // p <= max_branch
    ]


def branch_uniform_sample_arcs(
    n: int,
    *,
    max_branch: int = 1000,
    rng: random.Random | None = None,
) -> list[tuple[int, float, float]]:
    """Sample ``(branch, center, radius)`` arcs while preserving branch widths."""
    generator = rng or random.Random()
    return [
        (arc.branch, generator.random(), arc.radius)
        for arc in branch_uniform_arc_template(n, max_branch=max_branch)
    ]


def branch_uniform_null_rows(
    manifest_rows: list[CohortManifestRow],
    observed_rows: list[ResidualGapRow],
    *,
    model: str = BRANCH_UNIFORM_MODEL,
    max_branch: int = 1000,
    iterations: int = 1000,
    seed: int = 1729,
) -> list[BranchUniformNullRow]:
    """Compare observed residual gap counts with a branch-wise uniform null."""
    if model != BRANCH_UNIFORM_MODEL:
        raise ValueError(f"unsupported null model: {model}")
    if iterations < 1:
        raise ValueError("iterations must be >= 1")
    if max_branch < 1:
        raise ValueError("max_branch must be >= 1")

    manifest_keys = {
        (row.seed_n, row.cohort_role, row.n)
        for row in manifest_rows
        if row.eligible and row.n is not None
    }
    rows: list[BranchUniformNullRow] = []
    for observed in sorted(
        (row for row in observed_rows if row.seed_analysis_eligible),
        key=lambda row: (row.seed_n, _role_index(row.cohort_role), row.n),
    ):
        if (observed.seed_n, observed.cohort_role, observed.n) not in manifest_keys:
            continue
        template = branch_uniform_arc_template(observed.n, max_branch=max_branch)
        rng = random.Random(_row_seed(seed, observed.seed_n, observed.n, observed.cohort_role))
        counts = [
            _random_gap_count_from_template(template, rng)
            for _ in range(iterations)
        ]
        counts_sorted = sorted(counts)
        observed_count = observed.residual_gap_count
        rows.append(
            BranchUniformNullRow(
                seed_n=observed.seed_n,
                cohort_role=observed.cohort_role,
                n=observed.n,
                model=model,
                iterations=iterations,
                observed_residual_gap_count=observed_count,
                null_gap_count_mean=sum(counts) / len(counts),
                null_gap_count_p05=gap_quantile(counts_sorted, 0.05),
                null_gap_count_p50=gap_quantile(counts_sorted, 0.50),
                null_gap_count_p95=gap_quantile(counts_sorted, 0.95),
                observed_percentile=sum(1 for count in counts if count <= observed_count) / len(counts),
                observed_less_than_null_rate=sum(1 for count in counts if observed_count < count) / len(counts),
            )
        )
    return rows


def branch_uniform_null_summary_rows(
    rows: list[BranchUniformNullRow],
) -> list[BranchUniformNullSummaryRow]:
    """Summarize branch-uniform null rows by cohort role."""
    summaries: list[BranchUniformNullSummaryRow] = []
    for role in _cohort_roles(rows):
        role_rows = [row for row in rows if row.cohort_role == role]
        if not role_rows:
            continue
        summaries.append(
            BranchUniformNullSummaryRow(
                cohort_role=role,
                eligible_row_count=len(role_rows),
                median_observed_percentile=median([row.observed_percentile for row in role_rows]),
                median_observed_less_than_null_rate=median(
                    [row.observed_less_than_null_rate for row in role_rows]
                ),
                rows_below_null_p05=sum(
                    1
                    for row in role_rows
                    if row.observed_residual_gap_count < row.null_gap_count_p05
                ),
                rows_above_null_p95=sum(
                    1
                    for row in role_rows
                    if row.observed_residual_gap_count > row.null_gap_count_p95
                ),
            )
        )
    return summaries


def write_branch_uniform_null_csv(
    rows: list[BranchUniformNullRow],
    output_path: str | Path,
) -> None:
    """Write branch-uniform null rows as CSV."""
    _write_dataclass_csv(rows, output_path, list(BranchUniformNullRow.__dataclass_fields__))


def write_branch_uniform_null_summary_csv(
    rows: list[BranchUniformNullSummaryRow],
    output_path: str | Path,
) -> None:
    """Write branch-uniform null summary rows as CSV."""
    _write_dataclass_csv(rows, output_path, list(BranchUniformNullSummaryRow.__dataclass_fields__))


def read_branch_uniform_null_csv(path: str | Path) -> list[BranchUniformNullRow]:
    """Read branch-uniform null rows from CSV."""
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return [_branch_uniform_null_row_from_csv(row) for row in csv.DictReader(handle)]


def _random_gap_count_from_template(
    template: list[NullArcTemplate],
    rng: random.Random,
) -> int:
    intervals: list[tuple[float, float]] = []
    for arc in template:
        center = rng.random()
        radius = arc.radius
        width = 2.0 * radius
        if width >= 1.0:
            return 0
        start = center - radius
        end = center + radius
        if start < 0.0:
            intervals.append((0.0, end))
            intervals.append((1.0 + start, 1.0))
        elif end > 1.0:
            intervals.append((0.0, end - 1.0))
            intervals.append((start, 1.0))
        else:
            intervals.append((start, end))

    covered = merge_circular_intervals(intervals)
    if not covered:
        return 1
    if len(covered) == 1 and covered[0] == (0.0, 1.0):
        return 0

    gap_count = 0
    for index, (_, end) in enumerate(covered):
        next_start = covered[(index + 1) % len(covered)][0]
        gap_end = next_start + 1.0 if index == len(covered) - 1 else next_start
        if gap_end > end:
            gap_count += 1
    return gap_count


def _row_seed(base_seed: int, seed_n: int, n: int, cohort_role: str) -> int:
    return (
        base_seed
        + seed_n * 1_000_003
        + n * 10_007
        + _role_index(cohort_role) * 101
    )


def _role_index(role: str) -> int:
    if role in COHORT_ROLE_ORDER:
        return COHORT_ROLE_ORDER.index(role)
    return len(COHORT_ROLE_ORDER)


def _cohort_roles(rows: list[BranchUniformNullRow]) -> list[str]:
    present = {row.cohort_role for row in rows}
    return [role for role in COHORT_ROLE_ORDER if role in present] + sorted(
        present - set(COHORT_ROLE_ORDER)
    )


def _branch_uniform_null_row_from_csv(row: dict[str, str]) -> BranchUniformNullRow:
    return BranchUniformNullRow(
        seed_n=int(row["seed_n"]),
        cohort_role=row["cohort_role"],
        n=int(row["n"]),
        model=row["model"],
        iterations=int(row["iterations"]),
        observed_residual_gap_count=int(row["observed_residual_gap_count"]),
        null_gap_count_mean=float(row["null_gap_count_mean"]),
        null_gap_count_p05=float(row["null_gap_count_p05"]),
        null_gap_count_p50=float(row["null_gap_count_p50"]),
        null_gap_count_p95=float(row["null_gap_count_p95"]),
        observed_percentile=float(row["observed_percentile"]),
        observed_less_than_null_rate=float(row["observed_less_than_null_rate"]),
    )


def _write_dataclass_csv(rows: list[object], output_path: str | Path, fieldnames: list[str]) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})
