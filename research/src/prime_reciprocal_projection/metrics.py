"""Convergence metrics for PRP experiments."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .branches import branch_decomposition, limit_branch_mass
from .experiments import histogram_masses, ks_distance, limit_bin_masses, limit_cdf
from .fourier import fourier_coefficient, limit_fourier_coefficient
from .projection import fractional_parts, validate_n


@dataclass(frozen=True)
class ConvergenceRow:
    """One convergence summary row for a fixed N."""

    n: int
    prime_count: int
    hist_l1: float
    ks_distance: float
    branch_l1_k1_20: float
    branch_max_k1_20: float
    fourier_mean_m1_20: float
    fourier_max_m1_20: float
    fourier_max_mode_m1_20: int


def convergence_row(
    n: int,
    *,
    bins: int = 100,
    max_branch_k: int = 20,
    max_fourier_m: int = 20,
    fourier_samples: int = 256,
    fourier_k_max: int = 500,
) -> ConvergenceRow:
    """Compute v0 convergence metrics for one integer N."""
    n = validate_n(n)
    values = fractional_parts(n)
    _, empirical = histogram_masses(values, bins=bins)
    _, limit = limit_bin_masses(bins=bins)
    hist_l1 = sum(abs(a - b) for a, b in zip(empirical, limit))
    ks = ks_distance(values, limit_cdf)

    branches = {branch.k: branch for branch in branch_decomposition(n, max_k=max_branch_k)}
    branch_errors = [
        abs((branches[k].mass if k in branches else 0.0) - limit_branch_mass(k))
        for k in range(1, max_branch_k + 1)
    ]
    branch_l1 = sum(branch_errors)
    branch_max = max(branch_errors) if branch_errors else 0.0

    fourier_residuals = [
        abs(
            fourier_coefficient(n, m)
            - limit_fourier_coefficient(m, samples=fourier_samples, k_max=fourier_k_max)
        )
        for m in range(1, max_fourier_m + 1)
    ]
    fourier_max = max(fourier_residuals) if fourier_residuals else 0.0
    fourier_max_mode = fourier_residuals.index(fourier_max) + 1 if fourier_residuals else 0

    return ConvergenceRow(
        n=n,
        prime_count=len(values),
        hist_l1=hist_l1,
        ks_distance=ks,
        branch_l1_k1_20=branch_l1,
        branch_max_k1_20=branch_max,
        fourier_mean_m1_20=sum(fourier_residuals) / len(fourier_residuals),
        fourier_max_m1_20=fourier_max,
        fourier_max_mode_m1_20=fourier_max_mode,
    )


def convergence_table(ns: list[int]) -> list[ConvergenceRow]:
    """Compute convergence rows for a list of N values."""
    return [convergence_row(n) for n in ns]


def write_convergence_csv(rows: list[ConvergenceRow], output_path: str | Path) -> None:
    """Write convergence rows as CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(ConvergenceRow.__dataclass_fields__.keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})
