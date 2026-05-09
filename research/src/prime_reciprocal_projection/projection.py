"""Projection map Phi_N(p) = {N / p}."""

from __future__ import annotations

import math
from collections.abc import Iterable

from .primes import primes_up_to


def validate_n(n: int) -> int:
    """Validate and normalize an integer N."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("N must be an integer")
    if n < 2:
        raise ValueError("N must be >= 2")
    return n


def phi(n: int, p: int) -> float:
    """Return ``Phi_N(p) = {N / p}`` in ``[0, 1)``."""
    validate_n(n)
    if p <= 0:
        raise ValueError("p must be positive")
    return (n % p) / p


def fractional_parts(n: int, primes: Iterable[int] | None = None) -> list[float]:
    """Return ``{N/p}`` for primes ``p <= N``.

    If ``primes`` is supplied, it is filtered to values ``p <= N`` but is not
    primality-checked. Callers that need primality guarantees should pass
    ``primes_up_to(N)`` or omit the argument.
    """
    n = validate_n(n)
    prime_values = primes_up_to(n) if primes is None else [p for p in primes if p <= n]
    return [phi(n, p) for p in prime_values]


def empirical_cdf(values: Iterable[float], x: float) -> float:
    """Return empirical CDF mass at ``x`` for values in ``[0, 1)``."""
    data = list(values)
    if not data:
        return 0.0
    return sum(1 for value in data if value <= x) / len(data)


def fractional_part(value: float) -> float:
    """Return the fractional part of a real value in ``[0, 1)``."""
    return value - math.floor(value)

