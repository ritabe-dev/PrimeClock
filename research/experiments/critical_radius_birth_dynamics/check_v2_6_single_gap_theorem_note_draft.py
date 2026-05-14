#!/usr/bin/env python3
"""Audit the v2.6 single-gap theorem-note draft boundary."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from check_v2_6_special_point_obstruction import repo_root_from_script


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
NOTES_REL = EXPERIMENT_REL / "notes"

NOTE_REL = NOTES_REL / "prc_v2_6_single_gap_theorem_note_draft_v0_1.md"
DEPENDENCY_CHECKS = (
    EXPERIMENT_REL / "check_v2_6_general_lemma_readiness.py",
    EXPERIMENT_REL / "check_v2_6_special_point_theorem_note_candidate.py",
    EXPERIMENT_REL / "check_v2_6_single_gap_grid_containment_diagnostic.py",
    EXPERIMENT_REL / "check_v2_6_capacity_false_positive_decomposition.py",
)

REQUIRED_SECTIONS = (
    "## Goal",
    "## Setup",
    "## Lemma 1: Special Endpoint Spacing",
    "## Lemma 2: Residual Component Boundary",
    "## Lemma 3: Forbidden Special Remainders",
    "## Lemma 4: Central Endpoint Obstruction",
    "## Lemma 5: Single-Gap Grid Containment",
    "## Checked Support",
    "## Gate R Boundary",
    "## Non-claims",
)
REQUIRED_PHRASES = (
    "Current readiness is about 85-90%",
    "remaining work is about 0.5 slice",
    "dist(0, nearest old endpoint) >= 1/(2p_k)",
    "dist(1/2, nearest old endpoint other than 1/2) >= 1/p_k",
    "composite placement does not create new endpoints",
    "covered/uncovered state cannot change",
    "0, (q-1)/2, (q+1)/2",
    "1/(2q) < 1/(2p_k)",
    "1/q < 1/p_k",
    "endpoint-touch birth is obstructed",
    "G subset I_q(a)",
    "qR - 1/2 < a < qL + 1/2",
    "width 1 - q(R-L)",
    "capacity is only the size condition",
    "actual integer remainder a",
    "in checked scopes, Close(row) => parent residual set is single-gap",
    "strict q-grid containment matches close rows",
    "capacity false positives are q-grid misses",
    "endpoint-touch rows are zero",
    "source_theorem_note=promote_candidate",
    "single_gap_grid_containment_lemma=promote_candidate",
    "close_iff_grid_containment_general_theorem=defer",
    "all_births_single_gap_general_theorem=defer",
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
FORBIDDEN_PHRASES = (
    "public_theorem=promote",
    "doi_state=assigned",
    "github_release_url",
    "zenodo_version_doi",
    "b8_theorem=promote",
    "b8 full graph theorem",
    "general predictor theorem",
    "asymptotic law theorem",
)


def require_note(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / NOTE_REL
    if not path.is_file():
        failures.append(f"missing single-gap theorem-note draft: {NOTE_REL}")
        return
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.replace("`", "").split())
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"single-gap theorem-note draft missing section {section}")
    for phrase in REQUIRED_PHRASES:
        normalized_phrase = " ".join(phrase.replace("`", "").split())
        if normalized_phrase not in normalized:
            failures.append(f"single-gap theorem-note draft missing phrase {phrase!r}")
    for phrase in FORBIDDEN_PHRASES:
        normalized_phrase = " ".join(phrase.replace("`", "").split())
        if normalized_phrase in normalized:
            failures.append(f"single-gap theorem-note draft contains forbidden phrase {phrase!r}")
    for line_number, line in enumerate(text.splitlines(), start=1):
        normalized_line = " ".join(line.replace("`", "").split())
        if (
            "Close(row) iff strict q-grid containment" in normalized_line
            and "defer" not in normalized_line
        ):
            failures.append(
                "single-gap theorem-note draft contains undeferred global iff "
                f"language on line {line_number}"
            )


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
        "check_v2_6_single_gap_theorem_note_draft: "
        "checks=8, failed=0, "
        "theorem_note_draft=continue, public_theorem=defer"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
