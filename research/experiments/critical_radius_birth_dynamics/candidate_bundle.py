#!/usr/bin/env python3
"""Build or check the internal PRC v2.3 candidate bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from typing import Any
from pathlib import Path, PurePosixPath


EXPERIMENT_REL = "research/experiments/critical_radius_birth_dynamics"
MANIFEST_REL = f"{EXPERIMENT_REL}/candidate_bundle_manifest_v0_1.json"
DEFAULT_OUTPUT_PARENT = Path(tempfile.gettempdir()) / "prc-v2.3-candidate-latest"
LATEST_PATHS_FILE = "LATEST_CANDIDATE_PATHS.txt"
LATEST_LINKS_FILE = "LATEST_CANDIDATE_LINKS.md"
HASH_MANIFEST_FILE = "SHA256SUMS"
BUNDLE_FILE_MANIFEST = "BUNDLE_FILE_MANIFEST.txt"
CANDIDATE_NAME_PREFIX = "PrimeClock-v2.3-candidate-"
CANDIDATE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

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
CHECK_IGNORED_DIR_NAMES = {
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
}
CHECK_IGNORED_DIR_SUFFIXES = (
    ".dist-info",
    ".egg-info",
)
CHECK_TEXT_IGNORED_FILE_PATTERNS = (
    re.compile(r"candidate_workflow_.*\.ya?ml$"),
)

FORBIDDEN_PATH_MARKERS = {
    "AGENTS",
    "no_multigap",
    "prc_no_multigap",
    "prc_v2_4",
    "private_notes",
    "review_packages",
    "scratch",
}

def term(*parts: str) -> str:
    return "".join(parts)


FORBIDDEN_TEXT_MARKERS = {
    term("Release eligibility: excluded from v2.3 ", "candidate bundle until promoted"),
    term("Status: ", "future-work"),
}


FORBIDDEN_TEXT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        rf"\b{term('Chat', 'GPT')}\b",
        rf"\b{term('L', 'LM')}\b",
        rf"\b{term('A', 'I')}\b",
        rf"\b{term('pro', 'mpt')}\b",
        rf"\b{term('review ', 'package')}\b",
        rf"\b{term('generated-', 'review')}\b",
    ]
]


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
    ignored.update(name for name in names if is_generated_metadata_dir(name))
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


def path_is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def validate_bundle_name(name: str) -> str:
    if not name:
        raise ValueError("bundle name must not be empty")
    candidate = Path(name)
    if candidate.is_absolute() or candidate.name != name or name in {".", ".."}:
        raise ValueError(f"unsafe bundle name: {name!r}")
    if "/" in name or "\\" in name or ".." in candidate.parts:
        raise ValueError(f"unsafe bundle name: {name!r}")
    if not CANDIDATE_NAME_PATTERN.fullmatch(name):
        raise ValueError(f"unsafe bundle name: {name!r}")
    if not name.startswith(CANDIDATE_NAME_PREFIX):
        raise ValueError(
            f"bundle name must start with {CANDIDATE_NAME_PREFIX!r}: {name!r}"
        )
    return name


def ensure_existing_target_can_be_replaced(bundle_root: Path) -> None:
    if not bundle_root.exists():
        return
    if not bundle_root.is_dir():
        raise FileExistsError(f"refusing to replace non-directory: {bundle_root}")
    if any(bundle_root.iterdir()) and not (bundle_root / BUNDLE_FILE_MANIFEST).is_file():
        raise FileExistsError(
            "refusing to replace existing non-candidate directory without "
            f"{BUNDLE_FILE_MANIFEST}: {bundle_root}"
        )


def build_bundle(
    source_root: Path,
    output_parent: Path,
    name: str,
    manifest: dict[str, Any],
) -> Path:
    safe_name = validate_bundle_name(name)
    output_parent = output_parent.resolve()
    output_parent.mkdir(parents=True, exist_ok=True)
    bundle_root = (output_parent / safe_name).resolve()
    if not path_is_relative_to(bundle_root, output_parent):
        raise ValueError(f"unsafe output path: {bundle_root}")
    if bundle_root.exists():
        ensure_existing_target_can_be_replaced(bundle_root)
        shutil.rmtree(bundle_root)
    bundle_root.mkdir(parents=True)

    for entry in manifest["root_file_map"]:
        copy_file(source_root, bundle_root, entry["source"], entry["target"])
    for relative_path in manifest["root_files"] + manifest["research_files"]:
        copy_file(source_root, bundle_root, relative_path)
    for relative_dir in manifest["research_dirs"]:
        copy_dir(source_root, bundle_root, relative_dir)

    write_bundle_file_manifest(bundle_root)
    write_hash_manifest(bundle_root)
    return bundle_root


def sha256_bytes(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_generated_metadata_dir(name: str) -> bool:
    return name.endswith(CHECK_IGNORED_DIR_SUFFIXES)


def should_ignore_check_path(relative: Path) -> bool:
    return any(
        part in CHECK_IGNORED_DIR_NAMES or is_generated_metadata_dir(part)
        for part in relative.parts
    )


def bundle_files(bundle_root: Path, *, include_bundle_manifest: bool = True) -> list[Path]:
    files = []
    for path in bundle_root.rglob("*"):
        if not path.is_file() or path.name == HASH_MANIFEST_FILE:
            continue
        if not include_bundle_manifest and path.name == BUNDLE_FILE_MANIFEST:
            continue
        relative = path.relative_to(bundle_root)
        if any(
            part in EXCLUDED_DIR_NAMES or is_generated_metadata_dir(part)
            for part in relative.parts
        ):
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(bundle_root).as_posix())


def write_bundle_file_manifest(bundle_root: Path) -> None:
    lines = [
        path.relative_to(bundle_root).as_posix()
        for path in bundle_files(bundle_root, include_bundle_manifest=False)
    ]
    (bundle_root / BUNDLE_FILE_MANIFEST).write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def forbidden_bundle_paths(bundle_root: Path) -> list[str]:
    failures: list[str] = []
    for path in bundle_root.rglob("*"):
        relative = path.relative_to(bundle_root)
        if should_ignore_check_path(relative):
            continue
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


def forbidden_bundle_text(bundle_root: Path) -> list[str]:
    failures: list[str] = []
    for path in bundle_root.rglob("*"):
        relative_path = path.relative_to(bundle_root)
        if should_ignore_check_path(relative_path):
            continue
        if not path.is_file() or path.suffix not in {
            ".json",
            ".md",
            ".py",
            ".txt",
            ".yaml",
            ".yml",
        }:
            continue
        if any(pattern.fullmatch(path.name) for pattern in CHECK_TEXT_IGNORED_FILE_PATTERNS):
            continue
        relative = relative_path.as_posix()
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_TEXT_MARKERS:
            if marker in text:
                failures.append(f"forbidden candidate text marker {marker}: {relative}")
        for pattern in FORBIDDEN_TEXT_PATTERNS:
            match = pattern.search(text)
            if match:
                failures.append(
                    "process/private wording is not allowed in candidate artifacts: "
                    f"{match.group(0)!r} in {relative}"
                )
    return failures


def write_hash_manifest(bundle_root: Path) -> None:
    lines = [
        f"{sha256_bytes(path)}  {path.relative_to(bundle_root).as_posix()}"
        for path in bundle_files(bundle_root)
    ]
    (bundle_root / HASH_MANIFEST_FILE).write_text("\n".join(lines) + "\n", encoding="utf-8")


def resolve_manifest_path(
    bundle_root: Path,
    raw_relative_path: str,
    manifest_name: str,
    line_number: int,
    failures: list[str],
) -> tuple[str, Path] | None:
    relative_path = raw_relative_path.strip()
    if not relative_path:
        return None
    if "\\" in relative_path:
        failures.append(
            f"unsafe {manifest_name} path on line {line_number}: {relative_path}"
        )
        return None
    pure_path = PurePosixPath(relative_path)
    if pure_path.is_absolute() or any(part in {"", ".", ".."} for part in pure_path.parts):
        failures.append(
            f"unsafe {manifest_name} path on line {line_number}: {relative_path}"
        )
        return None
    target = (bundle_root / Path(*pure_path.parts)).resolve()
    resolved_root = bundle_root.resolve()
    if not path_is_relative_to(target, resolved_root):
        failures.append(
            f"unsafe {manifest_name} path on line {line_number}: {relative_path}"
        )
        return None
    return pure_path.as_posix(), target


def write_zip(bundle_root: Path) -> Path:
    zip_path = bundle_root.parent / f"{bundle_root.name}.zip"
    if zip_path.exists():
        zip_path.unlink()
    archive_root = Path(bundle_root.name)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in bundle_files(bundle_root) + [bundle_root / HASH_MANIFEST_FILE]:
            archive.write(
                path,
                (archive_root / path.relative_to(bundle_root)).as_posix(),
            )
    return zip_path


def write_latest_paths(
    output_parent: Path,
    bundle_root: Path,
    zip_path: Path | None,
) -> tuple[Path, Path]:
    latest_path = output_parent / LATEST_PATHS_FILE
    lines = [
        f"candidate package directory: {bundle_root}",
        f"candidate ZIP: {zip_path if zip_path else 'not generated'}",
    ]
    latest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    links_path = output_parent / LATEST_LINKS_FILE
    link_lines = [
        "# PRC v2.3 Candidate Links",
        "",
        f"- [Candidate package directory]({bundle_root})",
        (
            f"- [Candidate ZIP]({zip_path})"
            if zip_path
            else "- Candidate ZIP: not generated"
        ),
        f"- [Plain path note]({latest_path})",
    ]
    links_path.write_text("\n".join(link_lines) + "\n", encoding="utf-8")
    return latest_path, links_path


def check_bundle(bundle_root: Path, manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = forbidden_bundle_paths(bundle_root) + forbidden_bundle_text(bundle_root)
    readme = bundle_root / "README.md"
    if not readme.is_file():
        failures.append("missing README.md")
    else:
        text = readme.read_text(encoding="utf-8")
        for required in manifest["required_readme_phrases"]:
            if required not in text:
                failures.append(f"README.md missing required text: {required}")

    file_manifest = bundle_root / BUNDLE_FILE_MANIFEST
    expected_payload_paths: set[str] = set()
    if not file_manifest.is_file():
        failures.append(f"missing {BUNDLE_FILE_MANIFEST}")
    else:
        for line_number, line in enumerate(
            file_manifest.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            resolved = resolve_manifest_path(
                bundle_root,
                line,
                BUNDLE_FILE_MANIFEST,
                line_number,
                failures,
            )
            if resolved is None:
                continue
            relative_path, _ = resolved
            if relative_path in {HASH_MANIFEST_FILE, BUNDLE_FILE_MANIFEST}:
                failures.append(
                    f"invalid {BUNDLE_FILE_MANIFEST} line {line_number}: {relative_path}"
                )
                continue
            if relative_path in expected_payload_paths:
                failures.append(
                    f"duplicate {BUNDLE_FILE_MANIFEST} path on line {line_number}: "
                    f"{relative_path}"
                )
                continue
            expected_payload_paths.add(relative_path)

        actual_payload_paths = {
            path.relative_to(bundle_root).as_posix()
            for path in bundle_files(bundle_root, include_bundle_manifest=False)
        }
        for relative_path in sorted(expected_payload_paths - actual_payload_paths):
            failures.append(f"missing bundle file: {relative_path}")
        for relative_path in sorted(actual_payload_paths - expected_payload_paths):
            failures.append(f"unexpected bundle file: {relative_path}")

    hash_manifest = bundle_root / HASH_MANIFEST_FILE
    if not hash_manifest.is_file():
        failures.append(f"missing {HASH_MANIFEST_FILE}")
        return failures

    seen_paths: set[str] = set()
    for line_number, line in enumerate(
        hash_manifest.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        try:
            expected, relative_path = line.split("  ", 1)
        except ValueError:
            failures.append(f"invalid {HASH_MANIFEST_FILE} line {line_number}: {line!r}")
            continue
        if relative_path == HASH_MANIFEST_FILE:
            failures.append(f"{HASH_MANIFEST_FILE} must not hash itself")
            continue
        if relative_path in seen_paths:
            failures.append(f"duplicate {HASH_MANIFEST_FILE} path: {relative_path}")
            continue
        resolved = resolve_manifest_path(
            bundle_root,
            relative_path,
            HASH_MANIFEST_FILE,
            line_number,
            failures,
        )
        if resolved is None:
            continue
        relative_path, target = resolved
        if not target.is_file():
            failures.append(f"missing hashed file: {relative_path}")
            continue
        seen_paths.add(relative_path)
        actual = sha256_bytes(target)
        if actual != expected:
            failures.append(f"hash mismatch for {relative_path}")

    expected_hash_paths = {
        path.relative_to(bundle_root).as_posix()
        for path in bundle_files(bundle_root)
    }
    for relative_path in sorted(seen_paths - expected_hash_paths):
        failures.append(f"unexpected hashed file: {relative_path}")
    for path in bundle_files(bundle_root):
        relative_path = path.relative_to(bundle_root).as_posix()
        if relative_path not in seen_paths:
            failures.append(f"file missing from {HASH_MANIFEST_FILE}: {relative_path}")
    return failures


def main() -> int:
    source_root = repo_root()
    manifest = load_manifest(source_root)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUTPUT_PARENT,
        help=f"output parent directory (default: {DEFAULT_OUTPUT_PARENT})",
    )
    parser.add_argument("--name", default=manifest["default_name"])
    parser.add_argument("--zip", action="store_true", help="also write a ZIP next to the bundle")
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

    output_parent = args.out.resolve()
    try:
        bundle_root = build_bundle(source_root, output_parent, args.name, manifest)
    except (FileExistsError, ValueError) as error:
        print(f"FAIL: {error}")
        return 1
    zip_path = None
    if args.zip:
        zip_path = write_zip(bundle_root)
    latest_path, links_path = write_latest_paths(output_parent, bundle_root, zip_path)
    print(f"candidate package directory: {bundle_root}")
    print(f"candidate ZIP: {zip_path if zip_path else 'not generated'}")
    print(f"latest path note: {latest_path}")
    print(f"codex links note: {links_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
