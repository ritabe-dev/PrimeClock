#!/usr/bin/env python3
"""Audit v2.6 general lemma readiness boundaries."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from check_v2_6_special_point_obstruction import repo_root_from_script


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
NOTES_REL = EXPERIMENT_REL / "notes"

NOTE_REL = NOTES_REL / "prc_v2_6_general_lemma_readiness_v0_1.md"
DEPENDENCY_CHECKS = (
    EXPERIMENT_REL / "check_v2_6_single_gap_grid_containment_diagnostic.py",
    EXPERIMENT_REL / "check_v2_6_capacity_false_positive_decomposition.py",
)

REQUIRED_SECTIONS = (
    "## Goal",
    "## Lemmas That Can Be General",
    "## Lemmas Still Checked-Scope",
    "## Proof Obligations",
    "## Gate R Decision",
    "## Non-claims",
)
REQUIRED_PHRASES = (
    "Special Endpoint Spacing Lemma",
    "Residual Component Boundary Lemma",
    "Forbidden Special Remainder Lemma",
    "Central Endpoint Obstruction Lemma",
    "Single-Gap Grid Containment Lemma",
    "promote_candidate",
    "Close(row) iff strict q-grid containment",
    "defer",
    "capacity general separator",
    "reject",
    "G subset I_q(a)",
    "qR - 1/2 < a < qL + 1/2",
    "non-wrapping representative or splitting at 0/1",
    "interval width is 1 - q(R-L)",
    "actual integer a",
    "general_lemma_readiness=continue",
    "single_gap_grid_containment_lemma=promote_candidate",
    "close_iff_grid_containment_general_theorem=defer",
    "capacity_general_separator=reject",
    "mod6_theorem=defer",
    "public_theorem=defer",
    "no public theorem claim",
    "no DOI claim",
    "no GitHub Release claim",
    "no B8 theorem claim",
    "no B8 full graph claim",
    "no general predictor claim",
    "no asymptotic law claim",
    "Gate R source-only research",
)


def require_note(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / NOTE_REL
    if not path.is_file():
        failures.append(f"missing general lemma readiness note: {NOTE_REL}")
        return
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.replace("`", "").split())
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"general lemma readiness note missing section {section}")
    for phrase in REQUIRED_PHRASES:
        normalized_phrase = " ".join(phrase.replace("`", "").split())
        if normalized_phrase not in normalized:
            failures.append(f"general lemma readiness note missing phrase {phrase!r}")


def require_dependency_checks(repo_root: Path, failures: list[str]) -> None:
    for relative_path in DEPENDENCY_CHECKS:
        result = subprocess.run(
            [sys.executable, str(repo_root / relative_path)],
            cwd=repo_root / "research",
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failures.append(
                f"dependency check failed: {relative_path}\n"
                f"stdout={result.stdout}\nstderr={result.stderr}"
            )


def main() -> int:
    repo_root = repo_root_from_script()
    failures: list[str] = []

    require_note(repo_root, failures)
    require_dependency_checks(repo_root, failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_6_general_lemma_readiness: "
        "checks=7, failed=0, "
        "general_lemma_readiness=continue, public_theorem=defer"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
