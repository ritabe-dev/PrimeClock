"""Prefix-only transition grammar diagnostics for PRC v2.5."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from v2_5_residual_dynamics import (
    ResidualStateTransitionRow,
    read_residual_state_transition_csv,
    row_signature,
)

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_PREFIX_LINEAGE_GRAMMAR_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_prefix_lineage_grammar_v0_1.csv"
)
DEFAULT_PREFIX_GRAMMAR_ENRICHMENT_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_prefix_grammar_enrichment_v0_1.csv"
)


@dataclass(frozen=True)
class PrefixLineageGrammarRow:
    scope: str
    lineage_role: str
    prefix_transition_sequence: str
    prefix_component_delta_sequence: str
    lineage_count: int
    close_count: int
    near_miss_count: int
    capacity_nonclose_count: int
    close_rate: str
    diagnostic_role: str


@dataclass(frozen=True)
class PrefixGrammarEnrichmentRow:
    scope: str
    prefix_transition_sequence: str
    lineage_count: int
    close_count: int
    baseline_close_rate: str
    prefix_close_rate: str
    enrichment_ratio: str
    dominant_role: str


def build_prefix_lineage_grammar_rows(
    transition_rows: Iterable[ResidualStateTransitionRow] | None = None,
) -> list[PrefixLineageGrammarRow]:
    rows = (
        list(transition_rows)
        if transition_rows is not None
        else read_residual_state_transition_csv()
    )
    by_lineage = _rows_by_lineage(rows)
    grouped: dict[tuple[str, str, str, str], list[ResidualStateTransitionRow]] = {}
    for lineage_rows in by_lineage.values():
        ordered = sorted(lineage_rows, key=lambda row: row.layer_k)
        final = ordered[-1]
        prefix = ordered[:-1]
        transition_sequence = ">".join(row.transition_label for row in prefix)
        delta_sequence = ">".join(str(row.component_delta) for row in prefix)
        grouped.setdefault(
            (final.scope, final.lineage_role, transition_sequence, delta_sequence),
            [],
        ).append(final)

    totals_by_scope_role = Counter(
        (scope, role)
        for (scope, role, _sequence, _delta), lineage_rows in grouped.items()
        for _row in lineage_rows
    )
    result: list[PrefixLineageGrammarRow] = []
    for key in sorted(grouped):
        scope, role, sequence, delta_sequence = key
        lineage_rows = grouped[key]
        close_count = sum(row.is_close for row in lineage_rows)
        near_miss_count = sum(row.lineage_role == "near_miss" for row in lineage_rows)
        capacity_count = sum(
            row.lineage_role == "capacity_nonclose" for row in lineage_rows
        )
        share = Fraction(len(lineage_rows), totals_by_scope_role[(scope, role)])
        result.append(
            PrefixLineageGrammarRow(
                scope=scope,
                lineage_role=role,
                prefix_transition_sequence=sequence,
                prefix_component_delta_sequence=delta_sequence,
                lineage_count=len(lineage_rows),
                close_count=close_count,
                near_miss_count=near_miss_count,
                capacity_nonclose_count=capacity_count,
                close_rate=_ratio(close_count, len(lineage_rows)),
                diagnostic_role="dominant" if share >= Fraction(1, 10) else "rare",
            )
        )
    return result


def build_prefix_grammar_enrichment_rows(
    transition_rows: Iterable[ResidualStateTransitionRow] | None = None,
) -> list[PrefixGrammarEnrichmentRow]:
    rows = (
        list(transition_rows)
        if transition_rows is not None
        else read_residual_state_transition_csv()
    )
    by_lineage = _rows_by_lineage(rows)
    grouped: dict[tuple[str, str], list[ResidualStateTransitionRow]] = {}
    baseline_by_scope: dict[str, list[ResidualStateTransitionRow]] = {}
    for lineage_rows in by_lineage.values():
        ordered = sorted(lineage_rows, key=lambda row: row.layer_k)
        final = ordered[-1]
        sequence = ">".join(row.transition_label for row in ordered[:-1])
        grouped.setdefault((final.scope, sequence), []).append(final)
        baseline_by_scope.setdefault(final.scope, []).append(final)

    result: list[PrefixGrammarEnrichmentRow] = []
    for key in sorted(grouped):
        scope, sequence = key
        lineage_rows = grouped[key]
        baseline_rows = baseline_by_scope[scope]
        close_count = sum(row.is_close for row in lineage_rows)
        baseline_close = sum(row.is_close for row in baseline_rows)
        prefix_rate = Fraction(close_count, len(lineage_rows))
        baseline_rate = Fraction(baseline_close, len(baseline_rows))
        roles = Counter(row.lineage_role for row in lineage_rows)
        result.append(
            PrefixGrammarEnrichmentRow(
                scope=scope,
                prefix_transition_sequence=sequence,
                lineage_count=len(lineage_rows),
                close_count=close_count,
                baseline_close_rate=_format_fraction(baseline_rate),
                prefix_close_rate=_format_fraction(prefix_rate),
                enrichment_ratio=_format_fraction(
                    prefix_rate / baseline_rate if baseline_rate else Fraction(0)
                ),
                dominant_role=roles.most_common(1)[0][0],
            )
        )
    return result


def write_prefix_grammar_artifacts(
    *,
    grammar_path: str | Path = DEFAULT_PREFIX_LINEAGE_GRAMMAR_CSV,
    enrichment_path: str | Path = DEFAULT_PREFIX_GRAMMAR_ENRICHMENT_CSV,
) -> None:
    rows = read_residual_state_transition_csv()
    write_dataclass_csv(
        build_prefix_lineage_grammar_rows(rows),
        grammar_path,
        PrefixLineageGrammarRow,
    )
    write_dataclass_csv(
        build_prefix_grammar_enrichment_rows(rows),
        enrichment_path,
        PrefixGrammarEnrichmentRow,
    )


def read_prefix_lineage_grammar_csv(
    path: str | Path = DEFAULT_PREFIX_LINEAGE_GRAMMAR_CSV,
) -> list[PrefixLineageGrammarRow]:
    return _read_dataclass_csv(path, PrefixLineageGrammarRow)


def read_prefix_grammar_enrichment_csv(
    path: str | Path = DEFAULT_PREFIX_GRAMMAR_ENRICHMENT_CSV,
) -> list[PrefixGrammarEnrichmentRow]:
    return _read_dataclass_csv(path, PrefixGrammarEnrichmentRow)


def write_dataclass_csv(rows: Iterable[object], output_path: str | Path, row_type: type) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(row_type.__dataclass_fields__.keys())
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def _rows_by_lineage(
    rows: Iterable[ResidualStateTransitionRow],
) -> dict[str, list[ResidualStateTransitionRow]]:
    by_lineage: dict[str, list[ResidualStateTransitionRow]] = {}
    for row in rows:
        by_lineage.setdefault(row.lineage_id, []).append(row)
    return by_lineage


def _ratio(numerator: int, denominator: int) -> str:
    return _format_fraction(Fraction(numerator, denominator)) if denominator else "0"


def _format_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _read_dataclass_csv(path: str | Path, row_type: type):
    int_fields = {
        "lineage_count",
        "close_count",
        "near_miss_count",
        "capacity_nonclose_count",
    }
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for raw_row in csv.DictReader(handle):
            values = dict(raw_row)
            for field in int_fields:
                if field in values:
                    values[field] = int(values[field])
            rows.append(row_type(**values))
    return rows


def prefix_grammar_signature(row: object) -> tuple[object, ...]:
    return row_signature(row)
