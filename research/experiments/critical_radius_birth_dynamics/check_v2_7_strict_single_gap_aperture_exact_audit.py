#!/usr/bin/env python3
"""Audit recorded finite-scope birth rows for consistency with the v2.7 theorem note.

This is an implementation-consistency audit, not a mechanical proof of the
geometric theorem note.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[2]
DATA_DIR = EXPERIMENT_DIR / "data"
BIRTH_DYNAMICS_CSV = DATA_DIR / "prc_prime_prefix_birth_dynamics_k5_k7_v0_1.csv"
EXPECTED_SCOPE_COUNTS = {
    5: 14,   # B4 -> B5
    6: 42,   # B5 -> B6
    7: 714,  # B6 -> B7
}

ExactInterval = tuple[Fraction, Fraction]


def committed_csv_rows(path: Path, failures: list[str]) -> list[dict[str, str]]:
    if not path.is_file():
        failures.append(f"missing committed birth dynamics CSV: {path}")
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_fraction(text: str) -> Fraction:
    return Fraction(text)


def parse_interval(text: str) -> ExactInterval:
    left, right = text.split("-", 1)
    return parse_fraction(left), parse_fraction(right)


def parse_intervals(text: str) -> list[ExactInterval]:
    if not text:
        return []
    return [parse_interval(part) for part in text.split()]


def split_interval(interval: ExactInterval) -> list[ExactInterval]:
    start, end = interval
    if end >= start:
        return [(start, end)]
    return [(start, Fraction(1)), (Fraction(0), end)]


def exact_arc_intervals_for_residue(residue: int, p: int) -> list[ExactInterval]:
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


def classify_birth_containment(
    previous_gaps: list[ExactInterval],
    new_arcs: list[ExactInterval],
) -> tuple[Fraction, bool] | None:
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
                return None
            margins.append(max(min(left_margin, right_margin) for left_margin, right_margin in containing))
    margin = min(margins) if margins else Fraction(0)
    return margin, margin == 0


def strict_q_remainders(row: dict[str, str]) -> list[int]:
    previous_gaps = parse_intervals(row["previous_open_gap_boundary_endpoints"])
    q = int(row["new_prime"])
    valid: list[int] = []
    for remainder in range(q):
        containment = classify_birth_containment(
            previous_gaps,
            exact_arc_intervals_for_residue(remainder, q),
        )
        if containment is None:
            continue
        margin, _uses_endpoint_touching = containment
        if margin > 0:
            valid.append(remainder)
    return valid


def check_birth_rows(rows: list[dict[str, str]], failures: list[str]) -> None:
    by_k: dict[int, int] = defaultdict(int)
    by_parent: dict[tuple[int, int], list[int]] = defaultdict(list)

    for row in rows:
        k = int(row["k"])
        q = int(row["new_prime"])
        residue = int(row["residue"])
        parent = int(row["parent_residue_mod_previous"])
        new_prime_remainder = int(row["new_prime_remainder"])
        by_k[k] += 1
        by_parent[(k, parent)].append(new_prime_remainder)

        if row["birth_type"] != "strict_single_gap_birth":
            failures.append(
                f"non-strict-single-gap recorded birth row: k={k}, residue={residue}, "
                f"birth_type={row['birth_type']}"
            )
        if int(row["previous_open_gap_count"]) != 1:
            failures.append(
                f"recorded birth row is not single-gap: k={k}, residue={residue}, "
                f"previous_open_gap_count={row['previous_open_gap_count']}"
            )
        if row["uses_endpoint_touching"] != "False":
            failures.append(
                f"recorded birth row uses endpoint touching: k={k}, residue={residue}"
            )

        special_remainders = {0, (q - 1) // 2, (q + 1) // 2}
        if new_prime_remainder in special_remainders:
            failures.append(
                f"recorded birth row uses special remainder: k={k}, "
                f"q={q}, remainder={new_prime_remainder}"
            )

        previous_gaps = parse_intervals(row["previous_open_gap_boundary_endpoints"])
        recorded_containment = classify_birth_containment(
            previous_gaps,
            exact_arc_intervals_for_residue(new_prime_remainder, q),
        )
        if recorded_containment is None:
            failures.append(
                f"recorded birth row remainder does not contain old residual set: "
                f"k={k}, residue={residue}"
            )
            continue
        margin, uses_endpoint_touching = recorded_containment
        if uses_endpoint_touching:
            failures.append(
                f"recorded birth row has endpoint-touch containment: k={k}, "
                f"residue={residue}"
            )
        if margin != parse_fraction(row["containment_margin_fraction"]):
            failures.append(
                f"recorded containment margin mismatch: k={k}, residue={residue}"
            )

        valid_remainders = strict_q_remainders(row)
        if valid_remainders != [new_prime_remainder]:
            failures.append(
                f"birth parent does not have exactly one strict q-remainder: "
                f"k={k}, parent={parent}, "
                f"expected={[new_prime_remainder]}, actual={valid_remainders}"
            )

    for k, expected_count in EXPECTED_SCOPE_COUNTS.items():
        if by_k.get(k, 0) != expected_count:
            failures.append(
                f"checked finite scope k={k} birth count must be {expected_count}, "
                f"got {by_k.get(k, 0)}"
            )

    for (k, parent), remainders in sorted(by_parent.items()):
        if len(remainders) != 1:
            failures.append(
                f"birth parent has multiple recorded birth remainders: "
                f"k={k}, parent={parent}, remainders={remainders}"
            )


def main() -> int:
    failures: list[str] = []
    rows = committed_csv_rows(BIRTH_DYNAMICS_CSV, failures)
    check_birth_rows(rows, failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_7_strict_single_gap_aperture_exact_audit: "
        "checks=8, failed=0, "
        "recorded_birth_scopes=B4_to_B5,B5_to_B6,B6_to_B7, "
        f"recorded_birth_rows={len(rows)}, "
        "all_recorded_births=strict_single_gap, "
        "multigap_births=0, endpoint_touch_births=0, "
        "special_remainder_births=0, "
        "strict_remainder_uniqueness=passed, "
        "committed_csv=audited, "
        "exact_audit=implementation_consistency, "
        "mathematical_verification=not_claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
