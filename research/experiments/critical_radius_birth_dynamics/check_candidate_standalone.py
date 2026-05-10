#!/usr/bin/env python3
"""Standalone CSV checker for the internal PRC v2.3 candidate artifacts.

This checker intentionally uses only the Python standard library. It reads the
committed v2.3 candidate CSVs and checks the headline finite claims without
importing ``prime_reciprocal_projection`` or the experiment helper modules.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parent
DATA_DIR = EXPERIMENT_DIR / "data"

DEFAULT_PATHS = {
    "critical_radius": DATA_DIR / "prc_prime_prefix_critical_radius_k4_k5_v0_1.csv",
    "critical_radius_summary": DATA_DIR
    / "prc_prime_prefix_critical_radius_summary_v0_1.csv",
    "birth_threshold_crossing": DATA_DIR
    / "prc_prime_prefix_birth_threshold_crossing_k5_k7_v0_1.csv",
    "birth_dynamics": DATA_DIR / "prc_prime_prefix_birth_dynamics_k5_k7_v0_1.csv",
    "birth_dynamics_summary": DATA_DIR
    / "prc_prime_prefix_birth_dynamics_summary_v0_1.csv",
    "hash_manifest": DATA_DIR / "prc_v2_3_candidate_sha256sums_v0_1.txt",
    "out": DATA_DIR / "prc_v2_3_candidate_standalone_verification_v0_1.csv",
}

EXPECTED_BIRTH_COUNTS = {5: 14, 6: 42, 7: 714}
PRIMES_BY_K = {
    4: [2, 3, 5, 7],
    5: [2, 3, 5, 7, 11],
}
EXPECTED_HASH_PATHS = {
    "data/prc_prime_prefix_critical_radius_k4_k5_v0_1.csv",
    "data/prc_prime_prefix_critical_radius_summary_v0_1.csv",
    "data/prc_prime_prefix_critical_radius_near_misses_k4_k5_v0_1.csv",
    "data/prc_prime_prefix_near_miss_birth_parent_overlap_k4_k6_v0_1.csv",
    "data/prc_prime_prefix_near_miss_gap_geometry_k4_k5_v0_1.csv",
    "data/prc_prime_prefix_birth_threshold_crossing_k5_v0_1.csv",
    "data/prc_prime_prefix_birth_threshold_crossing_k5_k7_v0_1.csv",
    "data/prc_prime_prefix_birth_dynamics_k5_k7_v0_1.csv",
    "data/prc_prime_prefix_birth_dynamics_summary_v0_1.csv",
    "data/prc_v2_3_candidate_verification_v0_1.csv",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ExactInterval = tuple[Fraction, Fraction]


@dataclass(frozen=True)
class CheckResult:
    check_name: str
    total: int
    passed: int
    failed: int

    @property
    def status(self) -> str:
        return "pass" if self.failed == 0 else "fail"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256_bytes(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_hash_manifest(manifest_path: Path) -> CheckResult:
    checks: list[bool] = []
    manifest_root = manifest_path.parent.parent
    seen_paths: set[str] = set()
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, relative_path = line.split("  ", 1)
        except ValueError:
            checks.append(False)
            continue
        checks.append(True)
        if not SHA256_RE.fullmatch(expected):
            checks.append(False)
            continue
        checks.append(True)
        if relative_path in seen_paths:
            checks.append(False)
            continue
        checks.append(True)
        seen_paths.add(relative_path)
        if relative_path not in EXPECTED_HASH_PATHS:
            checks.append(False)
            continue
        checks.append(True)
        target = manifest_root / relative_path
        checks.append(target.is_file() and sha256_bytes(target) == expected)
    checks.extend(path in seen_paths for path in EXPECTED_HASH_PATHS)
    total = len(checks)
    failures = sum(1 for passed in checks if not passed)
    return CheckResult(
        "candidate_csv_hashes_exact",
        total,
        total - failures,
        failures,
    )


def level_set_residues(rows: list[dict[str, str]], k: int) -> set[int]:
    return {
        int(row["residue"])
        for row in rows
        if int(row["k"]) == k and Fraction(row["lambda_fraction"]) <= Fraction(1, 2)
    }


def center_for_residue(residue: int, p: int) -> Fraction:
    return Fraction(residue % p, p)


def circular_distance(left: Fraction, right: Fraction) -> Fraction:
    delta = abs((left - right) % 1)
    return min(delta, Fraction(1) - delta)


def critical_radius_from_definition(
    residue: int,
    primes: list[int],
) -> tuple[Fraction, Fraction, tuple[int, ...]]:
    centers = [(p, center_for_residue(residue, p)) for p in primes]
    candidates: set[Fraction] = {Fraction(0)}
    for _, center in centers:
        candidates.add(center % 1)
        candidates.add((center + Fraction(1, 2)) % 1)

    signs = (-1, 1)
    offsets = (-1, 0, 1)
    for left_index, (left_p, left_center) in enumerate(centers):
        for right_p, right_center in centers[left_index + 1 :]:
            for left_offset in offsets:
                lifted_left = left_center + left_offset
                for right_offset in offsets:
                    lifted_right = right_center + right_offset
                    for left_sign in signs:
                        for right_sign in signs:
                            denominator = left_p * left_sign - right_p * right_sign
                            if denominator == 0:
                                continue
                            numerator = (
                                left_p * left_sign * lifted_left
                                - right_p * right_sign * lifted_right
                            )
                            point = numerator / denominator
                            if not Fraction(0) <= point <= Fraction(1):
                                continue
                            if left_sign * (point - lifted_left) < 0:
                                continue
                            if right_sign * (point - lifted_right) < 0:
                                continue
                            candidates.add(point % 1)

    best_radius = Fraction(-1)
    best_point = Fraction(0)
    best_active: tuple[int, ...] = ()
    for point in sorted(candidates):
        distances = [
            (p * circular_distance(point, center), p)
            for p, center in centers
        ]
        radius = min(value for value, _ in distances)
        active = tuple(sorted(p for value, p in distances if value == radius))
        if radius > best_radius or (radius == best_radius and point < best_point):
            best_radius = radius
            best_point = point
            best_active = active

    return best_radius, best_point, best_active


def check_critical_radius_zero_residue(rows: list[dict[str, str]]) -> CheckResult:
    rows_by_k = {
        int(row["k"]): row
        for row in rows
        if row["residue"] == "0" and int(row["k"]) in PRIMES_BY_K
    }
    failures = 0
    for k in PRIMES_BY_K:
        row = rows_by_k.get(k)
        if row is None or Fraction(row["lambda_fraction"]) != Fraction(1):
            failures += 1
    total = len(PRIMES_BY_K)
    return CheckResult(
        "critical_radius_zero_residue_cusp_exact",
        total,
        total - failures,
        failures,
    )


def check_critical_radius_values_recomputed(rows: list[dict[str, str]]) -> CheckResult:
    failures = 0
    total = 0
    for row in rows:
        k = int(row["k"])
        primes = PRIMES_BY_K.get(k)
        if primes is None:
            continue
        total += 1
        expected_radius, _, _ = critical_radius_from_definition(
            int(row["residue"]),
            primes,
        )
        if Fraction(row["lambda_fraction"]) != expected_radius:
            failures += 1
    return CheckResult(
        "critical_radius_values_recomputed_from_definition",
        total,
        total - failures,
        failures,
    )


def check_c4_level_set(rows: list[dict[str, str]]) -> CheckResult:
    k4_rows = [row for row in rows if int(row["k"]) == 4]
    failures = 0
    if len(k4_rows) != 210:
        failures += 1
    if level_set_residues(rows, 4) != {2, 208}:
        failures += 1
    if any(row["status"] != "endpoint_covered" for row in k4_rows if row["residue"] in {"2", "208"}):
        failures += 1
    return CheckResult("critical_radius_c4_level_set_from_csv", 3, 3 - failures, failures)


def check_c5_level_set(rows: list[dict[str, str]]) -> CheckResult:
    k5_rows = [row for row in rows if int(row["k"]) == 5]
    failures = 0
    if len(k5_rows) != 2310:
        failures += 1
    level_set = level_set_residues(rows, 5)
    if len(level_set) != 36:
        failures += 1
    for row in k5_rows:
        in_level_set = int(row["residue"]) in level_set
        if (row["current_covering_residue"] == "True") != in_level_set:
            failures += 1
            break
    return CheckResult("critical_radius_c5_level_set_from_csv", 3, 3 - failures, failures)


def check_critical_radius_summary(
    rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> CheckResult:
    failures = 0
    total = len(summary_rows)
    rows_by_k = {
        k: [row for row in rows if int(row["k"]) == k]
        for k in [4, 5]
    }
    for summary in summary_rows:
        k = int(summary["k"])
        group = rows_by_k[k]
        robust = sum(row["status"] == "robust_covered" for row in group)
        endpoint = sum(row["status"] == "endpoint_covered" for row in group)
        uncovered = sum(row["status"] == "uncovered" for row in group)
        covered = robust + endpoint
        if int(summary["residue_count"]) != len(group):
            failures += 1
        elif int(summary["robust_covered_count"]) != robust:
            failures += 1
        elif int(summary["endpoint_covered_count"]) != endpoint:
            failures += 1
        elif int(summary["uncovered_count"]) != uncovered:
            failures += 1
        elif int(summary["covered_count"]) != covered:
            failures += 1
    return CheckResult("critical_radius_summary_matches_rows", total, total - failures, failures)


def check_birth_dynamics_summary(rows: list[dict[str, str]]) -> CheckResult:
    failures = 0
    total = len(EXPECTED_BIRTH_COUNTS)
    rows_by_k = {int(row["k"]): row for row in rows}
    for k, expected_count in EXPECTED_BIRTH_COUNTS.items():
        row = rows_by_k.get(k)
        if row is None:
            failures += 1
            continue
        if int(row["birth_count"]) != expected_count:
            failures += 1
        elif int(row["strict_single_gap_birth"]) != expected_count:
            failures += 1
        elif int(row["endpoint_single_gap_birth"]) != 0:
            failures += 1
        elif int(row["strict_multi_gap_birth"]) != 0:
            failures += 1
        elif int(row["endpoint_multi_gap_birth"]) != 0:
            failures += 1
        elif int(row["max_previous_open_gap_count"]) != 1:
            failures += 1
    return CheckResult("birth_dynamics_summary_strict_single_gap", total, total - failures, failures)


def check_birth_dynamics_rows(rows: list[dict[str, str]]) -> CheckResult:
    failures = 0
    total = sum(EXPECTED_BIRTH_COUNTS.values())
    if len(rows) != total:
        failures += 1
    for k, expected_count in EXPECTED_BIRTH_COUNTS.items():
        group = [row for row in rows if int(row["k"]) == k]
        if len(group) != expected_count:
            failures += 1
        for row in group:
            if row["birth_type"] != "strict_single_gap_birth":
                failures += 1
                break
            if int(row["previous_open_gap_count"]) != 1:
                failures += 1
                break
            if row["uses_endpoint_touching"] != "False":
                failures += 1
                break
    return CheckResult("birth_dynamics_rows_strict_single_gap", total + 4, total + 4 - failures, failures)


def split_interval(interval: ExactInterval) -> list[ExactInterval]:
    start, end = interval
    if end >= start:
        return [(start, end)]
    return [(start, Fraction(1)), (Fraction(0), end)]


def parse_intervals(value: str) -> list[ExactInterval]:
    intervals: list[ExactInterval] = []
    if not value:
        return intervals
    for item in value.split(";"):
        start, end = item.split("-", 1)
        intervals.append((Fraction(start), Fraction(end)))
    return intervals


def exact_arc_intervals_for_remainder(remainder: int, p: int) -> list[ExactInterval]:
    center = Fraction(remainder % p, p)
    radius = Fraction(1, 2 * p)
    start = center - radius
    end = center + radius
    if start < 0:
        return [(Fraction(0), end), (Fraction(1) + start, Fraction(1))]
    if end > 1:
        return [(Fraction(0), end - 1), (start, Fraction(1))]
    return [(start, end)]


def strict_containment_margin(
    previous_gaps: list[ExactInterval],
    new_arcs: list[ExactInterval],
) -> Fraction | None:
    arc_segments = [segment for arc in new_arcs for segment in split_interval(arc)]
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
            margins.append(
                max(
                    min(left_margin, right_margin)
                    for left_margin, right_margin in containing
                )
            )
    if not margins:
        return Fraction(0)
    return min(margins)


def check_unique_strict_single_gap_remainders(
    rows: list[dict[str, str]],
) -> CheckResult:
    failures = 0
    groups: dict[tuple[int, int], list[dict[str, str]]] = {}
    for row in rows:
        groups.setdefault(
            (int(row["k"]), int(row["parent_residue_mod_previous"])),
            [],
        ).append(row)
    total = len(rows) * 4 + len(EXPECTED_BIRTH_COUNTS) + len(groups)

    for k in EXPECTED_BIRTH_COUNTS:
        birth_count = sum(1 for row in rows if int(row["k"]) == k)
        parent_count = len(
            {
                int(row["parent_residue_mod_previous"])
                for row in rows
                if int(row["k"]) == k
            }
        )
        if birth_count != parent_count:
            failures += 1

    for group in groups.values():
        if len(group) != 1:
            failures += 1

    for row in rows:
        if row["birth_type"] != "strict_single_gap_birth":
            failures += 1
        if int(row["previous_open_gap_count"]) != 1:
            failures += 1
        if row["uses_endpoint_touching"] != "False":
            failures += 1

        previous_gaps = parse_intervals(row["previous_open_gap_boundary_endpoints"])
        new_prime = int(row["new_prime"])
        valid_remainders = []
        for remainder in range(new_prime):
            margin = strict_containment_margin(
                previous_gaps,
                exact_arc_intervals_for_remainder(remainder, new_prime),
            )
            if margin is not None and margin > 0:
                valid_remainders.append(remainder)
        if valid_remainders != [int(row["new_prime_remainder"])]:
            failures += 1

    return CheckResult(
        "birth_dynamics_b5_b6_b7_unique_strict_single_gap_remainders",
        total,
        total - failures,
        failures,
    )


def check_threshold_crossing(
    crossing_rows: list[dict[str, str]],
    birth_rows: list[dict[str, str]],
) -> CheckResult:
    failures = 0
    total = sum(EXPECTED_BIRTH_COUNTS.values())
    birth_sets = {
        k: {int(row["residue"]) for row in birth_rows if int(row["k"]) == k}
        for k in EXPECTED_BIRTH_COUNTS
    }
    crossing_sets = {
        k: {int(row["residue"]) for row in crossing_rows if int(row["k"]) == k}
        for k in EXPECTED_BIRTH_COUNTS
    }
    if crossing_sets != birth_sets:
        failures += 1
    for row in crossing_rows:
        if row["birth_type"] != "strict_single_gap_birth":
            failures += 1
            break
        if Fraction(row["parent_lambda_fraction"]) <= Fraction(1, 2):
            failures += 1
            break
        if Fraction(row["current_lambda_fraction"]) > Fraction(1, 2):
            failures += 1
            break
        if row["parent_status"] != "uncovered":
            failures += 1
            break
        if row["current_status"] not in {"robust_covered", "endpoint_covered"}:
            failures += 1
            break
    return CheckResult("birth_threshold_crossing_rows_match_births", total + 5, total + 5 - failures, failures)


def write_results(path: Path, results: list[CheckResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["check_name", "total", "passed", "failed", "status"],
            lineterminator="\n",
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "check_name": result.check_name,
                    "total": result.total,
                    "passed": result.passed,
                    "failed": result.failed,
                    "status": result.status,
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--critical-radius", type=Path, default=DEFAULT_PATHS["critical_radius"])
    parser.add_argument(
        "--critical-radius-summary",
        type=Path,
        default=DEFAULT_PATHS["critical_radius_summary"],
    )
    parser.add_argument(
        "--birth-threshold-crossing",
        type=Path,
        default=DEFAULT_PATHS["birth_threshold_crossing"],
    )
    parser.add_argument("--birth-dynamics", type=Path, default=DEFAULT_PATHS["birth_dynamics"])
    parser.add_argument(
        "--birth-dynamics-summary",
        type=Path,
        default=DEFAULT_PATHS["birth_dynamics_summary"],
    )
    parser.add_argument("--hash-manifest", type=Path, default=DEFAULT_PATHS["hash_manifest"])
    parser.add_argument("--out", type=Path, default=DEFAULT_PATHS["out"])
    args = parser.parse_args()

    critical_rows = read_csv(args.critical_radius)
    critical_summary_rows = read_csv(args.critical_radius_summary)
    birth_rows = read_csv(args.birth_dynamics)
    birth_summary_rows = read_csv(args.birth_dynamics_summary)
    crossing_rows = read_csv(args.birth_threshold_crossing)

    results = [
        check_hash_manifest(args.hash_manifest),
        check_critical_radius_zero_residue(critical_rows),
        check_critical_radius_values_recomputed(critical_rows),
        check_c4_level_set(critical_rows),
        check_c5_level_set(critical_rows),
        check_critical_radius_summary(critical_rows, critical_summary_rows),
        check_birth_dynamics_summary(birth_summary_rows),
        check_birth_dynamics_rows(birth_rows),
        check_unique_strict_single_gap_remainders(birth_rows),
        check_threshold_crossing(crossing_rows, birth_rows),
    ]
    write_results(args.out, results)
    failed = sum(result.failed for result in results)
    print(
        f"check_v2_3_candidate_standalone: checks={len(results)}, "
        f"failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
