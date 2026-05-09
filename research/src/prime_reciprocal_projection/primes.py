"""Prime helpers for PRP experiments."""

from __future__ import annotations

import math


def is_prime(value: int) -> bool:
    """Return whether ``value`` is prime."""
    if value < 2:
        return False
    if value == 2:
        return True
    if value % 2 == 0:
        return False
    limit = math.isqrt(value)
    for factor in range(3, limit + 1, 2):
        if value % factor == 0:
            return False
    return True


def primes_up_to(limit: int) -> list[int]:
    """Return all primes ``p <= limit`` using an Eratosthenes sieve."""
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    root = math.isqrt(limit)
    for value in range(2, root + 1):
        if sieve[value]:
            start = value * value
            step = value
            sieve[start : limit + 1 : step] = b"\x00" * (((limit - start) // step) + 1)
    return [value for value in range(2, limit + 1) if sieve[value]]


def pi_count(limit: int) -> int:
    """Return ``pi(limit)``, the number of primes up to ``limit``."""
    return len(primes_up_to(limit))
