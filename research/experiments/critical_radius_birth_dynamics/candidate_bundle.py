#!/usr/bin/env python3
"""Build or check an internal PRC candidate bundle."""

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
V2_5_CANDIDATE_MANIFEST_REL = (
    f"{EXPERIMENT_REL}/candidate_bundle_manifest_v2_5_v0_1.json"
)
V2_5_PUBLIC_THEOREM_MANIFEST_REL = (
    f"{EXPERIMENT_REL}/public_theorem_manifest_v2_5_v0_1.json"
)
V2_5_PUBLIC_THEOREM_RELEASE_MANIFEST_REL = (
    f"{EXPERIMENT_REL}/public_theorem_release_manifest_v2_5_v1_0.json"
)
V2_6_GATE_C_CANDIDATE_MANIFEST_REL = (
    f"{EXPERIMENT_REL}/gate_c_candidate_bundle_manifest_v2_6_v0_1.json"
)
V2_7_GATE_C_CANDIDATE_MANIFEST_REL = (
    f"{EXPERIMENT_REL}/gate_c_candidate_bundle_manifest_v2_7_v0_1.json"
)
V2_7_PUBLIC_THEOREM_PREFLIGHT_MANIFEST_REL = (
    f"{EXPERIMENT_REL}/public_theorem_preflight_bundle_manifest_v2_7_v1_0.json"
)
V2_7_PUBLIC_THEOREM_RELEASE_MANIFEST_REL = (
    f"{EXPERIMENT_REL}/public_theorem_release_manifest_v2_7_v1_0.json"
)
PROFILE_DEFAULTS = {
    "v2_5_candidate": {
        "manifest": V2_5_CANDIDATE_MANIFEST_REL,
        "output_parent": Path(tempfile.gettempdir()) / "primeclock-v25-candidate-latest",
    },
    "v2_5_public_theorem": {
        "manifest": V2_5_PUBLIC_THEOREM_MANIFEST_REL,
        "output_parent": Path(tempfile.gettempdir()) / "primeclock-v25-public-theorem-review",
    },
    "v2_5_public_theorem_release": {
        "manifest": V2_5_PUBLIC_THEOREM_RELEASE_MANIFEST_REL,
        "output_parent": Path(tempfile.gettempdir()) / "primeclock-v25-public-theorem-release",
    },
    "v2_6_gate_c_candidate": {
        "manifest": V2_6_GATE_C_CANDIDATE_MANIFEST_REL,
        "output_parent": Path(tempfile.gettempdir()) / "primeclock-v26-gate-c-candidate",
    },
    "v2_7_gate_c_candidate": {
        "manifest": V2_7_GATE_C_CANDIDATE_MANIFEST_REL,
        "output_parent": Path(tempfile.gettempdir()) / "primeclock-v27-gate-c-candidate",
    },
    "v2_7_public_theorem_preflight": {
        "manifest": V2_7_PUBLIC_THEOREM_PREFLIGHT_MANIFEST_REL,
        "output_parent": Path(tempfile.gettempdir()) / "primeclock-v27-public-theorem-preflight",
    },
    "v2_7_public_theorem_release": {
        "manifest": V2_7_PUBLIC_THEOREM_RELEASE_MANIFEST_REL,
        "output_parent": Path(tempfile.gettempdir()) / "primeclock-v271-public-theorem-release",
    },
}
LATEST_PATHS_FILE = "LATEST_CANDIDATE_PATHS.txt"
LATEST_LINKS_FILE = "LATEST_CANDIDATE_LINKS.md"
HASH_MANIFEST_FILE = "SHA256SUMS"
BUNDLE_FILE_MANIFEST = "BUNDLE_FILE_MANIFEST.txt"
DETERMINISTIC_ZIP_DATETIME = (1980, 1, 1, 0, 0, 0)
DETERMINISTIC_FILE_MODE = 0o644 << 16
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
    ".git",
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
    "candidate_workflow_v2_4",
    "candidate_workflow_v2_5",
    "check_v2_4",
    "check_v2_5",
    "no_multigap",
    "prc_no_multigap",
    "prc_v2_4",
    "prc_v2_5",
    "v2_4",
    "v2_5",
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


def load_manifest(source_root: Path, manifest_path: str | Path = MANIFEST_REL) -> dict[str, Any]:
    raw_path = Path(manifest_path)
    path = raw_path if raw_path.is_absolute() else source_root / raw_path
    with path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    failures = validate_manifest_schema(manifest)
    if failures:
        raise ValueError("; ".join(failures))
    return manifest


def validate_manifest_schema(manifest: object) -> list[str]:
    if not isinstance(manifest, dict):
        return ["bundle manifest must be a JSON object"]
    failures: list[str] = []
    required = {
        "id": str,
        "default_name": str,
        "root_file_map": list,
        "root_files": list,
        "research_files": list,
        "research_dirs": list,
        "required_readme_phrases": list,
    }
    for key, expected_type in required.items():
        if key not in manifest:
            failures.append(f"bundle manifest missing required key: {key}")
        elif not isinstance(manifest[key], expected_type):
            failures.append(f"bundle manifest key {key} must be {expected_type.__name__}")
    return failures


def missing_manifest_hint(manifest_path: str | Path) -> str:
    gate_c_label = term("Gate", " C")
    return (
        f"missing candidate manifest: {manifest_path}. "
        "For v2.5, pass --profile v2_5_candidate, "
        "--profile v2_5_public_theorem, --profile v2_5_public_theorem_release, "
        "for v2.7, pass --profile v2_7_public_theorem_preflight or "
        "--profile v2_7_public_theorem_release, "
        f"for later {gate_c_label} candidates pass the matching gate-c profile, "
        "or an explicit --manifest path."
    )


def resolve_bundle_relative_path(
    relative_path: str,
    *,
    field_name: str,
) -> Path:
    if "\\" in relative_path:
        raise ValueError(f"unsafe {field_name} path: {relative_path!r}")
    pure_path = PurePosixPath(relative_path)
    if pure_path.is_absolute() or any(part in {"", ".", ".."} for part in pure_path.parts):
        raise ValueError(f"unsafe {field_name} path: {relative_path!r}")
    return Path(*pure_path.parts)


def resolve_source_path(source_root: Path, relative_path: str, *, field_name: str) -> Path:
    relative = resolve_bundle_relative_path(relative_path, field_name=field_name)
    source = (source_root / relative).resolve()
    if not path_is_relative_to(source, source_root.resolve()):
        raise ValueError(f"unsafe {field_name} path outside source root: {relative_path!r}")
    return source


def resolve_target_path(bundle_root: Path, relative_path: str, *, field_name: str) -> Path:
    relative = resolve_bundle_relative_path(relative_path, field_name=field_name)
    target = (bundle_root / relative).resolve()
    if not path_is_relative_to(target, bundle_root.resolve()):
        raise ValueError(f"unsafe {field_name} path outside bundle root: {relative_path!r}")
    return target


def copy_file(
    source_root: Path,
    bundle_root: Path,
    source_relative_path: str,
    bundle_relative_path: str | None = None,
) -> None:
    source = resolve_source_path(source_root, source_relative_path, field_name="source")
    if not source.is_file():
        raise FileNotFoundError(f"Missing candidate file: {source_relative_path}")
    target = resolve_target_path(
        bundle_root,
        bundle_relative_path or source_relative_path,
        field_name="target",
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def ignore_noise(_: str, names: list[str]) -> set[str]:
    ignored = {name for name in names if name in EXCLUDED_DIR_NAMES}
    ignored.update(name for name in names if is_generated_metadata_dir(name))
    ignored.update(name for name in names if name == ".DS_Store")
    ignored.update(name for name in names if name.endswith((".zip", ".tar", ".tar.gz", ".tgz")))
    return ignored


def copy_dir(source_root: Path, bundle_root: Path, relative_path: str) -> None:
    source = resolve_source_path(source_root, relative_path, field_name="source directory")
    if not source.is_dir():
        raise FileNotFoundError(f"Missing candidate directory: {relative_path}")
    target = resolve_target_path(bundle_root, relative_path, field_name="target directory")
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


def candidate_name_prefix(manifest: dict[str, Any]) -> str:
    return str(manifest.get("candidate_name_prefix", CANDIDATE_NAME_PREFIX))


def validate_bundle_name(name: str, *, prefix: str = CANDIDATE_NAME_PREFIX) -> str:
    if not name:
        raise ValueError("bundle name must not be empty")
    candidate = Path(name)
    if candidate.is_absolute() or candidate.name != name or name in {".", ".."}:
        raise ValueError(f"unsafe bundle name: {name!r}")
    if "/" in name or "\\" in name or ".." in candidate.parts:
        raise ValueError(f"unsafe bundle name: {name!r}")
    if not CANDIDATE_NAME_PATTERN.fullmatch(name):
        raise ValueError(f"unsafe bundle name: {name!r}")
    if not name.startswith(prefix):
        raise ValueError(f"bundle name must start with {prefix!r}: {name!r}")
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
    safe_name = validate_bundle_name(name, prefix=candidate_name_prefix(manifest))
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


def effective_forbidden_path_markers(manifest: dict[str, Any]) -> set[str]:
    markers = set(FORBIDDEN_PATH_MARKERS)
    markers.difference_update(manifest.get("allowed_path_markers", []))
    markers.update(manifest.get("forbidden_path_markers", []))
    return markers


def forbidden_bundle_paths(bundle_root: Path, manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    forbidden_markers = effective_forbidden_path_markers(manifest)
    for path in bundle_root.rglob("*"):
        relative = path.relative_to(bundle_root)
        if should_ignore_check_path(relative):
            continue
        relative_text = relative.as_posix()
        if path.name == ".DS_Store":
            failures.append(f"forbidden local metadata file: {relative_text}")
            continue
        for marker in sorted(forbidden_markers, key=lambda value: (-len(value), value)):
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


def effective_forbidden_text_markers(manifest: dict[str, Any]) -> set[str]:
    markers = set(FORBIDDEN_TEXT_MARKERS)
    markers.difference_update(manifest.get("allowed_text_markers", []))
    markers.update(manifest.get("forbidden_text_markers", []))
    return markers


def forbidden_bundle_text(bundle_root: Path, manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    forbidden_markers = effective_forbidden_text_markers(manifest)
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
        for marker in forbidden_markers:
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
            arcname = (archive_root / path.relative_to(bundle_root)).as_posix()
            info = zipfile.ZipInfo(arcname)
            info.date_time = DETERMINISTIC_ZIP_DATETIME
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = DETERMINISTIC_FILE_MODE
            archive.writestr(info, path.read_bytes())
    return zip_path


def write_latest_paths(
    output_parent: Path,
    bundle_root: Path,
    zip_path: Path | None,
    *,
    title: str = "PRC Candidate Links",
) -> tuple[Path, Path]:
    latest_path = output_parent / LATEST_PATHS_FILE
    lines = [
        f"candidate package directory: {bundle_root}",
        f"candidate ZIP: {zip_path if zip_path else 'not generated'}",
    ]
    latest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    links_path = output_parent / LATEST_LINKS_FILE
    link_lines = [
        f"# {title}",
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
    failures: list[str] = forbidden_bundle_paths(bundle_root, manifest)
    failures.extend(forbidden_bundle_text(bundle_root, manifest))
    failures.extend(check_root_file_map_pairs(bundle_root, manifest))
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
    failures.extend(check_profile_specific_bundle(bundle_root, manifest))
    return failures


def check_root_file_map_pairs(bundle_root: Path, manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for entry in manifest.get("root_file_map", []):
        source_relative = entry.get("source") if isinstance(entry, dict) else None
        target_relative = entry.get("target") if isinstance(entry, dict) else None
        if not isinstance(source_relative, str) or not isinstance(target_relative, str):
            failures.append("root_file_map entries must contain source and target paths")
            continue
        try:
            source = resolve_target_path(
                bundle_root,
                source_relative,
                field_name="root_file_map source",
            )
            target = resolve_target_path(
                bundle_root,
                target_relative,
                field_name="root_file_map target",
            )
        except ValueError as error:
            failures.append(str(error))
            continue
        if not source.is_file():
            failures.append(f"missing mapped source file: {source_relative}")
            continue
        if not target.is_file():
            failures.append(f"missing mapped target file: {target_relative}")
            continue
        if sha256_bytes(source) != sha256_bytes(target):
            failures.append(
                f"mapped target differs from source: {source_relative} -> {target_relative}"
            )
    return failures


def check_profile_specific_bundle(bundle_root: Path, manifest: dict[str, Any]) -> list[str]:
    if manifest.get("id") == "prc_v2_6_gate_c_candidate_bundle_v0_1":
        return check_v2_6_gate_c_candidate_bundle(bundle_root, manifest)
    if manifest.get("id") == "prc_v2_7_gate_c_candidate_bundle_v0_1":
        return check_v2_7_gate_c_candidate_bundle(bundle_root, manifest)
    if manifest.get("id") == "prc_v2_7_public_theorem_preflight_bundle_v1_0":
        return check_v2_7_public_theorem_preflight_bundle(bundle_root, manifest)
    if manifest.get("id") == "prc_v2_7_public_theorem_release_bundle_v1_0":
        return check_v2_7_public_theorem_release_bundle(bundle_root, manifest)
    return []


def check_v2_6_gate_c_candidate_bundle(
    bundle_root: Path,
    manifest: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    gate_c_label = term("Gate", " C")
    candidate_manifest_path = (
        bundle_root
        / "research/experiments/critical_radius_birth_dynamics/"
        "prc_v2_6_gate_c_candidate_manifest_v0_1.json"
    )
    if not candidate_manifest_path.is_file():
        failures.append(f"missing v2.6 {gate_c_label} candidate manifest")
        return failures
    try:
        candidate_manifest = json.loads(candidate_manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"invalid v2.6 {gate_c_label} candidate manifest: {exc}")
        return failures
    artifacts = candidate_manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        failures.append(f"v2.6 {gate_c_label} candidate manifest artifacts must be an object")
        return failures
    for key in (
        "canonical_note",
        "checker",
        "workflow",
        "bundle_builder",
        "bundle_manifest",
    ):
        relative_path = artifacts.get(key)
        if not isinstance(relative_path, str):
            failures.append(f"v2.6 {gate_c_label} candidate manifest artifact {key} must be a path")
            continue
        if not (bundle_root / relative_path).is_file():
            failures.append(
                f"v2.6 {gate_c_label} candidate manifest artifact missing: {relative_path}"
            )
    canonical_note = artifacts.get("canonical_note")
    if isinstance(canonical_note, str):
        canonical_path = bundle_root / canonical_note
        theorem_note = bundle_root / "THEOREM_NOTE.md"
        if canonical_path.is_file() and theorem_note.is_file():
            if sha256_bytes(canonical_path) != sha256_bytes(theorem_note):
                failures.append("THEOREM_NOTE.md does not match canonical note")
    return failures


def check_v2_7_gate_c_candidate_bundle(
    bundle_root: Path,
    manifest: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    gate_c_label = term("Gate", " C")
    candidate_manifest_path = (
        bundle_root
        / "research/experiments/critical_radius_birth_dynamics/"
        "prc_v2_7_gate_c_candidate_manifest_v0_1.json"
    )
    if not candidate_manifest_path.is_file():
        failures.append(f"missing v2.7 {gate_c_label} candidate manifest")
        return failures
    try:
        candidate_manifest = json.loads(candidate_manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"invalid v2.7 {gate_c_label} candidate manifest: {exc}")
        return failures
    artifacts = candidate_manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        failures.append(f"v2.7 {gate_c_label} candidate manifest artifacts must be an object")
        return failures
    for key in (
        "canonical_note",
        "theorem_checker",
        "exact_audit",
        "gate_c_checker",
        "workflow",
        "bundle_builder",
        "bundle_manifest",
        "support_csv",
    ):
        relative_path = artifacts.get(key)
        if not isinstance(relative_path, str):
            failures.append(f"v2.7 {gate_c_label} candidate manifest artifact {key} must be a path")
            continue
        if not (bundle_root / relative_path).is_file():
            failures.append(
                f"v2.7 {gate_c_label} candidate manifest artifact missing: {relative_path}"
            )
    canonical_note = artifacts.get("canonical_note")
    if isinstance(canonical_note, str):
        canonical_path = bundle_root / canonical_note
        theorem_note = bundle_root / "THEOREM_NOTE.md"
        if canonical_path.is_file() and theorem_note.is_file():
            if sha256_bytes(canonical_path) != sha256_bytes(theorem_note):
                failures.append("THEOREM_NOTE.md does not match canonical note")
    return failures


def check_v2_7_public_theorem_preflight_bundle(
    bundle_root: Path,
    manifest: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    public_manifest_path = (
        bundle_root
        / "research/experiments/critical_radius_birth_dynamics/"
        "public_theorem_preflight_manifest_v2_7_v1_0.json"
    )
    if not public_manifest_path.is_file():
        failures.append("missing v2.7 public theorem preflight manifest")
        return failures
    try:
        public_manifest = json.loads(public_manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"invalid v2.7 public theorem preflight manifest: {exc}")
        return failures
    if public_manifest.get("doi_state") != "not_assigned":
        failures.append("v2.7 public theorem preflight manifest doi_state must be not_assigned")
    if public_manifest.get("github_release_url"):
        failures.append("v2.7 public theorem preflight manifest must not set GitHub Release URL")
    if public_manifest.get("zenodo_version_doi"):
        failures.append("v2.7 public theorem preflight manifest must not set Zenodo version DOI")

    canonical_note = (
        bundle_root
        / "research/experiments/critical_radius_birth_dynamics/"
        "notes/prc_v2_7_general_single_gap_aperture_theorem_note_v0_1.md"
    )
    theorem_note = bundle_root / "THEOREM_NOTE.md"
    if canonical_note.is_file() and theorem_note.is_file():
        if sha256_bytes(canonical_note) != sha256_bytes(theorem_note):
            failures.append("THEOREM_NOTE.md does not match canonical v2.7 theorem note")
    else:
        failures.append("missing canonical/root v2.7 theorem note pair")
    return failures


def check_v2_7_public_theorem_release_bundle(
    bundle_root: Path,
    manifest: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    public_manifest_path = (
        bundle_root
        / "research/experiments/critical_radius_birth_dynamics/"
        "public_theorem_release_manifest_v2_7_v1_0.json"
    )
    if not public_manifest_path.is_file():
        failures.append("missing v2.7 public theorem release manifest")
        return failures
    try:
        public_manifest = json.loads(public_manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"invalid v2.7 public theorem release manifest: {exc}")
        return failures
    if public_manifest.get("public_release") is not True:
        failures.append("v2.7 public theorem release manifest public_release must be true")
    if public_manifest.get("doi_state") != "not_assigned":
        failures.append("v2.7 public theorem release manifest doi_state must be not_assigned before DOI finalization")
    if public_manifest.get("zenodo_version_doi"):
        failures.append("v2.7 public theorem release manifest must not set Zenodo version DOI before finalization")
    if (bundle_root / "DRAFT_CITATION.cff").exists():
        failures.append("v2.7 public theorem release bundle must not include DRAFT_CITATION.cff")
    if not (bundle_root / "CITATION.cff").is_file():
        failures.append("v2.7 public theorem release bundle missing root CITATION.cff")

    canonical_note = (
        bundle_root
        / "research/experiments/critical_radius_birth_dynamics/"
        "notes/prc_v2_7_general_single_gap_aperture_theorem_note_v0_1.md"
    )
    theorem_note = bundle_root / "THEOREM_NOTE.md"
    if canonical_note.is_file() and theorem_note.is_file():
        if sha256_bytes(canonical_note) != sha256_bytes(theorem_note):
            failures.append("THEOREM_NOTE.md does not match canonical v2.7 theorem note")
    else:
        failures.append("missing canonical/root v2.7 theorem note pair")
    return failures


def main() -> int:
    source_root = repo_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILE_DEFAULTS),
        help=(
            "named bundle profile. Existing v2.3 defaults are used when this "
            "is omitted and --manifest is not supplied."
        ),
    )
    parser.add_argument(
        "--manifest",
        help=(
            "candidate manifest path, relative to repo root. Overrides "
            "--profile when supplied."
        ),
    )
    parser.add_argument(
        "--out",
        type=Path,
        help=(
            "output parent directory. Defaults to the selected profile output, "
            f"or {DEFAULT_OUTPUT_PARENT} for legacy v2.3."
        ),
    )
    parser.add_argument("--name")
    parser.add_argument("--zip", action="store_true", help="also write a ZIP next to the bundle")
    parser.add_argument("--check", type=Path, help="check an existing candidate bundle")
    args = parser.parse_args()
    profile = PROFILE_DEFAULTS.get(args.profile or "", {})
    manifest_path = args.manifest or profile.get("manifest", MANIFEST_REL)
    output_parent = (args.out or profile.get("output_parent", DEFAULT_OUTPUT_PARENT)).resolve()
    try:
        manifest = load_manifest(source_root, manifest_path)
    except FileNotFoundError:
        print(f"FAIL: {missing_manifest_hint(manifest_path)}")
        return 1
    except ValueError as error:
        print(f"FAIL: {error}")
        return 1
    name = args.name if args.name is not None else manifest["default_name"]

    if args.check:
        failures = check_bundle(args.check.resolve(), manifest)
        if failures:
            for failure in failures:
                print(f"FAIL: {failure}")
            return 1
        print(f"OK: {args.check.resolve()}")
        return 0

    try:
        bundle_root = build_bundle(source_root, output_parent, name, manifest)
    except (FileExistsError, ValueError) as error:
        print(f"FAIL: {error}")
        return 1
    zip_path = None
    if args.zip:
        zip_path = write_zip(bundle_root)
    latest_path, links_path = write_latest_paths(
        output_parent,
        bundle_root,
        zip_path,
        title=manifest.get("links_title", "PRC Candidate Links"),
    )
    print(f"candidate package directory: {bundle_root}")
    print(f"candidate ZIP: {zip_path if zip_path else 'not generated'}")
    print(f"latest path note: {latest_path}")
    print(f"links note: {links_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
