"""Source-only B8 aperture-orbit diagnostics for PRC v2.5."""

from __future__ import annotations

import csv
import hashlib
import os
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

from tools import (
    exact_arc_intervals_for_residue,
    first_primes,
    format_fraction,
    format_intervals,
    interval_length,
    residue_is_exactly_covered,
    residue_uncovered_intervals,
)
from v2_4_phase_gate_diagnostics import _signed_containment_margin, _unwrap_component
from v2_4_transition_pilot import (
    DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV,
    B5GapCloseTransitionPilotRow,
    TransitionProbeRow,
    circular_components,
    classify_canonical_transition,
    component_transition_stats,
    parse_interval_list,
    read_b5_gap_close_transition_pilot_csv,
    subtract_intervals,
)
from v2_5_b8_targeted_probe import read_b8_high_potential_probe_csv
from v2_5_residual_dynamics import row_signature

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_B8_FAILURE_FORENSICS_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_b8_failure_forensics_v0_1.csv"
)
DEFAULT_B8_PARENT_SELECTION_AUDIT_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_b8_parent_selection_audit_v0_1.csv"
)
DEFAULT_B8_APERTURE_ORBIT_PROBE_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_b8_aperture_orbit_probe_v0_1.csv"
)
DEFAULT_B8_APERTURE_ORBIT_SUMMARY_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_b8_aperture_orbit_summary_v0_1.csv"
)
DEFAULT_B8_BIRTH_OVERLAP_AUDIT_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_b8_birth_overlap_audit_v0_1.csv"
)
DEFAULT_B8_APERTURE_ORBIT_HEATMAP = (
    EXPERIMENT_DIR
    / "figures"
    / "v2_5"
    / "prc_v2_5_b8_aperture_orbit_heatmap_v0_1.png"
)

B8_PARENT_K = 7
B8_CHILD_K = 8
B8_PARENT_MODULUS = 510510
B8_CHILD_MODULUS = 9699690
B8_NEW_PRIME = 19
CAPACITY_TOP_GROUP = "capacity_top_200"
APERTURE_FRONTIER_GROUP = "aperture_frontier_top_400"
NEAR_ZERO_GROUP = "near_zero_margin_200"
ORBIT_DIVERSITY_GROUP = "orbit_diversity_400"
HASH_CONTROL_GROUP = "hash_control_200"


@dataclass(frozen=True)
class B8ParentCandidate:
    parent_residue: int
    parent_component_count: int
    parent_residual_measure: str
    parent_max_component_width: str
    best_lift_remainder: int
    best_child_residue: int
    best_phase_margin: str
    best_aperture_tension: str
    best_transition_label: str
    trim_lift_count: int
    miss_lift_count: int
    close_lift_count: int
    positive_margin_lift_count: int
    parent_mod210: int
    reflection_orbit: str
    width_bucket: str
    hash_score: str


@dataclass(frozen=True)
class B8ParentSeed:
    parent_residue: int
    old_gap_boundary_endpoints: str
    parent_component_count: int
    parent_residual_measure: str
    parent_max_component_width: str
    parent_mod210: int
    reflection_orbit: str
    width_bucket: str
    hash_score: str


@dataclass(frozen=True)
class B8ApertureOrbitProbeRow:
    selection_groups: str
    parent_rank: int
    parent_residue: int
    parent_component_count: int
    parent_residual_measure: str
    parent_max_component_width: str
    parent_mod210: int
    reflection_orbit: str
    capacity_pass: bool
    lift_remainder: int
    child_residue: int
    transition_label: str
    component_delta: int
    phase_margin: str
    phase_rank: int
    aperture_tension: str
    aperture_tension_rank: int
    gap_width: str
    gap_center: str
    slack: str
    nearest_q_grid_distance: str
    is_close: bool


@dataclass(frozen=True)
class B8FailureForensicsRow:
    selection_group: str
    parent_residue: int
    lift_remainder: int
    child_residue: int
    transition_label: str
    phase_margin: str
    phase_rank: int
    aperture_tension: str
    obstruction_bucket: str


@dataclass(frozen=True)
class B8ParentSelectionAuditRow:
    selection_groups: str
    parent_rank: int
    parent_residue: int
    parent_component_count: int
    parent_residual_measure: str
    parent_max_component_width: str
    best_lift_remainder: int
    best_phase_margin: str
    best_aperture_tension: str
    best_transition_label: str
    trim_lift_count: int
    miss_lift_count: int
    close_lift_count: int
    positive_margin_lift_count: int
    selection_failure_reason: str


@dataclass(frozen=True)
class B8ApertureOrbitSummaryRow:
    metric: str
    selection_group: str
    value: str
    note: str


@dataclass(frozen=True)
class B8BirthOverlapAuditRow:
    parent_residue: int
    child_residue: int
    lift_remainder: int
    selection_groups: str
    phase_margin: str
    aperture_tension: str
    parent_uncovered_exact: bool
    child_covered_exact: bool
    child_projects_to_parent: bool
    parent_gap_count_exact: int
    child_gap_count_exact: int
    exact_b8_birth: bool
    audit_status: str


def write_b8_aperture_orbit_artifacts(
    *,
    failure_path: str | Path = DEFAULT_B8_FAILURE_FORENSICS_CSV,
    audit_path: str | Path = DEFAULT_B8_PARENT_SELECTION_AUDIT_CSV,
    probe_path: str | Path = DEFAULT_B8_APERTURE_ORBIT_PROBE_CSV,
    summary_path: str | Path = DEFAULT_B8_APERTURE_ORBIT_SUMMARY_CSV,
    birth_audit_path: str | Path = DEFAULT_B8_BIRTH_OVERLAP_AUDIT_CSV,
    figure_path: str | Path = DEFAULT_B8_APERTURE_ORBIT_HEATMAP,
) -> None:
    candidates = scan_b8_parent_candidates()
    selected = select_b8_aperture_orbit_parents(candidates)
    group_map = _selection_group_map(selected)
    selected_list = _dedup_selected(selected)
    probe_rows = build_b8_aperture_orbit_probe_rows(selected_list, group_map)
    failure_rows = build_b8_failure_forensics_rows()
    audit_rows = build_b8_parent_selection_audit_rows(selected_list, group_map, probe_rows)
    birth_audit_rows = build_b8_birth_overlap_audit_rows(probe_rows)
    summary_rows = build_b8_aperture_orbit_summary_rows(
        probe_rows=probe_rows,
        audit_rows=audit_rows,
        failure_rows=failure_rows,
        birth_audit_rows=birth_audit_rows,
    )
    write_dataclass_csv(failure_rows, failure_path, B8FailureForensicsRow)
    write_dataclass_csv(audit_rows, audit_path, B8ParentSelectionAuditRow)
    write_dataclass_csv(probe_rows, probe_path, B8ApertureOrbitProbeRow)
    write_dataclass_csv(birth_audit_rows, birth_audit_path, B8BirthOverlapAuditRow)
    write_dataclass_csv(summary_rows, summary_path, B8ApertureOrbitSummaryRow)
    write_b8_aperture_orbit_heatmap(probe_rows, figure_path)


def scan_b8_parent_candidates(
    parent_rows: Iterable[TransitionProbeRow] | None = None,
) -> list[B8ParentCandidate]:
    """Build a bounded, stratified B8 parent pool before exact lift scoring."""
    source_rows = (
        list(parent_rows)
        if parent_rows is not None
        else read_b5_gap_close_transition_pilot_csv(DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV)
    )
    seeds: list[B8ParentSeed] = []
    for parent_row in source_rows:
        if classify_canonical_transition(parent_row) == "close":
            continue
        old_intervals = parse_interval_list(parent_row.remaining_gap_boundary_endpoints)
        if not old_intervals:
            continue
        seeds.append(_seed_for_parent(parent_row.child_residue, old_intervals))
    selected_seeds = _prefilter_b8_parent_seeds(seeds)
    return [
        _candidate_for_parent(
            seed.parent_residue,
            parse_interval_list(seed.old_gap_boundary_endpoints),
        )
        for seed in selected_seeds
    ]


def select_b8_aperture_orbit_parents(
    candidates: Sequence[B8ParentCandidate],
) -> dict[str, list[B8ParentCandidate]]:
    """Return deterministic parent selections for B8 source-only probes."""
    by_parent = {candidate.parent_residue: candidate for candidate in candidates}
    capacity_parent_ids = _capacity_top_parent_ids()
    capacity = [by_parent[parent] for parent in capacity_parent_ids if parent in by_parent]
    aperture = sorted(
        candidates,
        key=lambda row: (
            Fraction(row.best_aperture_tension),
            -Fraction(row.best_phase_margin),
            row.parent_residue,
        ),
    )[:400]
    near_zero = sorted(
        [row for row in candidates if Fraction(row.best_phase_margin) < 0],
        key=lambda row: (
            abs(Fraction(row.best_phase_margin)),
            Fraction(row.best_aperture_tension),
            row.parent_residue,
        ),
    )[:200]
    orbit_diversity = _orbit_diversity_selection(candidates, limit=400)
    hash_control = sorted(candidates, key=lambda row: (row.hash_score, row.parent_residue))[:200]
    return {
        CAPACITY_TOP_GROUP: capacity,
        APERTURE_FRONTIER_GROUP: aperture,
        NEAR_ZERO_GROUP: near_zero,
        ORBIT_DIVERSITY_GROUP: orbit_diversity,
        HASH_CONTROL_GROUP: hash_control,
    }


def build_b8_aperture_orbit_probe_rows(
    selected: Sequence[B8ParentCandidate] | dict[str, list[B8ParentCandidate]] | None = None,
    group_map: dict[int, set[str]] | None = None,
) -> list[B8ApertureOrbitProbeRow]:
    if selected is None:
        selected_by_group = select_b8_aperture_orbit_parents(scan_b8_parent_candidates())
        selected_list = _dedup_selected(selected_by_group)
        groups = _selection_group_map(selected_by_group)
    elif isinstance(selected, dict):
        selected_list = _dedup_selected(selected)
        groups = _selection_group_map(selected)
    else:
        selected_list = list(selected)
        groups = group_map or {row.parent_residue: set() for row in selected_list}

    old_interval_map = _old_intervals_for_b8_parents(
        [row.parent_residue for row in selected_list]
    )
    result: list[B8ApertureOrbitProbeRow] = []
    for parent_rank, parent in enumerate(selected_list, start=1):
        old_intervals = old_interval_map[parent.parent_residue]
        transition_rows = _b8_transition_rows_for_parent(parent.parent_residue, old_intervals)
        metrics = [(row, aperture_metrics_for_row(row)) for row in transition_rows]
        phase_rank = _rank_map(metrics, key_index="phase_margin", descending=True)
        tension_rank = _rank_map(metrics, key_index="aperture_tension", descending=False)
        selection_groups = ";".join(sorted(groups.get(parent.parent_residue, ())))
        for row, metric in sorted(metrics, key=lambda item: item[0].new_prime_remainder):
            label = classify_canonical_transition(row)
            result.append(
                B8ApertureOrbitProbeRow(
                    selection_groups=selection_groups,
                    parent_rank=parent_rank,
                    parent_residue=parent.parent_residue,
                    parent_component_count=parent.parent_component_count,
                    parent_residual_measure=parent.parent_residual_measure,
                    parent_max_component_width=parent.parent_max_component_width,
                    parent_mod210=parent.parent_mod210,
                    reflection_orbit=parent.reflection_orbit,
                    capacity_pass=(
                        parent.parent_component_count == 1
                        and Fraction(parent.parent_residual_measure) <= Fraction(1, B8_NEW_PRIME)
                    ),
                    lift_remainder=row.new_prime_remainder,
                    child_residue=row.child_residue,
                    transition_label=label,
                    component_delta=component_transition_stats(row).component_delta,
                    phase_margin=_format_fraction(metric.phase_margin),
                    phase_rank=phase_rank[row.child_residue],
                    aperture_tension=_format_fraction(metric.aperture_tension),
                    aperture_tension_rank=tension_rank[row.child_residue],
                    gap_width=_format_fraction(metric.gap_width),
                    gap_center=_format_fraction(metric.gap_center),
                    slack=_format_fraction(metric.slack),
                    nearest_q_grid_distance=_format_fraction(metric.nearest_q_grid_distance),
                    is_close=label == "close",
                )
            )
    return result


def build_b8_failure_forensics_rows() -> list[B8FailureForensicsRow]:
    parent_ids = _capacity_top_parent_ids()
    old_interval_map = _old_intervals_for_b8_parents(parent_ids)
    result: list[B8FailureForensicsRow] = []
    for parent in parent_ids:
        old_intervals = old_interval_map[parent]
        transition_rows = _b8_transition_rows_for_parent(parent, old_intervals)
        metrics = [(row, aperture_metrics_for_row(row)) for row in transition_rows]
        phase_rank = _rank_map(metrics, key_index="phase_margin", descending=True)
        for row, metric in sorted(metrics, key=lambda item: item[0].new_prime_remainder):
            label = classify_canonical_transition(row)
            result.append(
                B8FailureForensicsRow(
                    selection_group=CAPACITY_TOP_GROUP,
                    parent_residue=parent,
                    lift_remainder=row.new_prime_remainder,
                    child_residue=row.child_residue,
                    transition_label=label,
                    phase_margin=_format_fraction(metric.phase_margin),
                    phase_rank=phase_rank[row.child_residue],
                    aperture_tension=_format_fraction(metric.aperture_tension),
                    obstruction_bucket=_obstruction_bucket(label, metric.phase_margin),
                )
            )
    return result


def build_b8_parent_selection_audit_rows(
    selected: Sequence[B8ParentCandidate] | None = None,
    group_map: dict[int, set[str]] | None = None,
    probe_rows: Sequence[B8ApertureOrbitProbeRow] | None = None,
) -> list[B8ParentSelectionAuditRow]:
    selected_list = (
        list(selected)
        if selected is not None
        else _dedup_selected(select_b8_aperture_orbit_parents(scan_b8_parent_candidates()))
    )
    groups = group_map or {row.parent_residue: set() for row in selected_list}
    rows_by_parent: dict[int, list[B8ApertureOrbitProbeRow]] = defaultdict(list)
    if probe_rows is not None:
        for row in probe_rows:
            rows_by_parent[row.parent_residue].append(row)
    result: list[B8ParentSelectionAuditRow] = []
    for parent_rank, parent in enumerate(selected_list, start=1):
        child_rows = rows_by_parent.get(parent.parent_residue)
        if child_rows:
            best_row = min(child_rows, key=lambda row: (Fraction(row.aperture_tension), row.lift_remainder))
            trim_count = sum(row.transition_label == "trim" for row in child_rows)
            miss_count = sum(row.transition_label == "miss" for row in child_rows)
            close_count = sum(row.transition_label == "close" for row in child_rows)
            positive_count = sum(Fraction(row.phase_margin) > 0 for row in child_rows)
        else:
            best_row = None
            trim_count = parent.trim_lift_count
            miss_count = parent.miss_lift_count
            close_count = parent.close_lift_count
            positive_count = parent.positive_margin_lift_count
        result.append(
            B8ParentSelectionAuditRow(
                selection_groups=";".join(sorted(groups.get(parent.parent_residue, ()))),
                parent_rank=parent_rank,
                parent_residue=parent.parent_residue,
                parent_component_count=parent.parent_component_count,
                parent_residual_measure=parent.parent_residual_measure,
                parent_max_component_width=parent.parent_max_component_width,
                best_lift_remainder=(
                    best_row.lift_remainder if best_row else parent.best_lift_remainder
                ),
                best_phase_margin=(
                    best_row.phase_margin if best_row else parent.best_phase_margin
                ),
                best_aperture_tension=(
                    best_row.aperture_tension if best_row else parent.best_aperture_tension
                ),
                best_transition_label=(
                    best_row.transition_label if best_row else parent.best_transition_label
                ),
                trim_lift_count=trim_count,
                miss_lift_count=miss_count,
                close_lift_count=close_count,
                positive_margin_lift_count=positive_count,
                selection_failure_reason=_selection_failure_reason(
                    close_count=close_count,
                    positive_count=positive_count,
                    best_margin=Fraction(best_row.phase_margin if best_row else parent.best_phase_margin),
                    best_label=best_row.transition_label if best_row else parent.best_transition_label,
                ),
            )
        )
    return result


def build_b8_aperture_orbit_summary_rows(
    *,
    probe_rows: Sequence[B8ApertureOrbitProbeRow] | None = None,
    audit_rows: Sequence[B8ParentSelectionAuditRow] | None = None,
    failure_rows: Sequence[B8FailureForensicsRow] | None = None,
    birth_audit_rows: Sequence[B8BirthOverlapAuditRow] | None = None,
) -> list[B8ApertureOrbitSummaryRow]:
    probe = list(probe_rows) if probe_rows is not None else read_b8_aperture_orbit_probe_csv()
    audit = list(audit_rows) if audit_rows is not None else read_b8_parent_selection_audit_csv()
    failure = list(failure_rows) if failure_rows is not None else read_b8_failure_forensics_csv()
    birth_audit = (
        list(birth_audit_rows)
        if birth_audit_rows is not None
        else read_b8_birth_overlap_audit_csv()
    )
    summary: list[B8ApertureOrbitSummaryRow] = []
    for group in sorted({group for row in probe for group in row.selection_groups.split(";") if group}):
        group_rows = [row for row in probe if group in row.selection_groups.split(";")]
        group_parents = {row.parent_residue for row in group_rows}
        summary.extend(
            [
                B8ApertureOrbitSummaryRow("probe_parent_count", group, str(len(group_parents)), "deduped parents carrying this group label"),
                B8ApertureOrbitSummaryRow("probe_row_count", group, str(len(group_rows)), "19 lifts per selected parent"),
                B8ApertureOrbitSummaryRow("close_count", group, str(sum(row.is_close for row in group_rows)), "source-only B8 geometry close rows"),
                B8ApertureOrbitSummaryRow("positive_margin_count", group, str(sum(Fraction(row.phase_margin) > 0 for row in group_rows)), "positive signed containment margins"),
                B8ApertureOrbitSummaryRow("distinct_parent_measure_count", group, str(len({row.parent_residual_measure for row in group_rows})), "diversity check for parent gap widths"),
            ]
        )
    summary.extend(
        [
            B8ApertureOrbitSummaryRow("selected_parent_count", "all", str(len(audit)), "deduped selected parents"),
            B8ApertureOrbitSummaryRow("probe_row_count", "all", str(len(probe)), "deduped selected parents times 19 lifts"),
            B8ApertureOrbitSummaryRow("failure_forensics_rows", CAPACITY_TOP_GROUP, str(len(failure)), "negative baseline rows from existing B8 targeted probe"),
            B8ApertureOrbitSummaryRow("b8_birth_overlap_audit_rows", "all", str(len(birth_audit)), "independent coverage checks for close rows"),
            B8ApertureOrbitSummaryRow("b8_exact_birth_rows", "all", str(sum(row.exact_b8_birth for row in birth_audit)), "close rows independently verified as B8 births"),
        ]
    )
    return summary


def build_b8_birth_overlap_audit_rows(
    probe_rows: Sequence[B8ApertureOrbitProbeRow] | None = None,
) -> list[B8BirthOverlapAuditRow]:
    """Independently verify whether B8 geometry-close rows are B8 births."""
    rows = list(probe_rows) if probe_rows is not None else read_b8_aperture_orbit_probe_csv()
    parent_primes = first_primes(B8_PARENT_K)
    child_primes = first_primes(B8_CHILD_K)
    result: list[B8BirthOverlapAuditRow] = []
    for row in rows:
        if not row.is_close:
            continue
        parent_gaps = residue_uncovered_intervals(row.parent_residue, parent_primes)
        child_gaps = residue_uncovered_intervals(row.child_residue, child_primes)
        parent_uncovered = not residue_is_exactly_covered(row.parent_residue, parent_primes)
        child_covered = residue_is_exactly_covered(row.child_residue, child_primes)
        projects = row.child_residue % B8_PARENT_MODULUS == row.parent_residue
        exact_birth = parent_uncovered and child_covered and projects
        result.append(
            B8BirthOverlapAuditRow(
                parent_residue=row.parent_residue,
                child_residue=row.child_residue,
                lift_remainder=row.lift_remainder,
                selection_groups=row.selection_groups,
                phase_margin=row.phase_margin,
                aperture_tension=row.aperture_tension,
                parent_uncovered_exact=parent_uncovered,
                child_covered_exact=child_covered,
                child_projects_to_parent=projects,
                parent_gap_count_exact=len(parent_gaps),
                child_gap_count_exact=len(child_gaps),
                exact_b8_birth=exact_birth,
                audit_status="pass" if exact_birth else "fail",
            )
        )
    return result


def read_b8_failure_forensics_csv(
    path: str | Path = DEFAULT_B8_FAILURE_FORENSICS_CSV,
) -> list[B8FailureForensicsRow]:
    return _read_dataclass_csv(path, B8FailureForensicsRow)


def read_b8_parent_selection_audit_csv(
    path: str | Path = DEFAULT_B8_PARENT_SELECTION_AUDIT_CSV,
) -> list[B8ParentSelectionAuditRow]:
    return _read_dataclass_csv(path, B8ParentSelectionAuditRow)


def read_b8_aperture_orbit_probe_csv(
    path: str | Path = DEFAULT_B8_APERTURE_ORBIT_PROBE_CSV,
) -> list[B8ApertureOrbitProbeRow]:
    return _read_dataclass_csv(path, B8ApertureOrbitProbeRow)


def read_b8_aperture_orbit_summary_csv(
    path: str | Path = DEFAULT_B8_APERTURE_ORBIT_SUMMARY_CSV,
) -> list[B8ApertureOrbitSummaryRow]:
    return _read_dataclass_csv(path, B8ApertureOrbitSummaryRow)


def read_b8_birth_overlap_audit_csv(
    path: str | Path = DEFAULT_B8_BIRTH_OVERLAP_AUDIT_CSV,
) -> list[B8BirthOverlapAuditRow]:
    return _read_dataclass_csv(path, B8BirthOverlapAuditRow)


@dataclass(frozen=True)
class ApertureMetric:
    phase_margin: Fraction
    aperture_tension: Fraction
    gap_width: Fraction
    gap_center: Fraction
    slack: Fraction
    nearest_q_grid_distance: Fraction


def aperture_metrics_for_row(row: TransitionProbeRow) -> ApertureMetric:
    old_components = circular_components(parse_interval_list(row.old_gap_boundary_endpoints))
    arc_components = circular_components(parse_interval_list(row.new_prime_closed_arc_boundary_endpoints))
    if len(arc_components) != 1:
        raise ValueError("expected one circular new-prime arc")
    arc_interval = _unwrap_component(arc_components[0])
    arc_center = (arc_interval[0] + arc_interval[1]) / 2
    metrics = [_component_aperture_metric(component, arc_interval, arc_center, row.new_prime) for component in old_components]
    if not metrics:
        return ApertureMetric(Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(0))
    phase_margin = min(metric.phase_margin for metric in metrics)
    return max(
        metrics,
        key=lambda metric: (
            metric.phase_margin == phase_margin,
            -metric.aperture_tension,
            metric.gap_width,
        ),
    )


def write_dataclass_csv(rows: Iterable[object], output_path: str | Path, row_type: type) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(row_type.__dataclass_fields__.keys())
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def write_b8_aperture_orbit_heatmap(
    rows: Sequence[B8ApertureOrbitProbeRow],
    output_path: str | Path = DEFAULT_B8_APERTURE_ORBIT_HEATMAP,
) -> None:
    if "MPLCONFIGDIR" not in os.environ:
        os.environ["MPLCONFIGDIR"] = str(
            Path(tempfile.gettempdir()) / "primeclock-matplotlib"
        )
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    capacity_rows = [
        row for row in rows if CAPACITY_TOP_GROUP in row.selection_groups.split(";")
    ][:200 * B8_NEW_PRIME]
    frontier_rows = [
        row for row in rows if APERTURE_FRONTIER_GROUP in row.selection_groups.split(";")
    ][:200 * B8_NEW_PRIME]
    panels = [(CAPACITY_TOP_GROUP, capacity_rows), (APERTURE_FRONTIER_GROUP, frontier_rows)]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), constrained_layout=True)
    for ax, (title, panel_rows) in zip(axes, panels):
        xs = [row.lift_remainder for row in panel_rows]
        ys = [row.parent_rank for row in panel_rows]
        colors = [float(Fraction(row.phase_margin)) for row in panel_rows]
        scatter = ax.scatter(xs, ys, c=colors, cmap="coolwarm", s=12)
        ax.set_title(title)
        ax.set_xlabel("B8 lift remainder mod 19")
        ax.set_ylabel("selected parent rank")
        ax.grid(alpha=0.2)
    fig.colorbar(scatter, ax=axes, label="signed phase margin")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def b8_aperture_orbit_signature(row: object) -> tuple[object, ...]:
    return row_signature(row)


def _candidate_for_parent(parent_residue: int, old_intervals) -> B8ParentCandidate:
    old_components = circular_components(old_intervals)
    residual_measure = sum(interval_length(interval) for interval in old_intervals)
    max_width = max((sum(interval_length(segment) for segment in component.segments) for component in old_components), default=Fraction(0))
    lift_metrics = []
    for row in _b8_transition_rows_for_parent(parent_residue, old_intervals):
        metric = aperture_metrics_for_row(row)
        label = classify_canonical_transition(row)
        lift_metrics.append((row, metric, label))
    best_row, best_metric, best_label = max(
        lift_metrics,
        key=lambda item: (item[1].phase_margin, -item[0].new_prime_remainder),
    )
    label_counts = Counter(label for _row, _metric, label in lift_metrics)
    positive_count = sum(metric.phase_margin > 0 for _row, metric, _label in lift_metrics)
    return B8ParentCandidate(
        parent_residue=parent_residue,
        parent_component_count=len(old_components),
        parent_residual_measure=_format_fraction(residual_measure),
        parent_max_component_width=_format_fraction(max_width),
        best_lift_remainder=best_row.new_prime_remainder,
        best_child_residue=best_row.child_residue,
        best_phase_margin=_format_fraction(best_metric.phase_margin),
        best_aperture_tension=_format_fraction(best_metric.aperture_tension),
        best_transition_label=best_label,
        trim_lift_count=label_counts["trim"],
        miss_lift_count=label_counts["miss"],
        close_lift_count=label_counts["close"],
        positive_margin_lift_count=positive_count,
        parent_mod210=parent_residue % 210,
        reflection_orbit=_reflection_orbit(parent_residue % B8_NEW_PRIME, B8_NEW_PRIME),
        width_bucket=_width_bucket(max_width),
        hash_score=_stable_hash(parent_residue),
    )


def _seed_for_parent(parent_residue: int, old_intervals) -> B8ParentSeed:
    old_components = circular_components(old_intervals)
    residual_measure = sum(interval_length(interval) for interval in old_intervals)
    max_width = max(
        (
            sum(interval_length(segment) for segment in component.segments)
            for component in old_components
        ),
        default=Fraction(0),
    )
    return B8ParentSeed(
        parent_residue=parent_residue,
        old_gap_boundary_endpoints=format_intervals(old_intervals),
        parent_component_count=len(old_components),
        parent_residual_measure=_format_fraction(residual_measure),
        parent_max_component_width=_format_fraction(max_width),
        parent_mod210=parent_residue % 210,
        reflection_orbit=_reflection_orbit(parent_residue % B8_NEW_PRIME, B8_NEW_PRIME),
        width_bucket=_width_bucket(max_width),
        hash_score=_stable_hash(parent_residue),
    )


def _prefilter_b8_parent_seeds(seeds: Sequence[B8ParentSeed]) -> list[B8ParentSeed]:
    by_parent = {seed.parent_residue: seed for seed in seeds}
    selected: dict[int, B8ParentSeed] = {}

    for parent in _capacity_top_parent_ids():
        if parent in by_parent:
            selected[parent] = by_parent[parent]

    for seed in sorted(seeds, key=lambda row: (row.hash_score, row.parent_residue))[:600]:
        selected.setdefault(seed.parent_residue, seed)

    capacity_seeds = [
        seed
        for seed in seeds
        if seed.parent_component_count == 1
        and Fraction(seed.parent_residual_measure) <= Fraction(1, B8_NEW_PRIME)
    ]
    for seed in sorted(
        capacity_seeds,
        key=lambda row: (
            abs(Fraction(1, B8_NEW_PRIME) - Fraction(row.parent_residual_measure)),
            row.parent_residue,
        ),
    )[:1600]:
        selected.setdefault(seed.parent_residue, seed)

    for seed in _seed_orbit_diversity_selection(seeds, limit=1600):
        selected.setdefault(seed.parent_residue, seed)

    return sorted(selected.values(), key=lambda row: row.parent_residue)


def _seed_orbit_diversity_selection(
    seeds: Sequence[B8ParentSeed],
    *,
    limit: int,
) -> list[B8ParentSeed]:
    best_by_bucket: dict[tuple[object, ...], B8ParentSeed] = {}
    for seed in seeds:
        bucket = (
            seed.parent_mod210,
            seed.reflection_orbit,
            seed.parent_component_count,
            seed.width_bucket,
        )
        current = best_by_bucket.get(bucket)
        if current is None or (seed.hash_score, seed.parent_residue) < (
            current.hash_score,
            current.parent_residue,
        ):
            best_by_bucket[bucket] = seed
    return sorted(best_by_bucket.values(), key=lambda row: (row.hash_score, row.parent_residue))[:limit]


def _b8_transition_rows_for_parent(
    parent_residue: int,
    old_intervals,
) -> list[TransitionProbeRow]:
    rows: list[TransitionProbeRow] = []
    old_text = format_intervals(old_intervals)
    for lift_index in range(B8_NEW_PRIME):
        child_residue = parent_residue + lift_index * B8_PARENT_MODULUS
        new_arcs = exact_arc_intervals_for_residue(child_residue, B8_NEW_PRIME)
        remaining = subtract_intervals(old_intervals, new_arcs)
        row = B5GapCloseTransitionPilotRow(
            parent_k=B8_PARENT_K,
            child_k=B8_CHILD_K,
            parent_modulus=B8_PARENT_MODULUS,
            child_modulus=B8_CHILD_MODULUS,
            parent_residue=parent_residue,
            child_residue=child_residue,
            new_prime=B8_NEW_PRIME,
            new_prime_remainder=child_residue % B8_NEW_PRIME,
            old_gap_count=len(old_intervals),
            old_gap_boundary_endpoints=old_text,
            new_prime_closed_arc_boundary_endpoints=format_intervals(new_arcs),
            closed_gap_count=0,
            remaining_gap_count=len(remaining),
            remaining_gap_boundary_endpoints=format_intervals(remaining),
            transition_type="close" if not remaining else "not_close",
            is_b5_birth=False,
        )
        stats = component_transition_stats(row)
        rows.append(B5GapCloseTransitionPilotRow(**{**row.__dict__, "closed_gap_count": stats.closed_component_count}))
    return rows


def _old_intervals_for_b8_parents(parent_residues: Iterable[int]):
    wanted = set(parent_residues)
    found = {}
    for row in read_b5_gap_close_transition_pilot_csv(DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV):
        if row.child_residue not in wanted:
            continue
        if classify_canonical_transition(row) == "close":
            raise ValueError(f"B8 parent is already close at k=7: {row.child_residue}")
        found[row.child_residue] = parse_interval_list(row.remaining_gap_boundary_endpoints)
        if len(found) == len(wanted):
            return found
    missing = sorted(wanted - set(found))
    raise KeyError(f"B8 parent residues not found in B6->B7 graph: {missing[:5]}")


def _component_aperture_metric(component, arc_interval, arc_center: Fraction, q: int) -> ApertureMetric:
    gap_interval = _unwrap_component(component)
    gap_start, gap_end = gap_interval
    gap_width = gap_end - gap_start
    gap_center = (gap_start + gap_end) / 2
    signed_margin = _signed_containment_margin(gap_interval, arc_interval)
    slack = (Fraction(1, q) - gap_width) / 2
    distance = _circular_distance(gap_center, arc_center)
    return ApertureMetric(
        phase_margin=signed_margin,
        aperture_tension=distance - slack,
        gap_width=gap_width,
        gap_center=gap_center % 1,
        slack=slack,
        nearest_q_grid_distance=distance,
    )


def _capacity_top_parent_ids() -> list[int]:
    seen: set[int] = set()
    parents: list[int] = []
    for row in read_b8_high_potential_probe_csv():
        if row.parent_residue not in seen:
            seen.add(row.parent_residue)
            parents.append(row.parent_residue)
    return parents


def _orbit_diversity_selection(
    candidates: Sequence[B8ParentCandidate],
    *,
    limit: int,
) -> list[B8ParentCandidate]:
    best_by_bucket: dict[tuple[object, ...], B8ParentCandidate] = {}
    for candidate in candidates:
        bucket = (
            candidate.best_lift_remainder,
            candidate.parent_mod210,
            candidate.reflection_orbit,
            candidate.parent_component_count,
            candidate.width_bucket,
        )
        current = best_by_bucket.get(bucket)
        if current is None or _frontier_key(candidate) < _frontier_key(current):
            best_by_bucket[bucket] = candidate
    return sorted(best_by_bucket.values(), key=_frontier_key)[:limit]


def _frontier_key(candidate: B8ParentCandidate) -> tuple[Fraction, Fraction, int]:
    return (
        Fraction(candidate.best_aperture_tension),
        -Fraction(candidate.best_phase_margin),
        candidate.parent_residue,
    )


def _selection_group_map(
    selected: dict[str, list[B8ParentCandidate]],
) -> dict[int, set[str]]:
    groups: dict[int, set[str]] = defaultdict(set)
    for group, rows in selected.items():
        for row in rows:
            groups[row.parent_residue].add(group)
    return groups


def _dedup_selected(
    selected: dict[str, list[B8ParentCandidate]],
) -> list[B8ParentCandidate]:
    by_parent: dict[int, B8ParentCandidate] = {}
    for rows in selected.values():
        for row in rows:
            by_parent.setdefault(row.parent_residue, row)
    return sorted(by_parent.values(), key=lambda row: (-len(_selection_group_map(selected)[row.parent_residue]), _frontier_key(row)))


def _rank_map(
    rows: Sequence[tuple[TransitionProbeRow, ApertureMetric]],
    *,
    key_index: str,
    descending: bool,
) -> dict[int, int]:
    def metric_value(item):
        metric = item[1]
        value = getattr(metric, key_index)
        return -value if descending else value

    return {
        row.child_residue: index
        for index, (row, _metric) in enumerate(
            sorted(rows, key=lambda item: (metric_value(item), item[0].new_prime_remainder)),
            start=1,
        )
    }


def _obstruction_bucket(label: str, margin: Fraction) -> str:
    if label == "close" and margin > 0:
        return "none"
    if label == "trim" and margin < 0 and abs(margin) <= Fraction(1, 100):
        return "underreach"
    if label == "trim":
        return "wrong_side_trim"
    if label == "miss":
        return "pure_miss"
    return f"{label}_failure"


def _selection_failure_reason(
    *,
    close_count: int,
    positive_count: int,
    best_margin: Fraction,
    best_label: str,
) -> str:
    if close_count:
        return "has_close_geometry"
    if positive_count:
        return "positive_margin_without_close_check"
    if best_label == "trim" and abs(best_margin) <= Fraction(1, 100):
        return "near_underreach"
    if best_label == "trim":
        return "trim_but_margin_negative"
    return "best_lift_miss"


def _reflection_orbit(remainder: int, modulus: int) -> str:
    other = (-remainder) % modulus
    left, right = sorted((remainder, other))
    return f"{left}/{right}"


def _width_bucket(width: Fraction) -> str:
    if width <= Fraction(1, 100):
        return "tiny"
    if width <= Fraction(1, 50):
        return "small"
    if width <= Fraction(1, 25):
        return "medium"
    if width <= Fraction(1, 10):
        return "large"
    return "wide"


def _stable_hash(value: int) -> str:
    return hashlib.sha256(f"prc-v2.5-b8:{value}".encode("ascii")).hexdigest()


def _circular_distance(left: Fraction, right: Fraction) -> Fraction:
    raw = abs((left % 1) - (right % 1))
    return min(raw, 1 - raw)


def _format_fraction(value: Fraction) -> str:
    return format_fraction(value)


def _read_dataclass_csv(path: str | Path, row_type: type):
    int_fields = {
        "parent_rank",
        "parent_residue",
        "parent_component_count",
        "parent_mod210",
        "lift_remainder",
        "child_residue",
        "component_delta",
        "phase_rank",
        "aperture_tension_rank",
        "trim_lift_count",
        "miss_lift_count",
        "close_lift_count",
        "positive_margin_lift_count",
        "parent_gap_count_exact",
        "child_gap_count_exact",
    }
    bool_fields = {"capacity_pass", "is_close"}
    bool_fields.update(
        {
            "parent_uncovered_exact",
            "child_covered_exact",
            "child_projects_to_parent",
            "exact_b8_birth",
        }
    )
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
