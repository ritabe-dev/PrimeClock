#!/usr/bin/env python3
"""Check that a generated public release bundle stays clean."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


def term(*parts: str) -> str:
    return "".join(parts)


FORBIDDEN_PATH_PARTS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".matplotlib-cache",
    ".uv-cache",
    ".venv",
    "__pycache__",
    term("CSV_", "SUMMARY.md"),
    term("PRO", "MPT.md"),
    "dist",
    "local_notes",
    "node_modules",
    "private_notes",
    "review_packages",
    "scratch",
}

FORBIDDEN_PATH_PREFIXES = {
    "research/experiments/",
}

FORBIDDEN_FILENAME_PARTS = {
    "candidate_bundle",
    "candidate_bundle_manifest",
}

FORBIDDEN_TEXT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        rf"\b{term('PRO', 'MPT')}\.md\b",
        rf"\b{term('CSV_', 'SUMMARY')}\.md\b",
        rf"\b{term('review ', 'package')}\b",
        rf"\b{term('Suggested Review ', 'Prompt')}\b",
        rf"\b{term('Chat', 'GPT')}\b",
        rf"\b{term('Co', 'dex')}\b",
        rf"\b{term('Clau', 'de')}\b",
        rf"\b{term('Co', 'pilot')}\b",
        rf"\b{term('L', 'LM')}\b",
        rf"\b{term('large language ', 'model')}\b",
        rf"\b{term('language ', 'model')}\b",
    ]
]

TEXT_SUFFIXES = {
    ".cff",
    ".csv",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yml",
    ".yaml",
}

README_REQUIRED_TEXT = [
    "public release bundle",
    "finite `C_k/C_4/B_5`",
    "not included",
]

README_FORBIDDEN_TEXT = [
    "This source repository contains",
    "historical PrimeClock React/Vite visualization and the current",
    "The historical PrimeClock React/Vite visualization is not included",
    "PrimeClock Development Repository",
    "working tree for PrimeClock",
]


def sha256_bytes(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_text_file(path: Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name in {"LICENSE"}


def forbidden_path_reason(path: Path) -> str | None:
    if any(part in FORBIDDEN_PATH_PARTS for part in path.parts):
        return "path component"
    relative_path = path.as_posix()
    if any(relative_path.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES):
        return "path prefix"
    if any(part in path.name for part in FORBIDDEN_FILENAME_PARTS):
        return "filename"
    return None


def has_forbidden_path(path: Path) -> bool:
    return forbidden_path_reason(path) is not None


def check_paths(root: Path) -> list[str]:
    failures: list[str] = []
    for path in root.rglob("*"):
        relative_path = path.relative_to(root)
        if path.name == ".DS_Store":
            failures.append(f"forbidden local metadata file: {relative_path}")
        reason = forbidden_path_reason(relative_path)
        if reason:
            failures.append(f"forbidden {reason}: {relative_path}")
        if path.suffix in {".zip", ".tar", ".tgz"} or path.name.endswith(".tar.gz"):
            failures.append(f"forbidden archive file: {relative_path}")
    return failures


def check_text(root: Path) -> list[str]:
    failures: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or not is_text_file(path):
            continue
        if has_forbidden_path(path.relative_to(root)):
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_TEXT_PATTERNS:
            match = pattern.search(text)
            if match:
                failures.append(
                    f"forbidden text {match.group(0)!r} in {path.relative_to(root)}"
                )
    return failures


def check_hashes(root: Path) -> list[str]:
    manifest = root / "SHA256SUMS"
    if not manifest.is_file():
        return ["missing SHA256SUMS"]

    failures: list[str] = []
    seen_paths: set[str] = set()
    for line_number, line in enumerate(
        manifest.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        try:
            expected_hash, relative_path = line.split("  ", 1)
        except ValueError:
            failures.append(f"invalid SHA256SUMS line {line_number}: {line!r}")
            continue
        if not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            failures.append(f"invalid SHA256 on line {line_number}: {expected_hash!r}")
            continue
        if relative_path == "SHA256SUMS" or relative_path.startswith("../"):
            failures.append(f"invalid manifest path on line {line_number}: {relative_path!r}")
            continue

        target = root / relative_path
        if not target.is_file():
            failures.append(f"missing hashed file: {relative_path}")
            continue
        seen_paths.add(relative_path)
        actual_hash = sha256_bytes(target)
        if actual_hash != expected_hash:
            failures.append(
                f"hash mismatch for {relative_path}: expected {expected_hash}, got {actual_hash}"
            )

    for path in root.rglob("*"):
        if not path.is_file() or path.name == "SHA256SUMS":
            continue
        relative_path = path.relative_to(root).as_posix()
        if relative_path not in seen_paths:
            failures.append(f"file missing from SHA256SUMS: {relative_path}")
    return failures


def check_readme_guard(root: Path) -> list[str]:
    readme = root / "README.md"
    if not readme.is_file():
        return ["missing root README.md"]

    text = readme.read_text(encoding="utf-8")
    failures: list[str] = []
    for required in README_REQUIRED_TEXT:
        if required not in text:
            failures.append(f"root README.md missing required public-bundle text: {required!r}")
    for forbidden in README_FORBIDDEN_TEXT:
        if forbidden in text:
            failures.append(f"root README.md contains source-repository text: {forbidden!r}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release_root", type=Path)
    args = parser.parse_args()

    release_root = args.release_root.resolve()
    if not release_root.is_dir():
        raise SystemExit(f"Not a directory: {release_root}")

    failures = (
        check_paths(release_root)
        + check_text(release_root)
        + check_readme_guard(release_root)
        + check_hashes(release_root)
    )
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"OK: {release_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
