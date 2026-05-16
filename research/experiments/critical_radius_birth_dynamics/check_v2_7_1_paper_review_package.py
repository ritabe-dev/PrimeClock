#!/usr/bin/env python3
"""Check the v2.7.1 paper/reviewer reading bundle boundary."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
PAPER_REL = Path("paper/primeclock_prc_single_gap_aperture_classification.md")
REVIEWER_REL = Path("paper/README_FOR_REVIEWERS.md")
MANIFEST_REL = EXPERIMENT_REL / "paper_review_bundle_manifest_v2_7_1_v1_0.json"
THEOREM_NOTE_REL = (
    EXPERIMENT_REL / "notes/prc_v2_7_general_single_gap_aperture_theorem_note_v0_1.md"
)
FIGURE_RELS = (
    Path("paper/figures/old_arcs_residual_gaps.svg"),
    Path("paper/figures/multigap_obstruction.svg"),
    Path("paper/figures/single_gap_aperture_window.svg"),
)

REQUIRED_PHRASES = (
    "A Single-Gap Aperture Classification in a Prime-Indexed Circle-Arc Covering Model",
    "PRC circular-arc model",
    "direct one-prime q-lift",
    "geometric proof",
    "recorded birth rows consistency audit",
    "not a full finite-universe completeness audit",
    "no prime-gap theorem outside PRC model",
    "not a theorem about classical covering systems",
    "qR - 1/2 < tilde a < qL + 1/2",
)
FORBIDDEN_PHRASES = (
    "proves prime gaps",
    "prime gaps theorem",
    "asymptotic law theorem",
    "general predictor theorem",
    "is a mechanically verified proof",
    "finite audit proves",
    "checker proves the theorem",
)


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def normalized_text(text: str) -> str:
    return " ".join(text.replace("`", "").split())


def read_required(repo_root: Path, relative_path: Path, failures: list[str]) -> str:
    path = repo_root / relative_path
    if not path.is_file():
        failures.append(f"missing paper review file: {relative_path}")
        return ""
    return path.read_text(encoding="utf-8")


def run_script(repo_root: Path, relative_path: Path, failures: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, str(repo_root / relative_path)],
        cwd=repo_root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        failures.append(f"{relative_path} failed")
        if result.stdout:
            failures.append(result.stdout.strip())
        if result.stderr:
            failures.append(result.stderr.strip())


def main() -> int:
    repo_root = repo_root_from_script()
    failures: list[str] = []

    paper = read_required(repo_root, PAPER_REL, failures)
    reviewer = read_required(repo_root, REVIEWER_REL, failures)
    theorem_note = read_required(repo_root, THEOREM_NOTE_REL, failures)
    manifest_text = read_required(repo_root, MANIFEST_REL, failures)
    for figure_rel in FIGURE_RELS:
        figure_text = read_required(repo_root, figure_rel, failures)
        if figure_text and "<svg" not in figure_text:
            failures.append(f"figure is not SVG: {figure_rel}")

    combined = "\n".join([paper, reviewer, theorem_note, manifest_text])
    public_combined = "\n".join([paper, reviewer, theorem_note])
    normalized = normalized_text(combined)
    for phrase in REQUIRED_PHRASES:
        if normalized_text(phrase) not in normalized:
            failures.append(f"paper review materials missing phrase {phrase!r}")
    for phrase in FORBIDDEN_PHRASES:
        if normalized_text(phrase) in normalized_text(public_combined):
            failures.append(f"paper review materials contain forbidden phrase {phrase!r}")

    if manifest_text:
        manifest = json.loads(manifest_text)
        if manifest.get("id") != "prc_v2_7_1_paper_review_bundle_v1_0":
            failures.append("paper review manifest id mismatch")
        if manifest.get("default_name") != "PrimeClock-v2.7.1-paper-review-v1.0":
            failures.append("paper review manifest default_name mismatch")
        for required in (
            PAPER_REL.as_posix(),
            REVIEWER_REL.as_posix(),
            "research/experiments/critical_radius_birth_dynamics/check_v2_7_strict_single_gap_aperture_exact_audit.py",
            "research/experiments/critical_radius_birth_dynamics/data/prc_prime_prefix_birth_dynamics_k5_k7_v0_1.csv",
        ):
            if required not in manifest.get("research_files", []):
                failures.append(f"paper review manifest missing research file {required}")

    run_script(repo_root, EXPERIMENT_REL / "check_v2_7_general_single_gap_aperture_theorem_note.py", failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_7_1_paper_review_package: "
        "checks=7, failed=0, "
        "paper=present, reviewer_readme=present, figures=3, "
        "proof_vs_audit=separated, overclaim_hygiene=passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
