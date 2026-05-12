"""Source-only sibling-lift and itinerary controls for PRC v2.4."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

from tools import (
    birth_dynamics_rows,
    exact_arc_intervals_for_residue,
    first_primes,
    format_fraction,
    format_intervals,
    interval_length,
    primorial,
    residue_uncovered_intervals,
)
from v2_4_transition_pilot import (
    DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV,
    DEFAULT_B5_TRANSITION_PILOT_CSV,
    DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV,
    B5GapCloseTransitionPilotRow,
    TransitionProbeRow,
    build_transition_rows,
    canonical_transition_summary,
    circular_components,
    classify_canonical_transition,
    component_transition_stats,
    parse_interval_list,
    read_b5_gap_close_transition_pilot_csv,
)

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_SIBLING_LIFT_CONTROLS_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_sibling_lift_phase_controls_v0_1.csv"
)
DEFAULT_TRANSITION_ITINERARY_CONTROLS_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_transition_itinerary_controls_v0_1.csv"
)


@dataclass(frozen=True)
class SiblingLiftPhaseControlRow:
    scope: str
    parent_k: int
    child_k: int
    parent_residue: int
    new_prime: int
    old_component_count: int
    old_uncovered_measure: str
    close_lift_count: int
    birth_lift_count: int
    nonbirth_close_count: int
    close_remainders: str
    miss_count: int
    trim_count: int
    split_count: int
    partial_close_count: int
    nonclose_count: int


@dataclass(frozen=True)
class TransitionItineraryControlRow:
    scope: str
    birth_parent_residue: int
    child_residue: int
    new_prime_remainder: int
    is_birth: bool
    is_close: bool
    final_transition_label: str
    transition_sequence: str
    component_delta_sequence: str
    phase_remainder_sequence: str


def build_sibling_lift_phase_control_rows() -> list[SiblingLiftPhaseControlRow]:
    """Summarize final-prime sibling lift families for B5/B6/B7 scopes."""
    scoped_rows = [
        (
            "B4_to_B5_full",
            read_b5_gap_close_transition_pilot_csv(DEFAULT_B5_TRANSITION_PILOT_CSV),
        ),
        (
            "B5_to_B6_full",
            read_b5_gap_close_transition_pilot_csv(DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV),
        ),
        (
            "B6_to_B7_full",
            read_b5_gap_close_transition_pilot_csv(DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV),
        ),
    ]
    controls: list[SiblingLiftPhaseControlRow] = []
    for scope, rows in scoped_rows:
        by_parent: dict[int, list[TransitionProbeRow]] = {}
        for row in rows:
            by_parent.setdefault(row.parent_residue, []).append(row)
        for parent_residue in sorted(by_parent):
            controls.append(_sibling_lift_control_row(scope, by_parent[parent_residue]))
    return controls


def _sibling_lift_control_row(
    scope: str,
    rows: Sequence[TransitionProbeRow],
) -> SiblingLiftPhaseControlRow:
    first = rows[0]
    old_intervals = parse_interval_list(first.old_gap_boundary_endpoints)
    old_measure = sum(interval_length(interval) for interval in old_intervals)
    taxonomy = canonical_transition_summary(rows)
    close_rows = [
        row for row in rows if classify_canonical_transition(row) == "close"
    ]
    birth_rows = [row for row in rows if row.is_b5_birth]
    return SiblingLiftPhaseControlRow(
        scope=scope,
        parent_k=first.parent_k,
        child_k=first.child_k,
        parent_residue=first.parent_residue,
        new_prime=first.new_prime,
        old_component_count=len(circular_components(old_intervals)),
        old_uncovered_measure=format_fraction(old_measure),
        close_lift_count=len(close_rows),
        birth_lift_count=len(birth_rows),
        nonbirth_close_count=sum(not row.is_b5_birth for row in close_rows),
        close_remainders=";".join(
            str(row.new_prime_remainder) for row in sorted(close_rows, key=_row_sort_key)
        ),
        miss_count=taxonomy["miss"],
        trim_count=taxonomy["trim"],
        split_count=taxonomy["split"],
        partial_close_count=taxonomy["partial_close"],
        nonclose_count=len(rows) - len(close_rows),
    )


def build_transition_itinerary_control_rows() -> list[TransitionItineraryControlRow]:
    """Build sibling-lift itineraries for checked B5/B6/B7 birth-parent families."""
    birth_rows = birth_dynamics_rows(min_k=5, max_k=7)
    rows: list[TransitionItineraryControlRow] = []
    for child_k in (5, 6, 7):
        scope = f"B{child_k}_birth_parent_siblings"
        scoped_birth_rows = [row for row in birth_rows if row.k == child_k]
        sibling_rows = build_transition_rows(
            parent_k=child_k - 1,
            child_k=child_k,
            parent_residues={row.parent_residue_mod_previous for row in scoped_birth_rows},
            birth_rows=scoped_birth_rows,
            uncovered_only=False,
        )
        for sibling_row in sibling_rows:
            rows.append(_itinerary_control_row(scope, sibling_row))
    return rows


def _itinerary_control_row(
    scope: str,
    final_row: TransitionProbeRow,
) -> TransitionItineraryControlRow:
    labels: list[str] = []
    deltas: list[str] = []
    phases: list[str] = []
    previous_gaps: list[tuple[Fraction, Fraction]] | None = None
    previous_k = 0
    previous_modulus = 1
    previous_residue = 0
    for layer_k in range(1, final_row.child_k + 1):
        primes = first_primes(layer_k)
        layer_prime = primes[-1]
        layer_modulus = primorial(primes)
        layer_residue = final_row.child_residue % layer_modulus
        gaps = residue_uncovered_intervals(layer_residue, primes)
        if previous_gaps is None:
            labels.append("start")
            deltas.append("0")
        else:
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
                is_b5_birth=layer_k == final_row.child_k and final_row.is_b5_birth,
            )
            labels.append(classify_canonical_transition(transition_row))
            deltas.append(str(component_transition_stats(transition_row).component_delta))
        phases.append(str(layer_residue % layer_prime))
        previous_gaps = gaps
        previous_k = layer_k
        previous_modulus = layer_modulus
        previous_residue = layer_residue
    return TransitionItineraryControlRow(
        scope=scope,
        birth_parent_residue=final_row.parent_residue,
        child_residue=final_row.child_residue,
        new_prime_remainder=final_row.new_prime_remainder,
        is_birth=final_row.is_b5_birth,
        is_close=classify_canonical_transition(final_row) == "close",
        final_transition_label=classify_canonical_transition(final_row),
        transition_sequence=">".join(labels),
        component_delta_sequence=">".join(deltas),
        phase_remainder_sequence=">".join(phases),
    )


def write_nonbirth_control_csvs(
    *,
    sibling_path: str | Path = DEFAULT_SIBLING_LIFT_CONTROLS_CSV,
    itinerary_path: str | Path = DEFAULT_TRANSITION_ITINERARY_CONTROLS_CSV,
) -> None:
    write_dataclass_csv(
        build_sibling_lift_phase_control_rows(),
        sibling_path,
        SiblingLiftPhaseControlRow,
    )
    write_dataclass_csv(
        build_transition_itinerary_control_rows(),
        itinerary_path,
        TransitionItineraryControlRow,
    )


def read_sibling_lift_phase_control_csv(
    path: str | Path = DEFAULT_SIBLING_LIFT_CONTROLS_CSV,
) -> list[SiblingLiftPhaseControlRow]:
    return _read_dataclass_csv(path, SiblingLiftPhaseControlRow)


def read_transition_itinerary_control_csv(
    path: str | Path = DEFAULT_TRANSITION_ITINERARY_CONTROLS_CSV,
) -> list[TransitionItineraryControlRow]:
    return _read_dataclass_csv(path, TransitionItineraryControlRow)


def row_signature(row: object) -> tuple[object, ...]:
    return tuple(getattr(row, field) for field in row.__dataclass_fields__)


def write_dataclass_csv(rows: Iterable[object], output_path: str | Path, row_type: type) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(row_type.__dataclass_fields__.keys())
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def _read_dataclass_csv(path: str | Path, row_type: type):
    int_fields = {
        "parent_k",
        "child_k",
        "parent_residue",
        "new_prime",
        "old_component_count",
        "close_lift_count",
        "birth_lift_count",
        "nonbirth_close_count",
        "miss_count",
        "trim_count",
        "split_count",
        "partial_close_count",
        "nonclose_count",
        "birth_parent_residue",
        "child_residue",
        "new_prime_remainder",
    }
    bool_fields = {"is_birth", "is_close"}
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for raw_row in csv.DictReader(handle):
            values = dict(raw_row)
            for field in int_fields:
                if field in values:
                    values[field] = int(values[field])
            for field in bool_fields:
                if field in values:
                    values[field] = values[field] == "True"
            rows.append(row_type(**values))
    return rows


def _row_sort_key(row: TransitionProbeRow) -> tuple[int, int]:
    return (row.new_prime_remainder, row.child_residue)
