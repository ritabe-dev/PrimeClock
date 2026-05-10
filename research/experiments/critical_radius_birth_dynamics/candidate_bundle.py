#!/usr/bin/env python3
"""Build or check the internal PRC v2.3 candidate bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from typing import Any
from pathlib import Path


EXPERIMENT_REL = "research/experiments/critical_radius_birth_dynamics"
MANIFEST_REL = f"{EXPERIMENT_REL}/candidate_bundle_manifest_v0_1.json"

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

FORBIDDEN_PATH_MARKERS = {
    "AGENTS",
    "no_multigap",
    "prc_no_multigap",
    "prc_v2_4",
    "private_notes",
    "review_packages",
    "scratch",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_manifest(source_root: Path) -> dict[str, Any]:
    path = source_root / MANIFEST_REL
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def copy_file(
    source_root: Path,
    bundle_root: Path,
    source_relative_path: str,
    bundle_relative_path: str | None = None,
) -> None:
    source = source_root / source_relative_path
    if not source.is_file():
        raise FileNotFoundError(f"Missing candidate file: {source_relative_path}")
    target = bundle_root / (bundle_relative_path or source_relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def ignore_noise(_: str, names: list[str]) -> set[str]:
    ignored = {name for name in names if name in EXCLUDED_DIR_NAMES}
    ignored.update(name for name in names if name == ".DS_Store")
    ignored.update(name for name in names if name.endswith((".zip", ".tar", ".tar.gz", ".tgz")))
    return ignored


def copy_dir(source_root: Path, bundle_root: Path, relative_path: str) -> None:
    source = source_root / relative_path
    if not source.is_dir():
        raise FileNotFoundError(f"Missing candidate directory: {relative_path}")
    target = bundle_root / relative_path
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=ignore_noise)


def build_bundle(
    source_root: Path,
    output_parent: Path,
    name: str,
    manifest: dict[str, Any],
) -> Path:
    bundle_root = output_parent / name
    if bundle_root.exists():
        shutil.rmtree(bundle_root)
    bundle_root.mkdir(parents=True)

    for entry in manifest["root_file_map"]:
        copy_file(source_root, bundle_root, entry["source"], entry["target"])
    for relative_path in manifest["root_files"] + manifest["research_files"]:
        copy_file(source_root, bundle_root, relative_path)
    for relative_dir in manifest["research_dirs"]:
        copy_dir(source_root, bundle_root, relative_dir)

    write_hash_manifest(bundle_root)
    return bundle_root


def sha256_bytes(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bundle_files(bundle_root: Path) -> list[Path]:
    files = []
    for path in bundle_root.rglob("*"):
        if not path.is_file() or path.name == "SHA256SUMS":
            continue
        relative = path.relative_to(bundle_root)
        if any(part in EXCLUDED_DIR_NAMES for part in relative.parts):
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(bundle_root).as_posix())


def forbidden_bundle_paths(bundle_root: Path) -> list[str]:
    failures: list[str] = []
    for path in bundle_root.rglob("*"):
        relative = path.relative_to(bundle_root)
        relative_text = relative.as_posix()
        if path.name == ".DS_Store":
            failures.append(f"forbidden local metadata file: {relative_text}")
            continue
        for marker in FORBIDDEN_PATH_MARKERS:
            if marker in relative_text:
                failures.append(f"forbidden candidate path marker {marker}: {relative_text}")
                break
        for part in relative.parts:
            if part in EXCLUDED_DIR_NAMES:
                failures.append(f"forbidden path component {part}: {relative_text}")
                break
        if path.is_file() and (
            path.suffix in {".zip", ".tar", ".tgz"} or path.name.endswith(".tar.gz")
        ):
            failures.append(f"forbidden archive file: {relative_text}")
    return failures


def write_hash_manifest(bundle_root: Path) -> None:
    lines = [
        f"{sha256_bytes(path)}  {path.relative_to(bundle_root).as_posix()}"
        for path in bundle_files(bundle_root)
    ]
    (bundle_root / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def check_bundle(bundle_root: Path, manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = forbidden_bundle_paths(bundle_root)
    readme = bundle_root / "README.md"
    if not readme.is_file():
        failures.append("missing README.md")
    else:
        text = readme.read_text(encoding="utf-8")
        for required in manifest["required_readme_phrases"]:
            if required not in text:
                failures.append(f"README.md missing required text: {required}")

    manifest = bundle_root / "SHA256SUMS"
    if not manifest.is_file():
        failures.append("missing SHA256SUMS")
        return failures

    seen_paths: set[str] = set()
    for line_number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            expected, relative_path = line.split("  ", 1)
        except ValueError:
            failures.append(f"invalid SHA256SUMS line {line_number}: {line!r}")
            continue
        target = bundle_root / relative_path
        if not target.is_file():
            failures.append(f"missing hashed file: {relative_path}")
            continue
        seen_paths.add(relative_path)
        actual = sha256_bytes(target)
        if actual != expected:
            failures.append(f"hash mismatch for {relative_path}")

    for path in bundle_files(bundle_root):
        relative_path = path.relative_to(bundle_root).as_posix()
        if relative_path not in seen_paths:
            failures.append(f"file missing from SHA256SUMS: {relative_path}")
    return failures


def main() -> int:
    source_root = repo_root()
    manifest = load_manifest(source_root)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="output parent directory")
    parser.add_argument("--name", default=manifest["default_name"])
    parser.add_argument("--check", type=Path, help="check an existing candidate bundle")
    args = parser.parse_args()

    if args.check:
        failures = check_bundle(args.check.resolve(), manifest)
        if failures:
            for failure in failures:
                print(f"FAIL: {failure}")
            return 1
        print(f"OK: {args.check.resolve()}")
        return 0

    if not args.out:
        raise SystemExit("--out is required unless --check is used")
    bundle_root = build_bundle(source_root, args.out.resolve(), args.name, manifest)
    print(bundle_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
