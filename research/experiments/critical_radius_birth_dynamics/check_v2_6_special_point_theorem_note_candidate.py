#!/usr/bin/env python3
"""Audit v2.6 special-point theorem-note candidate readiness."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from check_v2_6_special_point_obstruction import repo_root_from_script


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
NOTES_REL = EXPERIMENT_REL / "notes"
NOTE_REL = NOTES_REL / "prc_v2_6_special_point_theorem_note_candidate_v0_1.md"
BRIDGE_NOTE_REL = NOTES_REL / "prc_v2_6_residual_component_boundary_bridge_v0_1.md"
ENDPOINT_DISTANCE_CHECK_REL = (
    EXPERIMENT_REL / "check_v2_6_endpoint_distance_proof_obligation.py"
)
THEOREM_NOTE_DECISION_CHECK_REL = (
    EXPERIMENT_REL / "check_v2_6_special_point_theorem_note_decision.py"
)
LOCAL_FIRST_CHECK_REL = EXPERIMENT_REL / "check_v2_6_gate_r_local_first_process.py"

REQUIRED_SECTIONS = (
    "## Definitions",
    "## Special Endpoint Spacing Lemma",
    "## Residual Component Boundary Lemma",
    "## Forbidden Special Remainder Lemma",
    "## Central Endpoint Obstruction Lemma",
    "## Remaining Risks",
    "## Non-claims",
)
REQUIRED_PHRASES = (
    "source-only theorem-note candidate",
    "old endpoints are the union",
    "Composite placement does not generate new endpoints",
    "1/(2p_k)",
    "1/p_k",
    "residual component adjacent to that side extends until the nearest old endpoint",
    "covered-special-side case is handled separately",
    "no old residual component based at that covered special point to close",
    "topological boundary statement",
    "a=0",
    "a=(q-1)/2",
    "a=(q+1)/2",
    "endpoint-touch birth cannot occur",
    "source_theorem_note=promote_candidate",
    "public_theorem=defer",
    "b8_theorem=reject_for_v2_6_gate_r",
    "mod6_theorem=defer",
    "pr_policy=local_first_until_checkpoint",
    "no public release claim",
    "no DOI claim",
    "no GitHub Release claim",
    "no B8 theorem",
    "no general predictor claim",
    "no asymptotic law claim",
)
BRIDGE_REQUIRED_SECTIONS = (
    "## Goal",
    "## Setup",
    "## Covered Special Side",
    "## Uncovered Special Side",
    "## Gate R Decision",
    "## Non-claims",
)
BRIDGE_REQUIRED_PHRASES = (
    "residual_component_boundary_bridge=proof_candidate",
    "covered_special_side=proof_candidate",
    "uncovered_special_side=proof_candidate",
    "public_theorem=defer",
    "no public theorem claim",
    "no DOI claim",
    "no GitHub Release claim",
    "no B8 theorem claim",
    "no general predictor claim",
    "no asymptotic law claim",
)


def require_note(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / NOTE_REL
    if not path.is_file():
        failures.append(f"missing theorem-note candidate note: {NOTE_REL}")
        return
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.replace("`", "").split())
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"theorem-note candidate missing section {section}")
    for phrase in REQUIRED_PHRASES:
        normalized_phrase = " ".join(phrase.replace("`", "").split())
        if normalized_phrase not in normalized:
            failures.append(f"theorem-note candidate missing phrase {phrase!r}")


def require_bridge_note(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / BRIDGE_NOTE_REL
    if not path.is_file():
        failures.append(f"missing residual component boundary bridge note: {BRIDGE_NOTE_REL}")
        return
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.replace("`", "").split())
    for section in BRIDGE_REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"residual component bridge note missing section {section}")
    for phrase in BRIDGE_REQUIRED_PHRASES:
        normalized_phrase = " ".join(phrase.replace("`", "").split())
        if normalized_phrase not in normalized:
            failures.append(f"residual component bridge note missing phrase {phrase!r}")


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
    require_bridge_note(repo_root, failures)
    require_checker_passes(repo_root, ENDPOINT_DISTANCE_CHECK_REL, failures)
    require_checker_passes(repo_root, THEOREM_NOTE_DECISION_CHECK_REL, failures)
    require_checker_passes(repo_root, LOCAL_FIRST_CHECK_REL, failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_6_special_point_theorem_note_candidate: "
        "checks=8, failed=0, "
        "source_theorem_note=promote_candidate, "
        "public_theorem=defer"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
