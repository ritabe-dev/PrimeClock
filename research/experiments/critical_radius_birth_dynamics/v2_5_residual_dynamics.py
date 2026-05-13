"""Source-only residual dynamics model for PRC v2.5."""

from __future__ import annotations

import csv
import math
import os
import tempfile
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from tools import format_fraction, interval_length
from v2_4_phase_gate_diagnostics import (
    PhaseGateLiftDiagnosticRow,
    build_phase_gate_lift_diagnostic_rows,
)
from v2_4_residual_lineage_atlas import (
    ResidualLineageAtlasRow,
    build_residual_lineage_atlas_rows,
)
from v2_4_transition_pilot import circular_components, parse_interval_list

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_RESIDUAL_STATE_TRANSITIONS_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_residual_state_transitions_v0_1.csv"
)
DEFAULT_RESIDUAL_LINEAGE_SUMMARY_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_residual_lineage_summary_v0_1.csv"
)

LINEAGE_CLOSE = "close"
LINEAGE_NONCLOSE = "nonclose"
LINEAGE_NEAR_MISS = "near_miss"
LINEAGE_CAPACITY_NONCLOSE = "capacity_nonclose"

SCOPE_TO_PHASE_SCOPE = {
    "B5_birth_parent_siblings": "B4_to_B5_full",
    "B6_birth_parent_siblings": "B5_to_B6_full",
    "B7_birth_parent_siblings": "B6_to_B7_full",
}


@dataclass(frozen=True)
class ResidualStateTransitionRow:
    scope: str
    lineage_id: str
    layer_k: int
    residue_mod_m: int
    old_component_count: int
    new_component_count: int
    component_delta: int
    total_residual_measure: str
    max_component_width: str
    transition_label: str
    phase_margin: str
    capacity_pass: bool
    is_close: bool
    is_birth: bool
    lineage_role: str


@dataclass(frozen=True)
class ResidualLineageSummaryRow:
    metric: str
    scope: str
    lineage_role: str
    value: str
    note: str


def build_residual_state_transition_rows(
    *,
    atlas_rows: Iterable[ResidualLineageAtlasRow] | None = None,
    phase_rows: Iterable[PhaseGateLiftDiagnosticRow] | None = None,
) -> list[ResidualStateTransitionRow]:
    """Build the canonical v2.5 residual state model from exact interval rows."""
    atlas = list(atlas_rows) if atlas_rows is not None else build_residual_lineage_atlas_rows()
    phase = list(phase_rows) if phase_rows is not None else build_phase_gate_lift_diagnostic_rows()
    phase_by_child = _phase_rows_by_atlas_child(phase)
    near_miss_children = _near_miss_child_keys(phase)
    roles = _lineage_roles(atlas, near_miss_children)

    rows: list[ResidualStateTransitionRow] = []
    for atlas_row in atlas:
        lineage_id = _lineage_id(atlas_row)
        phase_row = phase_by_child.get(
            (SCOPE_TO_PHASE_SCOPE[atlas_row.scope], atlas_row.child_residue)
        )
        final_layer = atlas_row.layer_k == _child_k_from_scope(atlas_row.scope)
        rows.append(
            ResidualStateTransitionRow(
                scope=atlas_row.scope,
                lineage_id=lineage_id,
                layer_k=atlas_row.layer_k,
                residue_mod_m=atlas_row.layer_residue,
                old_component_count=atlas_row.old_component_count,
                new_component_count=atlas_row.new_component_count,
                component_delta=atlas_row.component_delta,
                total_residual_measure=atlas_row.uncovered_measure,
                max_component_width=_max_component_width(atlas_row.component_endpoints),
                transition_label=atlas_row.transition_label,
                phase_margin=phase_row.phase_margin if final_layer and phase_row else "",
                capacity_pass=phase_row.capacity_pass if final_layer and phase_row else False,
                is_close=atlas_row.is_close if final_layer else False,
                is_birth=atlas_row.is_birth if final_layer else False,
                lineage_role=roles[lineage_id],
            )
        )
    return rows


def build_residual_lineage_summary_rows(
    rows: Iterable[ResidualStateTransitionRow] | None = None,
) -> list[ResidualLineageSummaryRow]:
    """Summarize v2.5 residual dynamics for Gate R checks."""
    row_list = list(rows) if rows is not None else build_residual_state_transition_rows()
    final_rows = [row for row in row_list if _is_final_layer(row)]
    by_role = Counter(row.lineage_role for row in final_rows)
    by_scope = Counter(row.scope for row in final_rows)
    transition_counts = Counter(row.transition_label for row in row_list)
    close_rows = [row for row in final_rows if row.is_close]
    capacity_nonclose = [
        row for row in final_rows if row.lineage_role == LINEAGE_CAPACITY_NONCLOSE
    ]

    summary = [
        ResidualLineageSummaryRow(
            "state_transition_rows",
            "all",
            "all",
            str(len(row_list)),
            "canonical v2.5 residual state rows across represented lineages",
        ),
        ResidualLineageSummaryRow(
            "final_lineages",
            "all",
            "all",
            str(len(final_rows)),
            "one final row per represented lineage",
        ),
        ResidualLineageSummaryRow(
            "final_close_lineages",
            "all",
            LINEAGE_CLOSE,
            str(len(close_rows)),
            "checked close/birth lineages in B5/B6/B7 scopes",
        ),
        ResidualLineageSummaryRow(
            "capacity_nonclose_lineages",
            "all",
            LINEAGE_CAPACITY_NONCLOSE,
            str(len(capacity_nonclose)),
            "capacity-satisfied non-close controls",
        ),
        ResidualLineageSummaryRow(
            "nonbirth_close_lineages",
            "all",
            "all",
            str(sum(row.is_close and not row.is_birth for row in final_rows)),
            "must remain zero for checked scopes",
        ),
        ResidualLineageSummaryRow(
            "positive_phase_close_lineages",
            "all",
            LINEAGE_CLOSE,
            str(sum(Fraction(row.phase_margin) > 0 for row in close_rows)),
            "close rows selected by positive signed phase margin",
        ),
        ResidualLineageSummaryRow(
            "near_miss_lineages",
            "all",
            LINEAGE_NEAR_MISS,
            str(by_role[LINEAGE_NEAR_MISS]),
            "best non-close sibling controls inside close-capable families",
        ),
    ]
    for scope in sorted(by_scope):
        scope_rows = [row for row in final_rows if row.scope == scope]
        summary.append(
            ResidualLineageSummaryRow(
                "final_lineages_by_scope",
                scope,
                "all",
                str(len(scope_rows)),
                "represented final lineages by scope",
            )
        )
        for role in sorted({row.lineage_role for row in scope_rows}):
            summary.append(
                ResidualLineageSummaryRow(
                    "final_lineages_by_role",
                    scope,
                    role,
                    str(sum(row.lineage_role == role for row in scope_rows)),
                    "final lineages by residual-dynamics role",
                )
            )
    for label in sorted(transition_counts):
        summary.append(
            ResidualLineageSummaryRow(
                "transition_label_count",
                "all",
                label,
                str(transition_counts[label]),
                "all layer-to-layer transition labels",
            )
        )
    return summary


def write_residual_dynamics_artifacts(
    *,
    transitions_path: str | Path = DEFAULT_RESIDUAL_STATE_TRANSITIONS_CSV,
    summary_path: str | Path = DEFAULT_RESIDUAL_LINEAGE_SUMMARY_CSV,
) -> None:
    rows = build_residual_state_transition_rows()
    write_dataclass_csv(rows, transitions_path, ResidualStateTransitionRow)
    write_dataclass_csv(
        build_residual_lineage_summary_rows(rows),
        summary_path,
        ResidualLineageSummaryRow,
    )


def read_residual_state_transition_csv(
    path: str | Path = DEFAULT_RESIDUAL_STATE_TRANSITIONS_CSV,
) -> list[ResidualStateTransitionRow]:
    return _read_dataclass_csv(path, ResidualStateTransitionRow)


def read_residual_lineage_summary_csv(
    path: str | Path = DEFAULT_RESIDUAL_LINEAGE_SUMMARY_CSV,
) -> list[ResidualLineageSummaryRow]:
    return _read_dataclass_csv(path, ResidualLineageSummaryRow)


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


def write_residual_dynamics_summary_figure(
    rows: Iterable[ResidualStateTransitionRow],
    output_path: str | Path,
) -> None:
    """Optional compact plot for manual review."""
    if "MPLCONFIGDIR" not in os.environ:
        os.environ["MPLCONFIGDIR"] = str(
            Path(tempfile.gettempdir()) / "primeclock-matplotlib"
        )
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    row_list = list(rows)
    by_role_layer: dict[tuple[str, int], list[Fraction]] = {}
    for row in row_list:
        by_role_layer.setdefault((row.lineage_role, row.layer_k), []).append(
            Fraction(row.total_residual_measure)
        )

    fig, ax = plt.subplots(figsize=(8.5, 5))
    for role in (LINEAGE_CLOSE, LINEAGE_NEAR_MISS, LINEAGE_CAPACITY_NONCLOSE):
        layers = sorted(layer for item_role, layer in by_role_layer if item_role == role)
        values = [
            float(sum(by_role_layer[(role, layer)], Fraction(0)) / len(by_role_layer[(role, layer)]))
            for layer in layers
        ]
        ax.plot(layers, values, marker="o", label=role)
    ax.set_title("PRC v2.5 residual dynamics seed")
    ax.set_xlabel("layer k")
    ax.set_ylabel("mean residual measure")
    ax.grid(alpha=0.25)
    ax.legend()
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def _lineage_id(row: ResidualLineageAtlasRow) -> str:
    return (
        f"{row.scope}:{row.control_group}:"
        f"{row.family_parent_residue}:{row.child_residue}"
    )


def _lineage_roles(
    atlas_rows: Iterable[ResidualLineageAtlasRow],
    near_miss_children: set[tuple[str, int]],
) -> dict[str, str]:
    final_rows = [
        row
        for row in atlas_rows
        if row.layer_k == _child_k_from_scope(row.scope)
    ]
    roles: dict[str, str] = {}
    for row in final_rows:
        key = (SCOPE_TO_PHASE_SCOPE[row.scope], row.child_residue)
        if row.is_close:
            role = LINEAGE_CLOSE
        elif row.control_group == "capacity_nonclose_control":
            role = LINEAGE_CAPACITY_NONCLOSE
        elif key in near_miss_children:
            role = LINEAGE_NEAR_MISS
        else:
            role = LINEAGE_NONCLOSE
        roles[_lineage_id(row)] = role
    return roles


def _near_miss_child_keys(
    phase_rows: Iterable[PhaseGateLiftDiagnosticRow],
) -> set[tuple[str, int]]:
    by_family: dict[tuple[str, int], list[PhaseGateLiftDiagnosticRow]] = {}
    for row in phase_rows:
        by_family.setdefault((row.scope, row.parent_residue), []).append(row)

    near_miss: set[tuple[str, int]] = set()
    for family_rows in by_family.values():
        if not any(row.is_close for row in family_rows):
            continue
        non_close_rows = [row for row in family_rows if not row.is_close]
        if not non_close_rows:
            continue
        best_margin = max(Fraction(row.phase_margin) for row in non_close_rows)
        for row in non_close_rows:
            if Fraction(row.phase_margin) == best_margin:
                near_miss.add((row.scope, row.child_residue))
    return near_miss


def _phase_rows_by_atlas_child(
    phase_rows: Iterable[PhaseGateLiftDiagnosticRow],
) -> dict[tuple[str, int], PhaseGateLiftDiagnosticRow]:
    return {(row.scope, row.child_residue): row for row in phase_rows}


def _max_component_width(component_endpoints: str) -> str:
    components = circular_components(parse_interval_list(component_endpoints))
    if not components:
        return "0"
    widths = [
        sum(interval_length(segment) for segment in component.segments)
        for component in components
    ]
    return format_fraction(max(widths))


def _child_k_from_scope(scope: str) -> int:
    if scope.startswith("B5"):
        return 5
    if scope.startswith("B6"):
        return 6
    if scope.startswith("B7"):
        return 7
    raise ValueError(f"unsupported v2.5 scope: {scope}")


def _is_final_layer(row: ResidualStateTransitionRow) -> bool:
    return row.layer_k == _child_k_from_scope(row.scope)


def final_rows_by_lineage(
    rows: Iterable[ResidualStateTransitionRow],
) -> dict[str, ResidualStateTransitionRow]:
    return {row.lineage_id: row for row in rows if _is_final_layer(row)}


def prefinal_rows_by_lineage(
    rows: Iterable[ResidualStateTransitionRow],
) -> dict[str, ResidualStateTransitionRow]:
    return {
        row.lineage_id: row
        for row in rows
        if row.layer_k == _child_k_from_scope(row.scope) - 1
    }


def transition_sequences_by_lineage(
    rows: Iterable[ResidualStateTransitionRow],
) -> dict[str, tuple[str, ...]]:
    by_lineage: dict[str, list[ResidualStateTransitionRow]] = {}
    for row in rows:
        by_lineage.setdefault(row.lineage_id, []).append(row)
    return {
        lineage_id: tuple(row.transition_label for row in sorted(items, key=lambda row: row.layer_k))
        for lineage_id, items in by_lineage.items()
    }


def child_gcd_stratum(row: ResidualStateTransitionRow) -> int:
    """Return gcd(row residue, M_k) using the row layer modulus."""
    from tools import first_primes, primorial

    return math.gcd(row.residue_mod_m, primorial(first_primes(row.layer_k)))


def _read_dataclass_csv(path: str | Path, row_type: type):
    int_fields = {
        "layer_k",
        "residue_mod_m",
        "old_component_count",
        "new_component_count",
        "component_delta",
    }
    bool_fields = {"capacity_pass", "is_close", "is_birth"}
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
