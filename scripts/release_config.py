#!/usr/bin/env python3
"""Shared public release configuration helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CONFIG_PATH = Path("release/public/release_config.json")


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def load_release_config(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or repo_root_from_script()
    path = root / CONFIG_PATH
    if not path.is_file():
        raise FileNotFoundError(f"Missing release config: {CONFIG_PATH}")
    config = json.loads(path.read_text(encoding="utf-8"))
    validate_release_config(config)
    return config


def validate_release_config(config: dict[str, Any]) -> None:
    required = {
        "public_release",
        "public_tag",
        "bundle_name",
        "root_release_notes",
        "research_release_notes",
        "github_release_url",
        "release_kind",
        "zenodo_expected",
        "allow_github_release",
        "zenodo_concept_doi",
    }
    missing = sorted(required.difference(config))
    if missing:
        raise ValueError(f"release_config missing keys: {', '.join(missing)}")

    release = config["public_release"]
    tag = config["public_tag"]
    bundle = config["bundle_name"]
    if tag != f"v{release}":
        raise ValueError(f"public_tag {tag!r} does not match public_release {release!r}")
    if bundle != f"PrimeClock-{release}":
        raise ValueError(f"bundle_name {bundle!r} does not match public_release {release!r}")
    if not config["github_release_url"].endswith(f"/{tag}"):
        raise ValueError("github_release_url does not end with public_tag")

    release_kind = config["release_kind"]
    if release_kind not in {"maintenance_sync", "doi_release"}:
        raise ValueError("release_kind must be 'maintenance_sync' or 'doi_release'")
    if not isinstance(config["zenodo_expected"], bool):
        raise ValueError("zenodo_expected must be a boolean")
    if not isinstance(config["allow_github_release"], bool):
        raise ValueError("allow_github_release must be a boolean")
    expected_release = release_kind == "doi_release"
    if config["zenodo_expected"] != expected_release:
        raise ValueError("zenodo_expected must match release_kind")
    if config["allow_github_release"] != expected_release:
        raise ValueError("allow_github_release must match release_kind")


def require_matching_version(config: dict[str, Any], requested_version: str | None) -> str:
    release = config["public_release"]
    if requested_version and requested_version != release:
        raise ValueError(
            f"Requested version {requested_version!r} does not match "
            f"release_config public_release {release!r}"
        )
    return release
