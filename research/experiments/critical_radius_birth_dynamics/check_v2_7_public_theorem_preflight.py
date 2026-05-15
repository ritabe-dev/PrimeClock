#!/usr/bin/env python3
"""Check the v2.7 Gate P public theorem preflight boundary."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
PUBLIC_README_REL = (
    EXPERIMENT_REL / "notes/prc_v2_7_public_theorem_readme_v1_0.md"
)
PUBLIC_RELEASE_NOTES_REL = (
    EXPERIMENT_REL / "notes/prc_v2_7_public_theorem_release_notes_v1_0.md"
)
PUBLIC_CITATION_REL = (
    EXPERIMENT_REL / "notes/prc_v2_7_public_theorem_citation_v1_0.cff"
)
PUBLIC_MANIFEST_REL = EXPERIMENT_REL / "public_theorem_preflight_manifest_v2_7_v1_0.json"
PUBLIC_WORKFLOW_REL = EXPERIMENT_REL / "public_theorem_release_workflow_v2_7_v1_0.yml"
PUBLIC_BUNDLE_WORKFLOW_REL = (
    EXPERIMENT_REL / "public_theorem_preflight_bundle_workflow_v2_7_v1_0.yml"
)
PUBLIC_RELEASE_MANIFEST_REL = EXPERIMENT_REL / "public_theorem_release_manifest_v2_7_v1_0.json"
REGISTRY_REL = Path("release/public/release_registry.json")
RELEASE_ID = "v2.7.0-prc-general-q-prime-theorem"
ASSET_NAME = "PrimeClock-v2.7-general-q-prime-theorem-v1.0.zip"

REQUIRED_PUBLIC_TEXT = (
    "PRC v2.7: General q-Prime Single-Gap Aperture Classification Theorem",
    "direct one-prime q-lift",
    "recorded birth rows consistency audit",
    "committed recorded birth rows in the finite next-prime support CSV",
    "not a full finite-universe completeness audit",
    "bundle-local workflow",
    "DOI and registry integrity checks are full-repository preflight checks only",
    "no B8 theorem",
    "no full transition-graph theorem",
    "no general predictor",
    "no asymptotic law",
    "no prime-gap theorem outside PRC model",
    "DRAFT_CITATION.cff",
)
REQUIRED_NON_CLAIMS = (
    "no B8 theorem",
    "no full transition-graph theorem",
    "no general predictor",
    "no asymptotic law",
    "no prime-gap theorem outside PRC model",
    "not a full finite-universe completeness audit",
)
FORBIDDEN_PUBLIC_TEXT = (
    "Version DOI: `10.5281/zenodo.",
    "Version DOI: 10.5281/zenodo.",
    "doi: \"10.5281/zenodo.",
    "https://github.com/ritabe-dev/PrimeClock/releases/tag/v2.7.0-prc-general-q-prime-theorem",
    "B8 theorem proven",
    "general predictor theorem",
    "asymptotic law theorem",
)
DOI_RE = re.compile(r"10\.5281/zenodo\.\d+")


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def is_public_preflight_bundle_root(repo_root: Path) -> bool:
    return (
        (repo_root / "BUNDLE_FILE_MANIFEST.txt").is_file()
        and (repo_root / "SHA256SUMS").is_file()
        and (repo_root / "THEOREM_NOTE.md").is_file()
        and (repo_root / "DRAFT_CITATION.cff").is_file()
    )


def normalized_text(text: str) -> str:
    return " ".join(text.replace("`", "").split())


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


def run_bundle_self_check(repo_root: Path, failures: list[str]) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(repo_root / EXPERIMENT_REL / "candidate_bundle.py"),
            "--profile",
            "v2_7_public_theorem_preflight",
            "--check",
            str(repo_root),
        ],
        cwd=repo_root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        failures.append("v2.7 public preflight bundle self-check failed")
        if result.stdout:
            failures.append(result.stdout.strip())
        if result.stderr:
            failures.append(result.stderr.strip())


def require_file(repo_root: Path, relative_path: Path, failures: list[str]) -> str:
    path = repo_root / relative_path
    if not path.is_file():
        failures.append(f"missing v2.7 public preflight file: {relative_path}")
        return ""
    return path.read_text(encoding="utf-8")


def check_public_docs(repo_root: Path, failures: list[str]) -> None:
    docs = {
        str(PUBLIC_README_REL): require_file(repo_root, PUBLIC_README_REL, failures),
        str(PUBLIC_RELEASE_NOTES_REL): require_file(repo_root, PUBLIC_RELEASE_NOTES_REL, failures),
        str(PUBLIC_CITATION_REL): require_file(repo_root, PUBLIC_CITATION_REL, failures),
    }
    combined = "\n".join(docs.values())
    normalized = normalized_text(combined)
    for phrase in REQUIRED_PUBLIC_TEXT:
        if normalized_text(phrase) not in normalized:
            failures.append(f"v2.7 public preflight docs missing phrase {phrase!r}")
    for phrase in FORBIDDEN_PUBLIC_TEXT:
        if phrase in combined:
            failures.append(f"v2.7 public preflight docs contain forbidden phrase {phrase!r}")
    if DOI_RE.search(combined):
        failures.append("v2.7 public preflight docs must not contain a Zenodo DOI")


def check_public_manifest(repo_root: Path, failures: list[str]) -> None:
    text = require_file(repo_root, PUBLIC_MANIFEST_REL, failures)
    if not text:
        return
    data = json.loads(text)
    expected = {
        "id": "prc_v2_7_public_theorem_preflight_bundle_v1_0",
        "status": "gate_p_preflight_manifest",
        "public_release": False,
        "base_public_release": "v2.5.0-prc-public-theorem",
        "github_release_tag": RELEASE_ID,
        "github_release_url": "",
        "doi_state": "not_assigned",
        "zenodo_version_doi": "",
        "planned_release_asset_name": ASSET_NAME,
        "theorem_scope": "general_q_prime_direct_lift_prc_circular_arc_model",
        "exact_audit_scope": "recorded_birth_rows_consistency_audit_not_full_finite_universe_completeness",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            failures.append(f"v2.7 public preflight manifest {key} must be {value!r}")
    for phrase in REQUIRED_NON_CLAIMS:
        if phrase not in "\n".join(data.get("promotion_boundary", [])):
            failures.append(f"v2.7 public preflight manifest missing boundary {phrase!r}")
    if DOI_RE.search(text):
        failures.append("v2.7 public preflight manifest must not contain a Zenodo DOI")


def check_registry_entry(repo_root: Path, failures: list[str]) -> None:
    if is_public_preflight_bundle_root(repo_root):
        return
    text = require_file(repo_root, REGISTRY_REL, failures)
    if not text:
        return
    registry = json.loads(text)
    matches = [
        entry for entry in registry.get("releases", []) if entry.get("release_id") == RELEASE_ID
    ]
    if len(matches) != 1:
        failures.append(f"release registry must contain exactly one {RELEASE_ID} entry")
        return
    entry = matches[0]
    expected = {
        "version": RELEASE_ID,
        "tag": RELEASE_ID,
        "title": "PRC v2.7: General q-Prime Single-Gap Aperture Classification Theorem",
        "release_kind": "doi_release",
        "doi_state": "not_assigned",
        "zenodo_concept_doi": "",
        "zenodo_version_doi": "",
        "github_release_url": "",
        "asset_name": ASSET_NAME,
        "workflow_path": str(PUBLIC_WORKFLOW_REL),
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            failures.append(f"release registry {RELEASE_ID} {key} must be {value!r}")
    if entry.get("manifest_path") not in {
        str(PUBLIC_MANIFEST_REL),
        str(PUBLIC_RELEASE_MANIFEST_REL),
    }:
        failures.append(
            f"release registry {RELEASE_ID} manifest_path must be a v2.7 preflight or release manifest"
        )
    if entry.get("citation_doi_policy") not in {"none", "version_doi"}:
        failures.append(
            f"release registry {RELEASE_ID} citation_doi_policy must be 'none' or 'version_doi'"
        )
    for phrase in REQUIRED_NON_CLAIMS:
        if phrase not in entry.get("non_claim_phrases", []):
            failures.append(f"release registry {RELEASE_ID} missing non-claim {phrase!r}")


def check_public_workflow(repo_root: Path, failures: list[str]) -> None:
    bundle_root = is_public_preflight_bundle_root(repo_root)
    workflow_rel = PUBLIC_BUNDLE_WORKFLOW_REL if bundle_root else PUBLIC_WORKFLOW_REL
    text = require_file(repo_root, workflow_rel, failures)
    if not text:
        return
    required_phrases = [
        RELEASE_ID,
        ASSET_NAME,
    ]
    if bundle_root:
        required_phrases.extend(
            [
                "public_release: false",
                "check_v2_7_public_theorem_preflight.py",
                "v2_7_public_theorem_preflight",
                "include_doi_integrity: false",
                "candidate_bundle.py",
                "SHA256SUMS",
            ]
        )
    else:
        required_phrases.extend(
            [
                "public_release: true",
                "check_v2_7_public_theorem_release.py",
                "v2_7_public_theorem_release",
                "include_doi_integrity: true",
                "public-theorem-doi-integrity",
                "scripts/check_release_doi_integrity.py",
            ]
        )
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"v2.7 public preflight workflow missing {phrase!r}")
    if bundle_root:
        for forbidden in (
            "public-theorem-doi-integrity",
            "scripts/check_release_doi_integrity.py",
            "release/public/release_registry.json",
        ):
            if forbidden in text:
                failures.append(
                    f"bundle-local v2.7 workflow contains repo-only phrase {forbidden!r}"
                )
    if DOI_RE.search(text):
        failures.append("v2.7 public preflight workflow must not contain a Zenodo DOI")


def main() -> int:
    repo_root = repo_root_from_script()
    failures: list[str] = []
    bundle_root = is_public_preflight_bundle_root(repo_root)

    run_script(
        repo_root,
        EXPERIMENT_REL / "check_v2_7_general_single_gap_aperture_theorem_note.py",
        failures,
    )
    run_script(
        repo_root,
        EXPERIMENT_REL / "check_v2_7_strict_single_gap_aperture_exact_audit.py",
        failures,
    )
    if bundle_root:
        run_bundle_self_check(repo_root, failures)
    else:
        run_script(repo_root, EXPERIMENT_REL / "check_v2_7_gate_c_candidate.py", failures)
    check_public_docs(repo_root, failures)
    check_public_manifest(repo_root, failures)
    check_registry_entry(repo_root, failures)
    check_public_workflow(repo_root, failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_7_public_theorem_preflight: "
        "checks=7, failed=0, gate_p=preflight_ready, public_release=defer, "
        "doi_state=not_assigned, exact_audit=recorded_birth_rows_consistency"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
