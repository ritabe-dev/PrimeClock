#!/usr/bin/env python3
"""Check the v2.7.1 public theorem release candidate boundary."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
RELEASE_README_REL = (
    EXPERIMENT_REL / "notes/prc_v2_7_public_theorem_release_readme_v1_0.md"
)
RELEASE_NOTES_REL = (
    EXPERIMENT_REL / "notes/prc_v2_7_public_theorem_release_notes_final_v1_0.md"
)
RELEASE_CITATION_REL = (
    EXPERIMENT_REL / "notes/prc_v2_7_public_theorem_release_citation_v1_0.cff"
)
RELEASE_MANIFEST_REL = EXPERIMENT_REL / "public_theorem_release_manifest_v2_7_v1_0.json"
RELEASE_WORKFLOW_REL = EXPERIMENT_REL / "public_theorem_release_workflow_v2_7_v1_0.yml"
RELEASE_BUNDLE_WORKFLOW_REL = (
    EXPERIMENT_REL / "public_theorem_release_bundle_workflow_v2_7_v1_0.yml"
)
REGISTRY_REL = Path("release/public/release_registry.json")
RELEASE_ID = "v2.7.1-prc-general-q-prime-theorem"
ASSET_NAME = "PrimeClock-v2.7.1-general-q-prime-theorem-v1.0.zip"
RELEASE_URL = "https://github.com/ritabe-dev/PrimeClock/releases/tag/v2.7.1-prc-general-q-prime-theorem"
DOI_RE = re.compile(r"10\.5281/zenodo\.\d+")

REQUIRED_PUBLIC_TEXT = (
    "PRC v2.7.1: General q-Prime Single-Gap Aperture Classification Theorem",
    "public theorem release text",
    "direct one-prime q-lift",
    "recorded birth rows consistency audit",
    "committed recorded birth rows in the finite next-prime support CSV",
    "not a full finite-universe completeness audit",
    "no B8 theorem",
    "no full transition-graph theorem",
    "no general predictor",
    "no asymptotic law",
    "no prime-gap theorem outside PRC model",
    "CITATION.cff",
    RELEASE_URL,
    "DOI and registry integrity checks are full-repository release-execution checks only",
)
FORBIDDEN_PUBLIC_TEXT = (
    "DRAFT_CITATION.cff",
    "not a DOI artifact",
    "not a GitHub Release",
    "B8 theorem proven",
    "general predictor theorem",
    "asymptotic law theorem",
)
REQUIRED_NON_CLAIMS = (
    "no B8 theorem",
    "no full transition-graph theorem",
    "no general predictor",
    "no asymptotic law",
    "no prime-gap theorem outside PRC model",
    "not a full finite-universe completeness audit",
)


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def is_public_release_bundle_root(repo_root: Path) -> bool:
    return (
        (repo_root / "BUNDLE_FILE_MANIFEST.txt").is_file()
        and (repo_root / "SHA256SUMS").is_file()
        and (repo_root / "THEOREM_NOTE.md").is_file()
        and (repo_root / "CITATION.cff").is_file()
    )


def normalized_text(text: str) -> str:
    return " ".join(text.replace("`", "").split())


def require_file(repo_root: Path, relative_path: Path, failures: list[str]) -> str:
    path = repo_root / relative_path
    if not path.is_file():
        failures.append(f"missing v2.7.1 public release file: {relative_path}")
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


def run_bundle_self_check(repo_root: Path, failures: list[str]) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(repo_root / EXPERIMENT_REL / "candidate_bundle.py"),
            "--profile",
            "v2_7_public_theorem_release",
            "--check",
            str(repo_root),
        ],
        cwd=repo_root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        failures.append("v2.7.1 public theorem release bundle self-check failed")
        if result.stdout:
            failures.append(result.stdout.strip())
        if result.stderr:
            failures.append(result.stderr.strip())


def check_public_docs(repo_root: Path, failures: list[str]) -> None:
    doi_state, version_doi = release_doi_state(repo_root, failures)
    docs = {
        str(RELEASE_README_REL): require_file(repo_root, RELEASE_README_REL, failures),
        str(RELEASE_NOTES_REL): require_file(repo_root, RELEASE_NOTES_REL, failures),
        str(RELEASE_CITATION_REL): require_file(repo_root, RELEASE_CITATION_REL, failures),
    }
    combined = "\n".join(docs.values())
    normalized = normalized_text(combined)
    for phrase in REQUIRED_PUBLIC_TEXT:
        if normalized_text(phrase) not in normalized:
            failures.append(f"v2.7.1 public release docs missing phrase {phrase!r}")
    if doi_state == "assigned":
        if version_doi not in combined:
            failures.append(f"v2.7.1 public release docs missing DOI {version_doi!r}")
        if "pending Zenodo publication" in combined:
            failures.append("v2.7.1 public release docs contain stale DOI pending phrase")
    else:
        if "pending Zenodo publication" not in combined:
            failures.append("v2.7.1 public release docs missing pending DOI phrase")
        if DOI_RE.search(combined):
            failures.append(
                "v2.7.1 public release docs must not contain a Zenodo DOI before finalization"
            )
    for phrase in FORBIDDEN_PUBLIC_TEXT:
        if phrase in combined:
            failures.append(f"v2.7.1 public release docs contain forbidden phrase {phrase!r}")


def release_doi_state(repo_root: Path, failures: list[str]) -> tuple[str, str]:
    text = require_file(repo_root, RELEASE_MANIFEST_REL, failures)
    if not text:
        return "not_assigned", ""
    data = json.loads(text)
    doi_state = data.get("doi_state")
    version_doi = data.get("zenodo_version_doi", "")
    if doi_state not in {"not_assigned", "assigned"}:
        failures.append("v2.7.1 public release manifest doi_state must be assigned or not_assigned")
        return "not_assigned", ""
    if doi_state == "assigned" and not DOI_RE.fullmatch(version_doi):
        failures.append("v2.7.1 public release manifest assigned DOI state needs Zenodo DOI")
    if doi_state == "not_assigned" and version_doi:
        failures.append("v2.7.1 public release manifest has DOI while doi_state is not_assigned")
    return doi_state, version_doi


def check_release_manifest(repo_root: Path, failures: list[str]) -> None:
    text = require_file(repo_root, RELEASE_MANIFEST_REL, failures)
    if not text:
        return
    data = json.loads(text)
    expected = {
        "id": "prc_v2_7_public_theorem_release_bundle_v1_0",
        "status": "public_theorem_release_manifest",
        "public_release": True,
        "base_public_release": "v2.5.0-prc-public-theorem",
        "github_release_tag": RELEASE_ID,
        "github_release_url": RELEASE_URL,
        "default_name": "PrimeClock-v2.7.1-general-q-prime-theorem-v1.0",
        "theorem_scope": "general_q_prime_direct_lift_prc_circular_arc_model",
        "exact_audit_scope": "recorded_birth_rows_consistency_audit_not_full_finite_universe_completeness",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            failures.append(f"v2.7.1 public release manifest {key} must be {value!r}")
    for phrase in REQUIRED_NON_CLAIMS:
        if phrase not in "\n".join(data.get("promotion_boundary", [])):
            failures.append(f"v2.7.1 public release manifest missing boundary {phrase!r}")
    doi_state, version_doi = release_doi_state(repo_root, failures)
    if doi_state == "assigned":
        if version_doi not in text:
            failures.append(f"v2.7.1 public release manifest missing DOI {version_doi!r}")
        if "pending Zenodo publication" in text:
            failures.append("v2.7.1 public release manifest contains stale DOI pending phrase")
    elif DOI_RE.search(text):
        failures.append("v2.7.1 public release manifest must not contain a Zenodo DOI before finalization")


def check_registry_entry(repo_root: Path, failures: list[str]) -> None:
    if is_public_release_bundle_root(repo_root):
        return
    doi_state, version_doi = release_doi_state(repo_root, failures)
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
        "title": "PRC v2.7.1: General q-Prime Single-Gap Aperture Classification Theorem",
        "release_kind": "doi_release",
        "zenodo_concept_doi": "",
        "github_release_url": RELEASE_URL,
        "asset_name": ASSET_NAME,
        "manifest_path": str(RELEASE_MANIFEST_REL),
        "workflow_path": str(RELEASE_WORKFLOW_REL),
        "citation_doi_policy": "version_doi",
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            failures.append(f"release registry {RELEASE_ID} {key} must be {value!r}")
    if entry.get("doi_state") != doi_state:
        failures.append(f"release registry {RELEASE_ID} doi_state must match manifest")
    if entry.get("zenodo_version_doi", "") != version_doi:
        failures.append(f"release registry {RELEASE_ID} zenodo_version_doi must match manifest")
    for phrase in REQUIRED_NON_CLAIMS:
        if phrase not in entry.get("non_claim_phrases", []):
            failures.append(f"release registry {RELEASE_ID} missing non-claim {phrase!r}")


def check_release_workflow(repo_root: Path, failures: list[str]) -> None:
    bundle_root = is_public_release_bundle_root(repo_root)
    workflow_rel = RELEASE_BUNDLE_WORKFLOW_REL if bundle_root else RELEASE_WORKFLOW_REL
    text = require_file(repo_root, workflow_rel, failures)
    if not text:
        return
    required_phrases = [
        RELEASE_ID,
        ASSET_NAME,
        "public_release: true",
        "check_v2_7_public_theorem_release.py",
        "v2_7_public_theorem_release",
    ]
    if bundle_root:
        required_phrases.extend(
            [
                "include_doi_integrity: false",
                "candidate_bundle.py",
                "SHA256SUMS",
            ]
        )
    else:
        required_phrases.extend(
            [
                "include_doi_integrity: true",
                "public-theorem-doi-integrity",
                "scripts/check_release_doi_integrity.py",
            ]
        )
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"v2.7.1 public release workflow missing {phrase!r}")
    if bundle_root:
        for forbidden in (
            "public-theorem-doi-integrity",
            "scripts/check_release_doi_integrity.py",
            "release/public/release_registry.json",
        ):
            if forbidden in text:
                failures.append(
                    f"bundle-local v2.7 release workflow contains repo-only phrase {forbidden!r}"
                )
    doi_state, _ = release_doi_state(repo_root, failures)
    if doi_state != "assigned" and DOI_RE.search(text):
        failures.append("v2.7.1 public release workflow must not contain a Zenodo DOI before finalization")


def main() -> int:
    repo_root = repo_root_from_script()
    failures: list[str] = []
    bundle_root = is_public_release_bundle_root(repo_root)

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
    check_public_docs(repo_root, failures)
    check_release_manifest(repo_root, failures)
    check_registry_entry(repo_root, failures)
    check_release_workflow(repo_root, failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    doi_state, _ = release_doi_state(repo_root, failures)
    print(
        "check_v2_7_public_theorem_release: "
        "checks=8, failed=0, public_release=review_ready, "
        f"doi_state={doi_state}, exact_audit=recorded_birth_rows_consistency"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
