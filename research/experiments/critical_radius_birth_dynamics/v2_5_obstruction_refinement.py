"""Refined non-close obstruction diagnostics for PRC v2.5."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from v2_4_phase_gate_diagnostics import (
    PhaseGateLiftDiagnosticRow,
    read_phase_gate_lift_diagnostics_csv,
)
from v2_5_margin_genesis import SCOPE_TO_PHASE_SCOPE
from v2_5_residual_dynamics import (
    ResidualStateTransitionRow,
    final_rows_by_lineage,
    read_residual_state_transition_csv,
    row_signature,
    transition_sequences_by_lineage,
)

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_REFINED_OBSTRUCTION_CLASSES_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_refined_obstruction_classes_v0_1.csv"
)
DEFAULT_OBSTRUCTION_BUCKET_SUMMARY_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_obstruction_bucket_summary_v0_1.csv"
)

OBSTRUCTION_NONE = "none"
OBSTRUCTION_CAPACITY = "capacity_obstruction"
OBSTRUCTION_WRONG_SIDE = "wrong_side"
OBSTRUCTION_UNDERREACH = "underreach"
OBSTRUCTION_SPLIT_HISTORY = "split_history"
OBSTRUCTION_SIBLING_DOMINATED = "sibling_dominated"
OBSTRUCTION_UNCLASSIFIED = "unclassified"


@dataclass(frozen=True)
class RefinedObstructionRow:
    scope: str
    lineage_id: str
    lineage_role: str
    parent_residue: int
    child_residue: int
    new_prime_remainder: int
    capacity_pass: bool
    phase_rank: int
    phase_margin: str
    prefix_transition_sequence: str
    refined_obstruction: str
    obstruction_reason: str


@dataclass(frozen=True)
class ObstructionBucketSummaryRow:
    scope: str
    refined_obstruction: str
    row_count: int
    share_of_nonclose: str
    note: str


def build_refined_obstruction_rows(
    *,
    transition_rows: Iterable[ResidualStateTransitionRow] | None = None,
    phase_rows: Iterable[PhaseGateLiftDiagnosticRow] | None = None,
) -> list[RefinedObstructionRow]:
    rows = (
        list(transition_rows)
        if transition_rows is not None
        else read_residual_state_transition_csv()
    )
    phase = (
        list(phase_rows)
        if phase_rows is not None
        else read_phase_gate_lift_diagnostics_csv()
    )
    final_rows = final_rows_by_lineage(rows)
    sequences = transition_sequences_by_lineage(rows)
    phase_by_child = {(row.scope, row.child_residue): row for row in phase}
    close_families = {
        (row.scope, row.parent_residue)
        for row in phase
        if row.is_close
    }
    result: list[RefinedObstructionRow] = []
    for lineage_id in sorted(final_rows):
        final = final_rows[lineage_id]
        phase_row = phase_by_child[(SCOPE_TO_PHASE_SCOPE[final.scope], final.residue_mod_m)]
        prefix_sequence = ">".join(sequences[lineage_id][:-1])
        bucket, reason = _classify_refined_obstruction(
            final=final,
            phase_row=phase_row,
            prefix_sequence=prefix_sequence,
            has_close_sibling=(phase_row.scope, phase_row.parent_residue) in close_families,
        )
        result.append(
            RefinedObstructionRow(
                scope=final.scope,
                lineage_id=lineage_id,
                lineage_role=final.lineage_role,
                parent_residue=phase_row.parent_residue,
                child_residue=final.residue_mod_m,
                new_prime_remainder=phase_row.new_prime_remainder,
                capacity_pass=phase_row.capacity_pass,
                phase_rank=phase_row.phase_rank_desc,
                phase_margin=phase_row.phase_margin,
                prefix_transition_sequence=prefix_sequence,
                refined_obstruction=bucket,
                obstruction_reason=reason,
            )
        )
    return result


def build_obstruction_bucket_summary_rows(
    rows: Iterable[RefinedObstructionRow] | None = None,
) -> list[ObstructionBucketSummaryRow]:
    row_list = list(rows) if rows is not None else build_refined_obstruction_rows()
    scopes = ["all", *sorted({row.scope for row in row_list})]
    result: list[ObstructionBucketSummaryRow] = []
    for scope in scopes:
        scoped = row_list if scope == "all" else [row for row in row_list if row.scope == scope]
        nonclose = [row for row in scoped if row.refined_obstruction != OBSTRUCTION_NONE]
        counts = Counter(row.refined_obstruction for row in scoped)
        for bucket in sorted(counts):
            result.append(
                ObstructionBucketSummaryRow(
                    scope=scope,
                    refined_obstruction=bucket,
                    row_count=counts[bucket],
                    share_of_nonclose=(
                        _format_fraction(Fraction(counts[bucket], len(nonclose)))
                        if nonclose and bucket != OBSTRUCTION_NONE
                        else "0"
                    ),
                    note="refined source-only obstruction bucket",
                )
            )
    return result


def write_obstruction_refinement_artifacts(
    *,
    classes_path: str | Path = DEFAULT_REFINED_OBSTRUCTION_CLASSES_CSV,
    summary_path: str | Path = DEFAULT_OBSTRUCTION_BUCKET_SUMMARY_CSV,
) -> None:
    rows = build_refined_obstruction_rows()
    write_dataclass_csv(rows, classes_path, RefinedObstructionRow)
    write_dataclass_csv(
        build_obstruction_bucket_summary_rows(rows),
        summary_path,
        ObstructionBucketSummaryRow,
    )


def read_refined_obstruction_csv(
    path: str | Path = DEFAULT_REFINED_OBSTRUCTION_CLASSES_CSV,
) -> list[RefinedObstructionRow]:
    return _read_dataclass_csv(path, RefinedObstructionRow)


def read_obstruction_bucket_summary_csv(
    path: str | Path = DEFAULT_OBSTRUCTION_BUCKET_SUMMARY_CSV,
) -> list[ObstructionBucketSummaryRow]:
    return _read_dataclass_csv(path, ObstructionBucketSummaryRow)


def write_dataclass_csv(rows: Iterable[object], output_path: str | Path, row_type: type) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(row_type.__dataclass_fields__.keys())
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def _classify_refined_obstruction(
    *,
    final: ResidualStateTransitionRow,
    phase_row: PhaseGateLiftDiagnosticRow,
    prefix_sequence: str,
    has_close_sibling: bool,
) -> tuple[str, str]:
    if final.is_close:
        return OBSTRUCTION_NONE, "close lineage; no obstruction assigned"
    if has_close_sibling:
        return (
            OBSTRUCTION_SIBLING_DOMINATED,
            "same parent family has a close sibling with better phase rank",
        )
    if not phase_row.capacity_pass:
        return (
            OBSTRUCTION_CAPACITY,
            "pre-final residual component fails single-component capacity",
        )
    if "split" in prefix_sequence or "partial_close" in prefix_sequence:
        return (
            OBSTRUCTION_SPLIT_HISTORY,
            "prefix history contains split or partial_close before final failure",
        )
    if abs(Fraction(phase_row.phase_margin)) <= Fraction(phase_row.new_arc_width):
        return (
            OBSTRUCTION_UNDERREACH,
            "capacity holds but containment margin remains near-negative",
        )
    return (
        OBSTRUCTION_WRONG_SIDE,
        "capacity holds but sibling phase sits outside the closing aperture",
    )


def _format_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _read_dataclass_csv(path: str | Path, row_type: type):
    int_fields = {
        "parent_residue",
        "child_residue",
        "new_prime_remainder",
        "phase_rank",
        "row_count",
    }
    bool_fields = {"capacity_pass"}
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


def obstruction_refinement_signature(row: object) -> tuple[object, ...]:
    return row_signature(row)
