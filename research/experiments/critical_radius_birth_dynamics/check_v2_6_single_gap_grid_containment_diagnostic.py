#!/usr/bin/env python3
"""Audit v2.6 single-gap q-grid containment diagnostic."""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from check_v2_6_special_point_obstruction import repo_root_from_script


Interval = tuple[Fraction, Fraction]

EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
DATA_REL = EXPERIMENT_REL / "data"
NOTES_REL = EXPERIMENT_REL / "notes"

PHASE_REL = DATA_REL / "prc_v2_4_phase_gate_lift_diagnostics_v0_1.csv"
SUMMARY_REL = DATA_REL / "prc_v2_6_single_gap_grid_containment_summary_v0_1.csv"
NOTE_REL = NOTES_REL / "prc_v2_6_single_gap_grid_containment_diagnostic_v0_1.md"

SCOPE_ORDER = ("B4_to_B5_full", "B5_to_B6_full", "B6_to_B7_full")
PRIMES_BY_K = {
    4: (2, 3, 5, 7),
    5: (2, 3, 5, 7, 11),
    6: (2, 3, 5, 7, 11, 13),
}
REQUIRED_SECTIONS = (
    "## Goal",
    "## Definitions",
    "## Single-Gap Grid Containment",
    "## Capacity vs Grid Alignment",
    "## Forbidden Remainders",
    "## Endpoint-Touch Strictness",
    "## Checked-Scope Audit",
    "## Gate R Decision",
    "## Non-claims",
)
REQUIRED_PHRASES = (
    "source-only v2.6 Gate R diagnostic",
    "single-gap q-grid containment",
    "I_q(a) = [(a - 1/2)/q, (a + 1/2)/q]",
    "qR - 1/2 < a < qL + 1/2",
    "q(R-L) < 1",
    "capacity=false_positive_filter_only",
    "grid endpoint-touch rows are 0",
    "strict single-gap q-grid containment matches close rows exactly",
    "diagnostic=continue",
    "single_gap_grid_containment=continue",
    "public_theorem=defer",
    "no theorem claim",
    "no predictor claim",
    "no public theorem claim",
    "no DOI claim",
    "no GitHub Release claim",
    "no B8 theorem claim",
    "no asymptotic law claim",
)
EXPECTED_ROWS = {
    "B4_to_B5_full": {
        "checked_lift_rows": "2288",
        "single_gap_lift_rows": "1573",
        "multi_gap_lift_rows": "715",
        "capacity_pass_rows": "308",
        "grid_strict_containment_rows": "14",
        "grid_endpoint_touch_rows": "0",
        "close_rows": "14",
        "nonclose_capacity_false_positive_rows": "294",
        "grid_close_mismatch_rows": "0",
        "decision": "single_gap_grid_containment_matches_close",
    },
    "B5_to_B6_full": {
        "checked_lift_rows": "29562",
        "single_gap_lift_rows": "17693",
        "multi_gap_lift_rows": "11869",
        "capacity_pass_rows": "2912",
        "grid_strict_containment_rows": "42",
        "grid_endpoint_touch_rows": "0",
        "close_rows": "42",
        "nonclose_capacity_false_positive_rows": "2870",
        "grid_close_mismatch_rows": "0",
        "decision": "single_gap_grid_containment_matches_close",
    },
    "B6_to_B7_full": {
        "checked_lift_rows": "501840",
        "single_gap_lift_rows": "267495",
        "multi_gap_lift_rows": "234345",
        "capacity_pass_rows": "50116",
        "grid_strict_containment_rows": "714",
        "grid_endpoint_touch_rows": "0",
        "close_rows": "714",
        "nonclose_capacity_false_positive_rows": "49402",
        "grid_close_mismatch_rows": "0",
        "decision": "single_gap_grid_containment_matches_close",
    },
}


@dataclass(frozen=True)
class Containment:
    margin: Fraction
    uses_endpoint_touching: bool


def read_csv(repo_root: Path, relative_path: Path) -> list[dict[str, str]]:
    path = repo_root / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"missing required artifact: {relative_path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def truth(value: str) -> bool:
    return value == "True"


def exact_arc_intervals_for_residue(residue: int, prime: int) -> list[Interval]:
    remainder = residue % prime
    center = Fraction(remainder, prime)
    radius = Fraction(1, 2 * prime)
    start = center - radius
    end = center + radius
    one = Fraction(1)
    if start < 0:
        return [(Fraction(0), end), (one + start, one)]
    if end > one:
        return [(Fraction(0), end - one), (start, one)]
    return [(start, end)]


def merge_closed_intervals(intervals: list[Interval]) -> list[Interval]:
    if not intervals:
        return []
    sorted_intervals = sorted(intervals)
    merged = [sorted_intervals[0]]
    for start, end in sorted_intervals[1:]:
        old_start, old_end = merged[-1]
        if start <= old_end:
            merged[-1] = (old_start, max(old_end, end))
        else:
            merged.append((start, end))
    return merged


def residue_uncovered_intervals(residue: int, primes: tuple[int, ...]) -> list[Interval]:
    covered: list[Interval] = []
    for prime in primes:
        covered.extend(exact_arc_intervals_for_residue(residue, prime))
    merged = merge_closed_intervals(covered)
    if not merged:
        return [(Fraction(0), Fraction(1))]
    gaps: list[Interval] = []
    for index, (_, end) in enumerate(merged):
        next_start = merged[(index + 1) % len(merged)][0]
        if index == len(merged) - 1:
            if end != Fraction(1) or next_start != 0:
                gaps.append((end, next_start))
        elif end < next_start:
            gaps.append((end, next_start))
    return gaps


def split_interval(interval: Interval) -> list[Interval]:
    start, end = interval
    if start <= end:
        return [interval]
    return [(start, Fraction(1)), (Fraction(0), end)]


def classify_birth_containment(
    previous_gaps: list[Interval],
    new_arcs: list[Interval],
) -> Containment:
    arc_segments = [segment for interval in new_arcs for segment in split_interval(interval)]
    margins: list[Fraction] = []
    for gap in previous_gaps:
        for gap_segment in split_interval(gap):
            containing = [
                (gap_segment[0] - arc[0], arc[1] - gap_segment[1])
                for arc in arc_segments
                if arc[0] <= gap_segment[0] and gap_segment[1] <= arc[1]
            ]
            if not containing:
                raise ValueError("birth gap is not contained in the new prime arc")
            margins.append(
                max(min(left_margin, right_margin) for left_margin, right_margin in containing)
            )
    margin = min(margins) if margins else Fraction(0)
    return Containment(margin=margin, uses_endpoint_touching=margin == 0)


def build_summary(phase_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    gaps_by_parent: dict[tuple[int, int], list[Interval]] = {}
    counters: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "checked_lift_rows": 0,
            "single_gap_lift_rows": 0,
            "multi_gap_lift_rows": 0,
            "capacity_pass_rows": 0,
            "grid_strict_containment_rows": 0,
            "grid_endpoint_touch_rows": 0,
            "close_rows": 0,
            "nonclose_capacity_false_positive_rows": 0,
            "grid_close_mismatch_rows": 0,
        }
    )

    for row in phase_rows:
        scope = row["scope"]
        parent_k = int(row["parent_k"])
        parent_residue = int(row["parent_residue"])
        q = int(row["new_prime"])
        remainder = int(row["new_prime_remainder"])
        gaps_key = (parent_k, parent_residue)
        if gaps_key not in gaps_by_parent:
            gaps_by_parent[gaps_key] = residue_uncovered_intervals(
                parent_residue,
                PRIMES_BY_K[parent_k],
            )
        gaps = gaps_by_parent[gaps_key]
        counter = counters[scope]
        counter["checked_lift_rows"] += 1
        counter["single_gap_lift_rows"] += int(len(gaps) == 1)
        counter["multi_gap_lift_rows"] += int(len(gaps) != 1)
        counter["capacity_pass_rows"] += int(truth(row["capacity_pass"]))
        counter["close_rows"] += int(truth(row["is_close"]))
        counter["nonclose_capacity_false_positive_rows"] += int(
            truth(row["capacity_pass"]) and not truth(row["is_close"])
        )

        new_arcs = exact_arc_intervals_for_residue(remainder, q)
        try:
            containment = classify_birth_containment(gaps, new_arcs)
            grid_close = containment.margin > 0
            counter["grid_strict_containment_rows"] += int(grid_close)
            counter["grid_endpoint_touch_rows"] += int(containment.uses_endpoint_touching)
            if containment.margin != Fraction(row["phase_margin"]):
                counter["grid_close_mismatch_rows"] += 1
        except ValueError:
            grid_close = False
        counter["grid_close_mismatch_rows"] += int(grid_close != truth(row["is_close"]))

    rows: list[dict[str, str]] = []
    for scope in SCOPE_ORDER:
        counter = counters[scope]
        rows.append(
            {
                "scope": scope,
                "checked_lift_rows": str(counter["checked_lift_rows"]),
                "single_gap_lift_rows": str(counter["single_gap_lift_rows"]),
                "multi_gap_lift_rows": str(counter["multi_gap_lift_rows"]),
                "capacity_pass_rows": str(counter["capacity_pass_rows"]),
                "grid_strict_containment_rows": str(
                    counter["grid_strict_containment_rows"]
                ),
                "grid_endpoint_touch_rows": str(counter["grid_endpoint_touch_rows"]),
                "close_rows": str(counter["close_rows"]),
                "nonclose_capacity_false_positive_rows": str(
                    counter["nonclose_capacity_false_positive_rows"]
                ),
                "grid_close_mismatch_rows": str(counter["grid_close_mismatch_rows"]),
                "decision": "single_gap_grid_containment_matches_close",
            }
        )
    return rows


def require_note(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / NOTE_REL
    if not path.is_file():
        failures.append(f"missing single-gap grid containment note: {NOTE_REL}")
        return
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.replace("`", "").split())
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"single-gap grid containment note missing section {section}")
    for phrase in REQUIRED_PHRASES:
        normalized_phrase = " ".join(phrase.replace("`", "").split())
        if normalized_phrase not in normalized:
            failures.append(
                f"single-gap grid containment note missing phrase {phrase!r}"
            )


def require_summary(repo_root: Path, failures: list[str]) -> None:
    regenerated = build_summary(read_csv(repo_root, PHASE_REL))
    committed = read_csv(repo_root, SUMMARY_REL)
    if committed != regenerated:
        failures.append(
            "committed single-gap grid containment summary differs from regenerated summary"
        )
        return
    by_scope = {row["scope"]: row for row in committed}
    if set(by_scope) != set(EXPECTED_ROWS):
        failures.append(f"unexpected single-gap grid containment scopes: {sorted(by_scope)}")
        return
    for scope, expected in EXPECTED_ROWS.items():
        row = by_scope[scope]
        for field, value in expected.items():
            if row.get(field) != value:
                failures.append(
                    f"{scope}: expected {field}={value!r}, got {row.get(field)!r}"
                )


def main() -> int:
    repo_root = repo_root_from_script()
    failures: list[str] = []

    require_note(repo_root, failures)
    require_summary(repo_root, failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_6_single_gap_grid_containment_diagnostic: "
        "checks=9, failed=0, "
        "single_gap_grid_containment=continue, public_theorem=defer"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
