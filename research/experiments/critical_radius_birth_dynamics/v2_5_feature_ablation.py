"""Source-only feature ablation diagnostics for PRC v2.5."""

from __future__ import annotations

import csv
import os
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Callable, Iterable

from v2_5_lineage_grammar import build_lineage_grammar_rows
from v2_5_residual_dynamics import (
    ResidualStateTransitionRow,
    child_gcd_stratum,
    final_rows_by_lineage,
    prefinal_rows_by_lineage,
    read_residual_state_transition_csv,
    row_signature,
    transition_sequences_by_lineage,
)

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_FEATURE_ABLATION_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_feature_ablation_v0_1.csv"
)
DEFAULT_FEATURE_ABLATION_FIGURE = (
    EXPERIMENT_DIR / "figures" / "v2_5" / "prc_v2_5_feature_ablation_v0_1.png"
)


@dataclass(frozen=True)
class FeatureAblationRow:
    feature_set: str
    scope: str
    candidate_count: int
    close_count: int
    top_k_hit_rate: str
    false_positive_rate: str
    near_miss_recovery: str
    diagnostic: str


def build_feature_ablation_rows(
    transition_rows: Iterable[ResidualStateTransitionRow] | None = None,
) -> list[FeatureAblationRow]:
    """Compare simple feature families for close-lineage ranking diagnostics."""
    rows = (
        list(transition_rows)
        if transition_rows is not None
        else read_residual_state_transition_csv()
    )
    final_rows = final_rows_by_lineage(rows)
    prefinal_rows = prefinal_rows_by_lineage(rows)
    sequences = transition_sequences_by_lineage(rows)
    grammar_rates = _grammar_close_rates(rows)

    contexts = {
        "all": list(final_rows.values()),
        **{
            scope: [row for row in final_rows.values() if row.scope == scope]
            for scope in sorted({row.scope for row in final_rows.values()})
        },
    }
    feature_scores = _feature_score_functions(
        prefinal_rows=prefinal_rows,
        sequences=sequences,
        grammar_rates=grammar_rates,
    )

    result: list[FeatureAblationRow] = []
    for feature_set, score_fn in feature_scores.items():
        for scope, scope_rows in contexts.items():
            result.append(_score_feature_set(feature_set, scope, scope_rows, score_fn))
    return result


def write_feature_ablation_artifacts(
    *,
    csv_path: str | Path = DEFAULT_FEATURE_ABLATION_CSV,
    figure_path: str | Path = DEFAULT_FEATURE_ABLATION_FIGURE,
) -> None:
    rows = build_feature_ablation_rows()
    write_dataclass_csv(rows, csv_path, FeatureAblationRow)
    write_feature_ablation_figure(rows, figure_path)


def read_feature_ablation_csv(
    path: str | Path = DEFAULT_FEATURE_ABLATION_CSV,
) -> list[FeatureAblationRow]:
    return _read_dataclass_csv(path, FeatureAblationRow)


def write_feature_ablation_figure(
    rows: Iterable[FeatureAblationRow],
    output_path: str | Path = DEFAULT_FEATURE_ABLATION_FIGURE,
) -> None:
    if "MPLCONFIGDIR" not in os.environ:
        os.environ["MPLCONFIGDIR"] = str(
            Path(tempfile.gettempdir()) / "primeclock-matplotlib"
        )
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    row_list = [row for row in rows if row.scope == "all"]
    labels = [row.feature_set for row in row_list]
    values = [float(Fraction(row.top_k_hit_rate)) for row in row_list]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.bar(labels, values, color="#2b8cbe")
    ax.set_title("PRC v2.5 feature ablation seed")
    ax.set_ylabel("top-k close hit rate")
    ax.set_ylim(0, 1.05)
    ax.tick_params(axis="x", rotation=28)
    ax.grid(axis="y", alpha=0.25)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
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


def _feature_score_functions(
    *,
    prefinal_rows: dict[str, ResidualStateTransitionRow],
    sequences: dict[str, tuple[str, ...]],
    grammar_rates: dict[tuple[str, str], Fraction],
) -> dict[str, Callable[[ResidualStateTransitionRow], Fraction]]:
    def prefinal(row: ResidualStateTransitionRow) -> ResidualStateTransitionRow:
        return prefinal_rows[row.lineage_id]

    def width_only(row: ResidualStateTransitionRow) -> Fraction:
        return Fraction(prefinal(row).max_component_width)

    def capacity_only(row: ResidualStateTransitionRow) -> Fraction:
        return Fraction(1 if row.capacity_pass else 0)

    def phase_margin_only(row: ResidualStateTransitionRow) -> Fraction:
        return Fraction(row.phase_margin) if row.phase_margin else Fraction(-10**9)

    def state_features(row: ResidualStateTransitionRow) -> Fraction:
        before = prefinal(row)
        return Fraction(before.max_component_width) - before.new_component_count

    def transition_grammar(row: ResidualStateTransitionRow) -> Fraction:
        prefix = ">".join(sequences[row.lineage_id][:-1])
        return grammar_rates.get((row.scope, prefix), Fraction(0))

    def arithmetic_strata(row: ResidualStateTransitionRow) -> Fraction:
        return Fraction(1 if child_gcd_stratum(row) > 1 else 0)

    def state_plus_grammar(row: ResidualStateTransitionRow) -> Fraction:
        return state_features(row) + transition_grammar(row)

    def state_grammar_phase(row: ResidualStateTransitionRow) -> Fraction:
        return phase_margin_only(row) * 1000 + state_plus_grammar(row)

    def state_grammar_phase_arithmetic(row: ResidualStateTransitionRow) -> Fraction:
        return state_grammar_phase(row) + arithmetic_strata(row)

    return {
        "width only": width_only,
        "capacity only": capacity_only,
        "phase margin only": phase_margin_only,
        "state features": state_features,
        "transition grammar": transition_grammar,
        "arithmetic strata": arithmetic_strata,
        "state + grammar": state_plus_grammar,
        "state + grammar + phase margin": state_grammar_phase,
        "state + grammar + phase margin + arithmetic": state_grammar_phase_arithmetic,
    }


def _grammar_close_rates(
    rows: Iterable[ResidualStateTransitionRow],
) -> dict[tuple[str, str], Fraction]:
    grammar_rows = build_lineage_grammar_rows(rows)
    rates: dict[tuple[str, str], list[tuple[int, int]]] = {}
    for row in grammar_rows:
        prefix = ">".join(row.transition_sequence.split(">")[:-1])
        rates.setdefault((row.scope, prefix), []).append((row.close_count, row.lineage_count))
    return {
        key: Fraction(sum(close for close, _count in values), sum(count for _close, count in values))
        for key, values in rates.items()
    }


def _score_feature_set(
    feature_set: str,
    scope: str,
    rows: list[ResidualStateTransitionRow],
    score_fn: Callable[[ResidualStateTransitionRow], Fraction],
) -> FeatureAblationRow:
    close_count = sum(row.is_close for row in rows)
    if close_count == 0:
        return FeatureAblationRow(
            feature_set,
            scope,
            len(rows),
            close_count,
            "0",
            "0",
            "0",
            "no close rows in this scope",
        )
    ranked = sorted(
        rows,
        key=lambda row: (-score_fn(row), row.scope, row.lineage_id),
    )
    top_k = ranked[:close_count]
    hits = sum(row.is_close for row in top_k)
    near_miss_total = sum(row.lineage_role == "near_miss" for row in rows)
    near_miss_top = sum(row.lineage_role == "near_miss" for row in top_k)
    return FeatureAblationRow(
        feature_set=feature_set,
        scope=scope,
        candidate_count=len(rows),
        close_count=close_count,
        top_k_hit_rate=f"{hits}/{close_count}",
        false_positive_rate=f"{close_count - hits}/{close_count}",
        near_miss_recovery=(
            f"{near_miss_top}/{near_miss_total}" if near_miss_total else "0"
        ),
        diagnostic="ranking diagnostic; not a statistical model",
    )


def _read_dataclass_csv(path: str | Path, row_type: type) -> list[FeatureAblationRow]:
    int_fields = {"candidate_count", "close_count"}
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for raw_row in csv.DictReader(handle):
            values = dict(raw_row)
            for field in int_fields:
                values[field] = int(values[field])
            rows.append(row_type(**values))
    return rows


def feature_ablation_signature(row: FeatureAblationRow) -> tuple[object, ...]:
    return row_signature(row)
