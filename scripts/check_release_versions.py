#!/usr/bin/env python3
"""Fail when public release version strings drift from release_config.json."""

from __future__ import annotations

import re
import argparse
from pathlib import Path

from release_config import load_release_config


def term(*parts: str) -> str:
    return "".join(parts)


PUBLIC_FACING_FILES = [
    ".github/workflows/verify.yml",
    "README.md",
    "VERIFY.md",
    "VERSION_MAP.md",
    "CITATION.cff",
    "DATA_FILES.md",
    "release/public/PUBLISH_CHECKLIST.md",
    "release/public/README.template.md",
    "release/public/release_config.json",
    "research/README.md",
    "research/PUBLIC_RELEASE_MANIFEST.md",
    "research/VERIFY_FINITE_C4_B5.md",
    "scripts/build_public_release.py",
    "scripts/finalize_release_doi.py",
    "scripts/publish_public_release.py",
    "scripts/update_public_hashes.py",
    "scripts/verify_public_release.py",
]

STALE_PATTERNS = [
    term("2.2.", "1"),
    term("v2.2.", "1"),
    term("PrimeClock-2.2.", "1"),
    term("2.2.", "2"),
    term("v2.2.", "2"),
    term("PrimeClock-2.2.", "2"),
]


def read(repo_root: Path, relative_path: str) -> str:
    path = repo_root / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"Missing public-facing file: {relative_path}")
    return path.read_text(encoding="utf-8")


def require_contains(
    failures: list[str],
    text: str,
    needle: str,
    relative_path: str,
) -> None:
    if needle not in text:
        failures.append(f"{relative_path} missing {needle!r}")


def check_root_readme(failures: list[str], text: str, tag: str) -> None:
    """Accept either the source-repo README or the generated bundle README."""
    if f"The {tag} public bundle" in text:
        require_contains(failures, text, "scripts/verify_public_release.py", "README.md")
        return

    bundle_needles = [
        "public release bundle",
        "finite `C_k/C_4/B_5`",
        "not included in this bundle",
    ]
    for needle in bundle_needles:
        require_contains(failures, text, needle, "README.md")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, help="Repository root to check")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    config = load_release_config(repo_root)
    release = config["public_release"]
    tag = config["public_tag"]
    bundle = config["bundle_name"]
    release_url = config["github_release_url"]
    concept_doi = config["zenodo_concept_doi"]
    version_doi = config.get("zenodo_version_doi")
    failures: list[str] = []

    citation = read(repo_root, "CITATION.cff")
    require_contains(failures, citation, f'version: "{release}"', "CITATION.cff")
    require_contains(failures, citation, f'url: "{release_url}"', "CITATION.cff")
    require_contains(failures, citation, f'doi: "{concept_doi}"', "CITATION.cff")
    if version_doi and re.search(rf'^doi: "{re.escape(version_doi)}"$', citation, re.MULTILINE):
        failures.append("CITATION.cff uses version DOI as top-level doi")

    workflow = read(repo_root, ".github/workflows/verify.yml")
    require_contains(
        failures,
        workflow,
        "python scripts/verify_public_release.py --out /tmp/primeclock-public-release --zip",
        ".github/workflows/verify.yml",
    )
    require_contains(failures, workflow, "actions/checkout@v6", ".github/workflows/verify.yml")
    require_contains(failures, workflow, "actions/setup-python@v6", ".github/workflows/verify.yml")

    readme = read(repo_root, "README.md")
    check_root_readme(failures, readme, tag)

    verify = read(repo_root, "VERIFY.md")
    require_contains(failures, verify, "scripts/verify_public_release.py", "VERIFY.md")

    version_map = read(repo_root, "VERSION_MAP.md")
    require_contains(failures, version_map, f"| Public release | `{tag}` |", "VERSION_MAP.md")
    require_contains(failures, version_map, f"`{bundle}`", "VERSION_MAP.md")

    manifest = read(repo_root, "research/PUBLIC_RELEASE_MANIFEST.md")
    require_contains(failures, manifest, config["root_release_notes"], "research/PUBLIC_RELEASE_MANIFEST.md")
    require_contains(failures, manifest, config["research_release_notes"], "research/PUBLIC_RELEASE_MANIFEST.md")
    require_contains(failures, manifest, "release/public/release_config.json", "research/PUBLIC_RELEASE_MANIFEST.md")

    config_text = read(repo_root, "release/public/release_config.json")
    require_contains(failures, config_text, '"release_kind":', "release/public/release_config.json")
    require_contains(failures, config_text, '"zenodo_expected":', "release/public/release_config.json")
    require_contains(failures, config_text, '"allow_github_release":', "release/public/release_config.json")

    for relative_path in PUBLIC_FACING_FILES:
        text = read(repo_root, relative_path)
        for stale in STALE_PATTERNS:
            if re.search(rf"(?<![0-9A-Za-z_.-]){re.escape(stale)}(?![0-9A-Za-z_.-])", text):
                failures.append(f"{relative_path} contains stale release string {stale!r}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"release version check passed: {tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
