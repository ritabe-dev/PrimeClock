"""Fourier diagnostics for empirical PRP measures."""

from __future__ import annotations

import cmath
import math

from .density import rho
from .projection import fractional_parts, validate_n


def fourier_coefficient(n: int, m: int) -> complex:
    """Return normalized empirical coefficient ``hat_mu_N(m)``."""
    validate_n(n)
    if not isinstance(m, int):
        raise TypeError("m must be an integer")
    values = fractional_parts(n)
    if not values:
        return 0j
    return sum(cmath.exp(-2j * math.pi * m * value) for value in values) / len(values)


def limit_fourier_coefficient(m: int, *, samples: int = 4096, k_max: int = 10000) -> complex:
    """Approximate ``int_0^1 rho(x) exp(-2*pi*i*m*x) dx``."""
    if not isinstance(m, int):
        raise TypeError("m must be an integer")
    if samples < 1:
        raise ValueError("samples must be >= 1")
    if m == 0:
        return 1 + 0j
    total = 0j
    for index in range(samples):
        x = (index + 0.5) / samples
        total += rho(x, k_max=k_max) * cmath.exp(-2j * math.pi * m * x)
    return total / samples
