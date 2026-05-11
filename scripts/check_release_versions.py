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
    "README.md",
    "VERIFY.md",
    "VERSION_MAP.md",
    "CITATION.cff",
    "DATA_FILES.md",
    "ERRATA.md",
    "release/public/MAINTENANCE_POLICY.md",
    "release/public/PUBLISH_CHECKLIST.md",
    "release/public/README.template.md",
    "release/public/verify.yml",
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
        "critical-radius",
        "gap-aperture",
    ]
    for needle in bundle_needles:
        require_contains(failures, text, needle, "README.md")


def check_readme_research_position(failures: list[str], text: str, relative_path: str) -> None:
    normalized = " ".join(text.split())
    for needle in [
        "Research Position",
        "project-defined finite prime-prefix circle-covering model",
        "classical covering systems of congruences",
        "does not claim a result about classical covering systems",
        "citable archived snapshots",
        "do not imply peer review",
    ]:
        require_contains(failures, normalized, needle, relative_path)


def check_public_workflow(failures: list[str], text: str, relative_path: str) -> None:
    require_contains(
        failures,
        text,
        "python scripts/verify_public_release.py --out",
        relative_path,
    )
    require_contains(failures, text, "scripts/verify_public_release.py", relative_path)
    require_contains(failures, text, "--zip", relative_path)
    require_contains(failures, text, "actions/checkout@v6", relative_path)
    require_contains(failures, text, "actions/setup-python@v6", relative_path)
    for forbidden in ["verify_candidate_workflow.py", "candidate_workflow_v0_1.yml"]:
        if forbidden in text:
            failures.append(
                f"{relative_path} contains candidate workflow reference {forbidden!r}"
            )


def check_public_verification_expectations(
    failures: list[str],
    *,
    readme: str,
    verify: str,
    research_readme: str,
    public_readme_template: str,
) -> None:
    if "PrimeClock Development Repository" in readme:
        require_contains(failures, readme, "focused pytest: 55 passed", "README.md")
    require_contains(failures, verify, "focused pytest: 55 passed", "VERIFY.md")
    require_contains(
        failures,
        verify,
        "public critical-radius/birth-dynamics pytest: 9 passed",
        "VERIFY.md",
    )
    for relative_path, text in [
        ("research/README.md", research_readme),
        ("release/public/README.template.md", public_readme_template),
    ]:
        require_contains(
            failures,
            text,
            "public critical-radius/birth-dynamics pytest: 9 passed",
            relative_path,
        )


def check_zenodo_version_doi_finalized(
    failures: list[str],
    *,
    version_doi: str | None,
    docs: dict[str, str],
) -> None:
    if not version_doi:
        return
    for relative_path, text in docs.items():
        if "pending Zenodo publication" in text:
            failures.append(
                f"{relative_path} still says pending Zenodo publication "
                f"after zenodo_version_doi is set"
            )
        require_contains(failures, text, version_doi, relative_path)


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

    check_public_workflow(failures, read(repo_root, "release/public/verify.yml"), "release/public/verify.yml")
    generated_workflow = repo_root / ".github" / "workflows" / "verify.yml"
    if generated_workflow.is_file():
        generated_workflow_text = generated_workflow.read_text(encoding="utf-8")
        # Source checkouts keep candidate jobs in .github/workflows/verify.yml.
        # Generated public bundles replace that file with the public workflow.
        if "Verify PrimeClock public release" not in generated_workflow_text:
            generated_workflow_text = ""
    if generated_workflow.is_file() and generated_workflow_text:
        check_public_workflow(
            failures,
            generated_workflow_text,
            ".github/workflows/verify.yml",
        )

    readme = read(repo_root, "README.md")
    check_root_readme(failures, readme, tag)
    check_readme_research_position(failures, readme, "README.md")

    public_readme_template = read(repo_root, "release/public/README.template.md")
    check_readme_research_position(
        failures,
        public_readme_template,
        "release/public/README.template.md",
    )

    verify = read(repo_root, "VERIFY.md")
    require_contains(failures, verify, "scripts/verify_public_release.py", "VERIFY.md")
    research_readme = read(repo_root, "research/README.md")
    version_map = read(repo_root, "VERSION_MAP.md")
    root_release_notes = read(repo_root, config["root_release_notes"])
    research_release_notes = read(repo_root, config["research_release_notes"])
    check_public_verification_expectations(
        failures,
        readme=readme,
        verify=verify,
        research_readme=research_readme,
        public_readme_template=public_readme_template,
    )
    check_zenodo_version_doi_finalized(
        failures,
        version_doi=version_doi,
        docs={
            "README.md": readme,
            "release/public/README.template.md": public_readme_template,
            "VERSION_MAP.md": version_map,
            config["root_release_notes"]: root_release_notes,
            config["research_release_notes"]: research_release_notes,
        },
    )

    require_contains(failures, version_map, f"| Public release | `{tag}` |", "VERSION_MAP.md")
    require_contains(failures, version_map, f"`{bundle}`", "VERSION_MAP.md")
    require_contains(failures, version_map, "release/public/MAINTENANCE_POLICY.md", "VERSION_MAP.md")
    require_contains(failures, version_map, "ERRATA.md", "VERSION_MAP.md")

    errata = read(repo_root, "ERRATA.md")
    require_contains(failures, errata, "Affected release:", "ERRATA.md")
    require_contains(failures, errata, "Type: errata | docs clarification | maintenance patch | superseded", "ERRATA.md")
    require_contains(failures, errata, "Impact: none | docs only | reproducibility | claim", "ERRATA.md")
    require_contains(failures, errata, "Affected release: v2.2.4", "ERRATA.md")
    require_contains(failures, errata, "Type: docs clarification", "ERRATA.md")
    require_contains(failures, errata, "Impact: docs only", "ERRATA.md")
    require_contains(failures, errata, "does not require a", "ERRATA.md")
    require_contains(failures, errata, "v2.2.5 patch release", "ERRATA.md")

    maintenance_policy = read(repo_root, "release/public/MAINTENANCE_POLICY.md")
    require_contains(failures, maintenance_policy, "Published GitHub tags and Zenodo archives", "release/public/MAINTENANCE_POLICY.md")
    require_contains(failures, maintenance_policy, "maintenance/v2.3.1  starts from v2.3.0", "release/public/MAINTENANCE_POLICY.md")
    require_contains(failures, maintenance_policy, "maintenance/v2.2.5  starts from v2.2.4", "release/public/MAINTENANCE_POLICY.md")

    manifest = read(repo_root, "research/PUBLIC_RELEASE_MANIFEST.md")
    require_contains(failures, manifest, config["root_release_notes"], "research/PUBLIC_RELEASE_MANIFEST.md")
    require_contains(failures, manifest, config["research_release_notes"], "research/PUBLIC_RELEASE_MANIFEST.md")
    require_contains(failures, manifest, "release/public/release_config.json", "research/PUBLIC_RELEASE_MANIFEST.md")

    config_text = read(repo_root, "release/public/release_config.json")
    require_contains(failures, config_text, '"release_kind":', "release/public/release_config.json")
    require_contains(failures, config_text, '"zenodo_expected":', "release/public/release_config.json")
    require_contains(failures, config_text, '"allow_github_release":', "release/public/release_config.json")
    require_contains(
        failures,
        config_text,
        '"doi_policy": "concept_doi_in_citation_version_doi_in_release_notes"',
        "release/public/release_config.json",
    )

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
