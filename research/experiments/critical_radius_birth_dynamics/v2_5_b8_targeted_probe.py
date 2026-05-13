"""Source-only B8 high-potential probe for PRC v2.5."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from v2_4_phase_gate_diagnostics import _phase_margin
from v2_4_transition_pilot import (
    TransitionProbeRow,
    build_transition_rows,
    classify_canonical_transition,
    component_transition_stats,
)
from v2_5_residual_dynamics import (
    ResidualStateTransitionRow,
    final_rows_by_lineage,
    read_residual_state_transition_csv,
    row_signature,
)

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_B8_HIGH_POTENTIAL_PROBE_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_b8_high_potential_probe_v0_1.csv"
)
DEFAULT_TOP_PARENT_CAP = 200


@dataclass(frozen=True)
class B8HighPotentialProbeRow:
    parent_rank: int
    source_lineage_id: str
    source_lineage_role: str
    parent_residue: int
    parent_component_count: int
    parent_residual_measure: str
    parent_max_component_width: str
    lift_remainder: int
    child_residue: int
    transition_label: str
    component_delta: int
    phase_margin: str
    phase_rank: int
    is_close: bool


def build_b8_high_potential_probe_rows(
    *,
    transition_rows: Iterable[ResidualStateTransitionRow] | None = None,
    top_parent_cap: int = DEFAULT_TOP_PARENT_CAP,
) -> list[B8HighPotentialProbeRow]:
    """Probe B7->B8 only for top prefix-potential non-close parents."""
    rows = (
        list(transition_rows)
        if transition_rows is not None
        else read_residual_state_transition_csv()
    )
    selected = _select_b8_parent_candidates(rows, top_parent_cap=top_parent_cap)
    if not selected:
        return []
    transition_rows_by_parent = _b8_transition_rows_by_parent(
        [row.residue_mod_m for row in selected]
    )
    selected_by_parent = {row.residue_mod_m: row for row in selected}
    result: list[B8HighPotentialProbeRow] = []
    for parent_rank, parent in enumerate(selected, start=1):
        probe_rows = transition_rows_by_parent[parent.residue_mod_m]
        margins = [(row, _phase_margin(row)) for row in probe_rows]
        rank_by_child = {
            row.child_residue: rank
            for rank, (row, _margin) in enumerate(
                sorted(
                    margins,
                    key=lambda item: (-item[1], item[0].new_prime_remainder),
                ),
                start=1,
            )
        }
        source = selected_by_parent[parent.residue_mod_m]
        for row, margin in sorted(margins, key=lambda item: item[0].new_prime_remainder):
            transition_label = classify_canonical_transition(row)
            result.append(
                B8HighPotentialProbeRow(
                    parent_rank=parent_rank,
                    source_lineage_id=source.lineage_id,
                    source_lineage_role=source.lineage_role,
                    parent_residue=row.parent_residue,
                    parent_component_count=source.new_component_count,
                    parent_residual_measure=source.total_residual_measure,
                    parent_max_component_width=source.max_component_width,
                    lift_remainder=row.new_prime_remainder,
                    child_residue=row.child_residue,
                    transition_label=transition_label,
                    component_delta=component_transition_stats(row).component_delta,
                    phase_margin=_format_fraction(margin),
                    phase_rank=rank_by_child[row.child_residue],
                    is_close=transition_label == "close",
                )
            )
    return result


def write_b8_high_potential_probe_csv(
    rows: Iterable[B8HighPotentialProbeRow] | None = None,
    output_path: str | Path = DEFAULT_B8_HIGH_POTENTIAL_PROBE_CSV,
) -> None:
    row_list = (
        list(rows)
        if rows is not None
        else build_b8_high_potential_probe_rows()
    )
    write_dataclass_csv(row_list, output_path, B8HighPotentialProbeRow)


def read_b8_high_potential_probe_csv(
    path: str | Path = DEFAULT_B8_HIGH_POTENTIAL_PROBE_CSV,
) -> list[B8HighPotentialProbeRow]:
    return _read_dataclass_csv(path, B8HighPotentialProbeRow)


def write_dataclass_csv(rows: Iterable[object], output_path: str | Path, row_type: type) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(row_type.__dataclass_fields__.keys())
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def _select_b8_parent_candidates(
    rows: Iterable[ResidualStateTransitionRow],
    *,
    top_parent_cap: int,
) -> list[ResidualStateTransitionRow]:
    final_rows = [
        row
        for row in final_rows_by_lineage(rows).values()
        if row.scope == "B7_birth_parent_siblings" and not row.is_close
    ]
    best_by_parent: dict[int, ResidualStateTransitionRow] = {}
    for row in final_rows:
        current = best_by_parent.get(row.residue_mod_m)
        if current is None or _b8_parent_score(row) > _b8_parent_score(current):
            best_by_parent[row.residue_mod_m] = row
    return sorted(
        best_by_parent.values(),
        key=lambda row: (-_b8_parent_score(row), row.residue_mod_m),
    )[:top_parent_cap]


def _b8_parent_score(row: ResidualStateTransitionRow) -> Fraction:
    capacity = row.new_component_count == 1 and Fraction(row.total_residual_measure) <= Fraction(1, 19)
    return (
        Fraction(100 if capacity else 0)
        + Fraction(row.total_residual_measure)
        - row.new_component_count
    )


def _b8_transition_rows_by_parent(
    parent_residues: Iterable[int],
) -> dict[int, list[TransitionProbeRow]]:
    rows = build_transition_rows(
        parent_k=7,
        child_k=8,
        parent_residues=parent_residues,
        birth_rows=[],
        uncovered_only=True,
    )
    by_parent: dict[int, list[TransitionProbeRow]] = {}
    for row in rows:
        by_parent.setdefault(row.parent_residue, []).append(row)
    return by_parent


def _format_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _read_dataclass_csv(path: str | Path, row_type: type):
    int_fields = {
        "parent_rank",
        "parent_residue",
        "parent_component_count",
        "lift_remainder",
        "child_residue",
        "component_delta",
        "phase_rank",
    }
    bool_fields = {"is_close"}
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


def b8_probe_signature(row: object) -> tuple[object, ...]:
    return row_signature(row)
