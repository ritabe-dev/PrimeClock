"""Certificate-depth diagnostics for PRC prime-prefix residue filtrations."""

from __future__ import annotations

import csv
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
