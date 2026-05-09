#!/usr/bin/env python3
"""Create or verify SHA256SUMS for the public release allowlist."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from build_public_release import (
    EXCLUDED_DIR_NAMES,
    RESEARCH_DIRS,
    RESEARCH_FILES,
    ROOT_FILE_MAP,
    ROOT_FILES,
)


HASH_MANIFEST = "SHA256SUMS"


def sha256_bytes(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_excluded_path(path: Path) -> bool:
    return any(part in EXCLUDED_DIR_NAMES for part in path.parts) or path.name == ".DS_Store"


def release_file_paths(repo_root: Path) -> list[tuple[str, str]]:
    paths: dict[str, str] = {}
    for source_path, release_path in ROOT_FILE_MAP:
        path = repo_root / source_path
        if not path.is_file():
            raise FileNotFoundError(f"Missing release file: {source_path}")
        paths[release_path] = source_path

    for relative_path in ROOT_FILES + RESEARCH_FILES:
        if relative_path == HASH_MANIFEST:
            continue
        path = repo_root / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"Missing release file: {relative_path}")
        paths[relative_path] = relative_path

    for relative_dir in RESEARCH_DIRS:
        root = repo_root / relative_dir
        if not root.is_dir():
            raise FileNotFoundError(f"Missing release directory: {relative_dir}")
        for path in root.rglob("*"):
            if not path.is_file() or is_excluded_path(path.relative_to(repo_root)):
                continue
            relative_path = path.relative_to(repo_root).as_posix()
            paths[relative_path] = relative_path
    return sorted(paths.items())


def render_manifest(repo_root: Path) -> str:
    lines = []
    for release_path, source_path in release_file_paths(repo_root):
        lines.append(f"{sha256_bytes(repo_root / source_path)}  {release_path}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if SHA256SUMS is not up to date instead of writing it",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    manifest_path = repo_root / HASH_MANIFEST
    expected = render_manifest(repo_root)
    if args.check:
        actual = manifest_path.read_text(encoding="utf-8") if manifest_path.exists() else ""
        if actual != expected:
            print(f"{HASH_MANIFEST} is not up to date")
            return 1
        print(f"{HASH_MANIFEST} is up to date")
        return 0

    manifest_path.write_text(expected, encoding="utf-8")
    print(f"Wrote {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
