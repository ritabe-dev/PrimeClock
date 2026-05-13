"""Source-only obstruction classification for PRC v2.5 residual dynamics."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from v2_5_residual_dynamics import (
    LINEAGE_CAPACITY_NONCLOSE,
    LINEAGE_NEAR_MISS,
    ResidualStateTransitionRow,
    final_rows_by_lineage,
    read_residual_state_transition_csv,
    row_signature,
    transition_sequences_by_lineage,
)

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_OBSTRUCTION_CLASSES_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_obstruction_classes_v0_1.csv"
)

OBSTRUCTION_NONE = "none"
OBSTRUCTION_CAPACITY = "capacity_obstruction"
OBSTRUCTION_PHASE = "phase_obstruction"
OBSTRUCTION_MULTI_COMPONENT = "multi_component_obstruction"
OBSTRUCTION_NEAR_MISS = "near_miss_obstruction"
OBSTRUCTION_LINEAGE = "lineage_obstruction"
OBSTRUCTION_ARITHMETIC = "arithmetic_obstruction"
OBSTRUCTION_UNCLASSIFIED = "unclassified"


@dataclass(frozen=True)
class ObstructionClassRow:
    scope: str
    lineage_id: str
    lineage_role: str
    child_residue: int
    is_close: bool
    is_birth: bool
    capacity_pass: bool
    phase_margin: str
    transition_sequence: str
    obstruction_class: str
    obstruction_reason: str


def build_obstruction_class_rows(
    transition_rows: Iterable[ResidualStateTransitionRow] | None = None,
) -> list[ObstructionClassRow]:
    """Classify final non-close rows by residual-dynamics failure mode."""
    rows = (
        list(transition_rows)
        if transition_rows is not None
        else read_residual_state_transition_csv()
    )
    final_rows = final_rows_by_lineage(rows)
    sequences = transition_sequences_by_lineage(rows)
    result: list[ObstructionClassRow] = []
    for lineage_id in sorted(final_rows):
        row = final_rows[lineage_id]
        obstruction, reason = _classify_obstruction(row, sequences[lineage_id])
        result.append(
            ObstructionClassRow(
                scope=row.scope,
                lineage_id=row.lineage_id,
                lineage_role=row.lineage_role,
                child_residue=row.residue_mod_m,
                is_close=row.is_close,
                is_birth=row.is_birth,
                capacity_pass=row.capacity_pass,
                phase_margin=row.phase_margin,
                transition_sequence=">".join(sequences[lineage_id]),
                obstruction_class=obstruction,
                obstruction_reason=reason,
            )
        )
    return result


def write_obstruction_class_csv(
    rows: Iterable[ObstructionClassRow] | None = None,
    output_path: str | Path = DEFAULT_OBSTRUCTION_CLASSES_CSV,
) -> None:
    row_list = list(rows) if rows is not None else build_obstruction_class_rows()
    write_dataclass_csv(row_list, output_path, ObstructionClassRow)


def read_obstruction_class_csv(
    path: str | Path = DEFAULT_OBSTRUCTION_CLASSES_CSV,
) -> list[ObstructionClassRow]:
    return _read_dataclass_csv(path, ObstructionClassRow)


def write_dataclass_csv(rows: Iterable[object], output_path: str | Path, row_type: type) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(row_type.__dataclass_fields__.keys())
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def _classify_obstruction(
    row: ResidualStateTransitionRow,
    sequence: tuple[str, ...],
) -> tuple[str, str]:
    if row.is_close:
        return OBSTRUCTION_NONE, "close lineage; no obstruction assigned"
    if row.lineage_role == LINEAGE_NEAR_MISS:
        return OBSTRUCTION_NEAR_MISS, "best non-close sibling in a close-capable family"
    if not row.capacity_pass:
        return OBSTRUCTION_CAPACITY, "pre-final residual state fails single-component capacity"
    if row.phase_margin and Fraction(row.phase_margin) <= 0:
        return OBSTRUCTION_PHASE, "capacity holds but signed phase margin is not positive"
    if row.old_component_count > 1:
        return OBSTRUCTION_MULTI_COMPONENT, "pre-final residual has multiple components"
    if "split" in sequence or "partial_close" in sequence:
        return OBSTRUCTION_LINEAGE, "history includes non-trivial split/partial-close transition"
    if row.lineage_role == LINEAGE_CAPACITY_NONCLOSE:
        return OBSTRUCTION_UNCLASSIFIED, "capacity-satisfied non-close without finer assignment"
    return OBSTRUCTION_UNCLASSIFIED, "non-close control left as explicit residual case"


def _read_dataclass_csv(path: str | Path, row_type: type) -> list[ObstructionClassRow]:
    int_fields = {"child_residue"}
    bool_fields = {"is_close", "is_birth", "capacity_pass"}
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for raw_row in csv.DictReader(handle):
            values = dict(raw_row)
            for field in int_fields:
                values[field] = int(values[field])
            for field in bool_fields:
                values[field] = values[field] == "True"
            rows.append(row_type(**values))
    return rows


def obstruction_signature(row: ObstructionClassRow) -> tuple[object, ...]:
    return row_signature(row)
