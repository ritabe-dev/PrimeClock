#!/usr/bin/env python3
"""Standalone rational checker for the PRC C4/B5 finite certificate CSVs.

This script intentionally uses only the Python standard library. It does not
import prime_reciprocal_projection package code, so it can serve as a small
external audit of the public finite-theorem CSVs.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Iterable

Interval = tuple[Fraction, Fraction]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify PRC C4/B5 finite certificate CSVs using only stdlib.",
    )
    parser.add_argument(
        "--ck-full",
        default="data/summaries/prc_prime_prefix_ck_full_v1_1.csv",
    )
    parser.add_argument(
        "--c4-exclusion-witnesses",
        default="data/summaries/prc_prime_prefix_c4_exclusion_witness_v1_6.csv",
    )
    parser.add_argument(
        "--c4-exclusion-summary",
        default="data/summaries/prc_prime_prefix_c4_exclusion_summary_v1_5.csv",
    )
    parser.add_argument(
        "--b5-birth-witnesses",
        default="data/summaries/prc_prime_prefix_birth_witness_v1_5.csv",
    )
    parser.add_argument(
        "--b5-birth-classification",
        default="data/summaries/prc_prime_prefix_b5_birth_classification_v1_5.csv",
    )
    parser.add_argument(
        "--b5-birth-pair-summary",
        default="data/summaries/prc_prime_prefix_b5_birth_pair_summary_v1_5.csv",
    )
    parser.add_argument(
        "--out",
        default=(
            "data/summaries/"
            "prc_prime_prefix_certificate_standalone_verification_v1_8.csv"
        ),
    )
    args = parser.parse_args()

    rows = verification_rows(
        ck_full_csv=args.ck_full,
        c4_exclusion_witness_csv=args.c4_exclusion_witnesses,
        c4_exclusion_summary_csv=args.c4_exclusion_summary,
        b5_birth_witness_csv=args.b5_birth_witnesses,
        b5_birth_classification_csv=args.b5_birth_classification,
        b5_birth_pair_summary_csv=args.b5_birth_pair_summary,
    )
    write_rows(rows, args.out)
    failed = sum(int(row["failed"]) for row in rows)
    print(
        "check_prime_prefix_c4_b5: "
        f"checks={len(rows)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows(
    *,
    ck_full_csv: str | Path,
    c4_exclusion_witness_csv: str | Path,
    c4_exclusion_summary_csv: str | Path,
    b5_birth_witness_csv: str | Path,
    b5_birth_classification_csv: str | Path,
    b5_birth_pair_summary_csv: str | Path,
) -> list[dict[str, str]]:
    ck_rows = read_csv(ck_full_csv)
    c4_witness_rows = read_csv(c4_exclusion_witness_csv)
    c4_summary_rows = read_csv(c4_exclusion_summary_csv)
    b5_witness_rows = read_csv(b5_birth_witness_csv)
    b5_classification_rows = read_csv(b5_birth_classification_csv)
    b5_pair_rows = read_csv(b5_birth_pair_summary_csv)

    checks: list[dict[str, str]] = []

    c4_positive_expected = {2, 208}
    c4_positive_actual = [
        int(row["residue"])
        for row in ck_rows
        if row.get("k") == "4"
    ]
    c4_positive_passed = (
        len(c4_positive_actual) == 2
        and set(c4_positive_actual) == c4_positive_expected
        and all(is_covered(residue, [2, 3, 5, 7]) for residue in c4_positive_actual)
    )
    checks.append(check("c4_positive_rows_exact", 2, 2 if c4_positive_passed else 0))

    c4_exclusion_expected = set(range(210)) - c4_positive_expected
    c4_exclusion_actual = [int(row["residue"]) for row in c4_witness_rows]
    c4_exclusion_set_passed = (
        len(c4_exclusion_actual) == 208
        and len(set(c4_exclusion_actual)) == 208
        and set(c4_exclusion_actual) == c4_exclusion_expected
    )
    checks.append(
        check(
            "c4_exclusion_rows_exact",
            208,
            208 if c4_exclusion_set_passed else 0,
        )
    )

    c4_witness_passed = sum(
        c4_witness_row_matches(row)
        for row in c4_witness_rows
    )
    checks.append(check("c4_exclusion_witness_fields_exact", 208, c4_witness_passed))

    expected_c4_summary = expected_c4_summary_tuples(c4_witness_rows)
    actual_c4_summary = actual_c4_summary_tuples(c4_summary_rows)
    c4_summary_unique = len(actual_c4_summary) == len(c4_summary_rows)
    c4_summary_passed = (
        len(expected_c4_summary & actual_c4_summary)
        if c4_summary_unique
        else 0
    )
    checks.append(
        check(
            "c4_summary_partitions_witness_rows",
            max(len(expected_c4_summary), len(actual_c4_summary)),
            c4_summary_passed,
        )
    )

    expected_c5 = expected_c5_rows()
    actual_c5 = {
        (int(row["residue"]), row["status"])
        for row in ck_rows
        if row.get("k") == "5"
    }
    c5_row_count = sum(1 for row in ck_rows if row.get("k") == "5")
    c5_passed = (
        len(expected_c5 & actual_c5)
        if len(actual_c5) == c5_row_count
        else 0
    )
    checks.append(check("c5_full_rows_exact", max(len(expected_c5), len(actual_c5)), c5_passed))

    expected_birth_residues = {residue for residue, status in expected_c5 if status == "birth"}
    b5_witness_residues = [int(row["residue"]) for row in b5_witness_rows]
    b5_witness_set_passed = (
        len(b5_witness_residues) == 14
        and len(set(b5_witness_residues)) == 14
        and set(b5_witness_residues) == expected_birth_residues
    )
    checks.append(
        check(
            "b5_birth_witness_rows_exact",
            14,
            14 if b5_witness_set_passed else 0,
        )
    )

    b5_witness_fields_passed = sum(
        b5_witness_row_matches(row)
        for row in b5_witness_rows
    )
    checks.append(check("b5_birth_witness_fields_exact", 14, b5_witness_fields_passed))

    expected_classification = expected_b5_classification_tuples()
    actual_classification = {b5_classification_tuple(row) for row in b5_classification_rows}
    classification_passed = (
        len(expected_classification & actual_classification)
        if len(actual_classification) == len(b5_classification_rows)
        else 0
    )
    checks.append(
        check(
            "b5_classification_rows_exact",
            max(len(expected_classification), len(actual_classification)),
            classification_passed,
        )
    )

    expected_pairs = expected_b5_pair_summary_tuples()
    actual_pairs = {b5_pair_summary_tuple(row) for row in b5_pair_rows}
    pairs_passed = (
        len(expected_pairs & actual_pairs)
        if len(actual_pairs) == len(b5_pair_rows)
        else 0
    )
    checks.append(
        check(
            "b5_pair_summary_rows_exact",
            max(len(expected_pairs), len(actual_pairs)),
            pairs_passed,
        )
    )

    return checks


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(rows: Iterable[dict[str, str]], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["check_name", "total", "passed", "failed", "status"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def check(name: str, total: int, passed: int) -> dict[str, str]:
    failed = total - passed
    return {
        "check_name": name,
        "total": str(total),
        "passed": str(passed),
        "failed": str(failed),
        "status": "pass" if failed == 0 else "fail",
    }


def expected_c5_rows() -> set[tuple[int, str]]:
    rows: set[tuple[int, str]] = set()
    for residue in range(2310):
        if is_covered(residue, [2, 3, 5, 7, 11]):
            status = "inherited" if residue % 210 in {2, 208} else "birth"
            rows.add((residue, status))
    return rows


def c4_witness_row_matches(row: dict[str, str]) -> bool:
    residue = int(row["residue"])
    gaps = uncovered_intervals(residue, [2, 3, 5, 7])
    measure = uncovered_measure(residue, [2, 3, 5, 7])
    if not gaps:
        return False
    witness = parse_fraction(row["witness_point"])
    return (
        row.get("k") == "4"
        and row.get("new_prime") == "7"
        and row.get("primorial") == "210"
        and row.get("reflection_residue") == str((-residue) % 210)
        and row.get("open_gap_count") == str(len(gaps))
        and row.get("uncovered_measure_fraction") == format_fraction(measure)
        and row.get("first_open_gap_boundary_endpoints") == format_intervals(gaps[:1])
        and row.get("witness_point") == format_fraction(circular_midpoint(gaps[0]))
        and row.get("open_gap_boundary_endpoints") == format_intervals(gaps)
        and point_in_open_interval(witness, gaps[0])
        and not point_is_covered_by_closed_arcs(witness, residue, [2, 3, 5, 7])
    )


def b5_witness_row_matches(row: dict[str, str]) -> bool:
    residue = int(row["residue"])
    gaps = uncovered_intervals(residue, [2, 3, 5, 7])
    measure = uncovered_measure(residue, [2, 3, 5, 7])
    new_arcs = arc_intervals(residue, 11)
    return (
        row.get("k") == "5"
        and row.get("new_prime") == "11"
        and row.get("primorial") == "2310"
        and row.get("residue_mod_previous") == str(residue % 210)
        and row.get("reflection_residue") == str((-residue) % 2310)
        and row.get("previous_open_gap_count") == str(len(gaps))
        and row.get("previous_prefix_uncovered_measure_fraction") == format_fraction(measure)
        and row.get("previous_prefix_uncovered_measure") == str(float(measure))
        and row.get("previous_open_gap_boundary_endpoints") == format_intervals(gaps)
        and row.get("new_prime_closed_arc_boundary_endpoints") == format_intervals(new_arcs)
        and row.get("uses_endpoint_touching") == str(uses_endpoint_touching(gaps, new_arcs))
        and not is_covered(residue, [2, 3, 5, 7])
        and is_covered(residue, [2, 3, 5, 7, 11])
        and all(gap_strictly_inside_closed_arcs(gap, new_arcs) for gap in gaps)
    )


def expected_b5_classification_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for residue, status in sorted(expected_c5_rows()):
        if status != "birth":
            continue
        reflection = (-residue) % 2310
        gaps = uncovered_intervals(residue, [2, 3, 5, 7])
        measure = uncovered_measure(residue, [2, 3, 5, 7])
        new_arcs = arc_intervals(residue, 11)
        rows.append(
            {
                "k": "5",
                "new_prime": "11",
                "primorial": "2310",
                "residue": str(residue),
                "reflection_residue": str(reflection),
                "reflection_pair_min": str(min(residue, reflection)),
                "reflection_pair_max": str(max(residue, reflection)),
                "parent_residue_mod_previous": str(residue % 210),
                "previous_open_gap_count": str(len(gaps)),
                "previous_prefix_uncovered_measure_fraction": format_fraction(measure),
                "previous_prefix_uncovered_measure": str(float(measure)),
                "previous_open_gap_boundary_endpoints": format_intervals(gaps),
                "new_prime_remainder": str(residue % 11),
                "new_prime_closed_arc_boundary_endpoints": format_intervals(new_arcs),
                "uses_endpoint_touching": str(uses_endpoint_touching(gaps, new_arcs)),
            }
        )
    return rows


def expected_b5_classification_tuples() -> set[tuple[str, ...]]:
    return {b5_classification_tuple(row) for row in expected_b5_classification_rows()}


def b5_classification_tuple(row: dict[str, str]) -> tuple[str, ...]:
    return (
        row["k"],
        row["new_prime"],
        row["primorial"],
        row["residue"],
        row["reflection_residue"],
        row["reflection_pair_min"],
        row["reflection_pair_max"],
        row["parent_residue_mod_previous"],
        row["previous_open_gap_count"],
        row["previous_prefix_uncovered_measure_fraction"],
        row["previous_prefix_uncovered_measure"],
        row["previous_open_gap_boundary_endpoints"],
        row["new_prime_remainder"],
        row["new_prime_closed_arc_boundary_endpoints"],
        row["uses_endpoint_touching"],
    )


def expected_b5_pair_summary_tuples() -> set[tuple[str, ...]]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in expected_b5_classification_rows():
        groups[(row["reflection_pair_min"], row["reflection_pair_max"])].append(row)

    tuples: set[tuple[str, ...]] = set()
    for (pair_min, pair_max), group in sorted(groups.items()):
        ordered = sorted(group, key=lambda row: int(row["residue"]))
        tuples.add(
            (
                "5",
                "11",
                "2310",
                pair_min,
                pair_max,
                join_pair(row["parent_residue_mod_previous"] for row in ordered),
                join_pair(row["previous_open_gap_count"] for row in ordered),
                join_pair(
                    row["previous_prefix_uncovered_measure_fraction"]
                    for row in ordered
                ),
                join_pair(row["previous_prefix_uncovered_measure"] for row in ordered),
                join_pair(row["previous_open_gap_boundary_endpoints"] for row in ordered),
                join_pair(row["new_prime_remainder"] for row in ordered),
                join_pair(
                    row["new_prime_closed_arc_boundary_endpoints"]
                    for row in ordered
                ),
                join_pair(row["uses_endpoint_touching"] for row in ordered),
            )
        )
    return tuples


def b5_pair_summary_tuple(row: dict[str, str]) -> tuple[str, ...]:
    return (
        row["k"],
        row["new_prime"],
        row["primorial"],
        row["reflection_pair_min"],
        row["reflection_pair_max"],
        row["parent_residue_pair_mod_previous"],
        row["previous_open_gap_count_pair"],
        row["previous_prefix_uncovered_measure_fraction_pair"],
        row["previous_prefix_uncovered_measure_pair"],
        row["previous_open_gap_boundary_endpoints_pair"],
        row["new_prime_remainder_pair"],
        row["new_prime_closed_arc_boundary_endpoints_pair"],
        row["uses_endpoint_touching_pair"],
    )


def expected_c4_summary_tuples(rows: Iterable[dict[str, str]]) -> set[tuple[str, ...]]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[(row["open_gap_count"], row["uncovered_measure_fraction"])].append(row)

    tuples: set[tuple[str, ...]] = set()
    for (gap_count, measure), group in groups.items():
        residues = sorted(int(row["residue"]) for row in group)
        samples = sorted({row["first_open_gap_boundary_endpoints"] for row in group})
        tuples.add(
            (
                "4",
                "7",
                "210",
                gap_count,
                measure,
                str(len(residues)),
                " ".join(str(residue) for residue in residues),
                " ".join(samples[:8]),
            )
        )
    return tuples


def actual_c4_summary_tuples(rows: Iterable[dict[str, str]]) -> set[tuple[str, ...]]:
    return {
        (
            row["k"],
            row["new_prime"],
            row["primorial"],
            row["open_gap_count"],
            row["uncovered_measure_fraction"],
            row["residue_count"],
            row["residues"],
            row["first_open_gap_boundary_endpoint_sample"],
        )
        for row in rows
    }


def is_covered(residue: int, primes: Iterable[int]) -> bool:
    intervals = [interval for p in primes for interval in raw_arc_intervals(residue, p)]
    intervals.sort(key=lambda item: (Fraction(item[0], item[1]), Fraction(item[2], item[3])))
    start_num, _, end_num, end_den = intervals[0]
    for next_start_num, next_start_den, next_end_num, next_end_den in intervals[1:]:
        if next_start_num * end_den <= end_num * next_start_den:
            if next_end_num * end_den > end_num * next_end_den:
                end_num, end_den = next_end_num, next_end_den
        else:
            return False
    return start_num == 0 and end_num >= end_den


def covered_intervals(residue: int, primes: Iterable[int]) -> list[Interval]:
    return merge_intervals([interval for p in primes for interval in arc_intervals(residue, p)])


def uncovered_intervals(residue: int, primes: Iterable[int]) -> list[Interval]:
    covered = covered_intervals(residue, primes)
    if not covered:
        return [(Fraction(0), Fraction(1))]
    if covered == [(Fraction(0), Fraction(1))]:
        return []

    gaps: list[Interval] = []
    one = Fraction(1)
    for index, (_, end) in enumerate(covered):
        next_start = covered[(index + 1) % len(covered)][0]
        gap_end = next_start + one if index == len(covered) - 1 else next_start
        if gap_end > end:
            gaps.append((end % one, gap_end % one))
    return gaps


def uncovered_measure(residue: int, primes: Iterable[int]) -> Fraction:
    return sum((interval_length(interval) for interval in uncovered_intervals(residue, primes)), Fraction(0))


def arc_intervals(residue: int, p: int) -> list[Interval]:
    remainder = residue % p
    center = Fraction(remainder, p)
    radius = Fraction(1, 2 * p)
    start = center - radius
    end = center + radius
    one = Fraction(1)
    if start < 0:
        return [(Fraction(0), end), (one + start, one)]
    if end > one:
        return [(Fraction(0), end - one), (start, one)]
    return [(start, end)]


def raw_arc_intervals(residue: int, p: int) -> list[tuple[int, int, int, int]]:
    remainder = residue % p
    denominator = 2 * p
    start = 2 * remainder - 1
    end = 2 * remainder + 1
    if start < 0:
        return [(0, 1, end, denominator), (denominator + start, denominator, 1, 1)]
    if end > denominator:
        return [(0, 1, end - denominator, denominator), (start, denominator, 1, 1)]
    return [(start, denominator, end, denominator)]


def merge_intervals(intervals: Iterable[Interval]) -> list[Interval]:
    normalized = [(start, end) for start, end in intervals if start != end]
    if not normalized:
        return []
    normalized.sort()
    merged: list[Interval] = []
    current_start, current_end = normalized[0]
    for start, end in normalized[1:]:
        if start <= current_end:
            current_end = max(current_end, end)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end
    merged.append((current_start, current_end))
    return merged


def gap_strictly_inside_closed_arcs(gap: Interval, arcs: Iterable[Interval]) -> bool:
    arc_segments = [segment for arc in arcs for segment in split_interval(arc)]
    for gap_segment in split_interval(gap):
        gap_start, gap_end = gap_segment
        if not any(
            point_in_open_interval(gap_start, arc_segment)
            and point_in_open_interval(gap_end, arc_segment)
            for arc_segment in arc_segments
        ):
            return False
    return True


def uses_endpoint_touching(gaps: Iterable[Interval], arcs: Iterable[Interval]) -> bool:
    arc_segments = [segment for arc in arcs for segment in split_interval(arc)]
    for gap in gaps:
        for gap_start, gap_end in split_interval(gap):
            for arc_start, arc_end in arc_segments:
                if arc_start <= gap_start and gap_end <= arc_end:
                    if gap_start == arc_start or gap_end == arc_end:
                        return True
                    break
            else:
                raise ValueError("gap is not contained in the new prime arc")
    return False


def point_is_covered_by_closed_arcs(point: Fraction, residue: int, primes: Iterable[int]) -> bool:
    return any(
        point_in_closed_interval(point, interval)
        for p in primes
        for interval in arc_intervals(residue, p)
    )


def point_in_closed_interval(point: Fraction, interval: Interval) -> bool:
    return any(start <= point <= end for start, end in split_interval(interval))


def point_in_open_interval(point: Fraction, interval: Interval) -> bool:
    return any(start < point < end for start, end in split_interval(interval))


def split_interval(interval: Interval) -> list[Interval]:
    start, end = interval
    if end >= start:
        return [(start, end)]
    return [(start, Fraction(1)), (Fraction(0), end)]


def interval_length(interval: Interval) -> Fraction:
    start, end = interval
    if end >= start:
        return end - start
    return Fraction(1) - start + end


def circular_midpoint(interval: Interval) -> Fraction:
    start, end = interval
    if end >= start:
        return (start + end) / 2
    return ((start + end + 1) / 2) % 1


def parse_fraction(text: str) -> Fraction:
    if "/" in text:
        numerator, denominator = text.split("/", 1)
        return Fraction(int(numerator), int(denominator))
    return Fraction(int(text), 1)


def parse_intervals(text: str) -> list[Interval]:
    if not text:
        return []
    intervals: list[Interval] = []
    for item in text.split(";"):
        start, end = item.split("-", 1)
        intervals.append((parse_fraction(start), parse_fraction(end)))
    return intervals


def format_fraction(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def format_intervals(intervals: Iterable[Interval]) -> str:
    return ";".join(
        f"{format_fraction(start)}-{format_fraction(end)}"
        for start, end in intervals
    )


def join_pair(values: Iterable[object]) -> str:
    return " / ".join(str(value) for value in values)


if __name__ == "__main__":
    raise SystemExit(main())
