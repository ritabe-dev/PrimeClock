"""Source-only helpers for the PRC v2.4 B5 transition pilot."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Sequence

EXPERIMENT_DIR = Path(__file__).resolve().parent

if TYPE_CHECKING:
    from tools import BirthDynamicsRow


DEFAULT_B5_TRANSITION_PILOT_CSV = (
    EXPERIMENT_DIR
    / "data"
    / "prc_v2_4_b5_gap_close_transition_pilot_v0_1.csv"
)
DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV = (
    EXPERIMENT_DIR
    / "data"
    / "prc_v2_4_b5_to_b6_full_transition_graph_v0_1.csv"
)
DEFAULT_B7_BIRTH_PARENT_TRANSITION_PROBE_CSV = (
    EXPERIMENT_DIR
    / "data"
    / "prc_v2_4_b7_birth_parent_transition_probe_v0_1.csv"
)
DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV = (
    EXPERIMENT_DIR
    / "data"
    / "prc_v2_4_b6_to_b7_full_transition_graph_v0_1.csv"
)

ZERO_RESIDUAL_STATE = "zero_residual_state"
TRANSITION_MISS = "miss"
TRANSITION_TRIM = "trim"
TRANSITION_SPLIT = "split"
TRANSITION_PARTIAL_CLOSE = "partial_close"
TRANSITION_CLOSE_TO_ZERO = "close_to_zero"
TRANSITION_CLOSE = "close"
REFINED_SIMPLE_TRIM = "simple_trim"
REFINED_MIXED = "mixed"
REFINED_COMPONENT_SPLIT = "component_split"
REFINED_MULTI_TRIM = "multi_trim"
REFINED_MULTI_PARTIAL_CLOSE = "multi_partial_close"
REFINED_COMPONENT_PRESERVING_TRIM = REFINED_MULTI_TRIM
TRANSITION_TAXONOMY_LABELS = (
    TRANSITION_MISS,
    TRANSITION_TRIM,
    TRANSITION_SPLIT,
    TRANSITION_PARTIAL_CLOSE,
    TRANSITION_CLOSE_TO_ZERO,
)

ExactInterval = tuple[Fraction, Fraction]


@dataclass(frozen=True)
class CircularComponent:
    """One open residual component on R/Z, represented by non-wrapping pieces."""

    segments: tuple[ExactInterval, ...]


@dataclass(frozen=True)
class B5GapCloseTransitionPilotRow:
    parent_k: int
    child_k: int
    parent_modulus: int
    child_modulus: int
    parent_residue: int
    child_residue: int
    new_prime: int
    new_prime_remainder: int
    old_gap_count: int
    old_gap_boundary_endpoints: str
    new_prime_closed_arc_boundary_endpoints: str
    closed_gap_count: int
    remaining_gap_count: int
    remaining_gap_boundary_endpoints: str
    transition_type: str
    is_b5_birth: bool


TransitionProbeRow = B5GapCloseTransitionPilotRow


@dataclass(frozen=True)
class ComponentTransitionStats:
    old_component_count: int
    new_component_count: int
    component_delta: int
    touched_component_count: int
    closed_component_count: int


@dataclass(frozen=True)
class B5GapCloseTransitionPilotSummary:
    total_rows: int
    parent_count: int
    child_count: int
    close_count: int
    not_close_count: int
    birth_count: int
    birth_close_count: int
    birth_remaining_zero_count: int
    non_birth_close_count: int
    canonical_miss_count: int
    canonical_trim_count: int
    canonical_split_count: int
    canonical_partial_close_count: int
    canonical_close_count: int
    trim_component_delta_zero_count: int
    trim_component_delta_positive_count: int
    close_to_zero_count: int
    partial_close_count: int
    trim_count: int
    split_count: int
    miss_count: int
    close_to_zero_reflection_pair_count: int
    close_aperture_family_count: int
    simple_trim_count: int
    mixed_count: int
    component_split_count: int
    multi_trim_count: int
    multi_partial_close_count: int
    component_preserving_trim_count: int


def read_b5_gap_close_transition_pilot_csv(
    path: str | Path = DEFAULT_B5_TRANSITION_PILOT_CSV,
) -> list[B5GapCloseTransitionPilotRow]:
    """Read the source-only v2.4 B5 gap-close transition pilot CSV."""
    int_fields = {
        "parent_k",
        "child_k",
        "parent_modulus",
        "child_modulus",
        "parent_residue",
        "child_residue",
        "new_prime",
        "new_prime_remainder",
        "old_gap_count",
        "closed_gap_count",
        "remaining_gap_count",
    }
    rows: list[B5GapCloseTransitionPilotRow] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for raw_row in csv.DictReader(handle):
            values = {
                key: int(value) if key in int_fields else value
                for key, value in raw_row.items()
            }
            values["is_b5_birth"] = raw_row["is_b5_birth"] == "True"
            rows.append(B5GapCloseTransitionPilotRow(**values))
    return rows


def write_transition_rows_csv(
    rows: Iterable[TransitionProbeRow],
    output_path: str | Path,
) -> None:
    """Write source-only transition rows with the shared probe schema."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(B5GapCloseTransitionPilotRow.__dataclass_fields__.keys())
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def b5_gap_close_transition_pilot_summary(
    rows: Iterable[B5GapCloseTransitionPilotRow],
) -> B5GapCloseTransitionPilotSummary:
    row_list = list(rows)
    birth_rows = [row for row in row_list if row.is_b5_birth]
    taxonomy_counts = transition_taxonomy_summary(row_list)
    canonical_counts = canonical_transition_summary(row_list)
    refined_counts = refined_transition_summary(row_list)
    close_to_zero_rows = [
        row
        for row in row_list
        if classify_canonical_transition(row) == TRANSITION_CLOSE
    ]
    trim_rows = [
        row for row in row_list if classify_canonical_transition(row) == TRANSITION_TRIM
    ]
    return B5GapCloseTransitionPilotSummary(
        total_rows=len(row_list),
        parent_count=len({row.parent_residue for row in row_list}),
        child_count=len({row.child_residue for row in row_list}),
        close_count=sum(row.transition_type == "close" for row in row_list),
        not_close_count=sum(row.transition_type == "not_close" for row in row_list),
        birth_count=len(birth_rows),
        birth_close_count=sum(row.transition_type == "close" for row in birth_rows),
        birth_remaining_zero_count=sum(row.remaining_gap_count == 0 for row in birth_rows),
        non_birth_close_count=sum(
            row.transition_type == "close" and not row.is_b5_birth for row in row_list
        ),
        canonical_miss_count=canonical_counts[TRANSITION_MISS],
        canonical_trim_count=canonical_counts[TRANSITION_TRIM],
        canonical_split_count=canonical_counts[TRANSITION_SPLIT],
        canonical_partial_close_count=canonical_counts[TRANSITION_PARTIAL_CLOSE],
        canonical_close_count=canonical_counts[TRANSITION_CLOSE],
        trim_component_delta_zero_count=sum(
            component_transition_stats(row).component_delta == 0 for row in trim_rows
        ),
        trim_component_delta_positive_count=sum(
            component_transition_stats(row).component_delta > 0 for row in trim_rows
        ),
        close_to_zero_count=taxonomy_counts[TRANSITION_CLOSE_TO_ZERO],
        partial_close_count=taxonomy_counts[TRANSITION_PARTIAL_CLOSE],
        trim_count=taxonomy_counts[TRANSITION_TRIM],
        split_count=taxonomy_counts[TRANSITION_SPLIT],
        miss_count=taxonomy_counts[TRANSITION_MISS],
        close_to_zero_reflection_pair_count=_reflection_pair_count(
            [row.parent_residue for row in close_to_zero_rows],
            modulus=row_list[0].parent_modulus if row_list else 1,
        ),
        close_aperture_family_count=len(
            {row.old_gap_boundary_endpoints for row in close_to_zero_rows}
        ),
        simple_trim_count=refined_counts[REFINED_SIMPLE_TRIM],
        mixed_count=refined_counts[REFINED_MIXED],
        component_split_count=refined_counts[REFINED_COMPONENT_SPLIT],
        multi_trim_count=refined_counts[REFINED_MULTI_TRIM],
        multi_partial_close_count=refined_counts[REFINED_MULTI_PARTIAL_CLOSE],
        component_preserving_trim_count=refined_counts[REFINED_MULTI_TRIM],
    )


def recompute_b5_transition_pilot_rows(
    birth_rows: Sequence["BirthDynamicsRow"] | None = None,
) -> list[B5GapCloseTransitionPilotRow]:
    """Recompute the source-only B5 transition pilot from exact helpers."""
    if str(EXPERIMENT_DIR) not in sys.path:
        sys.path.insert(0, str(EXPERIMENT_DIR))
    from tools import birth_dynamics_rows, first_primes, primorial

    child_k = 5
    parent_k = child_k - 1
    if birth_rows is None:
        birth_rows = birth_dynamics_rows(min_k=child_k, max_k=child_k)
    parent_modulus = primorial(first_primes(parent_k))
    return build_transition_rows(
        parent_k=parent_k,
        child_k=child_k,
        parent_residues=range(parent_modulus),
        birth_rows=birth_rows,
        uncovered_only=True,
    )

def build_transition_rows(
    *,
    parent_k: int,
    child_k: int,
    parent_residues: Iterable[int],
    birth_rows: Sequence["BirthDynamicsRow"],
    uncovered_only: bool = True,
) -> list[TransitionProbeRow]:
    """Build exact source-only transition rows for selected parent residues."""
    if child_k != parent_k + 1:
        raise ValueError("transition rows require child_k == parent_k + 1")
    if str(EXPERIMENT_DIR) not in sys.path:
        sys.path.insert(0, str(EXPERIMENT_DIR))
    from tools import (
        exact_arc_intervals_for_residue,
        first_primes,
        format_intervals,
        primorial,
        residue_uncovered_intervals,
    )

    parent_primes = first_primes(parent_k)
    child_primes = first_primes(child_k)
    new_prime = child_primes[-1]
    parent_modulus = primorial(parent_primes)
    child_modulus = primorial(child_primes)
    birth_keys = {
        (row.parent_residue_mod_previous, row.new_prime_remainder, row.residue)
        for row in birth_rows
        if row.k == child_k
    }

    rows: list[TransitionProbeRow] = []
    for parent_residue in sorted(set(parent_residues)):
        old_gaps = residue_uncovered_intervals(parent_residue, parent_primes)
        if not old_gaps:
            if uncovered_only:
                continue
            raise ValueError(f"parent residue is already covered: {parent_residue}")
        for lift_index in range(new_prime):
            child_residue = parent_residue + lift_index * parent_modulus
            new_arcs = exact_arc_intervals_for_residue(child_residue, new_prime)
            remaining_gaps = subtract_intervals(old_gaps, new_arcs)
            row = B5GapCloseTransitionPilotRow(
                parent_k=parent_k,
                child_k=child_k,
                parent_modulus=parent_modulus,
                child_modulus=child_modulus,
                parent_residue=parent_residue,
                child_residue=child_residue,
                new_prime=new_prime,
                new_prime_remainder=child_residue % new_prime,
                old_gap_count=len(old_gaps),
                old_gap_boundary_endpoints=format_intervals(old_gaps),
                new_prime_closed_arc_boundary_endpoints=format_intervals(new_arcs),
                closed_gap_count=0,
                remaining_gap_count=len(remaining_gaps),
                remaining_gap_boundary_endpoints=format_intervals(remaining_gaps),
                transition_type="close" if not remaining_gaps else "not_close",
                is_b5_birth=(
                    parent_residue,
                    child_residue % new_prime,
                    child_residue,
                )
                in birth_keys,
            )
            rows.append(_with_computed_closed_gap_count(row))
    return rows


def b5_to_b6_full_transition_rows(
    birth_rows: Sequence["BirthDynamicsRow"] | None = None,
) -> list[TransitionProbeRow]:
    """Build the source-only full B5->B6 transition graph rows."""
    if str(EXPERIMENT_DIR) not in sys.path:
        sys.path.insert(0, str(EXPERIMENT_DIR))
    from tools import birth_dynamics_rows, first_primes, primorial

    parent_k = 5
    child_k = 6
    if birth_rows is None:
        birth_rows = birth_dynamics_rows(min_k=child_k, max_k=child_k)
    parent_modulus = primorial(first_primes(parent_k))
    return build_transition_rows(
        parent_k=parent_k,
        child_k=child_k,
        parent_residues=range(parent_modulus),
        birth_rows=birth_rows,
        uncovered_only=True,
    )


def b6_birth_parent_transition_probe_rows(
    birth_rows: Sequence["BirthDynamicsRow"],
) -> list[TransitionProbeRow]:
    """Build the source-only B6 birth-parent neighborhood sanity probe rows."""
    b6_birth_rows = [row for row in birth_rows if row.k == 6]
    if not b6_birth_rows:
        raise ValueError("B6 birth rows are required for the v2.4 sanity probe")
    parent_residues = {row.parent_residue_mod_previous for row in b6_birth_rows}
    return build_transition_rows(
        parent_k=5,
        child_k=6,
        parent_residues=parent_residues,
        birth_rows=birth_rows,
        uncovered_only=False,
    )


def b7_birth_parent_transition_probe_rows(
    birth_rows: Sequence["BirthDynamicsRow"],
) -> list[TransitionProbeRow]:
    """Build the source-only B7 birth-parent neighborhood probe rows."""
    b7_birth_rows = [row for row in birth_rows if row.k == 7]
    if not b7_birth_rows:
        raise ValueError("B7 birth rows are required for the v2.4 probe")
    parent_residues = {row.parent_residue_mod_previous for row in b7_birth_rows}
    return build_transition_rows(
        parent_k=6,
        child_k=7,
        parent_residues=parent_residues,
        birth_rows=birth_rows,
        uncovered_only=False,
    )


def b6_to_b7_full_transition_rows(
    birth_rows: Sequence["BirthDynamicsRow"] | None = None,
) -> list[TransitionProbeRow]:
    """Build the source-only full B6->B7 transition graph rows."""
    if str(EXPERIMENT_DIR) not in sys.path:
        sys.path.insert(0, str(EXPERIMENT_DIR))
    from tools import birth_dynamics_rows, first_primes, primorial

    parent_k = 6
    child_k = 7
    if birth_rows is None:
        birth_rows = birth_dynamics_rows(min_k=child_k, max_k=child_k)
    parent_modulus = primorial(first_primes(parent_k))
    return build_transition_rows(
        parent_k=parent_k,
        child_k=child_k,
        parent_residues=range(parent_modulus),
        birth_rows=birth_rows,
        uncovered_only=True,
    )


def parse_interval_list(text: str) -> list[ExactInterval]:
    """Parse semicolon-separated exact intervals such as ``1/4-3/10``."""
    if not text:
        return []
    intervals: list[ExactInterval] = []
    for part in text.split(";"):
        if not part:
            continue
        start_text, end_text = part.split("-", maxsplit=1)
        intervals.append((Fraction(start_text), Fraction(end_text)))
    return intervals


def split_wrapped_intervals(intervals: Iterable[ExactInterval]) -> list[ExactInterval]:
    """Return non-wrapping representatives for intervals on R/Z."""
    split: list[ExactInterval] = []
    for start, end in intervals:
        if start < end:
            split.append((start, end))
        elif start > end:
            split.append((start, Fraction(1)))
            split.append((Fraction(0), end))
    return split


def circular_components(intervals: Iterable[ExactInterval]) -> list[CircularComponent]:
    """Normalize interval text pieces into circular components on R/Z.

    CSV rows use a cut at 0, so one circular component may appear as two pieces
    ending at 1 and starting at 0. This helper merges that representation before
    transition taxonomy checks use component counts.
    """
    pieces = sorted(split_wrapped_intervals(intervals), key=lambda item: item[0])
    if not pieces:
        return []
    components = [CircularComponent((piece,)) for piece in pieces]
    first = components[0]
    last = components[-1]
    if first.segments[0][0] == 0 and last.segments[-1][1] == 1:
        merged = CircularComponent(last.segments + first.segments)
        return [merged, *components[1:-1]]
    return components


def is_zero_residual_state(row: B5GapCloseTransitionPilotRow) -> bool:
    """Return whether a row has no residual open gaps after adding the new arc.

    This is the formal v2.4 ``zero-residual state``. It is not the same as a
    gap around the point 0 and is not the same as residue 0.
    """
    return row.remaining_gap_count == 0


def classify_canonical_transition(row: B5GapCloseTransitionPilotRow) -> str:
    """Return the v2.4 primary transition label from circular components."""
    stats = component_transition_stats(row)
    if stats.new_component_count == 0:
        return TRANSITION_CLOSE
    if stats.closed_component_count > 0:
        return TRANSITION_PARTIAL_CLOSE
    if stats.touched_component_count > 0:
        if stats.component_delta > 0:
            return TRANSITION_SPLIT
        return TRANSITION_TRIM
    return TRANSITION_MISS


def classify_transition(row: B5GapCloseTransitionPilotRow) -> str:
    """Classify a B5 pilot row using the computed v2.4 transition taxonomy."""
    canonical = classify_canonical_transition(row)
    if canonical == TRANSITION_CLOSE:
        return TRANSITION_CLOSE_TO_ZERO
    if canonical in {
        TRANSITION_MISS,
        TRANSITION_TRIM,
        TRANSITION_SPLIT,
        TRANSITION_PARTIAL_CLOSE,
    }:
        return canonical

    # Kept only as a compatibility fallback for older diagnostic paths.
    if is_zero_residual_state(row) and row.is_b5_birth:
        return TRANSITION_CLOSE_TO_ZERO
    if row.closed_gap_count > 0 and row.remaining_gap_count > 0:
        return TRANSITION_PARTIAL_CLOSE

    old_gaps = split_wrapped_intervals(
        parse_interval_list(row.old_gap_boundary_endpoints)
    )
    new_arcs = split_wrapped_intervals(
        parse_interval_list(row.new_prime_closed_arc_boundary_endpoints)
    )
    remaining_gaps = split_wrapped_intervals(
        parse_interval_list(row.remaining_gap_boundary_endpoints)
    )

    overlapped_old_gaps = [
        old_gap
        for old_gap in old_gaps
        if any(_positive_intersection(old_gap, new_arc) for new_arc in new_arcs)
    ]
    if not overlapped_old_gaps:
        return TRANSITION_MISS

    for old_gap in overlapped_old_gaps:
        inside_remaining = [
            remaining_gap
            for remaining_gap in remaining_gaps
            if _interval_contains(old_gap, remaining_gap)
        ]
        if len(inside_remaining) >= 2:
            return TRANSITION_SPLIT
    return TRANSITION_TRIM


def classify_refined_transition(row: B5GapCloseTransitionPilotRow) -> str:
    """Classify a row using circular-component transition definitions."""
    if is_zero_residual_state(row):
        return TRANSITION_CLOSE_TO_ZERO

    mapping = component_transition_mapping(row)
    old_components = mapping["old_components"]
    remaining_by_old = mapping["remaining_by_old"]
    overlapped_old_indexes = mapping["overlapped_old_indexes"]

    closed_old_indexes = {
        index
        for index in range(len(old_components))
        if len(remaining_by_old.get(index, ())) == 0
    }
    split_old_indexes = {
        index
        for index, remaining in remaining_by_old.items()
        if len(remaining) >= 2
    }
    changed_old_indexes = closed_old_indexes | split_old_indexes | overlapped_old_indexes

    if not overlapped_old_indexes:
        return TRANSITION_MISS
    if closed_old_indexes:
        if len(closed_old_indexes) == len(old_components):
            return TRANSITION_CLOSE_TO_ZERO
        if split_old_indexes or overlapped_old_indexes != closed_old_indexes:
            return REFINED_MIXED
        if len(closed_old_indexes) > 1:
            return REFINED_MULTI_PARTIAL_CLOSE
        return TRANSITION_PARTIAL_CLOSE
    if split_old_indexes:
        if len(changed_old_indexes) == 1:
            return REFINED_COMPONENT_SPLIT
        return REFINED_MIXED
    if len(overlapped_old_indexes) == 1 and _component_count_preserved(row):
        return REFINED_SIMPLE_TRIM
    if len(overlapped_old_indexes) > 1 and _component_count_preserved(row):
        return REFINED_MULTI_TRIM
    return REFINED_MIXED


def transition_taxonomy_summary(
    rows: Iterable[B5GapCloseTransitionPilotRow],
) -> Counter[str]:
    """Count computed taxonomy labels for source-only v2.4 B5 rows."""
    counts = Counter(classify_transition(row) for row in rows)
    for label in TRANSITION_TAXONOMY_LABELS:
        counts.setdefault(label, 0)
    return counts


def canonical_transition_summary(
    rows: Iterable[B5GapCloseTransitionPilotRow],
) -> Counter[str]:
    """Count the v2.4 primary transition labels."""
    labels = (
        TRANSITION_MISS,
        TRANSITION_TRIM,
        TRANSITION_SPLIT,
        TRANSITION_PARTIAL_CLOSE,
        TRANSITION_CLOSE,
    )
    counts = Counter(classify_canonical_transition(row) for row in rows)
    for label in labels:
        counts.setdefault(label, 0)
    return counts


def transition_row_key(row: B5GapCloseTransitionPilotRow) -> tuple[int, int, int]:
    """Return the stable key for comparing transition rows."""
    return (row.parent_residue, row.new_prime_remainder, row.child_residue)


def transition_row_geometry_signature(
    row: B5GapCloseTransitionPilotRow,
) -> tuple[object, ...]:
    """Return a canonical row signature for committed-vs-recomputed comparison."""
    stats = component_transition_stats(row)
    return (
        row.parent_k,
        row.child_k,
        row.parent_modulus,
        row.child_modulus,
        row.parent_residue,
        row.child_residue,
        row.new_prime,
        row.new_prime_remainder,
        _interval_component_signature(row.old_gap_boundary_endpoints),
        _interval_component_signature(row.new_prime_closed_arc_boundary_endpoints),
        _interval_component_signature(row.remaining_gap_boundary_endpoints),
        row.transition_type,
        row.is_b5_birth,
        classify_canonical_transition(row),
        stats.old_component_count,
        stats.new_component_count,
        stats.component_delta,
        stats.touched_component_count,
        stats.closed_component_count,
    )


def raw_gap_counts_match_intervals(row: B5GapCloseTransitionPilotRow) -> bool:
    """Return whether raw count fields match their interval text fields."""
    return (
        row.old_gap_count == len(parse_interval_list(row.old_gap_boundary_endpoints))
        and row.remaining_gap_count
        == len(parse_interval_list(row.remaining_gap_boundary_endpoints))
        and row.closed_gap_count == component_transition_stats(row).closed_component_count
    )


def refined_transition_summary(
    rows: Iterable[B5GapCloseTransitionPilotRow],
) -> Counter[str]:
    """Count refined circular-component taxonomy labels."""
    labels = (
        TRANSITION_MISS,
        REFINED_SIMPLE_TRIM,
        REFINED_MULTI_TRIM,
        REFINED_COMPONENT_SPLIT,
        TRANSITION_PARTIAL_CLOSE,
        REFINED_MULTI_PARTIAL_CLOSE,
        REFINED_MIXED,
        TRANSITION_CLOSE_TO_ZERO,
    )
    counts = Counter(classify_refined_transition(row) for row in rows)
    for label in labels:
        counts.setdefault(label, 0)
    return counts


def component_transition_mapping(
    row: B5GapCloseTransitionPilotRow,
) -> dict[str, object]:
    """Map old circular residual components to child components."""
    old_components = circular_components(
        parse_interval_list(row.old_gap_boundary_endpoints)
    )
    remaining_components = circular_components(
        parse_interval_list(row.remaining_gap_boundary_endpoints)
    )
    new_components = circular_components(
        parse_interval_list(row.new_prime_closed_arc_boundary_endpoints)
    )
    remaining_by_old: dict[int, tuple[int, ...]] = {}
    overlapped_old_indexes: set[int] = set()
    for old_index, old_component in enumerate(old_components):
        mapped_remaining = tuple(
            remaining_index
            for remaining_index, remaining_component in enumerate(remaining_components)
            if _component_contains(old_component, remaining_component)
        )
        if mapped_remaining:
            remaining_by_old[old_index] = mapped_remaining
        if any(
            _components_positive_intersection(old_component, new_component)
            for new_component in new_components
        ):
            overlapped_old_indexes.add(old_index)
    return {
        "old_components": old_components,
        "remaining_components": remaining_components,
        "new_components": new_components,
        "remaining_by_old": remaining_by_old,
        "overlapped_old_indexes": overlapped_old_indexes,
    }


def component_transition_stats(
    row: B5GapCloseTransitionPilotRow,
) -> ComponentTransitionStats:
    """Return structural attributes used alongside the primary taxonomy."""
    mapping = component_transition_mapping(row)
    old_components = mapping["old_components"]
    remaining_components = mapping["remaining_components"]
    remaining_by_old = mapping["remaining_by_old"]
    touched = mapping["overlapped_old_indexes"]
    old_count = len(old_components)
    new_count = len(remaining_components)
    closed_count = sum(
        1 for index in range(old_count) if len(remaining_by_old.get(index, ())) == 0
    )
    return ComponentTransitionStats(
        old_component_count=old_count,
        new_component_count=new_count,
        component_delta=new_count - old_count,
        touched_component_count=len(touched),
        closed_component_count=closed_count,
    )


def _with_computed_closed_gap_count(
    row: B5GapCloseTransitionPilotRow,
) -> B5GapCloseTransitionPilotRow:
    stats = component_transition_stats(row)
    return B5GapCloseTransitionPilotRow(
        **{
            **row.__dict__,
            "closed_gap_count": stats.closed_component_count,
        }
    )


def _interval_component_signature(text: str) -> tuple[tuple[ExactInterval, ...], ...]:
    components = circular_components(parse_interval_list(text))
    return tuple(
        tuple(sorted(component.segments, key=lambda interval: interval[0]))
        for component in sorted(
            components,
            key=lambda component: tuple(
                (segment[0], segment[1]) for segment in component.segments
            ),
        )
    )


def prime_zero_obstruction_holds(n: int, prefix_primes: Sequence[int]) -> bool:
    """Check the local prime-zero obstruction diagnostic.

    For a prime-like target ``n`` and a strict prefix of smaller primes, no
    prefix clock has remainder 0 at ``n``. Including ``n`` itself removes the
    obstruction.
    """
    return all(prime < n and n % prime != 0 for prime in prefix_primes)


def subtract_intervals(
    old_intervals: Iterable[ExactInterval],
    cover_intervals: Iterable[ExactInterval],
) -> list[ExactInterval]:
    """Subtract closed cover intervals from old open intervals using exact cuts."""
    remaining = split_wrapped_intervals(old_intervals)
    cover_segments = split_wrapped_intervals(cover_intervals)
    for cover_start, cover_end in cover_segments:
        next_remaining: list[ExactInterval] = []
        for start, end in remaining:
            if cover_end <= start or end <= cover_start:
                next_remaining.append((start, end))
                continue
            if start < cover_start:
                left = (start, min(cover_start, end))
                if left[0] < left[1]:
                    next_remaining.append(left)
            if cover_end < end:
                right = (max(cover_end, start), end)
                if right[0] < right[1]:
                    next_remaining.append(right)
        remaining = next_remaining
    return sorted(remaining, key=lambda interval: interval[0])


def _component_count_preserved(row: B5GapCloseTransitionPilotRow) -> bool:
    old_components = circular_components(
        parse_interval_list(row.old_gap_boundary_endpoints)
    )
    remaining_components = circular_components(
        parse_interval_list(row.remaining_gap_boundary_endpoints)
    )
    return len(old_components) == len(remaining_components)


def _positive_intersection(left: ExactInterval, right: ExactInterval) -> bool:
    return max(left[0], right[0]) < min(left[1], right[1])


def _interval_contains(container: ExactInterval, candidate: ExactInterval) -> bool:
    return container[0] <= candidate[0] and candidate[1] <= container[1]


def _component_contains(
    container: CircularComponent,
    candidate: CircularComponent,
) -> bool:
    return all(
        any(_interval_contains(container_segment, candidate_segment) for container_segment in container.segments)
        for candidate_segment in candidate.segments
    )


def _components_positive_intersection(
    left: CircularComponent,
    right: CircularComponent,
) -> bool:
    return any(
        _positive_intersection(left_segment, right_segment)
        for left_segment in left.segments
        for right_segment in right.segments
    )


def _reflection_pair_count(residues: Sequence[int], *, modulus: int) -> int:
    pairs = {
        tuple(sorted((residue % modulus, (-residue) % modulus)))
        for residue in residues
    }
    return len(pairs)
