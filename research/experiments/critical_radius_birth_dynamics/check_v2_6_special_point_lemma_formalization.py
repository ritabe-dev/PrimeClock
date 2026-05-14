#!/usr/bin/env python3
"""Audit v2.6 special-point lemma formalization readiness."""

from __future__ import annotations

import csv
from pathlib import Path

from check_v2_6_special_point_obstruction import (
    ENDPOINT_SUMMARY_REL,
    MOD6_SUMMARY_REL,
    SPECIAL_SUMMARY_REL,
    build_endpoint_summary,
    build_mod6_summary,
    build_special_summary,
    read_csv,
    repo_root_from_script,
)


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
DATA_REL = EXPERIMENT_REL / "data"
NOTES_REL = EXPERIMENT_REL / "notes"

PHASE_REL = DATA_REL / "prc_v2_4_phase_gate_lift_diagnostics_v0_1.csv"
BIRTH_REL = DATA_REL / "prc_prime_prefix_birth_dynamics_k5_k7_v0_1.csv"
FORMAL_NOTE_REL = NOTES_REL / "prc_v2_6_special_point_lemma_draft_v0_1.md"

REQUIRED_NOTE_SECTIONS = (
    "## Definitions",
    "## Endpoint Lattice Facts",
    "## Forbidden Special Remainder Proof Candidate",
    "## Central Endpoint Obstruction Proof Candidate",
    "## Proof Obligations",
    "## Finite Audit Evidence",
    "## Non-claims",
)

REQUIRED_NOTE_PHRASES = (
    "q=p_{k+1}",
    "old prefix contains 2,3,...,p_k",
    "0/1 is the same circular point",
    "proof candidate",
    "not a public theorem",
    "not a general predictor",
    "not an asymptotic law",
    "3 mod 6 ancestry diagnostic",
)


def read_committed_csv(repo_root: Path, relative_path: Path) -> list[dict[str, str]]:
    path = repo_root / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"missing committed summary artifact: {relative_path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require_formal_note(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / FORMAL_NOTE_REL
    if not path.is_file():
        failures.append(f"missing v2.6 formal lemma note: {FORMAL_NOTE_REL}")
        return
    text = path.read_text(encoding="utf-8")
    normalized_text = " ".join(text.replace("`", "").split())
    for section in REQUIRED_NOTE_SECTIONS:
        if section not in text:
            failures.append(f"formal lemma note missing section {section}")
    for phrase in REQUIRED_NOTE_PHRASES:
        normalized_phrase = " ".join(phrase.split())
        if normalized_phrase not in normalized_text:
            failures.append(f"formal lemma note missing phrase {phrase!r}")


def require_committed_summaries_match(
    repo_root: Path,
    phase_rows: list[dict[str, str]],
    birth_rows: list[dict[str, str]],
    failures: list[str],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    regenerated_special = build_special_summary(phase_rows)
    regenerated_endpoint = build_endpoint_summary(phase_rows, birth_rows)
    regenerated_mod6 = build_mod6_summary(phase_rows)
    for relative_path, regenerated in (
        (SPECIAL_SUMMARY_REL, regenerated_special),
        (ENDPOINT_SUMMARY_REL, regenerated_endpoint),
        (MOD6_SUMMARY_REL, regenerated_mod6),
    ):
        committed = read_committed_csv(repo_root, relative_path)
        if committed != regenerated:
            failures.append(f"committed summary differs from regenerated summary: {relative_path}")
    return regenerated_special, regenerated_endpoint, regenerated_mod6


def require_special_remainders(
    special_rows: list[dict[str, str]], failures: list[str]
) -> None:
    for row in special_rows:
        for key in ("positive_margin_rows", "close_rows", "birth_rows"):
            if row[key] != "0":
                failures.append(f"special remainder {key} is nonzero: {row}")


def require_endpoint_obstruction(
    endpoint_rows: list[dict[str, str]], failures: list[str]
) -> None:
    total_births = 0
    total_strict_single_gap = 0
    for row in endpoint_rows:
        total_births += int(row["birth_rows"])
        total_strict_single_gap += int(row["strict_single_gap_birth_rows"])
        for key in (
            "phase_endpoint_touch_rows",
            "phase_endpoint_touch_birth_rows",
            "endpoint_single_gap_birth_rows",
            "endpoint_multi_gap_birth_rows",
            "uses_endpoint_touching_rows",
        ):
            if row[key] != "0":
                failures.append(f"endpoint obstruction {key} is nonzero: {row}")
        if row["birth_rows"] != row["strict_single_gap_birth_rows"]:
            failures.append(f"not all birth rows are strict single-gap rows: {row}")
    if total_births != 770 or total_strict_single_gap != 770:
        failures.append(
            "expected 770 strict single-gap birth rows; "
            f"got births={total_births}, strict_single_gap={total_strict_single_gap}"
        )


def require_mod6_diagnostic_only(
    mod6_rows: list[dict[str, str]], failures: list[str]
) -> None:
    if len(mod6_rows) != 3:
        failures.append(f"expected 3 mod6 diagnostic rows; got {len(mod6_rows)}")
    if any("theorem" in row["decision"].lower() for row in mod6_rows):
        failures.append("mod6 decision must remain diagnostic and theorem-free")


def main() -> int:
    repo_root = repo_root_from_script()
    failures: list[str] = []
    phase_rows = read_csv(repo_root, PHASE_REL)
    birth_rows = read_csv(repo_root, BIRTH_REL)

    require_formal_note(repo_root, failures)
    special_rows, endpoint_rows, mod6_rows = require_committed_summaries_match(
        repo_root, phase_rows, birth_rows, failures
    )
    require_special_remainders(special_rows, failures)
    require_endpoint_obstruction(endpoint_rows, failures)
    require_mod6_diagnostic_only(mod6_rows, failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_6_special_point_lemma_formalization: "
        "checks=8, failed=0, "
        "route=formalize_special_point_lemmas, "
        "proof_status=candidate, mod6_theorem=defer"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
