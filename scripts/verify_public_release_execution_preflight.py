#!/usr/bin/env python3
"""Run version-agnostic public release execution guardrails."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from release_registry import REGISTRY_PATH, load_release_registry, release_entries, release_entry


RELEASE_SCRIPT_TEST_SELECTOR = (
    "public_release or publish_public_release or release_version or finalize_release"
)
REPO_ONLY_BUNDLE_WORKFLOW_PHRASES = [
    "scripts/check_release_doi_integrity.py",
    "release/public/release_registry.json",
    "public-theorem-doi-integrity",
]


def term(*parts: str) -> str:
    return "".join(parts)


PUBLIC_SURFACE_FORBIDDEN_PATTERNS = [
    re.compile(rf"\b{term('co', 'dex/')}", re.IGNORECASE),
    re.compile(rf"\b{term('Chat', 'GPT')}\b", re.IGNORECASE),
    re.compile(rf"\b{term('AI', '-generated')}\b", re.IGNORECASE),
    re.compile(rf"\b{term('review ', 'package')}\b", re.IGNORECASE),
]
STAGED_FORBIDDEN_PATTERNS = [
    re.compile(r"(^|/)\.DS_Store$"),
    re.compile(r"(^|/)node_modules/"),
    re.compile(r"(^|/)\.venv/"),
    re.compile(r"(^|/)dist/"),
    re.compile(r"(^|/)__pycache__/"),
    re.compile(r"(^|/)review_packages/[^/]+/$"),
    re.compile(r"(^|/)review_packages/[^/]+(?:\s*\(\d+\))?\.zip$"),
]


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def python_executable(repo_root: Path) -> str:
    venv_python = repo_root / "research" / ".venv" / "bin" / "python"
    return str(venv_python) if venv_python.is_file() else sys.executable


def run(command: list[str], *, cwd: Path, expected_stdout: str | None = None) -> str:
    print("+ " + " ".join(command))
    result = subprocess.run(command, cwd=cwd, check=False, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    if expected_stdout and expected_stdout not in result.stdout:
        raise SystemExit(
            "command stdout did not contain expected text "
            f"{expected_stdout!r}: {' '.join(command)}"
        )
    return result.stdout


def selected_entries(registry: dict[str, Any], release_id: str | None, all_releases: bool) -> list[dict[str, Any]]:
    if all_releases:
        return release_entries(registry)
    if release_id:
        return [release_entry(registry, release_id)]
    raise SystemExit("pass --all or --release-id")


def read_text(repo_root: Path, relative_path: str) -> str:
    path = repo_root / relative_path
    if not path.is_file():
        raise SystemExit(f"missing registered release file: {relative_path}")
    return path.read_text(encoding="utf-8")


def load_json(repo_root: Path, relative_path: str) -> dict[str, Any]:
    return json.loads(read_text(repo_root, relative_path))


def deterministic_github_release_url(tag: str) -> str:
    return f"https://github.com/ritabe-dev/PrimeClock/releases/tag/{tag}"


def run_release_doi_checks(repo_root: Path, entries: list[dict[str, Any]], *, python: str) -> None:
    for entry in entries:
        run(
            [
                python,
                "scripts/check_release_doi_integrity.py",
                "--release-id",
                entry["release_id"],
            ],
            cwd=repo_root,
            expected_stdout="check_release_doi_integrity: checked=1, failed=0",
        )
    run(
        [python, "scripts/check_release_doi_integrity.py", "--all"],
        cwd=repo_root,
        expected_stdout="check_release_doi_integrity:",
    )


def run_hash_and_release_script_checks(repo_root: Path, *, python: str) -> None:
    run([python, "scripts/render_public_surface.py", "--check"], cwd=repo_root)
    run([python, "scripts/update_public_hashes.py", "--check"], cwd=repo_root)
    run(
        [
            python,
            "-m",
            "pytest",
            "research/tests/test_covering_prime_prefix_filtration.py",
            "-q",
            "-k",
            RELEASE_SCRIPT_TEST_SELECTOR,
            "--durations=20",
        ],
        cwd=repo_root,
    )


def workflow_supports_public_theorem_review(text: str) -> bool:
    return "public-theorem-review" in text and "public-theorem-integrity" in text


def run_registered_workflows(repo_root: Path, entries: list[dict[str, Any]], *, python: str) -> None:
    for entry in entries:
        workflow_path = entry["workflow_path"]
        workflow_text = read_text(repo_root, workflow_path)
        if not workflow_supports_public_theorem_review(workflow_text):
            continue
        run(
            [
                python,
                "scripts/verify_candidate_workflow.py",
                "--config",
                workflow_path,
                "public-theorem-review",
            ],
            cwd=repo_root,
            expected_stdout="candidate gate: public-theorem-bundle",
        )


def candidate_bundle_manifest_bundle_workflows(manifest: dict[str, Any]) -> list[str]:
    workflows: list[str] = []
    for relative_path in manifest.get("research_files", []):
        if relative_path.endswith(".yml") and "_bundle_workflow_" in relative_path:
            workflows.append(relative_path)
    return workflows


def check_release_metadata_boundaries(repo_root: Path, entries: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    for entry in entries:
        expected_url = deterministic_github_release_url(entry["tag"])
        if entry["github_release_url"] and entry["github_release_url"] != expected_url:
            failures.append(
                f"{entry['release_id']}: github_release_url {entry['github_release_url']!r} "
                f"does not match deterministic tag URL {expected_url!r}"
            )

        workflow_text = read_text(repo_root, entry["workflow_path"])
        if workflow_supports_public_theorem_review(workflow_text):
            if "public-theorem-doi-integrity" not in workflow_text:
                failures.append(f"{entry['release_id']}: repo workflow missing DOI integrity gate")
            if "scripts/check_release_doi_integrity.py" not in workflow_text:
                failures.append(f"{entry['release_id']}: repo workflow missing DOI checker command")

        if not entry["manifest_path"].endswith(".json"):
            continue
        manifest = load_json(repo_root, entry["manifest_path"])
        for bundle_workflow_path in candidate_bundle_manifest_bundle_workflows(manifest):
            bundle_workflow_text = read_text(repo_root, bundle_workflow_path)
            for phrase in REPO_ONLY_BUNDLE_WORKFLOW_PHRASES:
                if phrase in bundle_workflow_text:
                    failures.append(
                        f"{entry['release_id']}: bundle-local workflow "
                        f"{bundle_workflow_path} contains repo-only phrase {phrase!r}"
                    )

        public_paths = (
            entry["readme_paths"]
            + entry["release_notes_paths"]
            + entry["citation_paths"]
            + [entry["manifest_path"], entry["workflow_path"]]
        )
        for public_path in sorted(set(public_paths)):
            public_text = read_text(repo_root, public_path)
            for pattern in PUBLIC_SURFACE_FORBIDDEN_PATTERNS:
                if pattern.search(public_text):
                    failures.append(
                        f"{entry['release_id']}: public release surface {public_path} "
                        f"contains forbidden public marker {pattern.pattern!r}"
                    )
    return failures


def check_release_assets(repo_root: Path, entries: list[dict[str, Any]]) -> None:
    for entry in entries:
        asset_path = repo_root / "review_packages" / entry["asset_name"]
        if not asset_path.is_file():
            print(f"release asset not present locally, skipping zip check: {asset_path}")
            continue
        run(["unzip", "-t", str(asset_path)], cwd=repo_root, expected_stdout="No errors detected")
        run(["shasum", "-a", "256", str(asset_path)], cwd=repo_root)


def staged_paths(repo_root: Path) -> list[str]:
    output = run(["git", "diff", "--cached", "--name-only"], cwd=repo_root)
    return [line.strip() for line in output.splitlines() if line.strip()]


def registered_release_asset_paths(entries: list[dict[str, Any]]) -> set[str]:
    return {f"review_packages/{entry['asset_name']}" for entry in entries}


def check_staged_junk(repo_root: Path, entries: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    allowed_assets = registered_release_asset_paths(entries)
    for relative_path in staged_paths(repo_root):
        if relative_path in allowed_assets:
            continue
        for pattern in STAGED_FORBIDDEN_PATTERNS:
            if pattern.search(relative_path):
                failures.append(f"staged forbidden release path: {relative_path}")
                break
    return failures


def check_remote_branch_hygiene(repo_root: Path) -> list[str]:
    failures: list[str] = []
    result = subprocess.run(
        ["git", "branch", "-r"],
        cwd=repo_root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return ["could not inspect remote branches for public release hygiene"]
    for line in result.stdout.splitlines():
        branch = line.strip()
        if branch.startswith(term("origin/co", "dex/")):
            failures.append(f"remote public branch uses forbidden prefix: {branch}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, help="Repository root to check")
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH, help="Release registry path")
    parser.add_argument("--release-id", help="Registered release id to check")
    parser.add_argument("--all", action="store_true", help="Check all registered releases")
    parser.add_argument("--check-staged", action="store_true", help="Reject staged generated junk")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve() if args.repo_root else repo_root_from_script()
    registry = load_release_registry(repo_root, args.registry)
    entries = selected_entries(registry, args.release_id, args.all)
    python = python_executable(repo_root)

    failures = check_release_metadata_boundaries(repo_root, entries)
    if args.check_staged:
        failures.extend(check_staged_junk(repo_root, entries))
        failures.extend(check_remote_branch_hygiene(repo_root))
    if failures:
        print("verify_public_release_execution_preflight: failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    run_release_doi_checks(repo_root, entries, python=python)
    run_hash_and_release_script_checks(repo_root, python=python)
    run_registered_workflows(repo_root, entries, python=python)
    check_release_assets(repo_root, entries)

    checked = ", ".join(entry["release_id"] for entry in entries)
    print(
        "verify_public_release_execution_preflight: "
        f"checked={len(entries)}, failed=0, releases={checked}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
