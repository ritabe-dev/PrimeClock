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
    failures = 0
    total = 0
    manifest_root = manifest_path.parent.parent
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        total += 1
        try:
            expected, relative_path = line.split("  ", 1)
        except ValueError:
            failures += 1
            continue
        target = manifest_root / relative_path
        if not target.is_file() or sha256_bytes(target) != expected:
            failures += 1
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
        check_c4_level_set(critical_rows),
        check_c5_level_set(critical_rows),
        check_critical_radius_summary(critical_rows, critical_summary_rows),
        check_birth_dynamics_summary(birth_summary_rows),
        check_birth_dynamics_rows(birth_rows),
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
