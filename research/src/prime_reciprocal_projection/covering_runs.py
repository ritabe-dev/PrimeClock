"""Consecutive-run analysis for exact PRC complete-covering values."""

from __future__ import annotations

import csv
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .cluster_scan import ClusterScanRow, read_cluster_scan_csv, unique_certified_values
from .covering import exact_is_completely_covered
from .covering_metrics import covering_row
from .primes import primes_up_to
from .projection import validate_n


DEFAULT_PREFILTER_TOLERANCE = 1e-12
PREFILTER_GUARANTEE_MAX_N = 1_000_000
PREFILTER_ERROR_SAFETY_FACTOR = 4096.0


@dataclass(frozen=True)
class CompleteCoveringRun:
    """One consecutive run of exact complete-covering integers."""

    start: int
    stop: int
    length: int


@dataclass(frozen=True)
class CompleteCoveringRunSummary:
    """Summary of consecutive exact complete-covering runs."""

    value_count: int
    run_count: int
    longest_run_length: int
    longest_run_start: int | None
    longest_run_stop: int | None
    multi_run_count: int
    values_in_multi_runs: int


@dataclass(frozen=True)
class CompleteCoveringScanResult:
    """Exact complete-covering values plus scan diagnostics."""

    start: int
    stop: int
    checked_count: int
    numeric_candidate_count: int
    exact_complete_count: int
    prefilter_tolerance: float | None
    values: tuple[int, ...]


@dataclass(frozen=True)
class RunTransitionStats:
    """Transition statistics for complete-covering values in an interval."""

    start: int
    stop: int
    complete_count: int
    run_count: int
    longest_run_length: int
    length2_run_count: int
    length3_start_count: int
    p_c0: float
    p_next_given_c0: float
    independent_adjacent_expectation: float
    c0_mod_6_counts: str
    length2_start_mod_6_counts: str
    small_gap_counts_1_to_10: str


@dataclass(frozen=True)
class Length2PairForensicsRow:
    """Forensic metrics around one length-2 complete-covering run."""

    run_start: int
    run_stop: int
    length: int
    start_mod_6: int
    stop_mod_6: int
    factorization_start: str
    factorization_stop: str
    a_n_minus_1: float
    a_n: float
    a_n_plus_1: float
    a_n_plus_2: float
    g_n_minus_1: float
    g_n: float
    g_n_plus_1: float
    g_n_plus_2: float
    component_count_n_minus_1: int
    component_count_n: int
    component_count_n_plus_1: int
    component_count_n_plus_2: int
    gap_fill_ratio_n_minus_1: float | None
    gap_fill_ratio_n: float | None
    gap_fill_ratio_n_plus_1: float | None
    gap_fill_ratio_n_plus_2: float | None


@dataclass(frozen=True)
class Length2NeighborhoodRow:
    """Long-form row for one integer near a length-2 run."""

    run_start: int
    run_stop: int
    n: int
    offset: int
    is_complete: bool
    uncovered_measure: float
    max_uncovered_gap: float
    component_count: int
    gap_fill_ratio: float | None


@dataclass(frozen=True)
class PrefilterValidationWindowRow:
    """Comparison of all-exact and prefiltered exact-certified values in a window."""

    window_start: int
    window_stop: int
    label: str
    all_exact_count: int
    prefilter_exact_count: int
    matches: bool
    all_exact_values: str
    prefilter_exact_values: str
    missing_from_prefilter: str
    extra_prefilter_values: str


def consecutive_runs(values: Iterable[int]) -> list[CompleteCoveringRun]:
    """Return maximal consecutive runs from integer values."""
    unique_values = sorted(set(values))
    if not unique_values:
        return []

    runs: list[CompleteCoveringRun] = []
    start = previous = unique_values[0]
    for value in unique_values[1:]:
        if value == previous + 1:
            previous = value
            continue
        runs.append(CompleteCoveringRun(start=start, stop=previous, length=previous - start + 1))
        start = previous = value
    runs.append(CompleteCoveringRun(start=start, stop=previous, length=previous - start + 1))
    return runs


def complete_covering_runs_from_cluster_rows(
    rows: Iterable[ClusterScanRow],
) -> list[CompleteCoveringRun]:
    """Return consecutive runs from unique certified values in cluster rows."""
    return consecutive_runs(unique_certified_values(list(rows)))


def complete_covering_runs_from_cluster_csv(path: str | Path) -> list[CompleteCoveringRun]:
    """Read a cluster scan CSV and return consecutive certified-value runs."""
    return complete_covering_runs_from_cluster_rows(read_cluster_scan_csv(path))


def read_complete_covering_runs_csv(path: str | Path) -> list[CompleteCoveringRun]:
    """Read consecutive complete-covering runs from CSV."""
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return [
            CompleteCoveringRun(
                start=int(row["start"]),
                stop=int(row["stop"]),
                length=int(row["length"]),
            )
            for row in csv.DictReader(handle)
        ]


def values_from_runs(runs: Iterable[CompleteCoveringRun]) -> list[int]:
    """Expand run rows into sorted complete-covering values."""
    values: list[int] = []
    for run in runs:
        values.extend(range(run.start, run.stop + 1))
    return sorted(set(values))


def length2_runs(runs: Iterable[CompleteCoveringRun]) -> list[CompleteCoveringRun]:
    """Return runs containing at least one adjacent complete-covering pair."""
    return [run for run in runs if run.length >= 2]


def exact_complete_values_in_range(start: int, stop: int) -> list[int]:
    """Exact-check every integer in ``[start, stop]`` and return complete values."""
    start = validate_n(start)
    stop = validate_n(stop)
    if stop < start:
        raise ValueError("stop must be >= start")
    prime_pool = primes_up_to(stop)
    values: list[int] = []
    active_primes: list[int] = []
    prime_index = 0
    for n in range(start, stop + 1):
        while prime_index < len(prime_pool) and prime_pool[prime_index] <= n:
            active_primes.append(prime_pool[prime_index])
            prime_index += 1
        if exact_is_completely_covered(n, primes=active_primes):
            values.append(n)
    return values


def required_prefilter_tolerance(
    max_n: int,
    *,
    safety_factor: float = PREFILTER_ERROR_SAFETY_FACTOR,
) -> float:
    """Return the conservative tolerance required by the v0 numeric prefilter.

    The current implementation computes every arc endpoint as a binary64 float
    from a rational value in ``[0, 1]``. The bound is intentionally conservative:
    it is a guardrail for the implemented scan, not a sharp floating-point
    analysis.
    """
    validate_n(max_n)
    if safety_factor <= 0:
        raise ValueError("safety_factor must be > 0")
    return safety_factor * sys.float_info.epsilon


def validate_prefilter_tolerance(
    max_n: int,
    *,
    tolerance: float = DEFAULT_PREFILTER_TOLERANCE,
    require_guarantee: bool = True,
) -> None:
    """Validate that a prefilter scan is inside the documented v0 guardrails."""
    max_n = validate_n(max_n)
    if tolerance < 0:
        raise ValueError("tolerance must be >= 0")
    if require_guarantee and max_n > PREFILTER_GUARANTEE_MAX_N:
        raise ValueError(
            "prefilter guarantee is currently documented only for "
            f"N <= {PREFILTER_GUARANTEE_MAX_N}; pass require_guarantee=False "
            "for exploratory scans beyond that range"
        )
    required = required_prefilter_tolerance(max_n)
    if tolerance < required:
        raise ValueError(
            f"tolerance={tolerance:g} is below the conservative required "
            f"prefilter tolerance {required:g}"
        )


def prefiltered_exact_complete_values_in_range(
    start: int,
    stop: int,
    *,
    tolerance: float = DEFAULT_PREFILTER_TOLERANCE,
    workers: int = 1,
    chunk_size: int = 100000,
    require_guarantee: bool = True,
) -> CompleteCoveringScanResult:
    """Numeric-prefilter a range, then exact-check every numeric candidate.

    The returned values are exact-certified. With the default guardrails, scans
    up to ``PREFILTER_GUARANTEE_MAX_N`` also require a tolerance large enough to
    bridge the documented binary64 endpoint error bound, preventing exact
    complete-covering values from being rejected by the numeric prefilter.
    """
    start = validate_n(start)
    stop = validate_n(stop)
    if stop < start:
        raise ValueError("stop must be >= start")
    validate_prefilter_tolerance(
        stop,
        tolerance=tolerance,
        require_guarantee=require_guarantee,
    )
    if workers < 1:
        raise ValueError("workers must be >= 1")
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")

    chunks = _range_chunks(start, stop, chunk_size)
    if workers == 1 or len(chunks) == 1:
        chunk_results = [_prefiltered_exact_complete_values_chunk((*chunk, tolerance)) for chunk in chunks]
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            chunk_results = list(
                executor.map(
                    _prefiltered_exact_complete_values_chunk,
                    [(*chunk, tolerance) for chunk in chunks],
                )
            )

    numeric_candidate_count = sum(result[0] for result in chunk_results)
    exact_values = sorted(value for _, values in chunk_results for value in values)
    return CompleteCoveringScanResult(
        start=start,
        stop=stop,
        checked_count=stop - start + 1,
        numeric_candidate_count=numeric_candidate_count,
        exact_complete_count=len(exact_values),
        prefilter_tolerance=tolerance,
        values=tuple(exact_values),
    )


def exact_complete_runs_in_range(start: int, stop: int) -> list[CompleteCoveringRun]:
    """Exact-check every integer in ``[start, stop]`` and return consecutive runs."""
    return consecutive_runs(exact_complete_values_in_range(start, stop))


def summarize_runs(runs: Iterable[CompleteCoveringRun]) -> CompleteCoveringRunSummary:
    """Summarize consecutive complete-covering runs."""
    run_list = list(runs)
    if not run_list:
        return CompleteCoveringRunSummary(
            value_count=0,
            run_count=0,
            longest_run_length=0,
            longest_run_start=None,
            longest_run_stop=None,
            multi_run_count=0,
            values_in_multi_runs=0,
        )
    longest = max(run_list, key=lambda run: (run.length, -run.start))
    return CompleteCoveringRunSummary(
        value_count=sum(run.length for run in run_list),
        run_count=len(run_list),
        longest_run_length=longest.length,
        longest_run_start=longest.start,
        longest_run_stop=longest.stop,
        multi_run_count=sum(1 for run in run_list if run.length >= 2),
        values_in_multi_runs=sum(run.length for run in run_list if run.length >= 2),
    )


def transition_stats_from_runs(
    runs: Iterable[CompleteCoveringRun],
    *,
    start: int,
    stop: int,
) -> RunTransitionStats:
    """Compute C0 transition statistics from run rows."""
    start = validate_n(start)
    stop = validate_n(stop)
    if stop < start:
        raise ValueError("stop must be >= start")

    run_list = list(runs)
    values = values_from_runs(run_list)
    value_set = set(values)
    checked_count = stop - start + 1
    adjacent_starts = sum(1 for value in values if value + 1 in value_set)
    triple_starts = sum(
        1 for value in values if value + 1 in value_set and value + 2 in value_set
    )
    gaps = [right - left for left, right in zip(values, values[1:])]
    complete_count = len(values)
    p_c0 = complete_count / checked_count
    return RunTransitionStats(
        start=start,
        stop=stop,
        complete_count=complete_count,
        run_count=len(run_list),
        longest_run_length=max((run.length for run in run_list), default=0),
        length2_run_count=adjacent_starts,
        length3_start_count=triple_starts,
        p_c0=p_c0,
        p_next_given_c0=adjacent_starts / complete_count if complete_count else 0.0,
        independent_adjacent_expectation=complete_count * p_c0,
        c0_mod_6_counts=_format_counts(_residue_counts(values, 6)),
        length2_start_mod_6_counts=_format_counts(
            _residue_counts((value for value in values if value + 1 in value_set), 6)
        ),
        small_gap_counts_1_to_10=_format_counts({gap: gaps.count(gap) for gap in range(1, 11)}),
    )


def length2_pair_forensics(runs: Iterable[CompleteCoveringRun]) -> list[Length2PairForensicsRow]:
    """Return compact forensic rows for every run with length at least 2."""
    pair_runs = length2_runs(runs)
    if not pair_runs:
        return []

    ns = sorted({n for run in pair_runs for n in range(run.start - 1, run.start + 3)})
    prime_pool = primes_up_to(max(ns))
    rows_by_n = {n: covering_row(n, primes=prime_pool) for n in ns}

    rows: list[Length2PairForensicsRow] = []
    for run in pair_runs:
        row_m1 = rows_by_n[run.start - 1]
        row_0 = rows_by_n[run.start]
        row_p1 = rows_by_n[run.start + 1]
        row_p2 = rows_by_n[run.start + 2]
        rows.append(
            Length2PairForensicsRow(
                run_start=run.start,
                run_stop=run.stop,
                length=run.length,
                start_mod_6=run.start % 6,
                stop_mod_6=run.stop % 6,
                factorization_start=factorization(run.start),
                factorization_stop=factorization(run.stop),
                a_n_minus_1=row_m1.uncovered_measure,
                a_n=row_0.uncovered_measure,
                a_n_plus_1=row_p1.uncovered_measure,
                a_n_plus_2=row_p2.uncovered_measure,
                g_n_minus_1=row_m1.max_uncovered_gap,
                g_n=row_0.max_uncovered_gap,
                g_n_plus_1=row_p1.max_uncovered_gap,
                g_n_plus_2=row_p2.max_uncovered_gap,
                component_count_n_minus_1=row_m1.uncovered_component_count,
                component_count_n=row_0.uncovered_component_count,
                component_count_n_plus_1=row_p1.uncovered_component_count,
                component_count_n_plus_2=row_p2.uncovered_component_count,
                gap_fill_ratio_n_minus_1=row_m1.gap_fill_ratio,
                gap_fill_ratio_n=row_0.gap_fill_ratio,
                gap_fill_ratio_n_plus_1=row_p1.gap_fill_ratio,
                gap_fill_ratio_n_plus_2=row_p2.gap_fill_ratio,
            )
        )
    return rows


def length2_neighborhood_rows(
    runs: Iterable[CompleteCoveringRun],
) -> list[Length2NeighborhoodRow]:
    """Return long-form ``N-1..N+2`` rows for length-2 runs."""
    pair_runs = length2_runs(runs)
    if not pair_runs:
        return []

    ns = sorted({n for run in pair_runs for n in range(run.start - 1, run.start + 3)})
    prime_pool = primes_up_to(max(ns))
    rows_by_n = {n: covering_row(n, primes=prime_pool) for n in ns}

    rows: list[Length2NeighborhoodRow] = []
    for run in pair_runs:
        for n in range(run.start - 1, run.start + 3):
            covering = rows_by_n[n]
            rows.append(
                Length2NeighborhoodRow(
                    run_start=run.start,
                    run_stop=run.stop,
                    n=n,
                    offset=n - run.start,
                    is_complete=run.start <= n <= run.stop,
                    uncovered_measure=covering.uncovered_measure,
                    max_uncovered_gap=covering.max_uncovered_gap,
                    component_count=covering.uncovered_component_count,
                    gap_fill_ratio=covering.gap_fill_ratio,
                )
            )
    return rows


def prefilter_validation_windows(
    windows: Iterable[tuple[int, int, str]],
    *,
    tolerance: float = 1e-12,
) -> list[PrefilterValidationWindowRow]:
    """Compare all-exact and prefiltered exact-certified values in windows."""
    rows: list[PrefilterValidationWindowRow] = []
    for start, stop, label in windows:
        exact_values = exact_complete_values_in_range(start, stop)
        prefilter_values = list(
            prefiltered_exact_complete_values_in_range(
                start,
                stop,
                tolerance=tolerance,
                chunk_size=max(1, stop - start + 1),
            ).values
        )
        exact_set = set(exact_values)
        prefilter_set = set(prefilter_values)
        rows.append(
            PrefilterValidationWindowRow(
                window_start=start,
                window_stop=stop,
                label=label,
                all_exact_count=len(exact_values),
                prefilter_exact_count=len(prefilter_values),
                matches=exact_values == prefilter_values,
                all_exact_values=_format_ints(exact_values),
                prefilter_exact_values=_format_ints(prefilter_values),
                missing_from_prefilter=_format_ints(sorted(exact_set - prefilter_set)),
                extra_prefilter_values=_format_ints(sorted(prefilter_set - exact_set)),
            )
        )
    return rows


def default_prefilter_validation_windows(
    runs: Iterable[CompleteCoveringRun],
    *,
    start: int = 2,
    stop: int = 1_000_000,
) -> list[tuple[int, int, str]]:
    """Return deterministic validation windows for the v0 forensic pass."""
    start = validate_n(start)
    stop = validate_n(stop)
    windows: list[tuple[int, int, str]] = []
    for run in length2_runs(runs):
        windows.append((max(2, run.start - 25), run.stop + 25, f"length2:{run.start}-{run.stop}"))
    block_start = start
    while block_start <= stop:
        block_stop = min(stop, 100_000 if block_start == 2 else block_start + 99_999)
        if block_stop - block_start + 1 < 501:
            break
        mid_start = block_start + 49_950
        mid_stop = block_start + 50_450
        if mid_stop <= block_stop:
            windows.append((mid_start, mid_stop, f"block-mid:{block_start}-{block_stop}"))
        block_start = block_stop + 1
    return windows


def factorization(n: int) -> str:
    """Return stable prime factorization text."""
    n = validate_n(n)
    factors: list[str] = []
    remaining = n
    divisor = 2
    while divisor * divisor <= remaining:
        exponent = 0
        while remaining % divisor == 0:
            remaining //= divisor
            exponent += 1
        if exponent:
            factors.append(f"{divisor}^{exponent}" if exponent > 1 else str(divisor))
        divisor += 1 if divisor == 2 else 2
    if remaining > 1:
        factors.append(str(remaining))
    return "*".join(factors)


def write_complete_covering_runs_csv(
    runs: Iterable[CompleteCoveringRun],
    output_path: str | Path,
) -> None:
    """Write complete-covering runs as CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(CompleteCoveringRun.__dataclass_fields__.keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for run in runs:
            writer.writerow({field: getattr(run, field) for field in fieldnames})


def write_dataclass_csv(rows: Iterable[object], output_path: str | Path, fieldnames: list[str]) -> None:
    """Write dataclass-like rows to CSV with stable field order."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {field: "" if (value := getattr(row, field)) is None else value for field in fieldnames}
            )


def write_run_transition_stats_csv(row: RunTransitionStats, output_path: str | Path) -> None:
    """Write one transition stats row to CSV."""
    write_dataclass_csv([row], output_path, list(RunTransitionStats.__dataclass_fields__))


def write_length2_pair_forensics_csv(
    rows: Iterable[Length2PairForensicsRow],
    output_path: str | Path,
) -> None:
    """Write length-2 pair forensics rows to CSV."""
    write_dataclass_csv(rows, output_path, list(Length2PairForensicsRow.__dataclass_fields__))


def write_length2_neighborhoods_csv(
    rows: Iterable[Length2NeighborhoodRow],
    output_path: str | Path,
) -> None:
    """Write length-2 neighborhood rows to CSV."""
    write_dataclass_csv(rows, output_path, list(Length2NeighborhoodRow.__dataclass_fields__))


def write_prefilter_validation_windows_csv(
    rows: Iterable[PrefilterValidationWindowRow],
    output_path: str | Path,
) -> None:
    """Write prefilter validation window rows to CSV."""
    write_dataclass_csv(rows, output_path, list(PrefilterValidationWindowRow.__dataclass_fields__))


def _is_completely_covered_numeric_with_primes(
    n: int,
    prime_values: list[int],
    *,
    tolerance: float,
) -> bool:
    intervals: list[tuple[float, float]] = []
    for p in prime_values:
        denominator = 2.0 * p
        start = (2.0 * (n % p) - 1.0) / denominator
        end = (2.0 * (n % p) + 1.0) / denominator
        if start < 0.0:
            intervals.append((0.0, end))
            intervals.append((1.0 + start, 1.0))
        elif end > 1.0:
            intervals.append((0.0, end - 1.0))
            intervals.append((start, 1.0))
        else:
            intervals.append((start, end))

    if not intervals:
        return False

    intervals.sort()
    first_start, current_end = intervals[0]
    if first_start > tolerance:
        return False
    for start, end in intervals[1:]:
        if start > current_end + tolerance:
            return False
        if end > current_end:
            current_end = end
            if current_end >= 1.0 - tolerance:
                return True
    return current_end >= 1.0 - tolerance


def _residue_counts(values: Iterable[int], modulus: int) -> dict[int, int]:
    counts = {residue: 0 for residue in range(modulus)}
    for value in values:
        counts[value % modulus] += 1
    return counts


def _format_counts(counts: dict[int, int]) -> str:
    return " ".join(f"{key}:{counts[key]}" for key in sorted(counts))


def _format_ints(values: Iterable[int]) -> str:
    return " ".join(str(value) for value in values)


def _range_chunks(start: int, stop: int, chunk_size: int) -> list[tuple[int, int]]:
    chunks: list[tuple[int, int]] = []
    chunk_start = start
    while chunk_start <= stop:
        chunk_stop = min(stop, chunk_start + chunk_size - 1)
        chunks.append((chunk_start, chunk_stop))
        chunk_start = chunk_stop + 1
    return chunks


def _prefiltered_exact_complete_values_chunk(
    args: tuple[int, int, float],
) -> tuple[int, tuple[int, ...]]:
    start, stop, tolerance = args
    prime_pool = primes_up_to(stop)
    active_primes: list[int] = []
    prime_index = 0
    while prime_index < len(prime_pool) and prime_pool[prime_index] < start:
        active_primes.append(prime_pool[prime_index])
        prime_index += 1

    numeric_candidate_count = 0
    exact_values: list[int] = []
    for n in range(start, stop + 1):
        while prime_index < len(prime_pool) and prime_pool[prime_index] <= n:
            active_primes.append(prime_pool[prime_index])
            prime_index += 1
        if not _is_completely_covered_numeric_with_primes(
            n,
            active_primes,
            tolerance=tolerance,
        ):
            continue
        numeric_candidate_count += 1
        if exact_is_completely_covered(n, primes=active_primes):
            exact_values.append(n)
    return numeric_candidate_count, tuple(exact_values)
