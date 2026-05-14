#!/usr/bin/env python3
"""Audit v2.6 special-point obstruction Gate R evidence."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
DATA_REL = EXPERIMENT_REL / "data"
NOTES_REL = EXPERIMENT_REL / "notes"

PHASE_REL = DATA_REL / "prc_v2_4_phase_gate_lift_diagnostics_v0_1.csv"
BIRTH_REL = DATA_REL / "prc_prime_prefix_birth_dynamics_k5_k7_v0_1.csv"
SPECIAL_SUMMARY_REL = DATA_REL / "prc_v2_6_special_remainder_audit_v0_1.csv"
ENDPOINT_SUMMARY_REL = DATA_REL / "prc_v2_6_endpoint_obstruction_audit_v0_1.csv"
MOD6_SUMMARY_REL = DATA_REL / "prc_v2_6_mod6_ancestry_summary_v0_1.csv"
NOTE_REL = NOTES_REL / "prc_v2_6_special_point_obstruction_gate_r_v0_1.md"

SCOPE_FOR_K = {
    "5": "B4_to_B5_full",
    "6": "B5_to_B6_full",
    "7": "B6_to_B7_full",
}
SCOPE_ORDER = ("B4_to_B5_full", "B5_to_B6_full", "B6_to_B7_full")
SPECIAL_CLASSES = ("zero", "central_left", "central_right")
REQUIRED_NOTE_SECTIONS = (
    "## Definitions",
    "## Endpoint Lattice Facts",
    "## Forbidden Special Remainder Lemma",
    "## Central Endpoint Obstruction Lemma",
    "## Relation To 3 Mod 6 Ancestry",
    "## Non-claims",
    "## Gate R Decision",
)
REQUIRED_NOTE_PHRASES = (
    "nearest old endpoint distance is at least 1/(2p_k)",
    "nearest old endpoint other than 1/2 is at least 1/p_k",
    "0/1 is a cut representation",
    "not a public theorem",
    "not a general predictor",
    "mod 6 ancestry diagnostic",
)


def repo_root_from_script() -> Path:
    path = Path(__file__).resolve()
    for parent in path.parents:
        if (parent / "release/public/release_registry.json").is_file():
            return parent
    raise RuntimeError("could not locate PrimeClock repository root")


def read_csv(repo_root: Path, relative_path: Path) -> list[dict[str, str]]:
    path = repo_root / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"missing required artifact: {relative_path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(repo_root: Path, relative_path: Path, rows: list[dict[str, str]]) -> Path:
    path = repo_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"no rows generated for {relative_path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def compare_or_seed_csv(
    repo_root: Path,
    relative_path: Path,
    rows: list[dict[str, str]],
    failures: list[str],
) -> Path:
    path = repo_root / relative_path
    if path.is_file():
        with path.open("r", encoding="utf-8", newline="") as handle:
            committed = list(csv.DictReader(handle))
        if committed != rows:
            failures.append(f"committed summary differs from regenerated summary: {relative_path}")
    return write_csv(repo_root, relative_path, rows)


def special_remainders(q: int) -> dict[str, int]:
    return {
        "zero": 0,
        "central_left": (q - 1) // 2,
        "central_right": (q + 1) // 2,
    }


def truth(value: str) -> bool:
    return value == "True"


def positive_fraction(value: str) -> bool:
    return Fraction(value) > 0


def build_special_summary(phase_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    counters: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    q_by_scope: dict[str, int] = {}
    remainder_by_key: dict[tuple[str, str], int] = {}
    for row in phase_rows:
        scope = row["scope"]
        q = int(row["new_prime"])
        q_by_scope[scope] = q
        special = special_remainders(q)
        remainder = int(row["new_prime_remainder"])
        for class_name, special_remainder in special.items():
            if remainder != special_remainder:
                continue
            key = (scope, class_name)
            remainder_by_key[key] = special_remainder
            counters[key]["lift_rows"] += 1
            counters[key]["capacity_pass_rows"] += int(truth(row["capacity_pass"]))
            counters[key]["phase_pass_rows"] += int(truth(row["phase_pass"]))
            counters[key]["positive_margin_rows"] += int(positive_fraction(row["phase_margin"]))
            counters[key]["close_rows"] += int(truth(row["is_close"]))
            counters[key]["birth_rows"] += int(truth(row["is_birth"]))
            counters[key]["endpoint_touch_rows"] += int(truth(row["endpoint_touch"]))

    rows: list[dict[str, str]] = []
    for scope in SCOPE_ORDER:
        q = q_by_scope[scope]
        for class_name in SPECIAL_CLASSES:
            key = (scope, class_name)
            counter = counters[key]
            rows.append(
                {
                    "scope": scope,
                    "new_prime": str(q),
                    "remainder_class": class_name,
                    "remainder": str(remainder_by_key[key]),
                    "lift_rows": str(counter["lift_rows"]),
                    "capacity_pass_rows": str(counter["capacity_pass_rows"]),
                    "phase_pass_rows": str(counter["phase_pass_rows"]),
                    "positive_margin_rows": str(counter["positive_margin_rows"]),
                    "close_rows": str(counter["close_rows"]),
                    "birth_rows": str(counter["birth_rows"]),
                    "endpoint_touch_rows": str(counter["endpoint_touch_rows"]),
                    "decision": "finite_supports_general_lemma_candidate",
                }
            )
    return rows


def build_endpoint_summary(
    phase_rows: list[dict[str, str]],
    birth_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    phase: dict[str, Counter[str]] = defaultdict(Counter)
    for row in phase_rows:
        scope = row["scope"]
        phase[scope]["lift_rows"] += 1
        phase[scope]["endpoint_touch_rows"] += int(truth(row["endpoint_touch"]))
        phase[scope]["endpoint_touch_close_rows"] += int(
            truth(row["endpoint_touch"]) and truth(row["is_close"])
        )
        phase[scope]["endpoint_touch_birth_rows"] += int(
            truth(row["endpoint_touch"]) and truth(row["is_birth"])
        )
        phase[scope]["close_rows"] += int(truth(row["is_close"]))
        phase[scope]["birth_rows"] += int(truth(row["is_birth"]))

    birth: dict[str, Counter[str]] = defaultdict(Counter)
    for row in birth_rows:
        scope = SCOPE_FOR_K[row["k"]]
        birth[scope]["birth_dynamics_rows"] += 1
        birth[scope][row["birth_type"]] += 1
        birth[scope]["uses_endpoint_touching_rows"] += int(truth(row["uses_endpoint_touching"]))
        birth[scope]["single_gap_birth_rows"] += int(row["previous_open_gap_count"] == "1")

    rows: list[dict[str, str]] = []
    for scope in SCOPE_ORDER:
        phase_counter = phase[scope]
        birth_counter = birth[scope]
        rows.append(
            {
                "scope": scope,
                "checked_lift_rows": str(phase_counter["lift_rows"]),
                "phase_endpoint_touch_rows": str(phase_counter["endpoint_touch_rows"]),
                "phase_endpoint_touch_close_rows": str(
                    phase_counter["endpoint_touch_close_rows"]
                ),
                "phase_endpoint_touch_birth_rows": str(
                    phase_counter["endpoint_touch_birth_rows"]
                ),
                "close_rows": str(phase_counter["close_rows"]),
                "birth_rows": str(phase_counter["birth_rows"]),
                "birth_dynamics_rows": str(birth_counter["birth_dynamics_rows"]),
                "strict_single_gap_birth_rows": str(
                    birth_counter["strict_single_gap_birth"]
                ),
                "endpoint_single_gap_birth_rows": str(
                    birth_counter["endpoint_single_gap_birth"]
                ),
                "strict_multi_gap_birth_rows": str(birth_counter["strict_multi_gap_birth"]),
                "endpoint_multi_gap_birth_rows": str(
                    birth_counter["endpoint_multi_gap_birth"]
                ),
                "uses_endpoint_touching_rows": str(
                    birth_counter["uses_endpoint_touching_rows"]
                ),
                "single_gap_birth_rows": str(birth_counter["single_gap_birth_rows"]),
                "decision": "finite_supports_central_endpoint_obstruction_candidate",
            }
        )
    return rows


def fraction_text(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0/0"
    return f"{numerator}/{denominator}"


def decimal_text(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0.000000"
    return f"{numerator / denominator:.6f}"


def build_mod6_summary(phase_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    family_mod6: dict[str, Counter[int]] = defaultdict(Counter)
    family_seen: set[tuple[str, int]] = set()
    close_mod6: dict[str, Counter[int]] = defaultdict(Counter)
    close_rows_by_scope: Counter[str] = Counter()

    for row in phase_rows:
        scope = row["scope"]
        parent = int(row["parent_residue"])
        family_key = (scope, parent)
        if family_key not in family_seen:
            family_seen.add(family_key)
            family_mod6[scope][parent % 6] += 1
        if truth(row["is_close"]):
            close_mod6[scope][parent % 6] += 1
            close_rows_by_scope[scope] += 1

    rows: list[dict[str, str]] = []
    for scope in SCOPE_ORDER:
        total_families = sum(family_mod6[scope].values())
        base_mod6_3 = family_mod6[scope][3]
        close_rows = close_rows_by_scope[scope]
        close_mod6_3 = close_mod6[scope][3]
        close_rate = Fraction(close_mod6_3, close_rows) if close_rows else Fraction(0)
        base_rate = Fraction(base_mod6_3, total_families) if total_families else Fraction(0)
        if close_rate > base_rate * 2:
            decision = "mod6_3_enriched_birth_ancestry_signal"
        else:
            decision = "weak_or_non_supportive_mod6_3_signal"
        rows.append(
            {
                "scope": scope,
                "total_parent_families": str(total_families),
                "base_mod6_3_count": str(base_mod6_3),
                "base_mod6_3_rate": fraction_text(base_mod6_3, total_families),
                "base_mod6_3_rate_decimal": decimal_text(base_mod6_3, total_families),
                "close_rows": str(close_rows),
                "close_mod6_3_count": str(close_mod6_3),
                "close_mod6_3_rate": fraction_text(close_mod6_3, close_rows),
                "close_mod6_3_rate_decimal": decimal_text(close_mod6_3, close_rows),
                "close_mod6_counts": " ".join(
                    f"{key}:{close_mod6[scope][key]}" for key in sorted(close_mod6[scope])
                ),
                "decision": decision,
            }
        )
    return rows


def require_note(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / NOTE_REL
    if not path.is_file():
        failures.append(f"missing special point obstruction note: {NOTE_REL}")
        return
    text = path.read_text(encoding="utf-8")
    for section in REQUIRED_NOTE_SECTIONS:
        if section not in text:
            failures.append(f"special point obstruction note missing section {section}")
    for phrase in REQUIRED_NOTE_PHRASES:
        if phrase not in text:
            failures.append(f"special point obstruction note missing phrase {phrase!r}")


def require_special_summary(rows: list[dict[str, str]], failures: list[str]) -> None:
    for row in rows:
        if row["phase_pass_rows"] != "0":
            failures.append(f"special remainder phase pass rows nonzero: {row}")
        if row["positive_margin_rows"] != "0":
            failures.append(f"special remainder positive margin rows nonzero: {row}")
        if row["close_rows"] != "0" or row["birth_rows"] != "0":
            failures.append(f"special remainder close/birth rows nonzero: {row}")


def require_endpoint_summary(rows: list[dict[str, str]], failures: list[str]) -> None:
    total_births = 0
    total_strict_single_gap = 0
    for row in rows:
        total_births += int(row["birth_rows"])
        total_strict_single_gap += int(row["strict_single_gap_birth_rows"])
        for key in (
            "phase_endpoint_touch_rows",
            "phase_endpoint_touch_close_rows",
            "phase_endpoint_touch_birth_rows",
            "endpoint_single_gap_birth_rows",
            "strict_multi_gap_birth_rows",
            "endpoint_multi_gap_birth_rows",
            "uses_endpoint_touching_rows",
        ):
            if row[key] != "0":
                failures.append(f"endpoint obstruction key {key} is nonzero: {row}")
        if row["birth_rows"] != row["birth_dynamics_rows"]:
            failures.append(f"phase and birth dynamics birth row counts differ: {row}")
        if row["birth_rows"] != row["strict_single_gap_birth_rows"]:
            failures.append(f"birth rows are not all strict single-gap rows: {row}")
    if total_births != 770 or total_strict_single_gap != 770:
        failures.append(
            f"expected 770 strict single-gap births; got births={total_births}, "
            f"strict_single_gap={total_strict_single_gap}"
        )


def require_mod6_summary(rows: list[dict[str, str]], failures: list[str]) -> None:
    by_scope = {row["scope"]: row for row in rows}
    if by_scope["B4_to_B5_full"]["decision"] != "weak_or_non_supportive_mod6_3_signal":
        failures.append("B4->B5 must remain recorded as weak/non-supportive for mod6=3")
    for scope in ("B5_to_B6_full", "B6_to_B7_full"):
        if by_scope[scope]["decision"] != "mod6_3_enriched_birth_ancestry_signal":
            failures.append(f"{scope} must remain recorded as mod6=3 enriched")


def main() -> int:
    repo_root = repo_root_from_script()
    failures: list[str] = []
    phase_rows = read_csv(repo_root, PHASE_REL)
    birth_rows = read_csv(repo_root, BIRTH_REL)

    require_note(repo_root, failures)
    special_rows = build_special_summary(phase_rows)
    endpoint_rows = build_endpoint_summary(phase_rows, birth_rows)
    mod6_rows = build_mod6_summary(phase_rows)

    require_special_summary(special_rows, failures)
    require_endpoint_summary(endpoint_rows, failures)
    require_mod6_summary(mod6_rows, failures)

    out_paths = [
        compare_or_seed_csv(repo_root, SPECIAL_SUMMARY_REL, special_rows, failures),
        compare_or_seed_csv(repo_root, ENDPOINT_SUMMARY_REL, endpoint_rows, failures),
        compare_or_seed_csv(repo_root, MOD6_SUMMARY_REL, mod6_rows, failures),
    ]

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_6_special_point_obstruction: "
        "checks=10, failed=0, "
        "route=continue_special_point_obstruction, mod6_theorem=defer, "
        "out="
        + ",".join(path.as_posix() for path in out_paths)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
