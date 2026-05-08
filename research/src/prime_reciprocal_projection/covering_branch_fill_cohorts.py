"""Matched cohort construction for PRC branch fill-in comparisons."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from .covering_branch_fill import BranchFillSummaryRow, branch_fill_rows, branch_fill_summary
from .covering_runs import CompleteCoveringRun, read_complete_covering_runs_csv, values_from_runs
from .primes import primes_up_to

COHORT_ROLES = (
    "complete",
    "local_mod6_control",
    "band_mod6_control",
    "band_ordinary_control",
)
DEFAULT_CHECKPOINTS = tuple([*range(1, 21), 30, 50, 100, 200, 500, 1000])


@dataclass(frozen=True)
class CohortManifestRow:
    """One complete or matched-control row for a seed."""

    seed_n: int
    cohort_role: str
    n: int | None
    bin_index: int
    bin_start: int
    bin_stop: int
    n_mod_6: int | None
    eligible: bool
    exclusion_reason: str


@dataclass(frozen=True)
class CohortBranchFillSummaryRow:
    """Branch fill-in summary row annotated with cohort identity."""

    seed_n: int
    cohort_role: str
    n: int
    bin_index: int
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


@dataclass(frozen=True)
class CohortBranchFillCheckpointRow:
    """One checkpoint row from a cohort branch fill-in curve."""

    seed_n: int
    cohort_role: str
    n: int
    bin_index: int
    max_branch: int
    branch: int
    cumulative_uncovered_measure: float
    full_uncovered_measure: float
    fill_fraction: float | None
    residual_fraction: float | None
    cumulative_max_gap: float
    cumulative_component_count: int
    exact_complete: bool


def build_cohort_manifest_from_runs_csv(
    runs_csv: str | Path,
    *,
    start: int = 1000,
    stop: int = 1_000_000,
    bin_count: int = 12,
    max_per_bin: int = 3,
    local_radius: int = 250,
) -> list[CohortManifestRow]:
    """Build the deterministic v0.4 complete/control cohort manifest."""
    return build_cohort_manifest(
        read_complete_covering_runs_csv(runs_csv),
        start=start,
        stop=stop,
        bin_count=bin_count,
        max_per_bin=max_per_bin,
        local_radius=local_radius,
    )


def build_cohort_manifest(
    runs: list[CompleteCoveringRun],
    *,
    start: int = 1000,
    stop: int = 1_000_000,
    bin_count: int = 12,
    max_per_bin: int = 3,
    local_radius: int = 250,
) -> list[CohortManifestRow]:
    """Build deterministic complete seeds and matched controls."""
    if start < 2:
        raise ValueError("start must be >= 2")
    if stop < start:
        raise ValueError("stop must be >= start")
    if bin_count < 1:
        raise ValueError("bin_count must be >= 1")
    if max_per_bin < 1:
        raise ValueError("max_per_bin must be >= 1")
    if local_radius < 0:
        raise ValueError("local_radius must be >= 0")

    complete_values = {value for value in values_from_runs(runs) if start <= value <= stop}
    bins = _log_bins(start, stop, bin_count)
    selected: list[tuple[int, int, int, int]] = []
    for bin_index, bin_start, bin_stop in bins:
        log_center = (math.log(bin_start) + math.log(bin_stop)) / 2.0
        in_bin = [n for n in complete_values if bin_start <= n <= bin_stop]
        selected.extend(
            (n, bin_index, bin_start, bin_stop)
            for n in sorted(in_bin, key=lambda value: (abs(math.log(value) - log_center), value))[
                :max_per_bin
            ]
        )

    rows: list[CohortManifestRow] = []
    for seed_n, bin_index, bin_start, bin_stop in sorted(selected):
        controls = _controls_for_seed(
            seed_n,
            start=start,
            stop=stop,
            bin_start=bin_start,
            bin_stop=bin_stop,
            complete_values=complete_values,
            local_radius=local_radius,
        )
        missing = [role for role in COHORT_ROLES[1:] if controls.get(role) is None]
        eligible = not missing
        reason = "" if eligible else "missing:" + ",".join(missing)
        values = {"complete": seed_n, **controls}
        for role in COHORT_ROLES:
            n = values.get(role)
            rows.append(
                CohortManifestRow(
                    seed_n=seed_n,
                    cohort_role=role,
                    n=n,
                    bin_index=bin_index,
                    bin_start=bin_start,
                    bin_stop=bin_stop,
                    n_mod_6=None if n is None else n % 6,
                    eligible=eligible,
                    exclusion_reason=reason,
                )
            )
    return rows


def cohort_branch_fill_tables(
    manifest_rows: list[CohortManifestRow],
    *,
    max_branch: int = 1000,
    checkpoints: tuple[int, ...] = DEFAULT_CHECKPOINTS,
) -> tuple[list[CohortBranchFillSummaryRow], list[CohortBranchFillCheckpointRow]]:
    """Compute branch fill-in summary and checkpoint rows for eligible cohorts."""
    eligible_rows = [row for row in manifest_rows if row.eligible and row.n is not None]
    if not eligible_rows:
        return [], []
    prime_pool = primes_up_to(max(row.n for row in eligible_rows if row.n is not None))
    checkpoint_set = {branch for branch in checkpoints if 1 <= branch <= max_branch}
    summary_rows: list[CohortBranchFillSummaryRow] = []
    checkpoint_rows: list[CohortBranchFillCheckpointRow] = []

    for row in eligible_rows:
        assert row.n is not None
        is_complete = row.cohort_role == "complete"
        fill_rows = branch_fill_rows(
            row.n,
            max_branch=max_branch,
            primes=prime_pool,
            exact_complete=is_complete,
        )
        summary_rows.append(_cohort_summary_row(row, branch_fill_summary(fill_rows)))
        for fill_row in fill_rows:
            if fill_row.branch not in checkpoint_set:
                continue
            checkpoint_rows.append(
                CohortBranchFillCheckpointRow(
                    seed_n=row.seed_n,
                    cohort_role=row.cohort_role,
                    n=row.n,
                    bin_index=row.bin_index,
                    max_branch=fill_row.max_branch,
                    branch=fill_row.branch,
                    cumulative_uncovered_measure=fill_row.cumulative_uncovered_measure,
                    full_uncovered_measure=fill_row.full_uncovered_measure,
                    fill_fraction=fill_row.fill_fraction,
                    residual_fraction=fill_row.residual_fraction,
                    cumulative_max_gap=fill_row.cumulative_max_gap,
                    cumulative_component_count=fill_row.cumulative_component_count,
                    exact_complete=fill_row.exact_complete,
                )
            )
    return summary_rows, checkpoint_rows


def read_cohort_manifest_csv(path: str | Path) -> list[CohortManifestRow]:
    """Read cohort manifest rows from CSV."""
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return [_manifest_row_from_csv(row) for row in csv.DictReader(handle)]


def write_cohort_manifest_csv(rows: list[CohortManifestRow], output_path: str | Path) -> None:
    """Write cohort manifest rows as CSV."""
    _write_dataclass_csv(rows, output_path, list(CohortManifestRow.__dataclass_fields__))


def write_cohort_branch_fill_summary_csv(
    rows: list[CohortBranchFillSummaryRow],
    output_path: str | Path,
) -> None:
    """Write cohort branch fill-in summary rows as CSV."""
    _write_dataclass_csv(rows, output_path, list(CohortBranchFillSummaryRow.__dataclass_fields__))


def write_cohort_branch_fill_checkpoints_csv(
    rows: list[CohortBranchFillCheckpointRow],
    output_path: str | Path,
) -> None:
    """Write cohort branch fill-in checkpoint rows as CSV."""
    _write_dataclass_csv(rows, output_path, list(CohortBranchFillCheckpointRow.__dataclass_fields__))


def _controls_for_seed(
    seed_n: int,
    *,
    start: int,
    stop: int,
    bin_start: int,
    bin_stop: int,
    complete_values: set[int],
    local_radius: int,
) -> dict[str, int | None]:
    used = {seed_n}
    controls: dict[str, int | None] = {}
    controls["local_mod6_control"] = _first_candidate(
        range(max(start, seed_n - local_radius), min(stop, seed_n + local_radius) + 1),
        complete_values=complete_values,
        used=used,
        predicate=lambda n: n % 6 == seed_n % 6,
        key=lambda n: (abs(n - seed_n), n),
    )
    if controls["local_mod6_control"] is not None:
        used.add(controls["local_mod6_control"])

    log_center = (math.log(bin_start) + math.log(bin_stop)) / 2.0
    band_values = range(bin_start, bin_stop + 1)
    controls["band_mod6_control"] = _first_candidate(
        band_values,
        complete_values=complete_values,
        used=used,
        predicate=lambda n: n % 6 == seed_n % 6,
        key=lambda n: (abs(math.log(n) - log_center), n),
    )
    if controls["band_mod6_control"] is not None:
        used.add(controls["band_mod6_control"])

    controls["band_ordinary_control"] = _first_candidate(
        band_values,
        complete_values=complete_values,
        used=used,
        predicate=lambda n: True,
        key=lambda n: (abs(math.log(n) - log_center), n),
    )
    return controls


def _first_candidate(
    values: range,
    *,
    complete_values: set[int],
    used: set[int],
    predicate,
    key,
) -> int | None:
    candidates = [
        n for n in values if n not in complete_values and n not in used and predicate(n)
    ]
    return None if not candidates else min(candidates, key=key)


def _cohort_summary_row(
    manifest_row: CohortManifestRow,
    summary: BranchFillSummaryRow,
) -> CohortBranchFillSummaryRow:
    assert manifest_row.n is not None
    return CohortBranchFillSummaryRow(
        seed_n=manifest_row.seed_n,
        cohort_role=manifest_row.cohort_role,
        n=manifest_row.n,
        bin_index=manifest_row.bin_index,
        max_branch=summary.max_branch,
        full_uncovered_measure=summary.full_uncovered_measure,
        exact_complete=summary.exact_complete,
        k50=summary.k50,
        k90=summary.k90,
        k99=summary.k99,
        k50_censored=summary.k50_censored,
        k90_censored=summary.k90_censored,
        k99_censored=summary.k99_censored,
        a_branch1=summary.a_branch1,
        a_last=summary.a_last,
        residual_last=summary.residual_last,
        cumulative_arc_width_last=summary.cumulative_arc_width_last,
    )


def _log_bins(start: int, stop: int, count: int) -> list[tuple[int, int, int]]:
    log_start = math.log(start)
    log_stop = math.log(stop)
    raw_edges = [
        int(round(math.exp(log_start + (log_stop - log_start) * index / count)))
        for index in range(count + 1)
    ]
    raw_edges[0] = start
    raw_edges[-1] = stop + 1
    edges: list[int] = []
    previous = start - 1
    for edge in raw_edges:
        edge = max(edge, previous + 1)
        edges.append(edge)
        previous = edge
    return [(index, edges[index], edges[index + 1] - 1) for index in range(count)]


def _manifest_row_from_csv(row: dict[str, str]) -> CohortManifestRow:
    return CohortManifestRow(
        seed_n=int(row["seed_n"]),
        cohort_role=row["cohort_role"],
        n=_optional_int(row["n"]),
        bin_index=int(row["bin_index"]),
        bin_start=int(row["bin_start"]),
        bin_stop=int(row["bin_stop"]),
        n_mod_6=_optional_int(row["n_mod_6"]),
        eligible=row["eligible"] == "True",
        exclusion_reason=row["exclusion_reason"],
    )


def _optional_int(value: str) -> int | None:
    return None if value == "" else int(value)


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
