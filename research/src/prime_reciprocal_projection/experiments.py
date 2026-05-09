"""Reusable experiment helpers."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from .density import rho_bin_mass


def histogram_masses(values: Iterable[float], *, bins: int = 100) -> tuple[list[float], list[float]]:
    """Return equal-width bin edges and normalized bin masses."""
    if bins < 1:
        raise ValueError("bins must be >= 1")
    data = list(values)
    edges = [index / bins for index in range(bins + 1)]
    counts = [0] * bins
    for value in data:
        if not 0 <= value < 1:
            raise ValueError("histogram values must be in [0, 1)")
        index = min(bins - 1, int(value * bins))
        counts[index] += 1
    total = len(data)
    masses = [0.0 for _ in counts] if total == 0 else [count / total for count in counts]
    return edges, masses


def limit_bin_masses(*, bins: int = 100, k_max: int = 10000) -> tuple[list[float], list[float]]:
    """Return equal-width bin edges and limiting rho bin masses."""
    if bins < 1:
        raise ValueError("bins must be >= 1")
    edges = [index / bins for index in range(bins + 1)]
    masses = [
        rho_bin_mass(edges[index], edges[index + 1], k_max=k_max) for index in range(bins)
    ]
    total = sum(masses)
    return edges, [mass / total for mass in masses]


def ks_distance(values: Iterable[float], cdf: Callable[[float], float]) -> float:
    """Return a one-sample Kolmogorov-Smirnov style distance."""
    data = sorted(values)
    total = len(data)
    if total == 0:
        return 0.0
    distance = 0.0
    for index, value in enumerate(data, start=1):
        upper = index / total
        lower = (index - 1) / total
        target = cdf(value)
        distance = max(distance, abs(upper - target), abs(target - lower))
    return distance


def limit_cdf(x: float, *, k_max: int = 10000) -> float:
    """Approximate ``int_0^x rho(t) dt``."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return rho_bin_mass(0.0, x, k_max=k_max)
