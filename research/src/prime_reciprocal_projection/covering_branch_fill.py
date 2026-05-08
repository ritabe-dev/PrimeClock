"""Branch-by-branch fill-in diagnostics for Prime Reciprocal Covering."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .covering import (
    PrimeArc,
    exact_is_completely_covered,
    merge_circular_intervals,
    uncovered_measure,
)
from .primes import primes_up_to
from .projection import validate_n


@dataclass(frozen=True)
class BranchFillRow:
    """One cumulative branch fill-in row for fixed N and branch k."""

    n: int
    max_branch: int
    branch: int
    branch_prime_count: int
    cumulative_prime_count: int
    cumulative_uncovered_measure: float
    full_uncovered_measure: float
    cumulative_minus_full: float
    fill_fraction: float | None
    residual_fraction: float | None
    branch_arc_width: float
    cumulative_arc_width: float
    marginal_uncovered_drop: float
    cumulative_max_gap: float
    cumulative_component_count: int
    exact_complete: bool


@dataclass(frozen=True)
class BranchFillSummaryRow:
    """Summary of cumulative branch fill-in speed for one N."""

    n: int
    max_branch: int
    full_uncovered_measure: float
    exact_complete: bool
    k50: int | None
    k90: int | None
    k99: int | None
    k50_censored: bool
    k90_censored: bool
    k99_censored: bool
    a_branch1: float
    a_last: float
    residual_last: float | None
    cumulative_arc_width_last: float


def branch_fill_rows(
    n: int,
    *,
    max_branch: int = 1000,
    primes: list[int] | None = None,
    exact_complete: bool | None = None,
) -> list[BranchFillRow]:
    """Return cumulative uncovered-measure rows for branches ``1..max_branch``.

    Branches are added in the PRP/PRC order ``k=floor(N/p)``. Row ``k`` measures
    coverage using all primes with branch index ``<= k``.
    """
    n = validate_n(n)
    if max_branch < 1:
        raise ValueError("max_branch must be >= 1")

    prime_values = primes_up_to(n) if primes is None else [p for p in primes if p <= n]
    full_measure = uncovered_measure(n, primes=prime_values)
    if exact_complete is None:
        exact_complete = exact_is_completely_covered(n, primes=prime_values)
    branches: dict[int, list[int]] = {}
    for p in prime_values:
        branch = n // p
        if 1 <= branch <= max_branch:
            branches.setdefault(branch, []).append(p)
    covered: list[tuple[float, float]] = []
    cumulative_arc_width = 0.0
    cumulative_prime_count = 0
    previous_measure = 1.0
    branch1_measure: float | None = None
    rows: list[BranchFillRow] = []

    for branch in range(1, max_branch + 1):
        branch_primes = branches.get(branch, [])
        cumulative_prime_count += len(branch_primes)
        branch_arc_width = sum(1.0 / p for p in branch_primes)
        cumulative_arc_width += branch_arc_width
        new_intervals = [
            interval
            for p in branch_primes
            for interval in _arc_intervals(PrimeArc(p=p, center=(n % p) / p, radius=1.0 / (2.0 * p)))
        ]
        if new_intervals:
            covered = merge_circular_intervals([*covered, *new_intervals])
        gaps = _uncovered_from_covered(covered)
        cumulative_measure = sum(_interval_length(gap) for gap in gaps)
        if branch1_measure is None:
            branch1_measure = cumulative_measure
        cumulative_max_gap = max((_interval_length(gap) for gap in gaps), default=0.0)
        cumulative_minus_full = cumulative_measure - full_measure
        denominator = branch1_measure - full_measure
        if denominator <= 0:
            fill_fraction = 1.0
            residual_fraction = 0.0
        else:
            fill_fraction = _clamp01((branch1_measure - cumulative_measure) / denominator)
            residual_fraction = _clamp01(cumulative_minus_full / denominator)
        rows.append(
            BranchFillRow(
                n=n,
                max_branch=max_branch,
                branch=branch,
                branch_prime_count=len(branch_primes),
                cumulative_prime_count=cumulative_prime_count,
                cumulative_uncovered_measure=cumulative_measure,
                full_uncovered_measure=full_measure,
                cumulative_minus_full=cumulative_minus_full,
                fill_fraction=fill_fraction,
                residual_fraction=residual_fraction,
                branch_arc_width=branch_arc_width,
                cumulative_arc_width=cumulative_arc_width,
                marginal_uncovered_drop=max(0.0, previous_measure - cumulative_measure),
                cumulative_max_gap=cumulative_max_gap,
                cumulative_component_count=len(gaps),
                exact_complete=exact_complete,
            )
        )
        previous_measure = cumulative_measure

    return rows


def branch_fill_summary_rows(
    ns: list[int],
    *,
    max_branch: int = 1000,
) -> list[BranchFillSummaryRow]:
    """Return one branch fill-in summary row for each N."""
    if not ns:
        return []
    prime_pool = primes_up_to(max(ns))
    rows: list[BranchFillSummaryRow] = []
    for n in ns:
        rows.append(branch_fill_summary(branch_fill_rows(n, max_branch=max_branch, primes=prime_pool)))
    return rows


def branch_fill_summary_table(rows: list[BranchFillRow]) -> list[BranchFillSummaryRow]:
    """Return summary rows grouped by N from long branch-fill rows."""
    grouped: dict[int, list[BranchFillRow]] = {}
    for row in rows:
        grouped.setdefault(row.n, []).append(row)
    return [branch_fill_summary(sorted(grouped[n], key=lambda row: row.branch)) for n in sorted(grouped)]


def branch_fill_summary(rows: list[BranchFillRow]) -> BranchFillSummaryRow:
    """Summarize one N's branch fill-in rows."""
    if not rows:
        raise ValueError("rows must not be empty")
    n_values = {row.n for row in rows}
    if len(n_values) != 1:
        raise ValueError("rows must contain exactly one N")

    first = rows[0]
    last = rows[-1]
    k50, k50_censored = _threshold_branch(rows, 0.50)
    k90, k90_censored = _threshold_branch(rows, 0.90)
    k99, k99_censored = _threshold_branch(rows, 0.99)
    return BranchFillSummaryRow(
        n=first.n,
        max_branch=first.max_branch,
        full_uncovered_measure=first.full_uncovered_measure,
        exact_complete=first.exact_complete,
        k50=k50,
        k90=k90,
        k99=k99,
        k50_censored=k50_censored,
        k90_censored=k90_censored,
        k99_censored=k99_censored,
        a_branch1=first.cumulative_uncovered_measure,
        a_last=last.cumulative_uncovered_measure,
        residual_last=last.residual_fraction,
        cumulative_arc_width_last=last.cumulative_arc_width,
    )


def branch_fill_table(ns: list[int], *, max_branch: int = 1000) -> list[BranchFillRow]:
    """Return cumulative branch fill-in rows for several N values."""
    if not ns:
        return []
    prime_pool = primes_up_to(max(ns))
    rows: list[BranchFillRow] = []
    for n in ns:
        rows.extend(branch_fill_rows(n, max_branch=max_branch, primes=prime_pool))
    return rows


def write_branch_fill_csv(rows: list[BranchFillRow], output_path: str | Path) -> None:
    """Write branch fill-in rows as CSV."""
    _write_dataclass_csv(rows, output_path, list(BranchFillRow.__dataclass_fields__))


def write_branch_fill_summary_csv(
    rows: list[BranchFillSummaryRow],
    output_path: str | Path,
) -> None:
    """Write branch fill-in summary rows as CSV."""
    _write_dataclass_csv(rows, output_path, list(BranchFillSummaryRow.__dataclass_fields__))


def read_branch_fill_csv(path: str | Path) -> list[BranchFillRow]:
    """Read branch fill-in rows from CSV."""
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return [_branch_fill_row_from_csv(row) for row in csv.DictReader(handle)]


def _write_dataclass_csv(rows: list[object], output_path: str | Path, fieldnames: list[str]) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {field: "" if (value := getattr(row, field)) is None else value for field in fieldnames}
            )


def _branch_fill_row_from_csv(row: dict[str, str]) -> BranchFillRow:
    return BranchFillRow(
        n=int(row["n"]),
        max_branch=int(row["max_branch"]),
        branch=int(row["branch"]),
        branch_prime_count=int(row["branch_prime_count"]),
        cumulative_prime_count=int(row["cumulative_prime_count"]),
        cumulative_uncovered_measure=float(row["cumulative_uncovered_measure"]),
        full_uncovered_measure=float(row["full_uncovered_measure"]),
        cumulative_minus_full=float(row["cumulative_minus_full"]),
        fill_fraction=_optional_float(row["fill_fraction"]),
        residual_fraction=_optional_float(row["residual_fraction"]),
        branch_arc_width=float(row["branch_arc_width"]),
        cumulative_arc_width=float(row["cumulative_arc_width"]),
        marginal_uncovered_drop=float(row["marginal_uncovered_drop"]),
        cumulative_max_gap=float(row["cumulative_max_gap"]),
        cumulative_component_count=int(row["cumulative_component_count"]),
        exact_complete=row["exact_complete"] == "True",
    )


def _threshold_branch(rows: list[BranchFillRow], threshold: float) -> tuple[int | None, bool]:
    for row in rows:
        if row.fill_fraction is not None and row.fill_fraction >= threshold:
            return row.branch, False
    return None, True


def _optional_float(value: str) -> float | None:
    return None if value == "" else float(value)


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def _arc_intervals(arc: PrimeArc) -> list[tuple[float, float]]:
    start = arc.center - arc.radius
    end = arc.center + arc.radius
    if arc.width >= 1.0:
        return [(0.0, 1.0)]
    if start < 0.0:
        return [(0.0, end), (1.0 + start, 1.0)]
    if end > 1.0:
        return [(0.0, end - 1.0), (start, 1.0)]
    return [(start, end)]


def _uncovered_from_covered(covered: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if not covered:
        return [(0.0, 1.0)]
    if len(covered) == 1 and covered[0] == (0.0, 1.0):
        return []

    gaps: list[tuple[float, float]] = []
    for index, (_, end) in enumerate(covered):
        next_start = covered[(index + 1) % len(covered)][0]
        gap_start = end
        gap_end = next_start + 1.0 if index == len(covered) - 1 else next_start
        if gap_end > gap_start:
            gaps.append((gap_start % 1.0, gap_end % 1.0))
    return gaps


def _interval_length(interval: tuple[float, float]) -> float:
    start, end = interval
    if end >= start:
        return end - start
    return 1.0 - start + end
