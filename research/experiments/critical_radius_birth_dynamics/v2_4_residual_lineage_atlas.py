"""Source-only exact residual lineage atlas for PRC v2.4."""

from __future__ import annotations

import csv
import os
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_RESIDUAL_LINEAGE_ATLAS_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_exact_residual_lineage_atlas_v0_1.csv"
)
DEFAULT_RESIDUAL_LINEAGE_ATLAS_SUMMARY_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_lineage_atlas_summary_v0_1.csv"
)
DEFAULT_LINEAGE_BIRTH_VS_NONBIRTH_FIGURE = (
    EXPERIMENT_DIR
    / "figures"
    / "v2_4"
    / "prc_v2_4_lineage_atlas_birth_vs_nonbirth_v0_1.png"
)
DEFAULT_LINEAGE_CAPACITY_CONTROLS_FIGURE = (
    EXPERIMENT_DIR
    / "figures"
    / "v2_4"
    / "prc_v2_4_lineage_atlas_capacity_controls_v0_1.png"
)

if str(EXPERIMENT_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_DIR))

from tools import (  # noqa: E402
    exact_arc_intervals_for_residue,
    first_primes,
    format_fraction,
    format_intervals,
    interval_length,
    primorial,
    residue_uncovered_intervals,
)
from v2_4_nonbirth_controls import (  # noqa: E402
    read_transition_itinerary_control_csv,
)
from v2_4_transition_pilot import (  # noqa: E402
    DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV,
    DEFAULT_B5_TRANSITION_PILOT_CSV,
    DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV,
    B5GapCloseTransitionPilotRow,
    TransitionProbeRow,
    circular_components,
    classify_canonical_transition,
    component_transition_stats,
    parse_interval_list,
    read_b5_gap_close_transition_pilot_csv,
)


@dataclass(frozen=True)
class ResidualLineageAtlasRow:
    scope: str
    control_group: str
    family_parent_residue: int
    child_residue: int
    final_remainder: int
    layer_k: int
    layer_residue: int
    is_birth: bool
    is_close: bool
    is_capacity_satisfied: bool
    old_component_count: int
    new_component_count: int
    uncovered_measure: str
    component_endpoints: str
    transition_label: str
    component_delta: int


@dataclass(frozen=True)
class ResidualLineageAtlasSummaryRow:
    metric: str
    scope: str
    value: str
    note: str


def build_residual_lineage_atlas_rows() -> list[ResidualLineageAtlasRow]:
    """Build exact k=1..7 residual lineages for birth and non-birth controls."""
    rows: list[ResidualLineageAtlasRow] = []
    for final_row in _birth_parent_sibling_final_rows():
        rows.extend(
            _lineage_rows(
                scope=final_row.scope,
                control_group="birth_parent_sibling",
                family_parent_residue=final_row.birth_parent_residue,
                child_k=_child_k_from_scope(final_row.scope),
                child_residue=final_row.child_residue,
                final_remainder=final_row.new_prime_remainder,
                is_birth=final_row.is_birth,
                is_close=final_row.is_close,
                is_capacity_satisfied=False,
            )
        )
    for scope, final_row in _capacity_nonclose_final_rows():
        rows.extend(
            _lineage_rows(
                scope=scope,
                control_group="capacity_nonclose_control",
                family_parent_residue=final_row.parent_residue,
                child_k=final_row.child_k,
                child_residue=final_row.child_residue,
                final_remainder=final_row.new_prime_remainder,
                is_birth=final_row.is_b5_birth,
                is_close=classify_canonical_transition(final_row) == "close",
                is_capacity_satisfied=True,
            )
        )
    return rows


def build_residual_lineage_atlas_summary_rows(
    atlas_rows: Iterable[ResidualLineageAtlasRow] | None = None,
) -> list[ResidualLineageAtlasSummaryRow]:
    """Summarize atlas counts used by Gate R."""
    rows = list(atlas_rows) if atlas_rows is not None else build_residual_lineage_atlas_rows()
    final_rows = [row for row in rows if row.layer_k == _child_k_from_scope(row.scope)]
    sibling_final = [
        row for row in final_rows if row.control_group == "birth_parent_sibling"
    ]
    capacity_final = [
        row for row in final_rows if row.control_group == "capacity_nonclose_control"
    ]
    sibling_birth = [row for row in sibling_final if row.is_birth]
    sibling_nonbirth = [row for row in sibling_final if not row.is_birth]
    capacity_by_scope = Counter(row.scope for row in capacity_final)
    final_by_scope = Counter(row.scope for row in final_rows)
    capacity_gate = _capacity_gate_family_counts()
    summary = [
        ResidualLineageAtlasSummaryRow(
            "atlas_rows",
            "all",
            str(len(rows)),
            "all exact residual lineage rows across k=1..7 scopes",
        ),
        ResidualLineageAtlasSummaryRow(
            "final_lifts",
            "all",
            str(len(final_rows)),
            "one final lift per represented lineage",
        ),
        ResidualLineageAtlasSummaryRow(
            "birth_sibling_final_lifts",
            "all",
            str(len(sibling_birth)),
            "checked B5/B6/B7 birth siblings",
        ),
        ResidualLineageAtlasSummaryRow(
            "nonbirth_sibling_final_lifts",
            "all",
            str(len(sibling_nonbirth)),
            "same-family non-birth sibling controls",
        ),
        ResidualLineageAtlasSummaryRow(
            "capacity_nonclose_final_lifts",
            "all",
            str(len(capacity_final)),
            "capacity-satisfied lifts that still do not close",
        ),
        ResidualLineageAtlasSummaryRow(
            "nonbirth_close_final_lifts",
            "all",
            str(sum(row.is_close and not row.is_birth for row in final_rows)),
            "would indicate close/birth mismatch",
        ),
        ResidualLineageAtlasSummaryRow(
            "capacity_gate_close_families",
            "all",
            str(capacity_gate["close"]),
            "all checked close families satisfy single-component capacity",
        ),
        ResidualLineageAtlasSummaryRow(
            "capacity_gate_nonclose_families",
            "all",
            str(capacity_gate["nonclose"]),
            "capacity gate is not sufficient by itself",
        ),
    ]
    for scope in sorted(final_by_scope):
        summary.append(
            ResidualLineageAtlasSummaryRow(
                "final_lifts_by_scope",
                scope,
                str(final_by_scope[scope]),
                "represented final lineages by scope",
            )
        )
    for scope in sorted(capacity_by_scope):
        summary.append(
            ResidualLineageAtlasSummaryRow(
                "capacity_nonclose_final_lifts_by_scope",
                scope,
                str(capacity_by_scope[scope]),
                "capacity-satisfied non-close final lineages by scope",
            )
        )
    return summary


def write_residual_lineage_atlas_artifacts(
    *,
    atlas_path: str | Path = DEFAULT_RESIDUAL_LINEAGE_ATLAS_CSV,
    summary_path: str | Path = DEFAULT_RESIDUAL_LINEAGE_ATLAS_SUMMARY_CSV,
    birth_vs_nonbirth_figure: str | Path = DEFAULT_LINEAGE_BIRTH_VS_NONBIRTH_FIGURE,
    capacity_controls_figure: str | Path = DEFAULT_LINEAGE_CAPACITY_CONTROLS_FIGURE,
) -> None:
    rows = build_residual_lineage_atlas_rows()
    summary_rows = build_residual_lineage_atlas_summary_rows(rows)
    write_dataclass_csv(rows, atlas_path, ResidualLineageAtlasRow)
    write_dataclass_csv(summary_rows, summary_path, ResidualLineageAtlasSummaryRow)
    write_birth_vs_nonbirth_figure(rows, birth_vs_nonbirth_figure)
    write_capacity_controls_figure(summary_rows, capacity_controls_figure)


def read_residual_lineage_atlas_csv(
    path: str | Path = DEFAULT_RESIDUAL_LINEAGE_ATLAS_CSV,
) -> list[ResidualLineageAtlasRow]:
    return _read_dataclass_csv(path, ResidualLineageAtlasRow)


def read_residual_lineage_atlas_summary_csv(
    path: str | Path = DEFAULT_RESIDUAL_LINEAGE_ATLAS_SUMMARY_CSV,
) -> list[ResidualLineageAtlasSummaryRow]:
    return _read_dataclass_csv(path, ResidualLineageAtlasSummaryRow)


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


def write_birth_vs_nonbirth_figure(
    rows: Iterable[ResidualLineageAtlasRow],
    output_path: str | Path,
) -> None:
    if "MPLCONFIGDIR" not in os.environ:
        os.environ["MPLCONFIGDIR"] = str(
            Path(tempfile.gettempdir()) / "primeclock-matplotlib"
        )
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    row_list = list(rows)
    groups = {
        "birth sibling": [
            row for row in row_list if row.control_group == "birth_parent_sibling" and row.is_birth
        ],
        "non-birth sibling": [
            row for row in row_list if row.control_group == "birth_parent_sibling" and not row.is_birth
        ],
        "capacity non-close": [
            row for row in row_list if row.control_group == "capacity_nonclose_control"
        ],
    }
    fig, ax = plt.subplots(figsize=(9, 5.2))
    for label, group_rows in groups.items():
        by_layer: dict[int, list[Fraction]] = {}
        for row in group_rows:
            by_layer.setdefault(row.layer_k, []).append(Fraction(row.uncovered_measure))
        layers = sorted(by_layer)
        values = [
            float(sum(by_layer[layer], Fraction(0)) / len(by_layer[layer]))
            for layer in layers
        ]
        ax.plot(layers, values, marker="o", label=label)
    ax.set_title("PRC v2.4 exact residual lineage atlas")
    ax.set_xlabel("layer k")
    ax.set_ylabel("mean residual measure")
    ax.grid(alpha=0.25)
    ax.legend()
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def write_capacity_controls_figure(
    summary_rows: Iterable[ResidualLineageAtlasSummaryRow],
    output_path: str | Path,
) -> None:
    if "MPLCONFIGDIR" not in os.environ:
        os.environ["MPLCONFIGDIR"] = str(
            Path(tempfile.gettempdir()) / "primeclock-matplotlib"
        )
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    by_metric = {row.metric: int(row.value) for row in summary_rows if row.scope == "all"}
    labels = ["close families", "non-close families"]
    values = [
        by_metric["capacity_gate_close_families"],
        by_metric["capacity_gate_nonclose_families"],
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    bars = ax.bar(labels, values, color=["#1b7837", "#7f7f7f"])
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(value),
            ha="center",
            va="bottom",
        )
    ax.set_title("Capacity gate is necessary-looking, not sufficient")
    ax.set_ylabel("single-component capacity families")
    ax.grid(axis="y", alpha=0.25)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def _birth_parent_sibling_final_rows():
    return read_transition_itinerary_control_csv()


def _capacity_nonclose_final_rows() -> list[tuple[str, TransitionProbeRow]]:
    result: list[tuple[str, TransitionProbeRow]] = []
    for scope, rows in _transition_scope_rows():
        by_parent: dict[int, list[TransitionProbeRow]] = {}
        for row in rows:
            by_parent.setdefault(row.parent_residue, []).append(row)
        for parent_rows in by_parent.values():
            first = parent_rows[0]
            old_intervals = parse_interval_list(first.old_gap_boundary_endpoints)
            old_components = circular_components(old_intervals)
            old_measure = sum(interval_length(interval) for interval in old_intervals)
            capacity_satisfied = (
                len(old_components) == 1 and old_measure <= Fraction(1, first.new_prime)
            )
            has_close = any(
                classify_canonical_transition(row) == "close" for row in parent_rows
            )
            if capacity_satisfied and not has_close:
                result.extend((scope, row) for row in parent_rows)
    return result


def _transition_scope_rows() -> list[tuple[str, list[TransitionProbeRow]]]:
    return [
        (
            "B5_birth_parent_siblings",
            read_b5_gap_close_transition_pilot_csv(DEFAULT_B5_TRANSITION_PILOT_CSV),
        ),
        (
            "B6_birth_parent_siblings",
            read_b5_gap_close_transition_pilot_csv(DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV),
        ),
        (
            "B7_birth_parent_siblings",
            read_b5_gap_close_transition_pilot_csv(DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV),
        ),
    ]


def _lineage_rows(
    *,
    scope: str,
    control_group: str,
    family_parent_residue: int,
    child_k: int,
    child_residue: int,
    final_remainder: int,
    is_birth: bool,
    is_close: bool,
    is_capacity_satisfied: bool,
) -> list[ResidualLineageAtlasRow]:
    rows: list[ResidualLineageAtlasRow] = []
    previous_gaps: list[tuple[Fraction, Fraction]] | None = None
    previous_k = 0
    previous_modulus = 1
    previous_residue = 0
    for layer_k in range(1, child_k + 1):
        primes = first_primes(layer_k)
        layer_prime = primes[-1]
        layer_modulus = primorial(primes)
        layer_residue = child_residue % layer_modulus
        gaps = residue_uncovered_intervals(layer_residue, primes)
        new_component_count = len(circular_components(gaps))
        transition_label = "start"
        component_delta = 0
        old_component_count = 0
        if previous_gaps is not None:
            old_component_count = len(circular_components(previous_gaps))
            transition_row = B5GapCloseTransitionPilotRow(
                parent_k=previous_k,
                child_k=layer_k,
                parent_modulus=previous_modulus,
                child_modulus=layer_modulus,
                parent_residue=previous_residue,
                child_residue=layer_residue,
                new_prime=layer_prime,
                new_prime_remainder=layer_residue % layer_prime,
                old_gap_count=len(previous_gaps),
                old_gap_boundary_endpoints=format_intervals(previous_gaps),
                new_prime_closed_arc_boundary_endpoints=format_intervals(
                    exact_arc_intervals_for_residue(layer_residue, layer_prime)
                ),
                closed_gap_count=0,
                remaining_gap_count=len(gaps),
                remaining_gap_boundary_endpoints=format_intervals(gaps),
                transition_type="close" if not gaps else "not_close",
                is_b5_birth=layer_k == child_k and is_birth,
            )
            transition_label = classify_canonical_transition(transition_row)
            component_delta = component_transition_stats(transition_row).component_delta
        rows.append(
            ResidualLineageAtlasRow(
                scope=scope,
                control_group=control_group,
                family_parent_residue=family_parent_residue,
                child_residue=child_residue,
                final_remainder=final_remainder,
                layer_k=layer_k,
                layer_residue=layer_residue,
                is_birth=is_birth,
                is_close=is_close,
                is_capacity_satisfied=is_capacity_satisfied,
                old_component_count=old_component_count,
                new_component_count=new_component_count,
                uncovered_measure=format_fraction(
                    sum(interval_length(interval) for interval in gaps)
                ),
                component_endpoints=format_intervals(gaps),
                transition_label=transition_label,
                component_delta=component_delta,
            )
        )
        previous_gaps = gaps
        previous_k = layer_k
        previous_modulus = layer_modulus
        previous_residue = layer_residue
    return rows


def _capacity_gate_family_counts() -> Counter[str]:
    counts: Counter[str] = Counter()
    for _scope, rows in _transition_scope_rows():
        by_parent: dict[int, list[TransitionProbeRow]] = {}
        for row in rows:
            by_parent.setdefault(row.parent_residue, []).append(row)
        for parent_rows in by_parent.values():
            first = parent_rows[0]
            old_intervals = parse_interval_list(first.old_gap_boundary_endpoints)
            capacity = (
                len(circular_components(old_intervals)) == 1
                and sum(interval_length(interval) for interval in old_intervals)
                <= Fraction(1, first.new_prime)
            )
            has_close = any(
                classify_canonical_transition(row) == "close" for row in parent_rows
            )
            if capacity and has_close:
                counts["close"] += 1
            elif capacity:
                counts["nonclose"] += 1
    return counts


def _child_k_from_scope(scope: str) -> int:
    if scope.startswith("B5"):
        return 5
    if scope.startswith("B6"):
        return 6
    if scope.startswith("B7"):
        return 7
    raise ValueError(f"unsupported atlas scope: {scope}")


def _read_dataclass_csv(path: str | Path, row_type: type):
    int_fields = {
        "family_parent_residue",
        "child_residue",
        "final_remainder",
        "layer_k",
        "layer_residue",
        "old_component_count",
        "new_component_count",
        "component_delta",
    }
    bool_fields = {"is_birth", "is_close", "is_capacity_satisfied"}
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
