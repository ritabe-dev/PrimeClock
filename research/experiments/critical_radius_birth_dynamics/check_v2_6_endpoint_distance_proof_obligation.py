#!/usr/bin/env python3
"""Audit v2.6 endpoint-distance proof-obligation readiness."""

from __future__ import annotations

import subprocess
import sys
from fractions import Fraction
from pathlib import Path

from check_v2_6_special_point_obstruction import repo_root_from_script


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
NOTES_REL = EXPERIMENT_REL / "notes"

NOTE_REL = NOTES_REL / "prc_v2_6_endpoint_distance_proof_obligation_v0_1.md"
OBSTRUCTION_CHECK_REL = EXPERIMENT_REL / "check_v2_6_special_point_obstruction.py"
FORMALIZATION_CHECK_REL = EXPERIMENT_REL / "check_v2_6_special_point_lemma_formalization.py"

CHECKED_SCOPES = (
    ("B4_to_B5_full", 7, 11),
    ("B5_to_B6_full", 11, 13),
    ("B6_to_B7_full", 13, 17),
)
OLD_ODD_PRIMES = (3, 5, 7, 11, 13)

REQUIRED_SECTIONS = (
    "## Definitions",
    "## Endpoint Lattice Near 0",
    "## Endpoint Lattice Near 1/2",
    "## p=2 Boundary",
    "## Implication For Special q-arcs",
    "## Remaining Risks",
    "## Gate R Decision",
)
REQUIRED_PHRASES = (
    "q=p_{k+1}",
    "old prime prefix contain `2,3,...,p_k`",
    "odd residues over `2p`",
    "0/1 is only a cut representation",
    "1/(2p_k)",
    "1/p_k",
    "p=2",
    "half-circle boundary convention",
    "q>p_k",
    "proof_status=candidate",
    "public_theorem=defer",
    "b8_theorem=reject_for_v2_6_gate_r",
    "not public theorems",
    "general predictor",
    "asymptotic law",
)


def read_note(repo_root: Path, failures: list[str]) -> str:
    path = repo_root / NOTE_REL
    if not path.is_file():
        failures.append(f"missing endpoint-distance proof note: {NOTE_REL}")
        return ""
    return path.read_text(encoding="utf-8")


def require_note(repo_root: Path, failures: list[str]) -> None:
    text = read_note(repo_root, failures)
    normalized = " ".join(text.replace("`", "").split())
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"endpoint-distance note missing section {section}")
    for phrase in REQUIRED_PHRASES:
        normalized_phrase = " ".join(phrase.replace("`", "").split())
        if normalized_phrase not in normalized:
            failures.append(f"endpoint-distance note missing phrase {phrase!r}")


def odd_prime_endpoints(prime: int) -> list[Fraction]:
    return [Fraction(numerator, 2 * prime) for numerator in range(1, 2 * prime, 2)]


def circular_distance_to_zero(point: Fraction) -> Fraction:
    return min(point, Fraction(1) - point)


def require_endpoint_lattice_bounds(failures: list[str]) -> None:
    for scope, p_k, q in CHECKED_SCOPES:
        old_primes = [prime for prime in OLD_ODD_PRIMES if prime <= p_k]
        endpoints = [endpoint for prime in old_primes for endpoint in odd_prime_endpoints(prime)]

        near_zero = min(circular_distance_to_zero(endpoint) for endpoint in endpoints)
        expected_zero = Fraction(1, 2 * p_k)
        if near_zero != expected_zero:
            failures.append(
                f"{scope}: nearest endpoint to 0 was {near_zero}, expected {expected_zero}"
            )

        half = Fraction(1, 2)
        noncentral_endpoint_distances = [
            abs(endpoint - half) for endpoint in endpoints if endpoint != half
        ]
        near_half = min(noncentral_endpoint_distances)
        expected_half = Fraction(1, p_k)
        if near_half != expected_half:
            failures.append(
                f"{scope}: nearest endpoint to 1/2 was {near_half}, expected {expected_half}"
            )

        if not (Fraction(1, 2 * q) < expected_zero):
            failures.append(f"{scope}: 1/(2q) is not shorter than 1/(2p_k)")
        if not (Fraction(1, q) < expected_half):
            failures.append(f"{scope}: 1/q is not shorter than 1/p_k")


def require_checker_passes(repo_root: Path, relative_path: Path, failures: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, str(repo_root / relative_path)],
        cwd=repo_root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        failures.append(f"required checker failed: {relative_path}: {output}")


def main() -> int:
    repo_root = repo_root_from_script()
    failures: list[str] = []

    require_note(repo_root, failures)
    require_endpoint_lattice_bounds(failures)
    require_checker_passes(repo_root, OBSTRUCTION_CHECK_REL, failures)
    require_checker_passes(repo_root, FORMALIZATION_CHECK_REL, failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_6_endpoint_distance_proof_obligation: "
        "checks=8, failed=0, "
        "proof_status=candidate, public_theorem=defer, "
        "b8_theorem=reject_for_v2_6_gate_r"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
