#!/usr/bin/env python3
"""Finalize a Zenodo version DOI for a registry-managed release."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from release_registry import REGISTRY_PATH, load_release_registry, release_entry, save_release_registry


DOI_RE = re.compile(r"10\.5281/zenodo\.\d+")
VERSION_DOI_RE = re.compile(r"Version DOI:\s*`?10\.5281/zenodo\.\d+`?")
PENDING_VERSION_RE = re.compile(
    r"Version DOI:\s*`?(?:pending Zenodo publication(?: for [^.`]+)?|pending)`?\.?",
    re.IGNORECASE,
)


def read_text(repo_root: Path, relative_path: str) -> str:
    return (repo_root / relative_path).read_text(encoding="utf-8")


def write_text(repo_root: Path, relative_path: str, text: str) -> None:
    (repo_root / relative_path).write_text(text, encoding="utf-8")


def replace_version_doi_text(text: str, version_doi: str) -> str:
    if VERSION_DOI_RE.search(text):
        return VERSION_DOI_RE.sub(f"Version DOI: `{version_doi}`", text)
    if PENDING_VERSION_RE.search(text):
        return PENDING_VERSION_RE.sub(f"Version DOI: `{version_doi}`", text)
    if "Version DOI:" in text:
        return re.sub(r"Version DOI:[^\n]*", f"Version DOI: `{version_doi}`", text, count=1)
    return text


def replace_citation_doi(text: str, version_doi: str) -> str:
    if re.search(r'^doi:\s*"?[^"\n]+"?\s*$', text, re.MULTILINE):
        return re.sub(r'^doi:\s*"?[^"\n]+"?\s*$', f'doi: "{version_doi}"', text, count=1, flags=re.MULTILINE)
    return text + f'\ndoi: "{version_doi}"\n'


def update_json_file(repo_root: Path, relative_path: str, updates: dict[str, Any]) -> None:
    path = repo_root / relative_path
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    for key, value in updates.items():
        if key in data and data[key] != value:
            data[key] = value
            changed = True
    if changed:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def update_registered_files(repo_root: Path, entry: dict[str, Any], version_doi: str) -> None:
    for relative_path in entry["readme_paths"] + entry["release_notes_paths"]:
        text = read_text(repo_root, relative_path)
        write_text(repo_root, relative_path, replace_version_doi_text(text, version_doi))

    if entry["citation_doi_policy"] == "version_doi":
        for relative_path in entry["citation_paths"]:
            text = read_text(repo_root, relative_path)
            write_text(repo_root, relative_path, replace_citation_doi(text, version_doi))

    json_updates = {
        "doi_state": "assigned",
        "zenodo_version_doi": version_doi,
    }
    if entry["manifest_path"].endswith(".json"):
        update_json_file(repo_root, entry["manifest_path"], json_updates)


def run_checker(repo_root: Path, registry_path: Path, release_id: str) -> int:
    checker = Path(__file__).resolve().with_name("check_release_doi_integrity.py")
    result = subprocess.run(
        [
            sys.executable,
            str(checker),
            "--repo-root",
            str(repo_root),
            "--registry",
            str(registry_path),
            "--release-id",
            release_id,
        ],
        cwd=Path.cwd(),
        check=False,
        text=True,
    )
    return result.returncode


def print_next_steps(entry: dict[str, Any]) -> None:
    print("next verification:")
    print("  python scripts/check_release_doi_integrity.py --all")
    if entry["workflow_path"]:
        print(
            "  research/.venv/bin/python scripts/verify_candidate_workflow.py "
            f"--config {entry['workflow_path']} public-theorem-review"
        )
    if entry["github_release_url"]:
        print("next GitHub release refresh:")
        print(
            f"  gh release edit {entry['tag']} --notes-file "
            f"{entry['release_notes_paths'][0]}"
        )
        if entry["asset_name"]:
            print(f"  gh release upload {entry['tag']} <path-to-{entry['asset_name']}> --clobber")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, help="Repository root to update")
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH, help="Release registry path")
    parser.add_argument("--release-id", required=True, help="Registered release id to update")
    parser.add_argument("--version-doi", required=True, help="Zenodo version DOI")
    parser.add_argument("--execute", action="store_true", help="Write updates")
    args = parser.parse_args()

    if not DOI_RE.fullmatch(args.version_doi):
        print(f"invalid Zenodo DOI: {args.version_doi}")
        return 1

    repo_root = args.repo_root.resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    registry = load_release_registry(repo_root, args.registry)
    entry = release_entry(registry, args.release_id)

    print(f"release_id: {entry['release_id']}")
    print(f"version DOI: {args.version_doi}")
    if not args.execute:
        print("dry-run: pass --execute to update registry-managed release DOI metadata")
        print_next_steps(entry)
        return 0

    entry["doi_state"] = "assigned"
    entry["zenodo_version_doi"] = args.version_doi
    save_release_registry(registry, repo_root, args.registry)
    update_registered_files(repo_root, entry, args.version_doi)
    print_next_steps(entry)
    return run_checker(repo_root, args.registry, args.release_id)


if __name__ == "__main__":
    raise SystemExit(main())
