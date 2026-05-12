"""Source-only helpers for PRC v2.4 early residual genealogy."""

from __future__ import annotations

import csv
import math
import sys
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_BIRTH_RESIDUAL_GENEALOGY_CSV = (
    EXPERIMENT_DIR
    / "data"
    / "prc_v2_4_birth_residual_genealogy_v0_1.csv"
)

if str(EXPERIMENT_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_DIR))

from tools import (  # noqa: E402
    BirthDynamicsRow,
    birth_dynamics_rows,
    exact_arc_intervals_for_residue,
    first_primes,
    format_fraction,
    format_intervals,
    primorial,
)
from prime_reciprocal_projection.covering_prime_prefix_filtration import (  # noqa: E402
    residue_uncovered_intervals,
    residue_uncovered_measure,
)
from v2_4_transition_pilot import (  # noqa: E402
    B5GapCloseTransitionPilotRow,
    TRANSITION_CLOSE,
    circular_components,
    classify_canonical_transition,
    component_transition_stats,
)


@dataclass(frozen=True)
class BirthResidualGenealogyRow:
    birth_k: int
    birth_residue: int
    birth_parent_residue: int
    birth_new_prime: int
    birth_new_prime_remainder: int
    layer_k: int
    layer_prime: int
    layer_modulus: int
    layer_residue: int
    residue_gcd_with_modulus: int
    zero_center_available: bool
    origin_component_present: bool
    residual_component_count: int
    uncovered_measure_fraction: str
    residual_component_endpoints: str
    transition_label: str
    transition_component_delta: int
    transition_touched_component_count: int
    transition_closed_component_count: int
    is_final_birth_layer: bool
    is_zero_residual_state: bool


def build_birth_residual_genealogy_rows(
    birth_rows: Sequence[BirthDynamicsRow] | None = None,
) -> list[BirthResidualGenealogyRow]:
    """Trace checked B5/B6/B7 birth residues back through all smaller prefixes."""
    if birth_rows is None:
        birth_rows = birth_dynamics_rows(min_k=5, max_k=7)
    rows: list[BirthResidualGenealogyRow] = []
    for birth_row in birth_rows:
        rows.extend(_birth_lineage_rows(birth_row))
    return rows


def _birth_lineage_rows(birth_row: BirthDynamicsRow) -> list[BirthResidualGenealogyRow]:
    rows: list[BirthResidualGenealogyRow] = []
    previous_gaps: list[tuple[Fraction, Fraction]] | None = None
    previous_k = 0
    previous_modulus = 1
    previous_residue = 0
    for layer_k in range(1, birth_row.k + 1):
        primes = first_primes(layer_k)
        layer_prime = primes[-1]
        layer_modulus = primorial(primes)
        layer_residue = birth_row.residue % layer_modulus
        gaps = residue_uncovered_intervals(layer_residue, primes)
        components = circular_components(gaps)
        transition_label = "start"
        transition_stats = None
        if previous_gaps is not None:
            transition_row = B5GapCloseTransitionPilotRow(
                parent_k=previous_k,
                child_k=layer_k,
                parent_modulus=previous_modulus,
                child_modulus=layer_modulus,
                parent_residue=previous_residue,
                child_residue=layer_residue,
                new_prime=layer_prime,
                new_prime_remainder=layer_residue % layer_prime,
                old_gap_count=len(previous_gaps),
                old_gap_boundary_endpoints=format_intervals(previous_gaps),
                new_prime_closed_arc_boundary_endpoints=format_intervals(
                    exact_arc_intervals_for_residue(layer_residue, layer_prime)
                ),
                closed_gap_count=0,
                remaining_gap_count=len(gaps),
                remaining_gap_boundary_endpoints=format_intervals(gaps),
                transition_type="close" if not gaps else "not_close",
                is_b5_birth=layer_k == birth_row.k,
            )
            transition_label = classify_canonical_transition(transition_row)
            transition_stats = component_transition_stats(transition_row)
        rows.append(
            BirthResidualGenealogyRow(
                birth_k=birth_row.k,
                birth_residue=birth_row.residue,
                birth_parent_residue=birth_row.parent_residue_mod_previous,
                birth_new_prime=birth_row.new_prime,
                birth_new_prime_remainder=birth_row.new_prime_remainder,
                layer_k=layer_k,
                layer_prime=layer_prime,
                layer_modulus=layer_modulus,
                layer_residue=layer_residue,
                residue_gcd_with_modulus=math.gcd(layer_residue, layer_modulus),
                zero_center_available=any(layer_residue % prime == 0 for prime in primes),
                origin_component_present=origin_component_present(components),
                residual_component_count=len(components),
                uncovered_measure_fraction=format_fraction(
                    residue_uncovered_measure(layer_residue, primes)
                ),
                residual_component_endpoints=format_intervals(gaps),
                transition_label=transition_label,
                transition_component_delta=(
                    0 if transition_stats is None else transition_stats.component_delta
                ),
                transition_touched_component_count=(
                    0 if transition_stats is None else transition_stats.touched_component_count
                ),
                transition_closed_component_count=(
                    0 if transition_stats is None else transition_stats.closed_component_count
                ),
                is_final_birth_layer=layer_k == birth_row.k,
                is_zero_residual_state=not gaps,
            )
        )
        previous_gaps = gaps
        previous_k = layer_k
        previous_modulus = layer_modulus
        previous_residue = layer_residue
    return rows


def origin_component_present(components: Iterable[object]) -> bool:
    """Return whether a circular residual component touches the cut point 0."""
    for component in components:
        for start, end in component.segments:
            if start == 0 or end == 1:
                return True
    return False


def read_birth_residual_genealogy_csv(
    path: str | Path = DEFAULT_BIRTH_RESIDUAL_GENEALOGY_CSV,
) -> list[BirthResidualGenealogyRow]:
    int_fields = {
        "birth_k",
        "birth_residue",
        "birth_parent_residue",
        "birth_new_prime",
        "birth_new_prime_remainder",
        "layer_k",
        "layer_prime",
        "layer_modulus",
        "layer_residue",
        "residue_gcd_with_modulus",
        "residual_component_count",
        "transition_component_delta",
        "transition_touched_component_count",
        "transition_closed_component_count",
    }
    bool_fields = {
        "zero_center_available",
        "origin_component_present",
        "is_final_birth_layer",
        "is_zero_residual_state",
    }
    rows: list[BirthResidualGenealogyRow] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for raw_row in csv.DictReader(handle):
            values = {
                key: int(value) if key in int_fields else value
                for key, value in raw_row.items()
            }
            for field in bool_fields:
                values[field] = raw_row[field] == "True"
            rows.append(BirthResidualGenealogyRow(**values))
    return rows


def write_birth_residual_genealogy_csv(
    rows: Iterable[BirthResidualGenealogyRow],
    output_path: str | Path,
) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(BirthResidualGenealogyRow.__dataclass_fields__.keys())
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def genealogy_row_key(row: BirthResidualGenealogyRow) -> tuple[int, int, int]:
    return (row.birth_k, row.birth_residue, row.layer_k)


def genealogy_row_signature(row: BirthResidualGenealogyRow) -> tuple[object, ...]:
    return tuple(getattr(row, field) for field in BirthResidualGenealogyRow.__dataclass_fields__)


def genealogy_transition_summary(rows: Iterable[BirthResidualGenealogyRow]) -> Counter[str]:
    return Counter(row.transition_label for row in rows)


def genealogy_layer_summary(
    rows: Iterable[BirthResidualGenealogyRow],
) -> Counter[tuple[int, int, str]]:
    return Counter((row.birth_k, row.layer_k, row.transition_label) for row in rows)


def final_birth_rows(
    rows: Iterable[BirthResidualGenealogyRow],
) -> list[BirthResidualGenealogyRow]:
    return [row for row in rows if row.is_final_birth_layer]


def prefinal_rows(
    rows: Iterable[BirthResidualGenealogyRow],
) -> list[BirthResidualGenealogyRow]:
    return [row for row in rows if not row.is_final_birth_layer]


def non_coprime_birth_count(rows: Iterable[BirthResidualGenealogyRow]) -> int:
    return sum(
        row.is_final_birth_layer and row.residue_gcd_with_modulus > 1
        for row in rows
    )


def close_transition_count(rows: Iterable[BirthResidualGenealogyRow]) -> int:
    return sum(row.transition_label == TRANSITION_CLOSE for row in rows)
