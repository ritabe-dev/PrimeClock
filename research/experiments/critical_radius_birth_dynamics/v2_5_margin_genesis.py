"""Prefix-only margin genesis diagnostics for PRC v2.5."""

from __future__ import annotations

import csv
import os
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from v2_4_phase_gate_diagnostics import (
    PhaseGateLiftDiagnosticRow,
    read_phase_gate_lift_diagnostics_csv,
)
from v2_5_prefix_grammar import build_prefix_grammar_enrichment_rows
from v2_5_residual_dynamics import (
    ResidualStateTransitionRow,
    final_rows_by_lineage,
    prefinal_rows_by_lineage,
    read_residual_state_transition_csv,
    row_signature,
    transition_sequences_by_lineage,
)

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_PREFIX_MARGIN_GENESIS_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_prefix_margin_genesis_v0_1.csv"
)
DEFAULT_CLOSE_NEARMISS_COUNTERFACTUAL_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_close_nearmiss_counterfactual_v0_1.csv"
)
DEFAULT_MARGIN_GENESIS_FIGURE = (
    EXPERIMENT_DIR / "figures" / "v2_5" / "prc_v2_5_margin_genesis_v0_1.png"
)

SCOPE_TO_PHASE_SCOPE = {
    "B5_birth_parent_siblings": "B4_to_B5_full",
    "B6_birth_parent_siblings": "B5_to_B6_full",
    "B7_birth_parent_siblings": "B6_to_B7_full",
}
PHASE_SCOPE_TO_RESIDUAL_SCOPE = {value: key for key, value in SCOPE_TO_PHASE_SCOPE.items()}


@dataclass(frozen=True)
class PrefixMarginGenesisRow:
    scope: str
    lineage_id: str
    lineage_role: str
    parent_residue: int
    child_residue: int
    new_prime_remainder: int
    prefix_transition_sequence: str
    prefix_component_delta_sequence: str
    prefix_total_residual_measure: str
    prefix_max_component_width: str
    prefix_component_count: int
    prefix_score_width: str
    prefix_score_capacity: str
    prefix_score_grammar: str
    prefix_score_state: str
    prefix_score_combined: str
    actual_phase_margin: str
    actual_phase_rank: int
    is_close: bool
    is_near_miss: bool


@dataclass(frozen=True)
class CloseNearMissCounterfactualRow:
    scope: str
    parent_residue: int
    close_child_residue: int
    near_miss_child_residue: int
    close_remainder: int
    near_miss_remainder: int
    close_margin: str
    near_miss_margin: str
    margin_gap: str
    close_rank: int
    near_miss_rank: int
    prefix_sequence_match: bool
    prefix_component_delta_match: bool
    close_prefinal_width: str
    near_miss_prefinal_width: str
    width_delta: str
    reflection_pair_match: bool


def build_prefix_margin_genesis_rows(
    *,
    transition_rows: Iterable[ResidualStateTransitionRow] | None = None,
    phase_rows: Iterable[PhaseGateLiftDiagnosticRow] | None = None,
) -> list[PrefixMarginGenesisRow]:
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
    prefinal_rows = prefinal_rows_by_lineage(rows)
    sequences = transition_sequences_by_lineage(rows)
    prefix_deltas = _prefix_delta_sequences_by_lineage(rows)
    phase_by_child = {(row.scope, row.child_residue): row for row in phase}
    grammar_rates = _prefix_close_rates(rows)

    result: list[PrefixMarginGenesisRow] = []
    for lineage_id in sorted(final_rows):
        final = final_rows[lineage_id]
        prefinal = prefinal_rows[lineage_id]
        phase_row = phase_by_child[(SCOPE_TO_PHASE_SCOPE[final.scope], final.residue_mod_m)]
        prefix_sequence = ">".join(sequences[lineage_id][:-1])
        prefix_delta_sequence = prefix_deltas[lineage_id]
        grammar_score = grammar_rates.get((final.scope, prefix_sequence), Fraction(0))
        width_score = Fraction(prefinal.max_component_width)
        capacity_score = Fraction(1 if _prefix_capacity_for_final_prime(prefinal, phase_row) else 0)
        state_score = width_score - prefinal.new_component_count
        combined = capacity_score * 100 + grammar_score * 10 + state_score
        result.append(
            PrefixMarginGenesisRow(
                scope=final.scope,
                lineage_id=lineage_id,
                lineage_role=final.lineage_role,
                parent_residue=phase_row.parent_residue,
                child_residue=final.residue_mod_m,
                new_prime_remainder=phase_row.new_prime_remainder,
                prefix_transition_sequence=prefix_sequence,
                prefix_component_delta_sequence=prefix_delta_sequence,
                prefix_total_residual_measure=prefinal.total_residual_measure,
                prefix_max_component_width=prefinal.max_component_width,
                prefix_component_count=prefinal.new_component_count,
                prefix_score_width=_format_fraction(width_score),
                prefix_score_capacity=_format_fraction(capacity_score),
                prefix_score_grammar=_format_fraction(grammar_score),
                prefix_score_state=_format_fraction(state_score),
                prefix_score_combined=_format_fraction(combined),
                actual_phase_margin=phase_row.phase_margin,
                actual_phase_rank=phase_row.phase_rank_desc,
                is_close=final.is_close,
                is_near_miss=final.lineage_role == "near_miss",
            )
        )
    return result


def build_close_nearmiss_counterfactual_rows(
    *,
    transition_rows: Iterable[ResidualStateTransitionRow] | None = None,
    phase_rows: Iterable[PhaseGateLiftDiagnosticRow] | None = None,
) -> list[CloseNearMissCounterfactualRow]:
    margin_rows = build_prefix_margin_genesis_rows(
        transition_rows=transition_rows,
        phase_rows=phase_rows,
    )
    by_family: dict[tuple[str, int], list[PrefixMarginGenesisRow]] = {}
    for row in margin_rows:
        by_family.setdefault((row.scope, row.parent_residue), []).append(row)

    result: list[CloseNearMissCounterfactualRow] = []
    for family_key in sorted(by_family):
        family = by_family[family_key]
        close_rows = [row for row in family if row.is_close]
        near_rows = [row for row in family if row.is_near_miss]
        if len(close_rows) != 1 or not near_rows:
            continue
        close = close_rows[0]
        near = sorted(
            near_rows,
            key=lambda row: (-Fraction(row.actual_phase_margin), row.child_residue),
        )[0]
        modulus = _child_modulus_from_scope(close.scope)
        result.append(
            CloseNearMissCounterfactualRow(
                scope=close.scope,
                parent_residue=close.parent_residue,
                close_child_residue=close.child_residue,
                near_miss_child_residue=near.child_residue,
                close_remainder=close.new_prime_remainder,
                near_miss_remainder=near.new_prime_remainder,
                close_margin=close.actual_phase_margin,
                near_miss_margin=near.actual_phase_margin,
                margin_gap=_format_fraction(
                    Fraction(close.actual_phase_margin) - Fraction(near.actual_phase_margin)
                ),
                close_rank=close.actual_phase_rank,
                near_miss_rank=near.actual_phase_rank,
                prefix_sequence_match=(
                    close.prefix_transition_sequence == near.prefix_transition_sequence
                ),
                prefix_component_delta_match=(
                    close.prefix_component_delta_sequence
                    == near.prefix_component_delta_sequence
                ),
                close_prefinal_width=close.prefix_max_component_width,
                near_miss_prefinal_width=near.prefix_max_component_width,
                width_delta=_format_fraction(
                    Fraction(close.prefix_max_component_width)
                    - Fraction(near.prefix_max_component_width)
                ),
                reflection_pair_match=(
                    close.new_prime_remainder % modulus
                    == (-near.new_prime_remainder) % modulus
                ),
            )
        )
    return result


def write_margin_genesis_artifacts(
    *,
    margin_path: str | Path = DEFAULT_PREFIX_MARGIN_GENESIS_CSV,
    counterfactual_path: str | Path = DEFAULT_CLOSE_NEARMISS_COUNTERFACTUAL_CSV,
    figure_path: str | Path = DEFAULT_MARGIN_GENESIS_FIGURE,
) -> None:
    rows = read_residual_state_transition_csv()
    phase_rows = read_phase_gate_lift_diagnostics_csv()
    margin_rows = build_prefix_margin_genesis_rows(
        transition_rows=rows,
        phase_rows=phase_rows,
    )
    counterfactual_rows = build_close_nearmiss_counterfactual_rows(
        transition_rows=rows,
        phase_rows=phase_rows,
    )
    write_dataclass_csv(margin_rows, margin_path, PrefixMarginGenesisRow)
    write_dataclass_csv(
        counterfactual_rows,
        counterfactual_path,
        CloseNearMissCounterfactualRow,
    )
    write_margin_genesis_figure(margin_rows, figure_path)


def read_prefix_margin_genesis_csv(
    path: str | Path = DEFAULT_PREFIX_MARGIN_GENESIS_CSV,
) -> list[PrefixMarginGenesisRow]:
    return _read_dataclass_csv(path, PrefixMarginGenesisRow)


def read_close_nearmiss_counterfactual_csv(
    path: str | Path = DEFAULT_CLOSE_NEARMISS_COUNTERFACTUAL_CSV,
) -> list[CloseNearMissCounterfactualRow]:
    return _read_dataclass_csv(path, CloseNearMissCounterfactualRow)


def write_margin_genesis_figure(
    rows: Iterable[PrefixMarginGenesisRow],
    output_path: str | Path = DEFAULT_MARGIN_GENESIS_FIGURE,
) -> None:
    if "MPLCONFIGDIR" not in os.environ:
        os.environ["MPLCONFIGDIR"] = str(
            Path(tempfile.gettempdir()) / "primeclock-matplotlib"
        )
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    row_list = list(rows)
    by_role = {
        "close": [row for row in row_list if row.lineage_role == "close"],
        "near_miss": [row for row in row_list if row.lineage_role == "near_miss"],
        "capacity_nonclose": [
            row for row in row_list if row.lineage_role == "capacity_nonclose"
        ],
    }
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), constrained_layout=True)
    labels = list(by_role)
    axes[0].boxplot(
        [
            [float(Fraction(row.prefix_score_combined)) for row in by_role[label]]
            for label in labels
        ],
        labels=labels,
        showfliers=False,
    )
    axes[0].set_title("Prefix-only combined score")
    axes[0].tick_params(axis="x", rotation=15)
    axes[0].grid(axis="y", alpha=0.25)

    axes[1].boxplot(
        [
            [float(Fraction(row.actual_phase_margin)) for row in by_role[label]]
            for label in labels
        ],
        labels=labels,
        showfliers=False,
    )
    axes[1].set_title("Terminal phase margin")
    axes[1].tick_params(axis="x", rotation=15)
    axes[1].grid(axis="y", alpha=0.25)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def write_dataclass_csv(rows: Iterable[object], output_path: str | Path, row_type: type) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(row_type.__dataclass_fields__.keys())
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def _prefix_close_rates(
    rows: Iterable[ResidualStateTransitionRow],
) -> dict[tuple[str, str], Fraction]:
    rates: dict[tuple[str, str], Fraction] = {}
    for row in build_prefix_grammar_enrichment_rows(rows):
        rates[(row.scope, row.prefix_transition_sequence)] = Fraction(row.prefix_close_rate)
    return rates


def _prefix_delta_sequences_by_lineage(
    rows: Iterable[ResidualStateTransitionRow],
) -> dict[str, str]:
    by_lineage: dict[str, list[ResidualStateTransitionRow]] = {}
    for row in rows:
        by_lineage.setdefault(row.lineage_id, []).append(row)
    return {
        lineage_id: ">".join(
            str(row.component_delta)
            for row in sorted(lineage_rows, key=lambda row: row.layer_k)[:-1]
        )
        for lineage_id, lineage_rows in by_lineage.items()
    }


def _prefix_capacity_for_final_prime(
    prefinal: PrefixMarginGenesisRow | ResidualStateTransitionRow,
    phase_row: PhaseGateLiftDiagnosticRow,
) -> bool:
    return (
        prefinal.new_component_count == 1
        and Fraction(prefinal.total_residual_measure) <= Fraction(1, phase_row.new_prime)
    )


def _child_modulus_from_scope(scope: str) -> int:
    if scope.startswith("B5"):
        return 11
    if scope.startswith("B6"):
        return 13
    if scope.startswith("B7"):
        return 17
    raise ValueError(f"unsupported scope: {scope}")


def _format_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _read_dataclass_csv(path: str | Path, row_type: type):
    int_fields = {
        "parent_residue",
        "child_residue",
        "new_prime_remainder",
        "prefix_component_count",
        "actual_phase_rank",
        "close_child_residue",
        "near_miss_child_residue",
        "close_remainder",
        "near_miss_remainder",
        "close_rank",
        "near_miss_rank",
    }
    bool_fields = {
        "is_close",
        "is_near_miss",
        "prefix_sequence_match",
        "prefix_component_delta_match",
        "reflection_pair_match",
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


def margin_genesis_signature(row: object) -> tuple[object, ...]:
    return row_signature(row)
