"""Source-only aperture-orbit historical calibration for PRC v2.5."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Sequence

from v2_4_phase_gate_diagnostics import (
    read_phase_gate_family_summary_csv,
    read_phase_gate_lift_diagnostics_csv,
    row_signature,
    write_dataclass_csv,
)
from v2_5_b8_control_calibration import (
    read_b8_control_calibration_summary_csv,
    read_b8_matched_nonbirth_control_csv,
    read_b8_sibling_control_csv,
)

EXPERIMENT_DIR = Path(__file__).resolve().parent

DEFAULT_APERTURE_ORBIT_BACKTEST_FAMILY_SUMMARY_CSV = (
    EXPERIMENT_DIR
    / "data"
    / "prc_v2_5_aperture_orbit_backtest_family_summary_v0_1.csv"
)
DEFAULT_APERTURE_ORBIT_BACKTEST_SCOPE_SUMMARY_CSV = (
    EXPERIMENT_DIR
    / "data"
    / "prc_v2_5_aperture_orbit_backtest_scope_summary_v0_1.csv"
)
DEFAULT_APERTURE_ORBIT_BACKTEST_B8_COMPARISON_CSV = (
    EXPERIMENT_DIR
    / "data"
    / "prc_v2_5_aperture_orbit_backtest_b8_comparison_v0_1.csv"
)

HISTORICAL_SCOPES = ("B4_to_B5_full", "B5_to_B6_full", "B6_to_B7_full")


@dataclass(frozen=True)
class ApertureOrbitBacktestFamilyRow:
    scope: str
    parent_residue: int
    new_prime: int
    capacity_pass: bool
    lift_count: int
    phase_pass_count: int
    close_lift_count: int
    birth_lift_count: int
    nonbirth_close_count: int
    best_phase_margin: str
    diagnostic_class: str


@dataclass(frozen=True)
class ApertureOrbitBacktestScopeRow:
    scope: str
    family_count: int
    lift_count: int
    close_count: int
    birth_count: int
    capacity_close_families: int
    capacity_nonclose_families: int
    false_positive_pressure: str
    close_phase_rank_1_count: int
    close_positive_margin_count: int
    nonclose_positive_margin_count: int
    nonbirth_close_count: int
    separator_status: str


@dataclass(frozen=True)
class ApertureOrbitBacktestB8ComparisonRow:
    cohort: str
    metric: str
    value: str
    note: str


def write_aperture_orbit_backtest_artifacts(
    *,
    family_path: str | Path = DEFAULT_APERTURE_ORBIT_BACKTEST_FAMILY_SUMMARY_CSV,
    scope_path: str | Path = DEFAULT_APERTURE_ORBIT_BACKTEST_SCOPE_SUMMARY_CSV,
    b8_path: str | Path = DEFAULT_APERTURE_ORBIT_BACKTEST_B8_COMPARISON_CSV,
) -> None:
    family_rows = build_aperture_orbit_backtest_family_rows()
    scope_rows = build_aperture_orbit_backtest_scope_rows(family_rows=family_rows)
    b8_rows = build_aperture_orbit_backtest_b8_comparison_rows()
    write_dataclass_csv(family_rows, family_path, ApertureOrbitBacktestFamilyRow)
    write_dataclass_csv(scope_rows, scope_path, ApertureOrbitBacktestScopeRow)
    write_dataclass_csv(b8_rows, b8_path, ApertureOrbitBacktestB8ComparisonRow)


def build_aperture_orbit_backtest_family_rows() -> list[ApertureOrbitBacktestFamilyRow]:
    rows = []
    for row in read_phase_gate_family_summary_csv():
        rows.append(
            ApertureOrbitBacktestFamilyRow(
                scope=row.scope,
                parent_residue=row.parent_residue,
                new_prime=row.new_prime,
                capacity_pass=row.capacity_pass,
                lift_count=row.lift_count,
                phase_pass_count=row.phase_pass_count,
                close_lift_count=row.close_lift_count,
                birth_lift_count=row.birth_lift_count,
                nonbirth_close_count=row.nonbirth_close_count,
                best_phase_margin=row.best_phase_margin,
                diagnostic_class=_family_diagnostic_class(row),
            )
        )
    return rows


def build_aperture_orbit_backtest_scope_rows(
    family_rows: Sequence[ApertureOrbitBacktestFamilyRow] | None = None,
) -> list[ApertureOrbitBacktestScopeRow]:
    families = (
        list(family_rows)
        if family_rows is not None
        else build_aperture_orbit_backtest_family_rows()
    )
    lift_rows = read_phase_gate_lift_diagnostics_csv()
    family_by_scope: dict[str, list[ApertureOrbitBacktestFamilyRow]] = defaultdict(list)
    lift_by_scope = defaultdict(list)
    for row in families:
        family_by_scope[row.scope].append(row)
    for row in lift_rows:
        lift_by_scope[row.scope].append(row)

    result: list[ApertureOrbitBacktestScopeRow] = []
    for scope in HISTORICAL_SCOPES:
        scope_families = family_by_scope[scope]
        scope_lifts = lift_by_scope[scope]
        close_lifts = [row for row in scope_lifts if row.is_close]
        nonclose_lifts = [row for row in scope_lifts if not row.is_close]
        capacity_close = sum(
            row.capacity_pass and row.close_lift_count > 0
            for row in scope_families
        )
        capacity_nonclose = sum(
            row.capacity_pass and row.close_lift_count == 0
            for row in scope_families
        )
        result.append(
            ApertureOrbitBacktestScopeRow(
                scope=scope,
                family_count=len(scope_families),
                lift_count=len(scope_lifts),
                close_count=sum(row.close_lift_count for row in scope_families),
                birth_count=sum(row.birth_lift_count for row in scope_families),
                capacity_close_families=capacity_close,
                capacity_nonclose_families=capacity_nonclose,
                false_positive_pressure=_ratio_text(capacity_nonclose, capacity_close),
                close_phase_rank_1_count=sum(row.phase_rank_desc == 1 for row in close_lifts),
                close_positive_margin_count=sum(
                    Fraction(row.phase_margin) > 0 for row in close_lifts
                ),
                nonclose_positive_margin_count=sum(
                    Fraction(row.phase_margin) > 0 for row in nonclose_lifts
                ),
                nonbirth_close_count=sum(row.is_close and not row.is_birth for row in scope_lifts),
                separator_status=_separator_status(scope_families, close_lifts, nonclose_lifts),
            )
        )
    return result


def build_aperture_orbit_backtest_b8_comparison_rows() -> list[ApertureOrbitBacktestB8ComparisonRow]:
    siblings = read_b8_sibling_control_csv()
    matched = read_b8_matched_nonbirth_control_csv()
    summary = read_b8_control_calibration_summary_csv()
    summary_map = {row.metric: row.value for row in summary}
    sibling_counts = Counter(row.sibling_role for row in siblings)
    return [
        ApertureOrbitBacktestB8ComparisonRow(
            "B8_sibling_control",
            "birth_close_count",
            str(sibling_counts["birth_close"]),
            "same-parent B8 close lifts",
        ),
        ApertureOrbitBacktestB8ComparisonRow(
            "B8_sibling_control",
            "sibling_nonbirth_count",
            str(sibling_counts["sibling_nonbirth"]),
            "same-parent sibling non-birth lifts",
        ),
        ApertureOrbitBacktestB8ComparisonRow(
            "B8_sibling_control",
            "birth_close_positive_margin_count",
            str(
                sum(
                    row.sibling_role == "birth_close" and Fraction(row.phase_margin) > 0
                    for row in siblings
                )
            ),
            "strict positive margin among B8 birth siblings",
        ),
        ApertureOrbitBacktestB8ComparisonRow(
            "B8_sibling_control",
            "sibling_nonbirth_positive_margin_count",
            str(
                sum(
                    row.sibling_role == "sibling_nonbirth"
                    and Fraction(row.phase_margin) > 0
                    for row in siblings
                )
            ),
            "must remain zero for same-parent non-birth controls",
        ),
        ApertureOrbitBacktestB8ComparisonRow(
            "B8_matched_nonbirth_control",
            "matched_nonbirth_count",
            str(len(matched)),
            "capacity-comparable matched non-birth rows",
        ),
        ApertureOrbitBacktestB8ComparisonRow(
            "B8_matched_nonbirth_control",
            "matched_positive_margin_count",
            str(sum(Fraction(row.control_phase_margin) > 0 for row in matched)),
            "must remain zero for matched non-birth controls",
        ),
        ApertureOrbitBacktestB8ComparisonRow(
            "B8_matched_nonbirth_control",
            "matched_measure_bucket_count",
            summary_map["matched_measure_bucket_count"],
            "matched controls should not collapse to one width",
        ),
        ApertureOrbitBacktestB8ComparisonRow(
            "B8_matched_nonbirth_control",
            "matched_reflection_orbit_count",
            summary_map["matched_reflection_orbit_count"],
            "matched controls should not collapse to one orbit",
        ),
        ApertureOrbitBacktestB8ComparisonRow(
            "B8_sample_calibration",
            "k8_sample_rows",
            summary_map["k8_sample_rows"],
            "sample calibration only, not recall",
        ),
        ApertureOrbitBacktestB8ComparisonRow(
            "B8_sample_calibration",
            "k8_sample_overlap_with_32",
            summary_map["k8_sample_overlap_with_32"],
            "overlap count only, not recall",
        ),
    ]


def read_aperture_orbit_backtest_family_csv(
    path: str | Path = DEFAULT_APERTURE_ORBIT_BACKTEST_FAMILY_SUMMARY_CSV,
) -> list[ApertureOrbitBacktestFamilyRow]:
    return _read_dataclass_csv(path, ApertureOrbitBacktestFamilyRow)


def read_aperture_orbit_backtest_scope_csv(
    path: str | Path = DEFAULT_APERTURE_ORBIT_BACKTEST_SCOPE_SUMMARY_CSV,
) -> list[ApertureOrbitBacktestScopeRow]:
    return _read_dataclass_csv(path, ApertureOrbitBacktestScopeRow)


def read_aperture_orbit_backtest_b8_comparison_csv(
    path: str | Path = DEFAULT_APERTURE_ORBIT_BACKTEST_B8_COMPARISON_CSV,
) -> list[ApertureOrbitBacktestB8ComparisonRow]:
    return _read_dataclass_csv(path, ApertureOrbitBacktestB8ComparisonRow)


def backtest_signature(row: object) -> tuple[object, ...]:
    return row_signature(row)


def _family_diagnostic_class(row) -> str:
    if row.capacity_pass and row.close_lift_count:
        return "capacity_close_family"
    if row.capacity_pass:
        return "capacity_nonclose_family"
    return "no_capacity_family"


def _separator_status(family_rows, close_lifts, nonclose_lifts) -> str:
    close_ok = all(
        row.capacity_pass
        and row.phase_pass_count == row.close_lift_count == row.birth_lift_count == 1
        and row.nonbirth_close_count == 0
        for row in family_rows
        if row.close_lift_count
    )
    close_lift_ok = all(
        row.phase_rank_desc == 1 and Fraction(row.phase_margin) > 0
        for row in close_lifts
    )
    nonclose_ok = all(Fraction(row.phase_margin) <= 0 for row in nonclose_lifts)
    return "stable_separator" if close_ok and close_lift_ok and nonclose_ok else "review"


def _ratio_text(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "undefined"
    return f"{numerator}/{denominator}"


def _read_dataclass_csv(path: str | Path, row_type: type):
    int_fields = {
        "parent_residue",
        "new_prime",
        "lift_count",
        "phase_pass_count",
        "close_lift_count",
        "birth_lift_count",
        "nonbirth_close_count",
        "family_count",
        "close_count",
        "birth_count",
        "capacity_close_families",
        "capacity_nonclose_families",
        "close_phase_rank_1_count",
        "close_positive_margin_count",
        "nonclose_positive_margin_count",
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
