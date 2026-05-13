"""Source-only exact hull obstruction diagnostics for PRC v2.5."""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

from tools import format_fraction
from v2_4_transition_pilot import (
    DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV,
    DEFAULT_B5_TRANSITION_PILOT_CSV,
    DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV,
    CircularComponent,
    circular_components,
    classify_canonical_transition,
    parse_interval_list,
    read_b5_gap_close_transition_pilot_csv,
)
from v2_5_b8_control_calibration import read_b8_sibling_control_csv

EXPERIMENT_DIR = Path(__file__).resolve().parent

DEFAULT_EXACT_HULL_OBSTRUCTION_FAMILY_CSV = (
    EXPERIMENT_DIR
    / "data"
    / "prc_v2_5_exact_hull_obstruction_family_v0_1.csv"
)
DEFAULT_EXACT_HULL_OBSTRUCTION_SUMMARY_CSV = (
    EXPERIMENT_DIR
    / "data"
    / "prc_v2_5_exact_hull_obstruction_summary_v0_1.csv"
)

HISTORICAL_TRANSITION_SOURCES = (
    ("B4_to_B5_full", DEFAULT_B5_TRANSITION_PILOT_CSV),
    ("B5_to_B6_full", DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV),
    ("B6_to_B7_full", DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV),
)


@dataclass(frozen=True)
class ExactHullObstructionFamilyRow:
    scope: str
    parent_residue: int
    new_prime: int
    old_component_count: int
    min_covering_hull_length: str
    new_arc_width: str
    hull_obstruction: bool
    close_lift_count: int
    birth_lift_count: int
    diagnostic_class: str


@dataclass(frozen=True)
class ExactHullObstructionSummaryRow:
    scope: str
    family_count: int
    multi_component_family_count: int
    hull_obstructed_multi_count: int
    multi_component_close_count: int
    single_component_close_count: int
    close_lift_count: int
    b8_checked_close_single_gap_count: int
    status: str


def write_exact_hull_obstruction_artifacts(
    *,
    family_path: str | Path = DEFAULT_EXACT_HULL_OBSTRUCTION_FAMILY_CSV,
    summary_path: str | Path = DEFAULT_EXACT_HULL_OBSTRUCTION_SUMMARY_CSV,
) -> None:
    family_rows = build_exact_hull_obstruction_family_rows()
    summary_rows = build_exact_hull_obstruction_summary_rows(family_rows)
    write_dataclass_csv(family_rows, family_path, ExactHullObstructionFamilyRow)
    write_dataclass_csv(summary_rows, summary_path, ExactHullObstructionSummaryRow)


def build_exact_hull_obstruction_family_rows() -> list[ExactHullObstructionFamilyRow]:
    result: list[ExactHullObstructionFamilyRow] = []
    for scope, path in HISTORICAL_TRANSITION_SOURCES:
        by_parent: dict[int, list[object]] = defaultdict(list)
        for row in read_b5_gap_close_transition_pilot_csv(path):
            by_parent[row.parent_residue].append(row)
        for parent_residue in sorted(by_parent):
            rows = by_parent[parent_residue]
            first = rows[0]
            components = circular_components(
                parse_interval_list(first.old_gap_boundary_endpoints)
            )
            new_arc_width = Fraction(1, first.new_prime)
            min_hull = minimum_circular_hull_length(components)
            close_count = sum(classify_canonical_transition(row) == "close" for row in rows)
            birth_count = sum(row.is_b5_birth for row in rows)
            hull_obstruction = len(components) > 1 and min_hull > new_arc_width
            result.append(
                ExactHullObstructionFamilyRow(
                    scope=scope,
                    parent_residue=parent_residue,
                    new_prime=first.new_prime,
                    old_component_count=len(components),
                    min_covering_hull_length=format_fraction(min_hull),
                    new_arc_width=format_fraction(new_arc_width),
                    hull_obstruction=hull_obstruction,
                    close_lift_count=close_count,
                    birth_lift_count=birth_count,
                    diagnostic_class=_diagnostic_class(
                        old_component_count=len(components),
                        hull_obstruction=hull_obstruction,
                        close_lift_count=close_count,
                    ),
                )
            )
    return result


def build_exact_hull_obstruction_summary_rows(
    family_rows: Sequence[ExactHullObstructionFamilyRow] | None = None,
) -> list[ExactHullObstructionSummaryRow]:
    rows = (
        list(family_rows)
        if family_rows is not None
        else build_exact_hull_obstruction_family_rows()
    )
    b8_single_gap_close_count = sum(
        row.sibling_role == "birth_close" and row.parent_gap_count_exact == 1
        for row in read_b8_sibling_control_csv()
    )
    by_scope: dict[str, list[ExactHullObstructionFamilyRow]] = defaultdict(list)
    for row in rows:
        by_scope[row.scope].append(row)
    result: list[ExactHullObstructionSummaryRow] = []
    for scope, _path in HISTORICAL_TRANSITION_SOURCES:
        scoped = by_scope[scope]
        multi = [row for row in scoped if row.old_component_count > 1]
        result.append(
            ExactHullObstructionSummaryRow(
                scope=scope,
                family_count=len(scoped),
                multi_component_family_count=len(multi),
                hull_obstructed_multi_count=sum(row.hull_obstruction for row in multi),
                multi_component_close_count=sum(row.close_lift_count > 0 for row in multi),
                single_component_close_count=sum(
                    row.old_component_count == 1 and row.close_lift_count > 0
                    for row in scoped
                ),
                close_lift_count=sum(row.close_lift_count for row in scoped),
                b8_checked_close_single_gap_count=b8_single_gap_close_count,
                status=_summary_status(scoped, multi),
            )
        )
    return result


def minimum_circular_hull_length(components: Sequence[CircularComponent]) -> Fraction:
    """Return the shortest circular arc that contains all residual components."""
    starts_and_widths = [_component_start_and_width(component) for component in components]
    if not starts_and_widths:
        return Fraction(0)
    best: Fraction | None = None
    for anchor, _width in starts_and_widths:
        right_edges = []
        for start, width in starts_and_widths:
            shifted_start = start if start >= anchor else start + 1
            right_edges.append(shifted_start + width)
        hull_length = max(right_edges) - anchor
        if best is None or hull_length < best:
            best = hull_length
    if best is None:
        raise ValueError("minimum hull length was not computed")
    return best


def read_exact_hull_obstruction_family_csv(
    path: str | Path = DEFAULT_EXACT_HULL_OBSTRUCTION_FAMILY_CSV,
) -> list[ExactHullObstructionFamilyRow]:
    return _read_dataclass_csv(path, ExactHullObstructionFamilyRow)


def read_exact_hull_obstruction_summary_csv(
    path: str | Path = DEFAULT_EXACT_HULL_OBSTRUCTION_SUMMARY_CSV,
) -> list[ExactHullObstructionSummaryRow]:
    return _read_dataclass_csv(path, ExactHullObstructionSummaryRow)


def hull_obstruction_signature(row: object) -> tuple[object, ...]:
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


def _component_start_and_width(component: CircularComponent) -> tuple[Fraction, Fraction]:
    start = component.segments[0][0] % 1
    width = sum(end - start for start, end in component.segments)
    return start, width


def _diagnostic_class(
    *,
    old_component_count: int,
    hull_obstruction: bool,
    close_lift_count: int,
) -> str:
    if close_lift_count:
        return "single_gap_close" if old_component_count == 1 else "multi_gap_close_review"
    if hull_obstruction:
        return "multi_gap_hull_obstructed"
    if old_component_count > 1:
        return "multi_gap_unobstructed_review"
    return "single_gap_nonclose"


def _summary_status(scoped, multi) -> str:
    multi_obstructed = all(row.hull_obstruction for row in multi)
    no_multi_close = all(row.close_lift_count == 0 for row in multi)
    close_single = all(
        row.old_component_count == 1 for row in scoped if row.close_lift_count > 0
    )
    return (
        "checked_hull_obstruction"
        if multi_obstructed and no_multi_close and close_single
        else "review"
    )


def _read_dataclass_csv(path: str | Path, row_type: type):
    int_fields = {
        "parent_residue",
        "new_prime",
        "old_component_count",
        "close_lift_count",
        "birth_lift_count",
        "family_count",
        "multi_component_family_count",
        "hull_obstructed_multi_count",
        "multi_component_close_count",
        "single_component_close_count",
        "b8_checked_close_single_gap_count",
    }
    bool_fields = {"hull_obstruction"}
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
