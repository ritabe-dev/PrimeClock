"""Source-only independent phase-gate diagnostics for PRC v2.4."""

from __future__ import annotations

import csv
import os
import tempfile
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

from tools import (
    exact_arc_intervals_for_residue,
    format_fraction,
    interval_length,
)
from v2_4_transition_pilot import (
    DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV,
    DEFAULT_B5_TRANSITION_PILOT_CSV,
    DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV,
    TransitionProbeRow,
    circular_components,
    classify_canonical_transition,
    parse_interval_list,
    read_b5_gap_close_transition_pilot_csv,
)

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_PHASE_GATE_LIFT_DIAGNOSTICS_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_phase_gate_lift_diagnostics_v0_1.csv"
)
DEFAULT_PHASE_GATE_FAMILY_SUMMARY_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_phase_gate_family_summary_v0_1.csv"
)
DEFAULT_PHASE_GATE_MARGIN_RANK_FIGURE = (
    EXPERIMENT_DIR
    / "figures"
    / "v2_4"
    / "prc_v2_4_phase_gate_margin_rank_v0_1.png"
)


@dataclass(frozen=True)
class PhaseGateLiftDiagnosticRow:
    scope: str
    parent_k: int
    child_k: int
    parent_residue: int
    child_residue: int
    new_prime: int
    new_prime_remainder: int
    old_component_count: int
    old_uncovered_measure: str
    new_arc_width: str
    capacity_pass: bool
    phase_margin: str
    phase_pass: bool
    endpoint_touch: bool
    phase_rank_desc: int
    is_close: bool
    is_birth: bool


@dataclass(frozen=True)
class PhaseGateFamilySummaryRow:
    scope: str
    parent_residue: int
    new_prime: int
    old_component_count: int
    old_uncovered_measure: str
    capacity_pass: bool
    lift_count: int
    phase_pass_count: int
    close_lift_count: int
    birth_lift_count: int
    nonbirth_close_count: int
    phase_pass_remainders: str
    close_remainders: str
    top_phase_remainders: str
    best_phase_margin: str


def build_phase_gate_lift_diagnostic_rows() -> list[PhaseGateLiftDiagnosticRow]:
    """Return independent phase-gate rows for every scoped sibling lift."""
    rows: list[PhaseGateLiftDiagnosticRow] = []
    for scope, transition_rows in _scoped_transition_rows():
        by_parent: dict[int, list[TransitionProbeRow]] = {}
        for row in transition_rows:
            by_parent.setdefault(row.parent_residue, []).append(row)
        for parent_residue in sorted(by_parent):
            rows.extend(_lift_rows_for_family(scope, by_parent[parent_residue]))
    return rows


def build_phase_gate_family_summary_rows(
    lift_rows: Iterable[PhaseGateLiftDiagnosticRow] | None = None,
) -> list[PhaseGateFamilySummaryRow]:
    """Summarize independent phase-gate diagnostics by sibling family."""
    rows = list(lift_rows) if lift_rows is not None else build_phase_gate_lift_diagnostic_rows()
    by_family: dict[tuple[str, int], list[PhaseGateLiftDiagnosticRow]] = {}
    for row in rows:
        by_family.setdefault((row.scope, row.parent_residue), []).append(row)

    summaries: list[PhaseGateFamilySummaryRow] = []
    for key in sorted(by_family):
        family_rows = sorted(by_family[key], key=lambda row: row.new_prime_remainder)
        first = family_rows[0]
        phase_pass_rows = [row for row in family_rows if row.phase_pass]
        close_rows = [row for row in family_rows if row.is_close]
        top_margin = max(Fraction(row.phase_margin) for row in family_rows)
        top_rows = [
            row for row in family_rows if Fraction(row.phase_margin) == top_margin
        ]
        summaries.append(
            PhaseGateFamilySummaryRow(
                scope=first.scope,
                parent_residue=first.parent_residue,
                new_prime=first.new_prime,
                old_component_count=first.old_component_count,
                old_uncovered_measure=first.old_uncovered_measure,
                capacity_pass=first.capacity_pass,
                lift_count=len(family_rows),
                phase_pass_count=len(phase_pass_rows),
                close_lift_count=len(close_rows),
                birth_lift_count=sum(row.is_birth for row in family_rows),
                nonbirth_close_count=sum(row.is_close and not row.is_birth for row in family_rows),
                phase_pass_remainders=";".join(str(row.new_prime_remainder) for row in phase_pass_rows),
                close_remainders=";".join(str(row.new_prime_remainder) for row in close_rows),
                top_phase_remainders=";".join(str(row.new_prime_remainder) for row in top_rows),
                best_phase_margin=format_fraction(top_margin),
            )
        )
    return summaries


def write_phase_gate_artifacts(
    *,
    lift_path: str | Path = DEFAULT_PHASE_GATE_LIFT_DIAGNOSTICS_CSV,
    family_path: str | Path = DEFAULT_PHASE_GATE_FAMILY_SUMMARY_CSV,
    figure_path: str | Path = DEFAULT_PHASE_GATE_MARGIN_RANK_FIGURE,
) -> None:
    """Write source-only phase-gate CSVs and the margin-rank figure."""
    lift_rows = build_phase_gate_lift_diagnostic_rows()
    family_rows = build_phase_gate_family_summary_rows(lift_rows)
    write_dataclass_csv(lift_rows, lift_path, PhaseGateLiftDiagnosticRow)
    write_dataclass_csv(family_rows, family_path, PhaseGateFamilySummaryRow)
    write_phase_gate_margin_rank_figure(lift_rows, family_rows, figure_path)


def read_phase_gate_lift_diagnostics_csv(
    path: str | Path = DEFAULT_PHASE_GATE_LIFT_DIAGNOSTICS_CSV,
) -> list[PhaseGateLiftDiagnosticRow]:
    return _read_dataclass_csv(path, PhaseGateLiftDiagnosticRow)


def read_phase_gate_family_summary_csv(
    path: str | Path = DEFAULT_PHASE_GATE_FAMILY_SUMMARY_CSV,
) -> list[PhaseGateFamilySummaryRow]:
    return _read_dataclass_csv(path, PhaseGateFamilySummaryRow)


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


def write_phase_gate_margin_rank_figure(
    lift_rows: Sequence[PhaseGateLiftDiagnosticRow],
    family_rows: Sequence[PhaseGateFamilySummaryRow],
    output_path: str | Path,
) -> None:
    """Write a compact figure showing close ranks and capacity false positives."""
    if "MPLCONFIGDIR" not in os.environ:
        os.environ["MPLCONFIGDIR"] = str(
            Path(tempfile.gettempdir()) / "primeclock-matplotlib"
        )
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    close_ranks = Counter(row.phase_rank_desc for row in lift_rows if row.is_close)
    capacity_counts = Counter(
        "capacity+close"
        if row.capacity_pass and row.close_lift_count
        else "capacity+nonclose"
        if row.capacity_pass
        else "no capacity"
        for row in family_rows
    )

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), constrained_layout=True)
    rank_labels = sorted(close_ranks)
    axes[0].bar([str(rank) for rank in rank_labels], [close_ranks[rank] for rank in rank_labels], color="#1b7837")
    axes[0].set_title("Close lift phase-margin rank")
    axes[0].set_xlabel("rank within sibling family")
    axes[0].set_ylabel("close lifts")
    axes[0].grid(axis="y", alpha=0.25)

    labels = ["capacity+close", "capacity+nonclose", "no capacity"]
    axes[1].bar(labels, [capacity_counts[label] for label in labels], color=["#1b7837", "#e08214", "#777777"])
    axes[1].set_title("Capacity gate is not sufficient")
    axes[1].set_ylabel("families")
    axes[1].tick_params(axis="x", rotation=14)
    axes[1].grid(axis="y", alpha=0.25)
    fig.suptitle("PRC v2.4 independent phase-gate diagnostics")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def _lift_rows_for_family(
    scope: str,
    rows: Sequence[TransitionProbeRow],
) -> list[PhaseGateLiftDiagnosticRow]:
    ordered_rows = sorted(rows, key=lambda row: (row.new_prime_remainder, row.child_residue))
    first = ordered_rows[0]
    old_intervals = parse_interval_list(first.old_gap_boundary_endpoints)
    old_components = circular_components(old_intervals)
    old_measure = sum(interval_length(interval) for interval in old_intervals)
    new_arc_width = Fraction(1, first.new_prime)
    capacity_pass = len(old_components) == 1 and old_measure <= new_arc_width

    computed: list[tuple[TransitionProbeRow, Fraction]] = [
        (row, _phase_margin(row)) for row in ordered_rows
    ]
    margin_order = {
        (row.parent_residue, row.child_residue): index + 1
        for index, (row, _margin) in enumerate(
            sorted(
                computed,
                key=lambda item: (
                    -item[1],
                    item[0].new_prime_remainder,
                    item[0].child_residue,
                ),
            )
        )
    }
    return [
        PhaseGateLiftDiagnosticRow(
            scope=scope,
            parent_k=row.parent_k,
            child_k=row.child_k,
            parent_residue=row.parent_residue,
            child_residue=row.child_residue,
            new_prime=row.new_prime,
            new_prime_remainder=row.new_prime_remainder,
            old_component_count=len(old_components),
            old_uncovered_measure=format_fraction(old_measure),
            new_arc_width=format_fraction(new_arc_width),
            capacity_pass=capacity_pass,
            phase_margin=format_fraction(margin),
            phase_pass=margin > 0,
            endpoint_touch=margin == 0,
            phase_rank_desc=margin_order[(row.parent_residue, row.child_residue)],
            is_close=classify_canonical_transition(row) == "close",
            is_birth=row.is_b5_birth,
        )
        for row, margin in computed
    ]


def _phase_margin(row: TransitionProbeRow) -> Fraction:
    """Return signed exact containment margin of old residual components in new arc."""
    old_components = circular_components(parse_interval_list(row.old_gap_boundary_endpoints))
    arc_components = circular_components(
        exact_arc_intervals_for_residue(row.child_residue, row.new_prime)
    )
    if len(arc_components) != 1:
        raise ValueError("expected one circular new-prime arc")
    arc_interval = _unwrap_component(arc_components[0])
    component_margins = [
        _signed_containment_margin(_unwrap_component(component), arc_interval)
        for component in old_components
    ]
    return min(component_margins) if component_margins else Fraction(0)


def _signed_containment_margin(
    gap_interval: tuple[Fraction, Fraction],
    arc_interval: tuple[Fraction, Fraction],
) -> Fraction:
    gap_start, gap_end = gap_interval
    arc_start, arc_end = arc_interval
    candidates = []
    for shift in (-1, 0, 1):
        shifted_start = arc_start + shift
        shifted_end = arc_end + shift
        candidates.append(min(gap_start - shifted_start, shifted_end - gap_end))
    return max(candidates)


def _unwrap_component(component) -> tuple[Fraction, Fraction]:
    segments = component.segments
    if len(segments) == 1:
        return segments[0]
    return (segments[0][0], segments[-1][1] + 1)


def _scoped_transition_rows() -> list[tuple[str, list[TransitionProbeRow]]]:
    return [
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


def _read_dataclass_csv(path: str | Path, row_type: type):
    int_fields = {
        "parent_k",
        "child_k",
        "parent_residue",
        "child_residue",
        "new_prime",
        "new_prime_remainder",
        "old_component_count",
        "phase_rank_desc",
        "lift_count",
        "phase_pass_count",
        "close_lift_count",
        "birth_lift_count",
        "nonbirth_close_count",
    }
    bool_fields = {
        "capacity_pass",
        "phase_pass",
        "endpoint_touch",
        "is_close",
        "is_birth",
    }
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
