#!/usr/bin/env python3
"""Shared multi-version release registry helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REGISTRY_PATH = Path("release/public/release_registry.json")


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def load_release_registry(
    repo_root: Path | None = None,
    registry_path: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or repo_root_from_script()
    path = registry_path or root / REGISTRY_PATH
    if not path.is_absolute():
        path = root / path
    if not path.is_file():
        raise FileNotFoundError(f"Missing release registry: {path}")
    registry = json.loads(path.read_text(encoding="utf-8"))
    validate_release_registry(registry)
    return registry


def save_release_registry(
    registry: dict[str, Any],
    repo_root: Path | None = None,
    registry_path: Path | None = None,
) -> None:
    root = repo_root or repo_root_from_script()
    path = registry_path or root / REGISTRY_PATH
    if not path.is_absolute():
        path = root / path
    path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")


def release_entries(registry: dict[str, Any]) -> list[dict[str, Any]]:
    return list(registry.get("releases", []))


def release_entry(registry: dict[str, Any], release_id: str) -> dict[str, Any]:
    matches = [entry for entry in release_entries(registry) if entry["release_id"] == release_id]
    if not matches:
        known = ", ".join(entry["release_id"] for entry in release_entries(registry))
        raise ValueError(f"Unknown release_id {release_id!r}. Registered releases: {known}")
    return matches[0]


def validate_release_registry(registry: dict[str, Any]) -> None:
    if registry.get("schema_version") != 1:
        raise ValueError("release_registry schema_version must be 1")
    releases = registry.get("releases")
    if not isinstance(releases, list) or not releases:
        raise ValueError("release_registry releases must be a non-empty list")

    required = {
        "release_id",
        "version",
        "tag",
        "title",
        "release_kind",
        "doi_state",
        "zenodo_concept_doi",
        "zenodo_version_doi",
        "github_release_url",
        "asset_name",
        "manifest_path",
        "workflow_path",
        "readme_paths",
        "release_notes_paths",
        "citation_paths",
        "citation_doi_policy",
        "asset_check_paths",
        "non_claim_phrases",
        "forbidden_phrases",
    }
    seen: set[str] = set()
    for entry in releases:
        missing = sorted(required.difference(entry))
        if missing:
            release_id = entry.get("release_id", "<missing release_id>")
            raise ValueError(f"release_registry {release_id} missing keys: {', '.join(missing)}")
        release_id = entry["release_id"]
        if release_id in seen:
            raise ValueError(f"duplicate release_id in release_registry: {release_id}")
        seen.add(release_id)

        if entry["doi_state"] not in {"not_assigned", "assigned"}:
            raise ValueError(f"{release_id}: doi_state must be not_assigned or assigned")
        if entry["citation_doi_policy"] not in {"concept_doi", "version_doi", "none"}:
            raise ValueError(
                f"{release_id}: citation_doi_policy must be concept_doi, version_doi, or none"
            )
        for list_key in [
            "readme_paths",
            "release_notes_paths",
            "citation_paths",
            "asset_check_paths",
            "non_claim_phrases",
            "forbidden_phrases",
        ]:
            if not isinstance(entry[list_key], list):
                raise ValueError(f"{release_id}: {list_key} must be a list")
