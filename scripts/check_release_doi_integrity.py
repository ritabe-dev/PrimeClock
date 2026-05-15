#!/usr/bin/env python3
"""Check DOI/citation consistency for all registered public releases."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from release_config import CONFIG_PATH, load_release_config
from release_registry import REGISTRY_PATH, load_release_registry, release_entries, release_entry


DOI_RE = re.compile(r"10\.5281/zenodo\.\d+")
VERSION_DOI_LINE_RE = re.compile(r"Version DOI:\s*`?10\.5281/zenodo\.\d+`?")
PENDING_PATTERNS = [
    "pending Zenodo publication",
    "do not cite a Zenodo DOI until a Zenodo archive exists",
    "DOI is pending",
    "DOI pending",
]
ROOT_FIXED_CHECKED_RE = re.compile(r"check_release_doi_integrity:\s*checked=\d+")
ROOT_README_FORBIDDEN_PHRASES = [
    "## Development App",
    "## Version-Line Workflow",
    "Gate R:",
    "Gate C:",
    "Gate P:",
    "source-only bridge",
    "next research line",
    "release-registry operating procedure",
    "`v2.6",
    "`maintenance/v2",
]


def read_text(repo_root: Path, relative_path: str) -> str:
    path = repo_root / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"Missing registered release file: {relative_path}")
    return path.read_text(encoding="utf-8")


def load_json(repo_root: Path, relative_path: str) -> dict[str, Any]:
    path = repo_root / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"Missing registered release file: {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def citation_doi(text: str) -> str | None:
    match = re.search(r'^doi:\s*"?([^"\n]+)"?\s*$', text, re.MULTILINE)
    return match.group(1) if match else None


def contains_stem_or_name(text: str, asset_name: str) -> bool:
    return asset_name in text or asset_name.removesuffix(".zip") in text


def validate_v2_3_compat_config(repo_root: Path, entry: dict[str, Any], failures: list[str]) -> None:
    if entry["manifest_path"] != CONFIG_PATH.as_posix():
        return
    config = load_release_config(repo_root)
    expected = {
        "public_release": entry["version"],
        "public_tag": entry["tag"],
        "github_release_url": entry["github_release_url"],
        "release_kind": entry["release_kind"],
        "zenodo_concept_doi": entry["zenodo_concept_doi"],
        "zenodo_version_doi": entry["zenodo_version_doi"],
    }
    for key, expected_value in expected.items():
        if config.get(key) != expected_value:
            failures.append(
                f"{entry['release_id']}: {CONFIG_PATH} {key}={config.get(key)!r} "
                f"does not match registry {expected_value!r}"
            )
    expected_asset_stem = entry["asset_name"].removesuffix(".zip")
    if config.get("bundle_name") != expected_asset_stem:
        failures.append(
            f"{entry['release_id']}: bundle_name {config.get('bundle_name')!r} "
            f"does not match registry asset stem {expected_asset_stem!r}"
        )


def check_assigned_doi(entry: dict[str, Any], failures: list[str]) -> None:
    version_doi = entry["zenodo_version_doi"]
    if entry["doi_state"] == "assigned":
        if not version_doi or not DOI_RE.fullmatch(version_doi):
            failures.append(f"{entry['release_id']}: assigned release missing valid version DOI")
    elif version_doi:
        failures.append(f"{entry['release_id']}: not_assigned release has version DOI {version_doi}")


def check_registered_texts(repo_root: Path, entry: dict[str, Any], failures: list[str]) -> None:
    version_doi = entry["zenodo_version_doi"]
    checked_paths = (
        entry["readme_paths"]
        + entry["release_notes_paths"]
        + entry["citation_paths"]
        + [entry["manifest_path"], entry["workflow_path"]]
        + entry["asset_check_paths"]
    )
    seen_paths = sorted(set(checked_paths))
    for relative_path in seen_paths:
        text = read_text(repo_root, relative_path)
        if entry["doi_state"] == "assigned":
            if relative_path not in {"README.md", "VERSION_MAP.md"}:
                stale_patterns = PENDING_PATTERNS + entry["forbidden_phrases"]
            else:
                stale_patterns = [
                    phrase
                    for phrase in entry["forbidden_phrases"]
                    if phrase not in PENDING_PATTERNS
                ]
            for stale in stale_patterns:
                if stale and stale in text:
                    failures.append(
                        f"{entry['release_id']}: {relative_path} contains stale DOI phrase {stale!r}"
                    )
        else:
            if VERSION_DOI_LINE_RE.search(text):
                failures.append(f"{entry['release_id']}: {relative_path} contains version DOI before assignment")

    public_text = "\n".join(
        read_text(repo_root, relative_path)
        for relative_path in entry["readme_paths"] + entry["release_notes_paths"]
    )
    for phrase in entry["non_claim_phrases"]:
        if phrase and phrase not in public_text:
            failures.append(f"{entry['release_id']}: registered public docs missing non-claim phrase {phrase!r}")

    if entry["doi_state"] == "assigned":
        for relative_path in entry["readme_paths"] + entry["release_notes_paths"]:
            text = read_text(repo_root, relative_path)
            if version_doi not in text:
                failures.append(f"{entry['release_id']}: {relative_path} missing version DOI {version_doi}")
            if entry["tag"] not in text:
                failures.append(f"{entry['release_id']}: {relative_path} missing tag {entry['tag']}")

    for relative_path in entry["asset_check_paths"]:
        text = read_text(repo_root, relative_path)
        if not contains_stem_or_name(text, entry["asset_name"]):
            failures.append(f"{entry['release_id']}: {relative_path} missing asset {entry['asset_name']}")


def check_citations(repo_root: Path, entry: dict[str, Any], failures: list[str]) -> None:
    expected_by_policy = {
        "concept_doi": entry["zenodo_concept_doi"],
        "version_doi": entry["zenodo_version_doi"],
        "none": "",
    }
    expected_doi = expected_by_policy[entry["citation_doi_policy"]]
    for relative_path in entry["citation_paths"]:
        text = read_text(repo_root, relative_path)
        actual_doi = citation_doi(text)
        if expected_doi:
            if actual_doi != expected_doi:
                failures.append(
                    f"{entry['release_id']}: {relative_path} citation DOI {actual_doi!r} "
                    f"does not match registry {expected_doi!r}"
                )
        elif actual_doi:
            failures.append(f"{entry['release_id']}: {relative_path} has DOI despite citation policy none")
        if entry["tag"] not in text and entry["version"] not in text:
            failures.append(f"{entry['release_id']}: {relative_path} missing tag/version")
        if entry["github_release_url"] and entry["github_release_url"] not in text:
            failures.append(f"{entry['release_id']}: {relative_path} missing GitHub release URL")

    if entry["release_id"] != "v2.3.0":
        top_level_citation = repo_root / "CITATION.cff"
        if top_level_citation.is_file() and entry["zenodo_version_doi"]:
            text = top_level_citation.read_text(encoding="utf-8")
            if entry["zenodo_version_doi"] in text:
                failures.append(
                    f"{entry['release_id']}: top-level CITATION.cff contains non-v2.3 DOI "
                    f"{entry['zenodo_version_doi']}"
                )


def check_manifest_fields(repo_root: Path, entry: dict[str, Any], failures: list[str]) -> None:
    manifest_path = entry["manifest_path"]
    if not manifest_path.endswith(".json"):
        return
    manifest = load_json(repo_root, manifest_path)
    text = json.dumps(manifest)
    for needle in [entry["tag"], entry["zenodo_version_doi"], entry["github_release_url"]]:
        if needle and needle not in text:
            failures.append(f"{entry['release_id']}: {manifest_path} missing registry value {needle!r}")


def check_release_asset_metadata(repo_root: Path, entry: dict[str, Any], failures: list[str]) -> None:
    if entry["release_notes_primary"] not in entry["release_notes_paths"]:
        failures.append(f"{entry['release_id']}: release_notes_primary is not registered")
    if entry["bundle_workflow_path"]:
        try:
            read_text(repo_root, entry["bundle_workflow_path"])
        except FileNotFoundError:
            failures.append(
                f"{entry['release_id']}: missing bundle_workflow_path {entry['bundle_workflow_path']}"
            )
    if entry["bundle_profile"] and entry["release_kind"] != "doi_release":
        failures.append(f"{entry['release_id']}: bundle_profile is only supported for DOI releases")
    if not entry["release_asset_sha256"]:
        failures.append(f"{entry['release_id']}: missing release_asset_sha256")
        return
    if not re.fullmatch(r"[0-9a-f]{64}", entry["release_asset_sha256"]):
        failures.append(f"{entry['release_id']}: release_asset_sha256 is not lowercase SHA256 hex")
        return
    asset_path = repo_root / "review_packages" / entry["asset_name"]
    if asset_path.is_file():
        actual = hashlib.sha256(asset_path.read_bytes()).hexdigest()
        if actual != entry["release_asset_sha256"]:
            failures.append(
                f"{entry['release_id']}: local asset SHA256 {actual} "
                f"does not match registry {entry['release_asset_sha256']}"
            )


def latest_assigned_release(entries: list[dict[str, Any]]) -> dict[str, Any]:
    assigned = [
        entry
        for entry in entries
        if entry["release_kind"] == "doi_release" and entry["doi_state"] == "assigned"
    ]
    if not assigned:
        raise ValueError("release_registry has no assigned DOI release")
    return assigned[-1]


def latest_registered_public_release(entries: list[dict[str, Any]]) -> dict[str, Any]:
    releases = [
        entry
        for entry in entries
        if entry["release_kind"] == "doi_release"
    ]
    if not releases:
        raise ValueError("release_registry has no public release")
    return releases[-1]


def require_release_metadata(
    *,
    relative_path: str,
    text: str,
    entry: dict[str, Any],
    label: str,
    failures: list[str],
) -> None:
    for needle in [
        entry["release_id"],
        entry["tag"],
        entry["title"],
        entry["asset_name"],
        entry["github_release_url"],
    ]:
        if needle and needle not in text:
            failures.append(f"{relative_path} missing {label} metadata {needle!r}")
    if entry["doi_state"] == "assigned":
        if entry["zenodo_version_doi"] and entry["zenodo_version_doi"] not in text:
            failures.append(
                f"{relative_path} missing {label} DOI {entry['zenodo_version_doi']!r}"
            )
    elif not any(pattern in text for pattern in PENDING_PATTERNS):
        failures.append(f"{relative_path} missing {label} DOI pending wording")


def check_repository_freshness(repo_root: Path, entries: list[dict[str, Any]]) -> list[str]:
    latest_public = latest_registered_public_release(entries)
    latest_assigned = latest_assigned_release(entries)
    failures: list[str] = []
    root_readme = read_text(repo_root, "README.md")
    version_map = read_text(repo_root, "VERSION_MAP.md")
    for phrase in ROOT_README_FORBIDDEN_PHRASES:
        if phrase in root_readme:
            failures.append(f"README.md contains internal-only public-surface phrase {phrase!r}")
    for relative_path, text in {
        "README.md": root_readme,
        "VERSION_MAP.md": version_map,
    }.items():
        require_release_metadata(
            relative_path=relative_path,
            text=text,
            entry=latest_public,
            label="current public release",
            failures=failures,
        )
        if latest_assigned["release_id"] != latest_public["release_id"]:
            require_release_metadata(
                relative_path=relative_path,
                text=text,
                entry=latest_assigned,
                label="latest DOI-backed release",
                failures=failures,
            )
        if ROOT_FIXED_CHECKED_RE.search(text):
            failures.append(f"{relative_path} contains fixed check_release_doi_integrity count")
    if "The current public release target is:" in version_map:
        failures.append("VERSION_MAP.md still uses singular stale current public release wording")
    if "## Current Release Target" in root_readme:
        failures.append("README.md still uses stale Current Release Target heading")
    if "For current public citation, use the `v2.3.0` release" in root_readme:
        failures.append("README.md still points current public citation at v2.3.0")
    return failures


def check_entry(repo_root: Path, entry: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    check_assigned_doi(entry, failures)
    validate_v2_3_compat_config(repo_root, entry, failures)
    check_registered_texts(repo_root, entry, failures)
    check_citations(repo_root, entry, failures)
    check_manifest_fields(repo_root, entry, failures)
    check_release_asset_metadata(repo_root, entry, failures)
    return failures


def selected_entries(registry: dict[str, Any], release_id: str | None, all_releases: bool) -> list[dict[str, Any]]:
    if all_releases:
        return release_entries(registry)
    if release_id:
        return [release_entry(registry, release_id)]
    raise ValueError("pass --all or --release-id")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, help="Repository root to check")
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH, help="Release registry path")
    parser.add_argument("--release-id", help="Registered release id to check")
    parser.add_argument("--all", action="store_true", help="Check all registered releases")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    registry = load_release_registry(repo_root, args.registry)
    entries = selected_entries(registry, args.release_id, args.all)

    all_failures: list[str] = []
    for entry in entries:
        all_failures.extend(check_entry(repo_root, entry))
    if args.all:
        all_failures.extend(check_repository_freshness(repo_root, release_entries(registry)))

    if all_failures:
        print("check_release_doi_integrity: failed")
        for failure in all_failures:
            print(f"- {failure}")
        return 1

    checked = ", ".join(entry["release_id"] for entry in entries)
    print(f"check_release_doi_integrity: checked={len(entries)}, failed=0, releases={checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
