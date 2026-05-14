#!/usr/bin/env python3
"""Audit v2.6 special-point Gate R review readiness."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

from check_v2_6_special_point_obstruction import repo_root_from_script


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
DATA_REL = EXPERIMENT_REL / "data"
NOTES_REL = EXPERIMENT_REL / "notes"

REVIEW_NOTE_REL = NOTES_REL / "prc_v2_6_special_point_gate_r_review_v0_1.md"
REVIEW_TABLE_REL = DATA_REL / "prc_v2_6_special_point_gate_r_review_table_v0_1.csv"
OBSTRUCTION_CHECK_REL = EXPERIMENT_REL / "check_v2_6_special_point_obstruction.py"
FORMALIZATION_CHECK_REL = EXPERIMENT_REL / "check_v2_6_special_point_lemma_formalization.py"

ALLOWED_STATUSES = {"ready", "continue", "defer", "blocked"}
REQUIRED_SECTIONS = (
    "## Goal",
    "## Lemma Candidates",
    "## Proof Obligations",
    "## Finite Audit Support",
    "## Gaps",
    "## Gate R Decision",
    "## Non-claims",
)
REQUIRED_PHRASES = (
    "Central Endpoint Obstruction Lemma",
    "Forbidden Special Remainder Lemma",
    "nearest old endpoint lower bounds",
    "finite audit tables",
    "public_theorem=defer",
    "mod6_theorem=defer",
    "b8_theorem=reject_for_v2_6_gate_r",
    "no public claim",
    "no DOI",
    "no B8 theorem",
    "no general predictor",
    "no asymptotic law",
)
REQUIRED_DECISIONS = {
    "forbidden_special_remainder": ("continue", "proof_candidate"),
    "central_endpoint_obstruction": ("continue", "proof_candidate"),
    "public_theorem": ("defer", "public_theorem_defer"),
    "mod6_theorem": ("defer", "mod6_theorem_defer"),
    "b8_theorem": ("blocked", "b8_theorem=reject_for_v2_6_gate_r"),
}


def read_text(repo_root: Path, relative_path: Path) -> str:
    path = repo_root / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"missing Gate R review artifact: {relative_path}")
    return path.read_text(encoding="utf-8")


def read_table(repo_root: Path) -> list[dict[str, str]]:
    path = repo_root / REVIEW_TABLE_REL
    if not path.is_file():
        raise FileNotFoundError(f"missing Gate R review table: {REVIEW_TABLE_REL}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require_review_note(repo_root: Path, failures: list[str]) -> None:
    text = read_text(repo_root, REVIEW_NOTE_REL)
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"review note missing section {section}")
    lowered = text.lower()
    for phrase in REQUIRED_PHRASES:
        if phrase.lower() not in lowered:
            failures.append(f"review note missing phrase {phrase!r}")


def require_review_table(repo_root: Path, failures: list[str]) -> None:
    rows = read_table(repo_root)
    by_item = {row["item"]: row for row in rows}
    if not rows:
        failures.append("review table is empty")
        return
    for row in rows:
        if row["status"] not in ALLOWED_STATUSES:
            failures.append(f"invalid review table status: {row}")
    for item, (status, decision) in REQUIRED_DECISIONS.items():
        row = by_item.get(item)
        if not row:
            failures.append(f"review table missing required item: {item}")
            continue
        if row["status"] != status:
            failures.append(f"review table item {item} has wrong status: {row}")
        if row["decision"] != decision:
            failures.append(f"review table item {item} has wrong decision: {row}")


def require_checker_passes(repo_root: Path, relative_path: Path, failures: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, str(repo_root / relative_path)],
        cwd=repo_root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        failures.append(f"required checker failed: {relative_path}: {output}")


def main() -> int:
    repo_root = repo_root_from_script()
    failures: list[str] = []

    require_review_note(repo_root, failures)
    require_review_table(repo_root, failures)
    require_checker_passes(repo_root, OBSTRUCTION_CHECK_REL, failures)
    require_checker_passes(repo_root, FORMALIZATION_CHECK_REL, failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_6_special_point_gate_r_review: "
        "checks=7, failed=0, "
        "gate_r=continue_special_point_obstruction, "
        "public_theorem=defer, mod6_theorem=defer, "
        "b8_theorem=reject_for_v2_6_gate_r"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
