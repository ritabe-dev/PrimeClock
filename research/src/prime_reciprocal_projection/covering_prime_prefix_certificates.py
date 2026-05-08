"""Certificate-depth diagnostics for PRC prime-prefix residue filtrations."""

from __future__ import annotations

import csv
import statistics
from bisect import bisect_left
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .covering_prime_prefix_filtration import (
    MAX_DEFAULT_FILTRATION_K,
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


def _optional_int(value: str) -> int | None:
    return int(value) if value else None


def _covered_source_depth_map(
    summary_rows: list[object],
    covered_sets: list[set[int]],
) -> dict[int, int]:
    max_modulus = summary_rows[-1].primorial  # type: ignore[attr-defined]
    source: dict[int, int] = {}
    for residue in sorted(covered_sets[-1]):
        for index, summary in enumerate(summary_rows):
            primorial = summary.primorial  # type: ignore[attr-defined]
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
