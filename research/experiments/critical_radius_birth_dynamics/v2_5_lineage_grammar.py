"""Source-only transition grammar summaries for PRC v2.5."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from v2_5_residual_dynamics import (
    DEFAULT_RESIDUAL_STATE_TRANSITIONS_CSV,
    ResidualStateTransitionRow,
    read_residual_state_transition_csv,
    row_signature,
)

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_LINEAGE_GRAMMAR_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_lineage_grammar_v0_1.csv"
)


@dataclass(frozen=True)
class LineageGrammarRow:
    scope: str
    lineage_role: str
    transition_sequence: str
    component_delta_sequence: str
    lineage_count: int
    close_count: int
    nonclose_count: int
    example_lineage_id: str
    diagnostic_role: str


def build_lineage_grammar_rows(
    transition_rows: Iterable[ResidualStateTransitionRow] | None = None,
) -> list[LineageGrammarRow]:
    """Compress exact residual lineages into transition grammar rows."""
    rows = (
        list(transition_rows)
        if transition_rows is not None
        else read_residual_state_transition_csv(DEFAULT_RESIDUAL_STATE_TRANSITIONS_CSV)
    )
    by_lineage: dict[str, list[ResidualStateTransitionRow]] = {}
    for row in rows:
        by_lineage.setdefault(row.lineage_id, []).append(row)

    grouped: dict[tuple[str, str, str, str], list[str]] = {}
    close_counts: Counter[tuple[str, str, str, str]] = Counter()
    for lineage_id, lineage_rows in by_lineage.items():
        ordered = sorted(lineage_rows, key=lambda row: row.layer_k)
        final = ordered[-1]
        transition_sequence = ">".join(row.transition_label for row in ordered)
        delta_sequence = ">".join(str(row.component_delta) for row in ordered)
        key = (final.scope, final.lineage_role, transition_sequence, delta_sequence)
        grouped.setdefault(key, []).append(lineage_id)
        if final.is_close:
            close_counts[key] += 1

    result: list[LineageGrammarRow] = []
    totals_by_scope_role = Counter((key[0], key[1]) for key, value in grouped.items() for _ in value)
    for key in sorted(grouped):
        scope, role, transition_sequence, delta_sequence = key
        lineage_ids = grouped[key]
        close_count = close_counts[key]
        nonclose_count = len(lineage_ids) - close_count
        share = len(lineage_ids) / totals_by_scope_role[(scope, role)]
        result.append(
            LineageGrammarRow(
                scope=scope,
                lineage_role=role,
                transition_sequence=transition_sequence,
                component_delta_sequence=delta_sequence,
                lineage_count=len(lineage_ids),
                close_count=close_count,
                nonclose_count=nonclose_count,
                example_lineage_id=sorted(lineage_ids)[0],
                diagnostic_role="dominant" if share >= 0.1 else "rare",
            )
        )
    return result


def write_lineage_grammar_csv(
    rows: Iterable[LineageGrammarRow] | None = None,
    output_path: str | Path = DEFAULT_LINEAGE_GRAMMAR_CSV,
) -> None:
    row_list = list(rows) if rows is not None else build_lineage_grammar_rows()
    write_dataclass_csv(row_list, output_path, LineageGrammarRow)


def read_lineage_grammar_csv(
    path: str | Path = DEFAULT_LINEAGE_GRAMMAR_CSV,
) -> list[LineageGrammarRow]:
    return _read_dataclass_csv(path, LineageGrammarRow)


def write_dataclass_csv(rows: Iterable[object], output_path: str | Path, row_type: type) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(row_type.__dataclass_fields__.keys())
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def _read_dataclass_csv(path: str | Path, row_type: type) -> list[LineageGrammarRow]:
    int_fields = {"lineage_count", "close_count", "nonclose_count"}
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for raw_row in csv.DictReader(handle):
            values = dict(raw_row)
            for field in int_fields:
                values[field] = int(values[field])
            rows.append(row_type(**values))
    return rows


def grammar_signature(row: LineageGrammarRow) -> tuple[object, ...]:
    return row_signature(row)
