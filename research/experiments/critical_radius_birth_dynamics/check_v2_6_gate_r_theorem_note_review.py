#!/usr/bin/env python3
"""Audit the v2.6 Gate R theorem-note review boundary."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from check_v2_6_special_point_obstruction import repo_root_from_script


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
NOTE_REL = EXPERIMENT_REL / "notes/prc_v2_6_gate_r_theorem_note_review_v0_1.md"
DEPENDENCY_CHECKS = (
    EXPERIMENT_REL / "check_v2_6_single_gap_theorem_note_draft.py",
    EXPERIMENT_REL / "check_v2_6_general_lemma_readiness.py",
)
REQUIRED_SECTIONS = (
    "## Goal",
    "## Keep",
    "## Trim",
    "## Defer",
    "## Gate R Decision",
    "## Non-claims",
)
REQUIRED_PHRASES = (
    "Current readiness is about 85-90%",
    "remaining work is about 0.5 slice",
    "special endpoint spacing near 0 and 1/2",
    "residual components extend to the next old endpoint",
    "special q-clouds are shorter",
    "Residual Component Boundary Lemma",
    "Forbidden Special Remainder Lemma",
    "Central Endpoint Obstruction Lemma",
    "Single-Gap Grid Containment Lemma",
    "Do not promote diagnostic explanations into the proof body",
    "mod 6 ancestry",
    "k=2 multi-gap dilution",
    "capacity false-positive decomposition",
    "B8 feasibility",
    "Close(row) iff strict q-grid containment",
    "all births are single-gap",
    "capacity false positives are all grid misses",
    "mod 6 ancestry theorem",
    "k=2 multi-gap dilution theorem",
    "Capacity as a general separator is rejected",
    "gate_r=local_only",
    "theorem_note_review=continue",
    "source_theorem_note=promote_candidate_after_boundary_tightening",
    "residual_component_boundary_bridge=tighten_next",
    "close_iff_grid_containment_general_theorem=defer",
    "capacity_general_separator=reject",
    "mod6_theorem=defer",
    "public_theorem=defer",
    "root_readme_unchanged=true",
    "no public theorem claim",
    "no DOI claim",
    "no GitHub Release claim",
    "no B8 theorem claim",
    "no general predictor claim",
    "no asymptotic law claim",
)
FORBIDDEN_NOTE_PHRASES = (
    "public_theorem=promote",
    "doi_state=assigned",
    "zenodo_version_doi",
    "b8_theorem=promote",
    "general predictor theorem",
    "asymptotic law theorem",
)
ROOT_README_FORBIDDEN_PHRASES = (
    "Development App",
    "v2.6",
    "Gate R",
    "Gate C",
    "Gate P",
    "next research line",
    "source-only bridge",
    "Version-Line Workflow",
)


def normalized(text: str) -> str:
    return " ".join(text.replace("`", "").split())


def require_note(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / NOTE_REL
    if not path.is_file():
        failures.append(f"missing Gate R theorem-note review: {NOTE_REL}")
        return
    text = path.read_text(encoding="utf-8")
    flat = normalized(text)
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"Gate R theorem-note review missing section {section}")
    for phrase in REQUIRED_PHRASES:
        if normalized(phrase) not in flat:
            failures.append(f"Gate R theorem-note review missing phrase {phrase!r}")
    for phrase in FORBIDDEN_NOTE_PHRASES:
        if normalized(phrase) in flat:
            failures.append(f"Gate R theorem-note review contains forbidden phrase {phrase!r}")


def require_root_readme_external(repo_root: Path, failures: list[str]) -> None:
    text = (repo_root / "README.md").read_text(encoding="utf-8")
    for phrase in ROOT_README_FORBIDDEN_PHRASES:
        if phrase in text:
            failures.append(f"root README contains internal Gate R phrase {phrase!r}")


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
    release_guard = subprocess.run(
        [sys.executable, str(repo_root / "scripts/check_release_doi_integrity.py"), "--all"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if release_guard.returncode != 0:
        failures.append(
            "release DOI integrity guard failed\n"
            f"stdout={release_guard.stdout}\nstderr={release_guard.stderr}"
        )


def main() -> int:
    repo_root = repo_root_from_script()
    failures: list[str] = []

    require_note(repo_root, failures)
    require_root_readme_external(repo_root, failures)
    require_dependency_checks(repo_root, failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_6_gate_r_theorem_note_review: "
        "checks=7, failed=0, "
        "gate_r=local_only, theorem_note_review=continue, public_theorem=defer"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
