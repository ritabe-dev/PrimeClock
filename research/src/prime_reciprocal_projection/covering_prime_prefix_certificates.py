"""Certificate-depth diagnostics for PRC prime-prefix residue filtrations."""

from __future__ import annotations

import csv
import statistics
from bisect import bisect_left
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from .covering_prime_prefix_filtration import (
    MAX_DEFAULT_FILTRATION_K,
    PrimePrefixResidueFiltrationRow,
    prime_prefix_residue_filtration_data,
)
from .covering_runs import read_complete_covering_runs_csv, values_from_runs

PREFIX_CERTIFICATE_STATUS = "prefix_certificate"
NO_PREFIX_CERTIFICATE_STATUS = "no_prefix_certificate_within_max_k"


@dataclass(frozen=True)
class PrimePrefixCertificateRow:
    """One complete-covering value classified by prime-prefix certificate depth."""

    n: int
    k_cert: int | None
    p_cert: int | None
    primorial_cert: int | None
    residue_cert: int | None
    checked_max_k: int
    checked_max_prime: int
    certificate_status: str
    mod210: int
    trivial_c4_certificate: bool


@dataclass(frozen=True)
class PrimePrefixCertificateSummaryRow:
    """Aggregate certificate-depth counts."""

    certificate_status: str
    k_cert: int | None
    p_cert: int | None
    complete_count: int
    share_of_complete: float
    min_n: int
    max_n: int
    checked_max_k: int
    checked_max_prime: int


@dataclass(frozen=True)
class PrimePrefixUncertifiedResidueRow:
    """One no-prefix-certificate value positioned against the checked C_k set."""

    n: int
    checked_max_k: int
    checked_max_prime: int
    residue_modulus: int
    residue: int
    mod210: int
    mod2310: int
    nearest_covered_residue: int
    nearest_covered_source_k: int
    nearest_covered_source_prime: int
    circular_residue_distance: int
    normalized_residue_distance: float


@dataclass(frozen=True)
class PrimePrefixUncertifiedMod210SummaryRow:
    """Modulo-210 summary for no-prefix-certificate rows."""

    mod210: int
    uncertified_count: int
    share_of_uncertified: float
    nearest_distance_median: float
    nearest_distance_max: int
    sample_n: str


@dataclass(frozen=True)
class PrimePrefixUncertifiedOverallSummaryRow:
    """Overall scalar summary for no-prefix-certificate residue profiling."""

    metric: str
    value: str


@dataclass(frozen=True)
class PrimePrefixUncertifiedMatchedProfileRow:
    """Uncertified complete value or matched non-complete control residue profile."""

    seed_n: int
    cohort_role: str
    n: int
    control_delta: int
    checked_max_k: int
    checked_max_prime: int
    residue_modulus: int
    residue: int
    mod210: int
    mod2310: int
    nearest_covered_residue: int
    nearest_covered_source_k: int
    nearest_covered_source_prime: int
    circular_residue_distance: int
    normalized_residue_distance: float


@dataclass(frozen=True)
class PrimePrefixUncertifiedMatchedSummaryRow:
    """Cohort-level summary for uncertified complete/control residue profiles."""

    cohort_role: str
    row_count: int
    unique_n_count: int
    unique_mod210_count: int
    nearest_distance_median: float
    nearest_distance_p90: int
    nearest_distance_p99: int
    nearest_distance_max: int


@dataclass(frozen=True)
class PrimePrefixUncertifiedMatchedPairDeltaRow:
    """Paired complete-control distance delta for one metric."""

    seed_n: int
    control_role: str
    complete_n: int
    control_n: int
    metric: str
    complete_value: float
    control_value: float
    delta_complete_minus_control: float


@dataclass(frozen=True)
class PrimePrefixUncertifiedMod210AuditRow:
    """Class-level paired distance audit for uncertified complete/control rows."""

    control_role: str
    seed_mod210: int
    pair_count: int
    complete_distance_median: float
    control_distance_median: float
    median_delta_complete_minus_control: float
    complete_smaller_count: int
    complete_larger_count: int
    tie_count: int
    complete_smaller_rate: float
    complete_larger_rate: float
    sample_seed_n: str


@dataclass(frozen=True)
class PrimePrefixUncertifiedSourceDepthSummaryRow:
    """Nearest-C_k source-depth summary for matched residue profile rows."""

    cohort_role: str
    nearest_covered_source_k: int
    nearest_covered_source_prime: int
    row_count: int
    share_of_role: float
    nearest_distance_median: float
    nearest_distance_max: int


@dataclass(frozen=True)
class PrimePrefixUncertifiedMod210ClassReviewRow:
    """Pivoted modulo-210 class review row for paired control audits."""

    seed_mod210: int
    max_pair_count: int
    local_mod210_pair_count: int | None
    local_any_pair_count: int | None
    local_mod210_median_delta: float | None
    local_any_median_delta: float | None
    median_delta_difference_any_minus_mod210: float | None
    local_mod210_complete_smaller_rate: float | None
    local_any_complete_smaller_rate: float | None
    smaller_rate_difference_any_minus_mod210: float | None
    local_mod210_complete_larger_rate: float | None
    local_any_complete_larger_rate: float | None
    direction_label: str
    priority_label: str
    sample_seed_n: str


@dataclass(frozen=True)
class PrimePrefixUncertifiedMod210ClassDetailRow:
    """Selected modulo-210 class row expanded back to seed/control profiles."""

    selected_rank: int
    seed_mod210: int
    priority_label: str
    direction_label: str
    seed_n: int
    cohort_role: str
    n: int
    control_delta: int
    row_mod210: int
    residue: int
    nearest_covered_residue: int
    nearest_covered_source_k: int
    nearest_covered_source_prime: int
    circular_residue_distance: int
    complete_circular_residue_distance: int
    distance_minus_complete: int
    normalized_residue_distance: float


@dataclass(frozen=True)
class PrimePrefixUncertifiedMod210ClassSourceSummaryRow:
    """Selected class summary by cohort role and nearest C_k source depth."""

    seed_mod210: int
    selected_rank: int
    priority_label: str
    direction_label: str
    cohort_role: str
    nearest_covered_source_k: int
    nearest_covered_source_prime: int
    row_count: int
    share_within_class_role: float
    circular_residue_distance_median: float
    circular_residue_distance_p90: int
    circular_residue_distance_max: int
    distance_minus_complete_median: float
    distance_minus_complete_min: int
    distance_minus_complete_max: int


def prime_prefix_certificate_rows(
    values: Iterable[int],
    *,
    max_k: int = MAX_DEFAULT_FILTRATION_K,
    allow_large_k: bool = False,
) -> list[PrimePrefixCertificateRow]:
    """Return certificate-depth rows for exact complete-covering values."""
    summary_rows, _, covered_sets = prime_prefix_residue_filtration_data(
        max_k=max_k,
        birth_sample_limit=0,
        allow_large_k=allow_large_k,
    )
    checked_max_prime = summary_rows[-1].new_prime
    rows: list[PrimePrefixCertificateRow] = []
    for n in sorted(values):
        k_cert: int | None = None
        p_cert: int | None = None
        primorial_cert: int | None = None
        residue_cert: int | None = None
        for index, summary in enumerate(summary_rows):
            if summary.new_prime > n:
                break
            residue = n % summary.primorial
            if residue in covered_sets[index]:
                k_cert = summary.k
                p_cert = summary.new_prime
                primorial_cert = summary.primorial
                residue_cert = residue
                break

        status = (
            PREFIX_CERTIFICATE_STATUS
            if k_cert is not None
            else NO_PREFIX_CERTIFICATE_STATUS
        )
        rows.append(
            PrimePrefixCertificateRow(
                n=n,
                k_cert=k_cert,
                p_cert=p_cert,
                primorial_cert=primorial_cert,
                residue_cert=residue_cert,
                checked_max_k=max_k,
                checked_max_prime=checked_max_prime,
                certificate_status=status,
                mod210=n % 210,
                trivial_c4_certificate=k_cert == 4,
            )
        )
    return rows


def prime_prefix_certificate_rows_from_runs_csv(
    path: str | Path,
    *,
    max_k: int = MAX_DEFAULT_FILTRATION_K,
    allow_large_k: bool = False,
) -> list[PrimePrefixCertificateRow]:
    """Read complete-covering runs and classify every contained value."""
    runs = read_complete_covering_runs_csv(path)
    return prime_prefix_certificate_rows(
        values_from_runs(runs),
        max_k=max_k,
        allow_large_k=allow_large_k,
    )


def prime_prefix_certificate_summary_rows(
    rows: Iterable[PrimePrefixCertificateRow],
) -> list[PrimePrefixCertificateSummaryRow]:
    """Aggregate certificate rows by status and certificate depth."""
    row_values = list(rows)
    if not row_values:
        return []
    total = len(row_values)
    groups: dict[tuple[str, int | None, int | None], list[PrimePrefixCertificateRow]] = {}
    for row in row_values:
        groups.setdefault((row.certificate_status, row.k_cert, row.p_cert), []).append(row)

    def sort_key(item: tuple[tuple[str, int | None, int | None], list[PrimePrefixCertificateRow]]):
        (status, k_cert, p_cert), _ = item
        status_rank = 0 if status == PREFIX_CERTIFICATE_STATUS else 1
        return (status_rank, k_cert if k_cert is not None else 10**9, p_cert or 10**9)

    summary: list[PrimePrefixCertificateSummaryRow] = []
    for (status, k_cert, p_cert), group_rows in sorted(groups.items(), key=sort_key):
        ns = [row.n for row in group_rows]
        first = group_rows[0]
        summary.append(
            PrimePrefixCertificateSummaryRow(
                certificate_status=status,
                k_cert=k_cert,
                p_cert=p_cert,
                complete_count=len(group_rows),
                share_of_complete=len(group_rows) / total,
                min_n=min(ns),
                max_n=max(ns),
                checked_max_k=first.checked_max_k,
                checked_max_prime=first.checked_max_prime,
            )
        )
    return summary


def read_prime_prefix_certificate_csv(
    path: str | Path,
) -> list[PrimePrefixCertificateRow]:
    """Read certificate-depth rows from CSV."""
    rows: list[PrimePrefixCertificateRow] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                PrimePrefixCertificateRow(
                    n=int(row["n"]),
                    k_cert=_optional_int(row["k_cert"]),
                    p_cert=_optional_int(row["p_cert"]),
                    primorial_cert=_optional_int(row["primorial_cert"]),
                    residue_cert=_optional_int(row["residue_cert"]),
                    checked_max_k=int(row["checked_max_k"]),
                    checked_max_prime=int(row["checked_max_prime"]),
                    certificate_status=row["certificate_status"],
                    mod210=int(row["mod210"]),
                    trivial_c4_certificate=row["trivial_c4_certificate"] == "True",
                )
            )
    return rows


def prime_prefix_uncertified_residue_rows(
    certificate_rows: Iterable[PrimePrefixCertificateRow],
    *,
    max_k: int,
    allow_large_k: bool = False,
) -> list[PrimePrefixUncertifiedResidueRow]:
    """Profile rows without prefix certificates against the checked C_k set."""
    summary_rows, _, covered_sets = prime_prefix_residue_filtration_data(
        max_k=max_k,
        birth_sample_limit=0,
        allow_large_k=allow_large_k,
    )
    max_summary = summary_rows[-1]
    modulus = max_summary.primorial
    covered = sorted(covered_sets[-1])
    source_k_by_residue = _covered_source_depth_map(summary_rows, covered_sets)

    rows: list[PrimePrefixUncertifiedResidueRow] = []
    for certificate in certificate_rows:
        if certificate.certificate_status != NO_PREFIX_CERTIFICATE_STATUS:
            continue
        residue = certificate.n % modulus
        nearest_residue, distance = _nearest_circular_residue(residue, covered, modulus)
        nearest_source_k = source_k_by_residue[nearest_residue]
        nearest_source_prime = summary_rows[nearest_source_k - 1].new_prime
        rows.append(
            PrimePrefixUncertifiedResidueRow(
                n=certificate.n,
                checked_max_k=max_k,
                checked_max_prime=max_summary.new_prime,
                residue_modulus=modulus,
                residue=residue,
                mod210=certificate.n % 210,
                mod2310=certificate.n % 2310,
                nearest_covered_residue=nearest_residue,
                nearest_covered_source_k=nearest_source_k,
                nearest_covered_source_prime=nearest_source_prime,
                circular_residue_distance=distance,
                normalized_residue_distance=distance / modulus,
            )
        )
    return rows


def prime_prefix_uncertified_mod210_summary_rows(
    rows: Iterable[PrimePrefixUncertifiedResidueRow],
) -> list[PrimePrefixUncertifiedMod210SummaryRow]:
    """Summarize uncertified rows by modulo 210 class."""
    row_values = list(rows)
    total = len(row_values)
    groups: dict[int, list[PrimePrefixUncertifiedResidueRow]] = {}
    for row in row_values:
        groups.setdefault(row.mod210, []).append(row)

    summary: list[PrimePrefixUncertifiedMod210SummaryRow] = []
    for mod210, group_rows in sorted(
        groups.items(), key=lambda item: (-len(item[1]), item[0])
    ):
        distances = [row.circular_residue_distance for row in group_rows]
        sample = " ".join(str(n) for n in sorted(row.n for row in group_rows)[:10])
        summary.append(
            PrimePrefixUncertifiedMod210SummaryRow(
                mod210=mod210,
                uncertified_count=len(group_rows),
                share_of_uncertified=len(group_rows) / total if total else 0.0,
                nearest_distance_median=statistics.median(distances),
                nearest_distance_max=max(distances),
                sample_n=sample,
            )
        )
    return summary


def prime_prefix_uncertified_overall_summary_rows(
    rows: Iterable[PrimePrefixUncertifiedResidueRow],
) -> list[PrimePrefixUncertifiedOverallSummaryRow]:
    """Return scalar summary rows for uncertified residue profiling."""
    row_values = list(rows)
    if not row_values:
        return [
            PrimePrefixUncertifiedOverallSummaryRow("uncertified_count", "0"),
        ]
    distances = sorted(row.circular_residue_distance for row in row_values)
    return [
        PrimePrefixUncertifiedOverallSummaryRow("uncertified_count", str(len(row_values))),
        PrimePrefixUncertifiedOverallSummaryRow(
            "checked_max_k", str(row_values[0].checked_max_k)
        ),
        PrimePrefixUncertifiedOverallSummaryRow(
            "checked_max_prime", str(row_values[0].checked_max_prime)
        ),
        PrimePrefixUncertifiedOverallSummaryRow(
            "residue_modulus", str(row_values[0].residue_modulus)
        ),
        PrimePrefixUncertifiedOverallSummaryRow(
            "unique_mod210_count", str(len({row.mod210 for row in row_values}))
        ),
        PrimePrefixUncertifiedOverallSummaryRow(
            "nearest_distance_median", str(statistics.median(distances))
        ),
        PrimePrefixUncertifiedOverallSummaryRow(
            "nearest_distance_p90", str(_nearest_rank_quantile(distances, 0.9))
        ),
        PrimePrefixUncertifiedOverallSummaryRow(
            "nearest_distance_p99", str(_nearest_rank_quantile(distances, 0.99))
        ),
        PrimePrefixUncertifiedOverallSummaryRow(
            "nearest_distance_max", str(max(distances))
        ),
    ]


def read_prime_prefix_uncertified_residue_csv(
    path: str | Path,
) -> list[PrimePrefixUncertifiedResidueRow]:
    """Read uncertified residue profile rows from CSV."""
    rows: list[PrimePrefixUncertifiedResidueRow] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                PrimePrefixUncertifiedResidueRow(
                    n=int(row["n"]),
                    checked_max_k=int(row["checked_max_k"]),
                    checked_max_prime=int(row["checked_max_prime"]),
                    residue_modulus=int(row["residue_modulus"]),
                    residue=int(row["residue"]),
                    mod210=int(row["mod210"]),
                    mod2310=int(row["mod2310"]),
                    nearest_covered_residue=int(row["nearest_covered_residue"]),
                    nearest_covered_source_k=int(row["nearest_covered_source_k"]),
                    nearest_covered_source_prime=int(row["nearest_covered_source_prime"]),
                    circular_residue_distance=int(row["circular_residue_distance"]),
                    normalized_residue_distance=float(row["normalized_residue_distance"]),
                )
            )
    return rows


def read_prime_prefix_uncertified_matched_profile_csv(
    path: str | Path,
) -> list[PrimePrefixUncertifiedMatchedProfileRow]:
    """Read matched complete/control residue profile rows from CSV."""
    rows: list[PrimePrefixUncertifiedMatchedProfileRow] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                PrimePrefixUncertifiedMatchedProfileRow(
                    seed_n=int(row["seed_n"]),
                    cohort_role=row["cohort_role"],
                    n=int(row["n"]),
                    control_delta=int(row["control_delta"]),
                    checked_max_k=int(row["checked_max_k"]),
                    checked_max_prime=int(row["checked_max_prime"]),
                    residue_modulus=int(row["residue_modulus"]),
                    residue=int(row["residue"]),
                    mod210=int(row["mod210"]),
                    mod2310=int(row["mod2310"]),
                    nearest_covered_residue=int(row["nearest_covered_residue"]),
                    nearest_covered_source_k=int(row["nearest_covered_source_k"]),
                    nearest_covered_source_prime=int(row["nearest_covered_source_prime"]),
                    circular_residue_distance=int(row["circular_residue_distance"]),
                    normalized_residue_distance=float(row["normalized_residue_distance"]),
                )
            )
    return rows


def read_prime_prefix_uncertified_mod210_audit_csv(
    path: str | Path,
) -> list[PrimePrefixUncertifiedMod210AuditRow]:
    """Read modulo-210 paired audit rows from CSV."""
    rows: list[PrimePrefixUncertifiedMod210AuditRow] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                PrimePrefixUncertifiedMod210AuditRow(
                    control_role=row["control_role"],
                    seed_mod210=int(row["seed_mod210"]),
                    pair_count=int(row["pair_count"]),
                    complete_distance_median=float(row["complete_distance_median"]),
                    control_distance_median=float(row["control_distance_median"]),
                    median_delta_complete_minus_control=float(
                        row["median_delta_complete_minus_control"]
                    ),
                    complete_smaller_count=int(row["complete_smaller_count"]),
                    complete_larger_count=int(row["complete_larger_count"]),
                    tie_count=int(row["tie_count"]),
                    complete_smaller_rate=float(row["complete_smaller_rate"]),
                    complete_larger_rate=float(row["complete_larger_rate"]),
                    sample_seed_n=row["sample_seed_n"],
                )
            )
    return rows


def read_prime_prefix_uncertified_mod210_class_review_csv(
    path: str | Path,
) -> list[PrimePrefixUncertifiedMod210ClassReviewRow]:
    """Read pivoted modulo-210 class review rows from CSV."""
    rows: list[PrimePrefixUncertifiedMod210ClassReviewRow] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                PrimePrefixUncertifiedMod210ClassReviewRow(
                    seed_mod210=int(row["seed_mod210"]),
                    max_pair_count=int(row["max_pair_count"]),
                    local_mod210_pair_count=_optional_int(row["local_mod210_pair_count"]),
                    local_any_pair_count=_optional_int(row["local_any_pair_count"]),
                    local_mod210_median_delta=_optional_float(
                        row["local_mod210_median_delta"]
                    ),
                    local_any_median_delta=_optional_float(
                        row["local_any_median_delta"]
                    ),
                    median_delta_difference_any_minus_mod210=_optional_float(
                        row["median_delta_difference_any_minus_mod210"]
                    ),
                    local_mod210_complete_smaller_rate=_optional_float(
                        row["local_mod210_complete_smaller_rate"]
                    ),
                    local_any_complete_smaller_rate=_optional_float(
                        row["local_any_complete_smaller_rate"]
                    ),
                    smaller_rate_difference_any_minus_mod210=_optional_float(
                        row["smaller_rate_difference_any_minus_mod210"]
                    ),
                    local_mod210_complete_larger_rate=_optional_float(
                        row["local_mod210_complete_larger_rate"]
                    ),
                    local_any_complete_larger_rate=_optional_float(
                        row["local_any_complete_larger_rate"]
                    ),
                    direction_label=row["direction_label"],
                    priority_label=row["priority_label"],
                    sample_seed_n=row["sample_seed_n"],
                )
            )
    return rows


def read_prime_prefix_uncertified_mod210_class_detail_csv(
    path: str | Path,
) -> list[PrimePrefixUncertifiedMod210ClassDetailRow]:
    """Read selected modulo-210 class detail rows from CSV."""
    rows: list[PrimePrefixUncertifiedMod210ClassDetailRow] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                PrimePrefixUncertifiedMod210ClassDetailRow(
                    selected_rank=int(row["selected_rank"]),
                    seed_mod210=int(row["seed_mod210"]),
                    priority_label=row["priority_label"],
                    direction_label=row["direction_label"],
                    seed_n=int(row["seed_n"]),
                    cohort_role=row["cohort_role"],
                    n=int(row["n"]),
                    control_delta=int(row["control_delta"]),
                    row_mod210=int(row["row_mod210"]),
                    residue=int(row["residue"]),
                    nearest_covered_residue=int(row["nearest_covered_residue"]),
                    nearest_covered_source_k=int(row["nearest_covered_source_k"]),
                    nearest_covered_source_prime=int(
                        row["nearest_covered_source_prime"]
                    ),
                    circular_residue_distance=int(row["circular_residue_distance"]),
                    complete_circular_residue_distance=int(
                        row["complete_circular_residue_distance"]
                    ),
                    distance_minus_complete=int(row["distance_minus_complete"]),
                    normalized_residue_distance=float(row["normalized_residue_distance"]),
                )
            )
    return rows


def prime_prefix_uncertified_matched_profile_rows(
    uncertified_rows: Iterable[PrimePrefixUncertifiedResidueRow],
    *,
    complete_values: set[int],
    start: int = 2,
    stop: int = 1_000_000,
    local_radius: int = 250,
    max_k: int = 8,
    allow_large_k: bool = False,
) -> list[PrimePrefixUncertifiedMatchedProfileRow]:
    """Build complete/control residue profiles for uncertified complete values."""
    if start < 2:
        raise ValueError("start must be >= 2")
    if stop < start:
        raise ValueError("stop must be >= start")
    if local_radius < 0:
        raise ValueError("local_radius must be >= 0")

    summary_rows, _, covered_sets = prime_prefix_residue_filtration_data(
        max_k=max_k,
        birth_sample_limit=0,
        allow_large_k=allow_large_k,
    )
    max_summary = summary_rows[-1]
    covered = sorted(covered_sets[-1])
    source_k_by_residue = _covered_source_depth_map(summary_rows, covered_sets)

    rows: list[PrimePrefixUncertifiedMatchedProfileRow] = []
    for uncertified in sorted(uncertified_rows, key=lambda row: row.n):
        candidate_values = [
            ("complete_uncertified", uncertified.n),
            (
                "local_mod210_control",
                _nearest_noncomplete_control(
                    uncertified.n,
                    complete_values=complete_values,
                    start=start,
                    stop=stop,
                    local_radius=local_radius,
                    predicate=lambda n, seed=uncertified.n: n % 210 == seed % 210,
                ),
            ),
            (
                "local_any_control",
                _nearest_noncomplete_control(
                    uncertified.n,
                    complete_values=complete_values,
                    start=start,
                    stop=stop,
                    local_radius=local_radius,
                    predicate=lambda _n: True,
                ),
            ),
        ]
        for role, n in candidate_values:
            if n is None:
                continue
            rows.append(
                _matched_profile_row(
                    seed_n=uncertified.n,
                    role=role,
                    n=n,
                    max_summary=max_summary,
                    covered=covered,
                    source_k_by_residue=source_k_by_residue,
                    summary_rows=summary_rows,
                )
            )
    return rows


def prime_prefix_uncertified_matched_profile_rows_from_csv(
    uncertified_profile_csv: str | Path,
    complete_runs_csv: str | Path,
    *,
    start: int = 2,
    stop: int = 1_000_000,
    local_radius: int = 250,
    max_k: int = 8,
    allow_large_k: bool = False,
) -> list[PrimePrefixUncertifiedMatchedProfileRow]:
    """Read inputs and build matched complete/control residue profile rows."""
    complete_values = set(values_from_runs(read_complete_covering_runs_csv(complete_runs_csv)))
    return prime_prefix_uncertified_matched_profile_rows(
        read_prime_prefix_uncertified_residue_csv(uncertified_profile_csv),
        complete_values=complete_values,
        start=start,
        stop=stop,
        local_radius=local_radius,
        max_k=max_k,
        allow_large_k=allow_large_k,
    )


def prime_prefix_uncertified_matched_summary_rows(
    rows: Iterable[PrimePrefixUncertifiedMatchedProfileRow],
) -> list[PrimePrefixUncertifiedMatchedSummaryRow]:
    """Summarize matched residue profile rows by cohort role."""
    row_values = list(rows)
    groups: dict[str, list[PrimePrefixUncertifiedMatchedProfileRow]] = {}
    for row in row_values:
        groups.setdefault(row.cohort_role, []).append(row)

    role_order = {
        "complete_uncertified": 0,
        "local_mod210_control": 1,
        "local_any_control": 2,
    }
    summary: list[PrimePrefixUncertifiedMatchedSummaryRow] = []
    for role, group_rows in sorted(groups.items(), key=lambda item: role_order.get(item[0], 99)):
        distances = sorted(row.circular_residue_distance for row in group_rows)
        summary.append(
            PrimePrefixUncertifiedMatchedSummaryRow(
                cohort_role=role,
                row_count=len(group_rows),
                unique_n_count=len({row.n for row in group_rows}),
                unique_mod210_count=len({row.mod210 for row in group_rows}),
                nearest_distance_median=statistics.median(distances),
                nearest_distance_p90=_nearest_rank_quantile(distances, 0.9),
                nearest_distance_p99=_nearest_rank_quantile(distances, 0.99),
                nearest_distance_max=max(distances),
            )
        )
    return summary


def prime_prefix_uncertified_matched_pair_delta_rows(
    rows: Iterable[PrimePrefixUncertifiedMatchedProfileRow],
) -> list[PrimePrefixUncertifiedMatchedPairDeltaRow]:
    """Return paired deltas for complete versus matched controls."""
    by_seed_role = {(row.seed_n, row.cohort_role): row for row in rows}
    deltas: list[PrimePrefixUncertifiedMatchedPairDeltaRow] = []
    for (seed_n, role), control in sorted(by_seed_role.items()):
        if role == "complete_uncertified":
            continue
        complete = by_seed_role.get((seed_n, "complete_uncertified"))
        if complete is None:
            continue
        for metric in ("circular_residue_distance", "normalized_residue_distance"):
            complete_value = float(getattr(complete, metric))
            control_value = float(getattr(control, metric))
            deltas.append(
                PrimePrefixUncertifiedMatchedPairDeltaRow(
                    seed_n=seed_n,
                    control_role=role,
                    complete_n=complete.n,
                    control_n=control.n,
                    metric=metric,
                    complete_value=complete_value,
                    control_value=control_value,
                    delta_complete_minus_control=complete_value - control_value,
                )
            )
    return deltas


def prime_prefix_uncertified_mod210_audit_rows(
    rows: Iterable[PrimePrefixUncertifiedMatchedProfileRow],
) -> list[PrimePrefixUncertifiedMod210AuditRow]:
    """Return mod-210 paired distance audit rows for each control role."""
    by_seed_role = {(row.seed_n, row.cohort_role): row for row in rows}
    groups: dict[tuple[str, int], list[tuple[PrimePrefixUncertifiedMatchedProfileRow, PrimePrefixUncertifiedMatchedProfileRow]]] = {}
    for (seed_n, role), control in by_seed_role.items():
        if role == "complete_uncertified":
            continue
        complete = by_seed_role.get((seed_n, "complete_uncertified"))
        if complete is None:
            continue
        groups.setdefault((role, complete.mod210), []).append((complete, control))

    audit_rows: list[PrimePrefixUncertifiedMod210AuditRow] = []
    for (role, mod210), pairs in sorted(
        groups.items(), key=lambda item: (-len(item[1]), item[0][0], item[0][1])
    ):
        complete_distances = [complete.circular_residue_distance for complete, _ in pairs]
        control_distances = [control.circular_residue_distance for _, control in pairs]
        deltas = [
            complete.circular_residue_distance - control.circular_residue_distance
            for complete, control in pairs
        ]
        smaller = sum(delta < 0 for delta in deltas)
        larger = sum(delta > 0 for delta in deltas)
        ties = sum(delta == 0 for delta in deltas)
        sample = " ".join(str(seed) for seed in sorted(complete.seed_n for complete, _ in pairs)[:10])
        audit_rows.append(
            PrimePrefixUncertifiedMod210AuditRow(
                control_role=role,
                seed_mod210=mod210,
                pair_count=len(pairs),
                complete_distance_median=statistics.median(complete_distances),
                control_distance_median=statistics.median(control_distances),
                median_delta_complete_minus_control=statistics.median(deltas),
                complete_smaller_count=smaller,
                complete_larger_count=larger,
                tie_count=ties,
                complete_smaller_rate=smaller / len(pairs),
                complete_larger_rate=larger / len(pairs),
                sample_seed_n=sample,
            )
        )
    return audit_rows


def prime_prefix_uncertified_source_depth_summary_rows(
    rows: Iterable[PrimePrefixUncertifiedMatchedProfileRow],
) -> list[PrimePrefixUncertifiedSourceDepthSummaryRow]:
    """Summarize nearest covered residue source depth by cohort role."""
    row_values = list(rows)
    role_counts: dict[str, int] = {}
    groups: dict[tuple[str, int, int], list[PrimePrefixUncertifiedMatchedProfileRow]] = {}
    for row in row_values:
        role_counts[row.cohort_role] = role_counts.get(row.cohort_role, 0) + 1
        key = (
            row.cohort_role,
            row.nearest_covered_source_k,
            row.nearest_covered_source_prime,
        )
        groups.setdefault(key, []).append(row)

    role_order = {
        "complete_uncertified": 0,
        "local_mod210_control": 1,
        "local_any_control": 2,
    }
    summary: list[PrimePrefixUncertifiedSourceDepthSummaryRow] = []
    for (role, source_k, source_prime), group_rows in sorted(
        groups.items(), key=lambda item: (role_order.get(item[0][0], 99), item[0][1])
    ):
        distances = [row.circular_residue_distance for row in group_rows]
        summary.append(
            PrimePrefixUncertifiedSourceDepthSummaryRow(
                cohort_role=role,
                nearest_covered_source_k=source_k,
                nearest_covered_source_prime=source_prime,
                row_count=len(group_rows),
                share_of_role=len(group_rows) / role_counts[role],
                nearest_distance_median=statistics.median(distances),
                nearest_distance_max=max(distances),
            )
        )
    return summary


def prime_prefix_uncertified_mod210_class_review_rows(
    audit_rows: Iterable[PrimePrefixUncertifiedMod210AuditRow],
) -> list[PrimePrefixUncertifiedMod210ClassReviewRow]:
    """Return pivoted review rows for choosing modulo-210 classes to inspect."""
    by_class_role = {(row.seed_mod210, row.control_role): row for row in audit_rows}
    seed_classes = sorted({seed_mod210 for seed_mod210, _ in by_class_role})
    rows: list[PrimePrefixUncertifiedMod210ClassReviewRow] = []
    for seed_mod210 in seed_classes:
        mod210_row = by_class_role.get((seed_mod210, "local_mod210_control"))
        any_row = by_class_role.get((seed_mod210, "local_any_control"))
        max_pair_count = max(
            row.pair_count for row in (mod210_row, any_row) if row is not None
        )
        mod210_delta = (
            mod210_row.median_delta_complete_minus_control
            if mod210_row is not None
            else None
        )
        any_delta = (
            any_row.median_delta_complete_minus_control if any_row is not None else None
        )
        median_delta_difference = (
            any_delta - mod210_delta
            if mod210_delta is not None and any_delta is not None
            else None
        )
        mod210_smaller_rate = (
            mod210_row.complete_smaller_rate if mod210_row is not None else None
        )
        any_smaller_rate = any_row.complete_smaller_rate if any_row is not None else None
        smaller_rate_difference = (
            any_smaller_rate - mod210_smaller_rate
            if mod210_smaller_rate is not None and any_smaller_rate is not None
            else None
        )
        direction_label = _class_direction_label(mod210_delta, any_delta)
        priority_label = _class_priority_label(
            max_pair_count=max_pair_count,
            direction_label=direction_label,
            median_delta_difference=median_delta_difference,
            smaller_rate_difference=smaller_rate_difference,
        )
        sample_source = any_row or mod210_row
        rows.append(
            PrimePrefixUncertifiedMod210ClassReviewRow(
                seed_mod210=seed_mod210,
                max_pair_count=max_pair_count,
                local_mod210_pair_count=(
                    mod210_row.pair_count if mod210_row is not None else None
                ),
                local_any_pair_count=any_row.pair_count if any_row is not None else None,
                local_mod210_median_delta=mod210_delta,
                local_any_median_delta=any_delta,
                median_delta_difference_any_minus_mod210=median_delta_difference,
                local_mod210_complete_smaller_rate=mod210_smaller_rate,
                local_any_complete_smaller_rate=any_smaller_rate,
                smaller_rate_difference_any_minus_mod210=smaller_rate_difference,
                local_mod210_complete_larger_rate=(
                    mod210_row.complete_larger_rate if mod210_row is not None else None
                ),
                local_any_complete_larger_rate=(
                    any_row.complete_larger_rate if any_row is not None else None
                ),
                direction_label=direction_label,
                priority_label=priority_label,
                sample_seed_n=sample_source.sample_seed_n if sample_source else "",
            )
        )
    return sorted(
        rows,
        key=lambda row: (
            _priority_rank(row.priority_label),
            -row.max_pair_count,
            -abs(row.median_delta_difference_any_minus_mod210 or 0.0),
            row.seed_mod210,
        ),
    )


def prime_prefix_uncertified_mod210_class_detail_rows(
    profile_rows: Iterable[PrimePrefixUncertifiedMatchedProfileRow],
    class_review_rows: Iterable[PrimePrefixUncertifiedMod210ClassReviewRow],
    *,
    class_limit: int = 8,
    selected_mod210: Iterable[int] | None = None,
) -> list[PrimePrefixUncertifiedMod210ClassDetailRow]:
    """Expand selected modulo-210 classes to their seed/control profile rows."""
    if class_limit < 1:
        raise ValueError("class_limit must be >= 1")
    review_values = list(class_review_rows)
    review_by_class = {row.seed_mod210: row for row in review_values}
    selected_classes = (
        list(dict.fromkeys(selected_mod210))
        if selected_mod210 is not None
        else [row.seed_mod210 for row in review_values[:class_limit]]
    )
    rank_by_class = {seed_mod210: index + 1 for index, seed_mod210 in enumerate(selected_classes)}
    selected_set = set(selected_classes)

    profile_values = [
        row for row in profile_rows if row.seed_n % 210 in selected_set
    ]
    by_seed_role = {(row.seed_n, row.cohort_role): row for row in profile_values}
    role_order = {
        "complete_uncertified": 0,
        "local_mod210_control": 1,
        "local_any_control": 2,
    }
    detail_rows: list[PrimePrefixUncertifiedMod210ClassDetailRow] = []
    for row in sorted(
        profile_values,
        key=lambda item: (
            rank_by_class[item.seed_n % 210],
            item.seed_n,
            role_order.get(item.cohort_role, 99),
            item.n,
        ),
    ):
        seed_mod210 = row.seed_n % 210
        review = review_by_class.get(seed_mod210)
        complete = by_seed_role.get((row.seed_n, "complete_uncertified"))
        if complete is None:
            continue
        detail_rows.append(
            PrimePrefixUncertifiedMod210ClassDetailRow(
                selected_rank=rank_by_class[seed_mod210],
                seed_mod210=seed_mod210,
                priority_label=review.priority_label if review else "",
                direction_label=review.direction_label if review else "",
                seed_n=row.seed_n,
                cohort_role=row.cohort_role,
                n=row.n,
                control_delta=row.control_delta,
                row_mod210=row.mod210,
                residue=row.residue,
                nearest_covered_residue=row.nearest_covered_residue,
                nearest_covered_source_k=row.nearest_covered_source_k,
                nearest_covered_source_prime=row.nearest_covered_source_prime,
                circular_residue_distance=row.circular_residue_distance,
                complete_circular_residue_distance=complete.circular_residue_distance,
                distance_minus_complete=(
                    row.circular_residue_distance - complete.circular_residue_distance
                ),
                normalized_residue_distance=row.normalized_residue_distance,
            )
        )
    return detail_rows


def prime_prefix_uncertified_mod210_class_source_summary_rows(
    detail_rows: Iterable[PrimePrefixUncertifiedMod210ClassDetailRow],
) -> list[PrimePrefixUncertifiedMod210ClassSourceSummaryRow]:
    """Summarize selected modulo-210 detail rows by source depth."""
    row_values = list(detail_rows)
    role_totals: dict[tuple[int, str], int] = {}
    groups: dict[
        tuple[int, int, str, str, str, int, int],
        list[PrimePrefixUncertifiedMod210ClassDetailRow],
    ] = {}
    for row in row_values:
        role_totals[(row.seed_mod210, row.cohort_role)] = (
            role_totals.get((row.seed_mod210, row.cohort_role), 0) + 1
        )
        key = (
            row.seed_mod210,
            row.selected_rank,
            row.priority_label,
            row.direction_label,
            row.cohort_role,
            row.nearest_covered_source_k,
            row.nearest_covered_source_prime,
        )
        groups.setdefault(key, []).append(row)

    role_order = {
        "complete_uncertified": 0,
        "local_mod210_control": 1,
        "local_any_control": 2,
    }
    summary: list[PrimePrefixUncertifiedMod210ClassSourceSummaryRow] = []
    for (
        seed_mod210,
        selected_rank,
        priority_label,
        direction_label,
        role,
        source_k,
        source_prime,
    ), group_rows in sorted(
        groups.items(),
        key=lambda item: (
            item[0][1],
            item[0][0],
            role_order.get(item[0][4], 99),
            item[0][5],
        ),
    ):
        distances = sorted(row.circular_residue_distance for row in group_rows)
        deltas = sorted(row.distance_minus_complete for row in group_rows)
        summary.append(
            PrimePrefixUncertifiedMod210ClassSourceSummaryRow(
                seed_mod210=seed_mod210,
                selected_rank=selected_rank,
                priority_label=priority_label,
                direction_label=direction_label,
                cohort_role=role,
                nearest_covered_source_k=source_k,
                nearest_covered_source_prime=source_prime,
                row_count=len(group_rows),
                share_within_class_role=(
                    len(group_rows) / role_totals[(seed_mod210, role)]
                ),
                circular_residue_distance_median=statistics.median(distances),
                circular_residue_distance_p90=_nearest_rank_quantile(distances, 0.9),
                circular_residue_distance_max=max(distances),
                distance_minus_complete_median=statistics.median(deltas),
                distance_minus_complete_min=min(deltas),
                distance_minus_complete_max=max(deltas),
            )
        )
    return summary


def write_prime_prefix_certificate_csv(
    rows: Iterable[PrimePrefixCertificateRow],
    output_path: str | Path,
) -> None:
    """Write certificate-depth rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixCertificateRow)


def write_prime_prefix_certificate_summary_csv(
    rows: Iterable[PrimePrefixCertificateSummaryRow],
    output_path: str | Path,
) -> None:
    """Write certificate-depth summary rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixCertificateSummaryRow)


def write_prime_prefix_uncertified_residue_csv(
    rows: Iterable[PrimePrefixUncertifiedResidueRow],
    output_path: str | Path,
) -> None:
    """Write uncertified residue profile rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixUncertifiedResidueRow)


def write_prime_prefix_uncertified_mod210_summary_csv(
    rows: Iterable[PrimePrefixUncertifiedMod210SummaryRow],
    output_path: str | Path,
) -> None:
    """Write modulo-210 uncertified summary rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixUncertifiedMod210SummaryRow)


def write_prime_prefix_uncertified_overall_summary_csv(
    rows: Iterable[PrimePrefixUncertifiedOverallSummaryRow],
    output_path: str | Path,
) -> None:
    """Write overall uncertified summary rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixUncertifiedOverallSummaryRow)


def write_prime_prefix_uncertified_matched_profile_csv(
    rows: Iterable[PrimePrefixUncertifiedMatchedProfileRow],
    output_path: str | Path,
) -> None:
    """Write matched residue profile rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixUncertifiedMatchedProfileRow)


def write_prime_prefix_uncertified_matched_summary_csv(
    rows: Iterable[PrimePrefixUncertifiedMatchedSummaryRow],
    output_path: str | Path,
) -> None:
    """Write matched residue profile summary rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixUncertifiedMatchedSummaryRow)


def write_prime_prefix_uncertified_matched_pair_delta_csv(
    rows: Iterable[PrimePrefixUncertifiedMatchedPairDeltaRow],
    output_path: str | Path,
) -> None:
    """Write matched residue profile pair deltas as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixUncertifiedMatchedPairDeltaRow)


def write_prime_prefix_uncertified_mod210_audit_csv(
    rows: Iterable[PrimePrefixUncertifiedMod210AuditRow],
    output_path: str | Path,
) -> None:
    """Write mod-210 paired audit rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixUncertifiedMod210AuditRow)


def write_prime_prefix_uncertified_source_depth_summary_csv(
    rows: Iterable[PrimePrefixUncertifiedSourceDepthSummaryRow],
    output_path: str | Path,
) -> None:
    """Write source-depth summary rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixUncertifiedSourceDepthSummaryRow)


def write_prime_prefix_uncertified_mod210_class_review_csv(
    rows: Iterable[PrimePrefixUncertifiedMod210ClassReviewRow],
    output_path: str | Path,
) -> None:
    """Write pivoted modulo-210 class review rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixUncertifiedMod210ClassReviewRow)


def write_prime_prefix_uncertified_mod210_class_detail_csv(
    rows: Iterable[PrimePrefixUncertifiedMod210ClassDetailRow],
    output_path: str | Path,
) -> None:
    """Write selected modulo-210 class detail rows as CSV."""
    _write_dataclass_csv(rows, output_path, PrimePrefixUncertifiedMod210ClassDetailRow)


def write_prime_prefix_uncertified_mod210_class_source_summary_csv(
    rows: Iterable[PrimePrefixUncertifiedMod210ClassSourceSummaryRow],
    output_path: str | Path,
) -> None:
    """Write selected class source-depth summary rows as CSV."""
    _write_dataclass_csv(
        rows,
        output_path,
        PrimePrefixUncertifiedMod210ClassSourceSummaryRow,
    )


def _optional_int(value: str) -> int | None:
    return int(value) if value else None


def _optional_float(value: str) -> float | None:
    return float(value) if value else None


def _matched_profile_row(
    *,
    seed_n: int,
    role: str,
    n: int,
    max_summary: PrimePrefixResidueFiltrationRow,
    covered: list[int],
    source_k_by_residue: dict[int, int],
    summary_rows: list[PrimePrefixResidueFiltrationRow],
) -> PrimePrefixUncertifiedMatchedProfileRow:
    modulus = max_summary.primorial
    residue = n % modulus
    nearest_residue, distance = _nearest_circular_residue(residue, covered, modulus)
    nearest_source_k = source_k_by_residue[nearest_residue]
    nearest_source_prime = summary_rows[nearest_source_k - 1].new_prime
    return PrimePrefixUncertifiedMatchedProfileRow(
        seed_n=seed_n,
        cohort_role=role,
        n=n,
        control_delta=n - seed_n,
        checked_max_k=max_summary.k,
        checked_max_prime=max_summary.new_prime,
        residue_modulus=modulus,
        residue=residue,
        mod210=n % 210,
        mod2310=n % 2310,
        nearest_covered_residue=nearest_residue,
        nearest_covered_source_k=nearest_source_k,
        nearest_covered_source_prime=nearest_source_prime,
        circular_residue_distance=distance,
        normalized_residue_distance=distance / modulus,
    )


def _nearest_noncomplete_control(
    seed_n: int,
    *,
    complete_values: set[int],
    start: int,
    stop: int,
    local_radius: int,
    predicate: Callable[[int], bool],
) -> int | None:
    candidates = (
        n
        for n in range(max(start, seed_n - local_radius), min(stop, seed_n + local_radius) + 1)
        if n != seed_n and n not in complete_values and predicate(n)
    )
    return min(candidates, key=lambda n: (abs(n - seed_n), n), default=None)


def _covered_source_depth_map(
    summary_rows: list[PrimePrefixResidueFiltrationRow],
    covered_sets: list[set[int]],
) -> dict[int, int]:
    max_modulus = summary_rows[-1].primorial
    source: dict[int, int] = {}
    for residue in sorted(covered_sets[-1]):
        for index, summary in enumerate(summary_rows):
            primorial = summary.primorial
            if residue % primorial in covered_sets[index]:
                source[residue] = index + 1
                break
        else:
            raise ValueError(f"covered residue missing source depth modulo {max_modulus}")
    return source


def _nearest_circular_residue(
    residue: int,
    sorted_residues: list[int],
    modulus: int,
) -> tuple[int, int]:
    if not sorted_residues:
        raise ValueError("sorted_residues must not be empty")
    index = bisect_left(sorted_residues, residue)
    candidates = [
        sorted_residues[index % len(sorted_residues)],
        sorted_residues[index - 1],
    ]
    nearest = min(candidates, key=lambda candidate: (_circular_distance(residue, candidate, modulus), candidate))
    return nearest, _circular_distance(residue, nearest, modulus)


def _circular_distance(left: int, right: int, modulus: int) -> int:
    distance = abs(left - right)
    return min(distance, modulus - distance)


def _nearest_rank_quantile(values: list[int], q: float) -> int:
    if not values:
        return 0
    index = min(len(values) - 1, max(0, int(q * (len(values) - 1))))
    return values[index]


def _delta_sign(value: float | None) -> str:
    if value is None:
        return "missing"
    if value < 0:
        return "complete_smaller"
    if value > 0:
        return "complete_larger"
    return "tied"


def _class_direction_label(
    mod210_delta: float | None,
    any_delta: float | None,
) -> str:
    mod210_sign = _delta_sign(mod210_delta)
    any_sign = _delta_sign(any_delta)
    if mod210_sign == any_sign:
        return mod210_sign
    return f"mod210_{mod210_sign}__any_{any_sign}"


def _class_priority_label(
    *,
    max_pair_count: int,
    direction_label: str,
    median_delta_difference: float | None,
    smaller_rate_difference: float | None,
) -> str:
    high_count = max_pair_count >= 100
    large_delta_gap = (
        median_delta_difference is not None and abs(median_delta_difference) >= 5
    )
    large_rate_gap = (
        smaller_rate_difference is not None and abs(smaller_rate_difference) >= 0.2
    )
    if high_count and "__" in direction_label:
        return "large_class_mixed_direction"
    if high_count and (large_delta_gap or large_rate_gap):
        return "large_class_large_control_gap"
    if high_count:
        return "large_class_baseline"
    if "__" in direction_label:
        return "small_class_mixed_direction"
    return "small_class"


def _priority_rank(label: str) -> int:
    order = {
        "large_class_mixed_direction": 0,
        "large_class_large_control_gap": 1,
        "large_class_baseline": 2,
        "small_class_mixed_direction": 3,
        "small_class": 4,
    }
    return order.get(label, 99)


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
