#!/usr/bin/env python3
"""Build a clean public release bundle from an explicit allowlist."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from release_config import load_release_config, require_matching_version


ROOT_FILE_MAP = [
    ("release/public/README.template.md", "README.md"),
]

BASE_ROOT_FILES = [
    "LICENSE",
    "CITATION.cff",
    "DATA_FILES.md",
    "SHA256SUMS",
    "VERSION_MAP.md",
    "VERIFY.md",
    ".github/workflows/verify.yml",
    "release/public/PUBLISH_CHECKLIST.md",
    "release/public/README.template.md",
    "release/public/release_config.json",
    "scripts/build_public_release.py",
    "scripts/check_public_release.py",
    "scripts/check_release_versions.py",
    "scripts/finalize_release_doi.py",
    "scripts/publish_public_release.py",
    "scripts/release_config.py",
    "scripts/update_public_hashes.py",
    "scripts/verify_public_release.py",
]

BASE_RESEARCH_FILES = [
    "research/README.md",
    "research/PUBLIC_RELEASE_MANIFEST.md",
    "research/VERIFY_FINITE_C4_B5.md",
    "research/pyproject.toml",
    "research/setup.py",
    "research/certificates/check_prime_prefix_c4_b5.py",
    "research/tests/test_covering_prime_prefix_filtration.py",
    "research/notes/prc_finite_certificate_note_v2_0.md",
    "research/notes/claims_finite_c4_b5.md",
    "research/notes/known-results.md",
    "research/data/summaries/prc_prime_prefix_residue_covering_filtration_v0_1.csv",
    "research/data/summaries/prc_prime_prefix_residue_covering_birth_samples_v0_1.csv",
    "research/data/summaries/prc_prime_prefix_ck_full_v1_1.csv",
    "research/data/summaries/prc_prime_prefix_c4_exclusion_witness_v1_6.csv",
    "research/data/summaries/prc_prime_prefix_c4_exclusion_summary_v1_5.csv",
    "research/data/summaries/prc_prime_prefix_birth_witness_v1_5.csv",
    "research/data/summaries/prc_prime_prefix_b5_birth_classification_v1_5.csv",
    "research/data/summaries/prc_prime_prefix_b5_birth_pair_summary_v1_5.csv",
    "research/data/summaries/prc_prime_prefix_certificate_verification_v1_7.csv",
    "research/data/summaries/prc_prime_prefix_certificate_standalone_verification_v1_8.csv",
]

RESEARCH_DIRS = [
    "research/src/prime_reciprocal_projection",
]

EXCLUDED_DIR_NAMES = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".matplotlib-cache",
    ".uv-cache",
    ".venv",
    "__pycache__",
    "dist",
    "node_modules",
    "review_packages",
}


def root_files(config: dict[str, str]) -> list[str]:
    return BASE_ROOT_FILES + [config["root_release_notes"]]


def research_files(config: dict[str, str]) -> list[str]:
    return BASE_RESEARCH_FILES + [config["research_release_notes"]]


def copy_file(
    repo_root: Path,
    release_root: Path,
    relative_path: str,
    release_relative_path: str | None = None,
) -> None:
    source = repo_root / relative_path
    if not source.is_file() and release_relative_path is not None:
        fallback_source = repo_root / release_relative_path
        if fallback_source.is_file():
            source = fallback_source
    if not source.is_file():
        raise FileNotFoundError(f"Missing release file: {relative_path}")
    target = release_root / (release_relative_path or relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def ignore_release_noise(_: str, names: list[str]) -> set[str]:
    ignored = {name for name in names if name in EXCLUDED_DIR_NAMES}
    ignored.update(name for name in names if name == ".DS_Store")
    ignored.update(name for name in names if name.endswith((".zip", ".tar", ".tar.gz", ".tgz")))
    return ignored


def copy_dir(repo_root: Path, release_root: Path, relative_path: str) -> None:
    source = repo_root / relative_path
    if not source.is_dir():
        raise FileNotFoundError(f"Missing release directory: {relative_path}")
    target = release_root / relative_path
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=ignore_release_noise)


def build_release(repo_root: Path, output_dir: Path, version: str | None = None) -> Path:
    config = load_release_config(repo_root)
    require_matching_version(config, version)
    release_root = output_dir / config["bundle_name"]
    if release_root.exists():
        shutil.rmtree(release_root)
    release_root.mkdir(parents=True)

    for source_path, release_path in ROOT_FILE_MAP:
        copy_file(repo_root, release_root, source_path, release_path)
    for relative_path in root_files(config) + research_files(config):
        copy_file(repo_root, release_root, relative_path)
    for relative_path in RESEARCH_DIRS:
        copy_dir(repo_root, release_root, relative_path)

    return release_root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        help="Release version. If set, it must match release/public/release_config.json.",
    )
    parser.add_argument("--out", required=True, type=Path, help="Output parent directory")
    parser.add_argument("--zip", action="store_true", help="Also create a .zip archive beside the bundle")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    try:
        release_root = build_release(repo_root, args.out.resolve(), args.version)
    except ValueError as error:
        print(f"FAIL: {error}")
        return 1
    print(release_root)
    if args.zip:
        archive_base = release_root
        existing_archive = archive_base.parent / f"{archive_base.name}.zip"
        if existing_archive.exists():
            existing_archive.unlink()
        archive_path = shutil.make_archive(str(archive_base), "zip", release_root.parent, release_root.name)
        print(archive_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
