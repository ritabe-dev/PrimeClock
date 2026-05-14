#!/usr/bin/env python3
"""Audit v2.6 special-point theorem-note decision readiness."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from check_v2_6_special_point_obstruction import repo_root_from_script


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
NOTES_REL = EXPERIMENT_REL / "notes"
NOTE_REL = NOTES_REL / "prc_v2_6_special_point_theorem_note_decision_v0_1.md"
ENDPOINT_DISTANCE_CHECK_REL = (
    EXPERIMENT_REL / "check_v2_6_endpoint_distance_proof_obligation.py"
)
LOCAL_FIRST_CHECK_REL = EXPERIMENT_REL / "check_v2_6_gate_r_local_first_process.py"

REQUIRED_SECTIONS = (
    "## Goal",
    "## Candidate Lemmas",
    "## Endpoint-Distance Bridge",
    "## Promote-Defer Decision",
    "## Proof Gaps",
    "## Non-claims",
)
REQUIRED_PHRASES = (
    "Central Endpoint Obstruction Lemma",
    "promote only as a theorem-note candidate",
    "Forbidden Special Remainder Lemma",
    "defer unless the residual-gap containment bridge is clean",
    "3 mod 6 ancestry",
    "diagnostic only",
    "Decision: defer full theorem-note promotion",
    "decision=defer_full_theorem_note",
    "next=close_residual_gap_bridge",
    "public_theorem=defer",
    "b8_theorem=reject_for_v2_6_gate_r",
    "mod6_theorem=defer",
    "pr_policy=local_first_until_checkpoint",
    "no public theorem claim",
    "no DOI claim",
    "no GitHub Release claim",
    "no B8 theorem",
    "no general predictor claim",
    "no asymptotic law claim",
    "PR #6 remains a draft checkpoint candidate",
)


def require_note(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / NOTE_REL
    if not path.is_file():
        failures.append(f"missing theorem-note decision note: {NOTE_REL}")
        return
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.replace("`", "").split())
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"theorem-note decision missing section {section}")
    for phrase in REQUIRED_PHRASES:
        normalized_phrase = " ".join(phrase.replace("`", "").split())
        if normalized_phrase not in normalized:
            failures.append(f"theorem-note decision missing phrase {phrase!r}")


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

    require_note(repo_root, failures)
    require_checker_passes(repo_root, ENDPOINT_DISTANCE_CHECK_REL, failures)
    require_checker_passes(repo_root, LOCAL_FIRST_CHECK_REL, failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_6_special_point_theorem_note_decision: "
        "checks=7, failed=0, "
        "decision=defer_full_theorem_note, "
        "next=close_residual_gap_bridge"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
