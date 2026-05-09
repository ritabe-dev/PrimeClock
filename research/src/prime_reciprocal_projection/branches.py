"""Branch decomposition for floor(N / p) = k."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .primes import primes_up_to
from .projection import validate_n


@dataclass(frozen=True)
class Branch:
    """One branch ``B_{N,k}`` in the PRP decomposition."""

    k: int
    count: int
    mass: float
    limit_mass: float


def limit_branch_mass(k: int) -> float:
    """Return the limiting branch mass ``1 / (k(k+1))``."""
    if k < 1:
        raise ValueError("k must be >= 1")
    return 1.0 / (k * (k + 1))


def branch_decomposition(n: int, *, max_k: int | None = None) -> list[Branch]:
    """Return exact branch counts for primes ``p <= N``.

    Branch ``k`` is ``N/(k+1) < p <= N/k``, equivalently
    ``floor(N/p) == k``.
    """
    n = validate_n(n)
    primes = primes_up_to(n)
    total = len(primes)
    counts: dict[int, int] = defaultdict(int)
    for p in primes:
        k = n // p
        if max_k is None or k <= max_k:
            counts[k] += 1
    return [
        Branch(k=k, count=count, mass=count / total, limit_mass=limit_branch_mass(k))
        for k, count in sorted(counts.items())
    ]

