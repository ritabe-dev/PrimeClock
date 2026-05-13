"""Source-only B8 control calibration for PRC v2.5."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Sequence

from tools import first_primes, format_fraction, residue_is_exactly_covered, residue_uncovered_intervals
from v2_5_b8_aperture_orbit_probe import (
    B8_CHILD_K,
    B8_PARENT_K,
    B8_PARENT_MODULUS,
    DEFAULT_B8_APERTURE_ORBIT_PROBE_CSV,
    DEFAULT_B8_BIRTH_OVERLAP_AUDIT_CSV,
    aperture_metrics_for_row,
    read_b8_aperture_orbit_probe_csv,
    read_b8_birth_overlap_audit_csv,
    write_dataclass_csv,
    _b8_transition_rows_for_parent,
    _old_intervals_for_b8_parents,
    _rank_map,
)
from v2_4_transition_pilot import classify_canonical_transition, component_transition_stats

EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[2]

DEFAULT_B8_CONTROL_OVERLAP_AUDIT_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_b8_control_overlap_audit_v0_1.csv"
)
DEFAULT_B8_SIBLING_NONBIRTH_CONTROLS_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_b8_sibling_nonbirth_controls_v0_1.csv"
)
DEFAULT_B8_MATCHED_NONBIRTH_CONTROLS_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_b8_matched_nonbirth_controls_v0_1.csv"
)
DEFAULT_B8_CONTROL_CALIBRATION_SUMMARY_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_b8_control_calibration_summary_v0_1.csv"
)
DEFAULT_K8_BIRTH_SAMPLE_CSV = (
    REPO_ROOT
    / "research"
    / "data"
    / "summaries"
    / "prc_prime_prefix_residue_covering_birth_samples_k8_v0_3.csv"
)


@dataclass(frozen=True)
class B8SiblingControlRow:
    parent_residue: int
    child_residue: int
    lift_remainder: int
    sibling_role: str
    phase_margin: str
    aperture_tension: str
    phase_rank: int
    transition_label: str
    component_delta: int
    parent_uncovered_exact: bool
    child_covered_exact: bool
    child_projects_to_parent: bool
    parent_gap_count_exact: int
    child_gap_count_exact: int
    exact_b8_birth: bool


@dataclass(frozen=True)
class B8MatchedNonbirthControlRow:
    birth_parent_residue: int
    birth_child_residue: int
    control_parent_residue: int
    control_child_residue: int
    control_lift_remainder: int
    match_rank: int
    match_reason: str
    birth_parent_residual_measure: str
    control_parent_residual_measure: str
    birth_reflection_orbit: str
    control_reflection_orbit: str
    birth_parent_mod210: int
    control_parent_mod210: int
    control_phase_margin: str
    control_aperture_tension: str
    control_transition_label: str
    control_capacity_pass: bool
    control_parent_uncovered_exact: bool
    control_child_covered_exact: bool
    control_exact_b8_birth: bool


@dataclass(frozen=True)
class B8ControlOverlapAuditRow:
    sample_residue: int
    sample_previous_prefix_uncovered_measure: str
    in_aperture_orbit_32: bool
    matching_parent_residue: int
    matching_lift_remainder: int
    calibration_role: str


@dataclass(frozen=True)
class B8ControlCalibrationSummaryRow:
    metric: str
    value: str
    note: str


def write_b8_control_calibration_artifacts(
    *,
    sibling_path: str | Path = DEFAULT_B8_SIBLING_NONBIRTH_CONTROLS_CSV,
    matched_path: str | Path = DEFAULT_B8_MATCHED_NONBIRTH_CONTROLS_CSV,
    overlap_path: str | Path = DEFAULT_B8_CONTROL_OVERLAP_AUDIT_CSV,
    summary_path: str | Path = DEFAULT_B8_CONTROL_CALIBRATION_SUMMARY_CSV,
) -> None:
    sibling_rows = build_b8_sibling_control_rows()
    matched_rows = build_b8_matched_nonbirth_control_rows()
    overlap_rows = build_b8_control_overlap_audit_rows()
    summary_rows = build_b8_control_calibration_summary_rows(
        sibling_rows=sibling_rows,
        matched_rows=matched_rows,
        overlap_rows=overlap_rows,
    )
    write_dataclass_csv(sibling_rows, sibling_path, B8SiblingControlRow)
    write_dataclass_csv(matched_rows, matched_path, B8MatchedNonbirthControlRow)
    write_dataclass_csv(overlap_rows, overlap_path, B8ControlOverlapAuditRow)
    write_dataclass_csv(summary_rows, summary_path, B8ControlCalibrationSummaryRow)


def build_b8_sibling_control_rows() -> list[B8SiblingControlRow]:
    birth_rows = read_b8_birth_overlap_audit_csv(DEFAULT_B8_BIRTH_OVERLAP_AUDIT_CSV)
    parent_ids = sorted({row.parent_residue for row in birth_rows})
    birth_children = {row.child_residue for row in birth_rows}
    old_interval_map = _old_intervals_for_b8_parents(parent_ids)
    parent_primes = first_primes(B8_PARENT_K)
    child_primes = first_primes(B8_CHILD_K)
    result: list[B8SiblingControlRow] = []
    for parent in parent_ids:
        parent_gaps = residue_uncovered_intervals(parent, parent_primes)
        parent_uncovered = not residue_is_exactly_covered(parent, parent_primes)
        transition_rows = _b8_transition_rows_for_parent(parent, old_interval_map[parent])
        metrics = [(row, aperture_metrics_for_row(row)) for row in transition_rows]
        phase_rank = _rank_map(metrics, key_index="phase_margin", descending=True)
        for row, metric in sorted(metrics, key=lambda item: item[0].new_prime_remainder):
            child_gaps = residue_uncovered_intervals(row.child_residue, child_primes)
            child_covered = residue_is_exactly_covered(row.child_residue, child_primes)
            projects = row.child_residue % B8_PARENT_MODULUS == parent
            exact_birth = parent_uncovered and child_covered and projects
            label = classify_canonical_transition(row)
            result.append(
                B8SiblingControlRow(
                    parent_residue=parent,
                    child_residue=row.child_residue,
                    lift_remainder=row.new_prime_remainder,
                    sibling_role=(
                        "birth_close"
                        if row.child_residue in birth_children
                        else "sibling_nonbirth"
                    ),
                    phase_margin=format_fraction(metric.phase_margin),
                    aperture_tension=format_fraction(metric.aperture_tension),
                    phase_rank=phase_rank[row.child_residue],
                    transition_label=label,
                    component_delta=component_transition_stats(row).component_delta,
                    parent_uncovered_exact=parent_uncovered,
                    child_covered_exact=child_covered,
                    child_projects_to_parent=projects,
                    parent_gap_count_exact=len(parent_gaps),
                    child_gap_count_exact=len(child_gaps),
                    exact_b8_birth=exact_birth,
                )
            )
    return result


def build_b8_matched_nonbirth_control_rows(
    *,
    rows_per_birth: int = 2,
) -> list[B8MatchedNonbirthControlRow]:
    probe_rows = read_b8_aperture_orbit_probe_csv(DEFAULT_B8_APERTURE_ORBIT_PROBE_CSV)
    birth_rows = [row for row in probe_rows if row.is_close]
    candidates = [
        row
        for row in probe_rows
        if (
            not row.is_close
            and row.capacity_pass
            and Fraction(row.phase_margin) <= 0
            and row.transition_label != "close"
        )
    ]
    parent_primes = first_primes(B8_PARENT_K)
    child_primes = first_primes(B8_CHILD_K)
    used_children: set[int] = set()
    result: list[B8MatchedNonbirthControlRow] = []
    for birth in sorted(birth_rows, key=lambda row: (row.parent_residue, row.child_residue)):
        ranked = sorted(
            [
                row
                for row in candidates
                if row.child_residue not in used_children
                and row.parent_residue != birth.parent_residue
            ],
            key=lambda row: _matched_control_key(birth, row),
        )[:rows_per_birth]
        if len(ranked) < rows_per_birth:
            raise ValueError(f"not enough matched controls for birth child {birth.child_residue}")
        for index, control in enumerate(ranked, start=1):
            used_children.add(control.child_residue)
            parent_uncovered = not residue_is_exactly_covered(
                control.parent_residue,
                parent_primes,
            )
            child_covered = residue_is_exactly_covered(control.child_residue, child_primes)
            result.append(
                B8MatchedNonbirthControlRow(
                    birth_parent_residue=birth.parent_residue,
                    birth_child_residue=birth.child_residue,
                    control_parent_residue=control.parent_residue,
                    control_child_residue=control.child_residue,
                    control_lift_remainder=control.lift_remainder,
                    match_rank=index,
                    match_reason=_match_reason(birth, control),
                    birth_parent_residual_measure=birth.parent_residual_measure,
                    control_parent_residual_measure=control.parent_residual_measure,
                    birth_reflection_orbit=birth.reflection_orbit,
                    control_reflection_orbit=control.reflection_orbit,
                    birth_parent_mod210=birth.parent_mod210,
                    control_parent_mod210=control.parent_mod210,
                    control_phase_margin=control.phase_margin,
                    control_aperture_tension=control.aperture_tension,
                    control_transition_label=control.transition_label,
                    control_capacity_pass=control.capacity_pass,
                    control_parent_uncovered_exact=parent_uncovered,
                    control_child_covered_exact=child_covered,
                    control_exact_b8_birth=(
                        parent_uncovered
                        and child_covered
                        and control.child_residue % B8_PARENT_MODULUS == control.parent_residue
                    ),
                )
            )
    return result


def build_b8_control_overlap_audit_rows(
    sample_path: str | Path = DEFAULT_K8_BIRTH_SAMPLE_CSV,
) -> list[B8ControlOverlapAuditRow]:
    birth_rows = read_b8_birth_overlap_audit_csv(DEFAULT_B8_BIRTH_OVERLAP_AUDIT_CSV)
    by_child = {row.child_residue: row for row in birth_rows}
    result: list[B8ControlOverlapAuditRow] = []
    with Path(sample_path).open("r", encoding="utf-8", newline="") as handle:
        for raw_row in csv.DictReader(handle):
            if int(raw_row["k"]) != B8_CHILD_K:
                continue
            residue = int(raw_row["residue"])
            match = by_child.get(residue)
            result.append(
                B8ControlOverlapAuditRow(
                    sample_residue=residue,
                    sample_previous_prefix_uncovered_measure=raw_row[
                        "previous_prefix_uncovered_measure"
                    ],
                    in_aperture_orbit_32=match is not None,
                    matching_parent_residue=match.parent_residue if match else -1,
                    matching_lift_remainder=match.lift_remainder if match else -1,
                    calibration_role="sample_overlap_only_not_recall",
                )
            )
    return result


def build_b8_control_calibration_summary_rows(
    *,
    sibling_rows: Sequence[B8SiblingControlRow] | None = None,
    matched_rows: Sequence[B8MatchedNonbirthControlRow] | None = None,
    overlap_rows: Sequence[B8ControlOverlapAuditRow] | None = None,
) -> list[B8ControlCalibrationSummaryRow]:
    siblings = list(sibling_rows) if sibling_rows is not None else read_b8_sibling_control_csv()
    matched = list(matched_rows) if matched_rows is not None else read_b8_matched_nonbirth_control_csv()
    overlap = list(overlap_rows) if overlap_rows is not None else read_b8_control_overlap_audit_csv()
    sibling_counts = Counter(row.sibling_role for row in siblings)
    summary = [
        B8ControlCalibrationSummaryRow("sibling_parent_count", str(len({row.parent_residue for row in siblings})), "32 audited B8 birth parent families"),
        B8ControlCalibrationSummaryRow("sibling_row_count", str(len(siblings)), "19 lifts for each audited birth parent"),
        B8ControlCalibrationSummaryRow("sibling_birth_close_count", str(sibling_counts["birth_close"]), "one audited close lift per birth parent"),
        B8ControlCalibrationSummaryRow("sibling_nonbirth_count", str(sibling_counts["sibling_nonbirth"]), "remaining sibling lifts"),
        B8ControlCalibrationSummaryRow("matched_nonbirth_count", str(len(matched)), "two deterministic matched non-birth controls per audited birth"),
        B8ControlCalibrationSummaryRow("matched_measure_bucket_count", str(len({row.control_parent_residual_measure for row in matched})), "matched controls should not collapse to one width"),
        B8ControlCalibrationSummaryRow("matched_reflection_orbit_count", str(len({row.control_reflection_orbit for row in matched})), "matched controls should not collapse to one orbit"),
        B8ControlCalibrationSummaryRow("k8_sample_rows", str(len(overlap)), "existing k8 birth sample rows used only for calibration"),
        B8ControlCalibrationSummaryRow("k8_sample_overlap_with_32", str(sum(row.in_aperture_orbit_32 for row in overlap)), "overlap count only; not recall"),
    ]
    return summary


def read_b8_sibling_control_csv(
    path: str | Path = DEFAULT_B8_SIBLING_NONBIRTH_CONTROLS_CSV,
) -> list[B8SiblingControlRow]:
    return _read_dataclass_csv(path, B8SiblingControlRow)


def read_b8_matched_nonbirth_control_csv(
    path: str | Path = DEFAULT_B8_MATCHED_NONBIRTH_CONTROLS_CSV,
) -> list[B8MatchedNonbirthControlRow]:
    return _read_dataclass_csv(path, B8MatchedNonbirthControlRow)


def read_b8_control_overlap_audit_csv(
    path: str | Path = DEFAULT_B8_CONTROL_OVERLAP_AUDIT_CSV,
) -> list[B8ControlOverlapAuditRow]:
    return _read_dataclass_csv(path, B8ControlOverlapAuditRow)


def read_b8_control_calibration_summary_csv(
    path: str | Path = DEFAULT_B8_CONTROL_CALIBRATION_SUMMARY_CSV,
) -> list[B8ControlCalibrationSummaryRow]:
    return _read_dataclass_csv(path, B8ControlCalibrationSummaryRow)


def _matched_control_key(birth, control) -> tuple[object, ...]:
    return (
        abs(Fraction(control.parent_residual_measure) - Fraction(birth.parent_residual_measure)),
        control.reflection_orbit != birth.reflection_orbit,
        control.parent_mod210 != birth.parent_mod210,
        abs(Fraction(control.phase_margin)),
        Fraction(control.aperture_tension),
        control.parent_residue,
        control.child_residue,
    )


def _match_reason(birth, control) -> str:
    parts = ["capacity_nonclose"]
    if control.parent_residual_measure == birth.parent_residual_measure:
        parts.append("same_width")
    else:
        parts.append("nearest_width")
    if control.reflection_orbit == birth.reflection_orbit:
        parts.append("same_reflection_orbit")
    if control.parent_mod210 == birth.parent_mod210:
        parts.append("same_mod210")
    return ";".join(parts)


def _read_dataclass_csv(path: str | Path, row_type: type):
    int_fields = {
        "parent_residue",
        "child_residue",
        "lift_remainder",
        "phase_rank",
        "component_delta",
        "parent_gap_count_exact",
        "child_gap_count_exact",
        "birth_parent_residue",
        "birth_child_residue",
        "control_parent_residue",
        "control_child_residue",
        "control_lift_remainder",
        "match_rank",
        "birth_parent_mod210",
        "control_parent_mod210",
        "sample_residue",
        "matching_parent_residue",
        "matching_lift_remainder",
    }
    bool_fields = {
        "parent_uncovered_exact",
        "child_covered_exact",
        "child_projects_to_parent",
        "exact_b8_birth",
        "control_capacity_pass",
        "control_parent_uncovered_exact",
        "control_child_covered_exact",
        "control_exact_b8_birth",
        "in_aperture_orbit_32",
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


def control_calibration_signature(row: object) -> tuple[object, ...]:
    return tuple(getattr(row, field) for field in row.__dataclass_fields__)
