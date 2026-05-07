"""Limit and finite-N density models for PRP."""

from __future__ import annotations

import math

from .projection import validate_n


def _validate_unit_interval(x: float) -> float:
    if not 0 <= x < 1:
        raise ValueError("x must be in [0, 1)")
    return float(x)


def rho(x: float, *, k_max: int = 10000) -> float:
    """Approximate ``rho(x) = sum_{k>=1} 1/(k+x)^2``.

    The truncation error is bounded above by roughly ``1 / (k_max + x)``.
    """
    x = _validate_unit_interval(x)
    if k_max < 1:
        raise ValueError("k_max must be >= 1")
    return sum(1.0 / ((k + x) ** 2) for k in range(1, k_max + 1))


def rho_bin_mass(left: float, right: float, *, k_max: int = 10000) -> float:
    """Approximate ``int_left^right rho(x) dx`` for ``0 <= left <= right <= 1``."""
    if not 0 <= left <= right <= 1:
        raise ValueError("bin endpoints must satisfy 0 <= left <= right <= 1")
    if k_max < 1:
        raise ValueError("k_max must be >= 1")
    return sum((1.0 / (k + left)) - (1.0 / (k + right)) for k in range(1, k_max + 1))


def rho_n_pnt(n: int, x: float, *, k_max: int | None = None, normalize_grid: int = 256) -> float:
    """Finite-N PNT density model, normalized numerically on ``[0, 1)``.

    This is a model, not a theorem:

    ``sum N / ((k+x)^2 log(N/(k+x)))``, clipped to ``N/(k+x) >= 2``.
    """
    n = validate_n(n)
    x = _validate_unit_interval(x)
    if normalize_grid < 16:
        raise ValueError("normalize_grid must be >= 16")
    max_possible_k = max(1, int(n / 2))
    max_k = min(20000, max_possible_k) if k_max is None else min(k_max, max_possible_k)

    def raw(point: float) -> float:
        total = 0.0
        for k in range(1, max_k + 1):
            y = k + point
            if n / y < 2:
                break
            total += n / ((y**2) * math.log(n / y))
        return total

    # Midpoint normalization avoids evaluating the half-open endpoint x=1.
    norm = sum(raw((index + 0.5) / normalize_grid) for index in range(normalize_grid))
    norm /= normalize_grid
    if norm == 0:
        return 0.0
    return raw(x) / norm


def rho_integral_midpoint(*, samples: int = 2000, k_max: int = 10000) -> float:
    """Numerically integrate ``rho`` over ``[0, 1)`` by midpoint rule."""
    if samples < 1:
        raise ValueError("samples must be >= 1")
    return sum(rho((index + 0.5) / samples, k_max=k_max) for index in range(samples)) / samples
