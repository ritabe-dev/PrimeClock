#!/usr/bin/env python3
"""Audit the v2.6 minimal Gate C candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
MANIFEST_REL = EXPERIMENT_REL / "prc_v2_6_gate_c_candidate_manifest_v0_1.json"
THEOREM_CHECKER_REL = EXPERIMENT_REL / "check_v2_6_single_gap_theorem_note_draft.py"
EXPECTED_ARTIFACTS = {
    "canonical_note": str(
        EXPERIMENT_REL / "notes/prc_v2_6_single_gap_theorem_note_draft_v0_1.md"
    ),
    "checker": str(THEOREM_CHECKER_REL),
    "workflow": str(EXPERIMENT_REL / "candidate_workflow_v2_6_v0_1.yml"),
    "bundle_builder": str(EXPERIMENT_REL / "candidate_bundle.py"),
    "bundle_manifest": str(
        EXPERIMENT_REL / "gate_c_candidate_bundle_manifest_v2_6_v0_1.json"
    ),
    "bundle_profile": "v2_6_gate_c_candidate",
    "bundle_name": "PrimeClock-v2.6-gate-c-candidate-v0.1",
}
REQUIRED_BOUNDARIES = (
    "not_public_release",
    "no_doi",
    "no_github_release",
    "no_registry_entry",
    "no_b8_theorem",
    "no_predictor",
    "no_asymptotic_law",
)
FORBIDDEN_MANIFEST_TEXT = (
    "release/public/release_registry.json",
    "zenodo",
    "doi_state",
    "github_release_url",
    "CITATION.cff",
)
FORBIDDEN_README_TEXT = (
    "Gate R",
    "Gate C",
    "Gate P",
    "v2.6",
    "support package",
)
REQUIRED_BUNDLE_FILES = (
    "README.md",
    "THEOREM_NOTE.md",
    "VERIFY.md",
    "LICENSE",
    "scripts/verify_candidate_workflow.py",
    "research/experiments/critical_radius_birth_dynamics/candidate_bundle.py",
    "research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_6_v0_1.yml",
    "research/experiments/critical_radius_birth_dynamics/check_v2_6_single_gap_theorem_note_draft.py",
    "research/experiments/critical_radius_birth_dynamics/check_v2_6_gate_c_candidate.py",
    "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_6_gate_c_candidate_readme_v0_1.md",
    "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_6_gate_c_candidate_verify_v0_1.md",
    "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_6_single_gap_theorem_note_draft_v0_1.md",
    "research/experiments/critical_radius_birth_dynamics/prc_v2_6_gate_c_candidate_manifest_v0_1.json",
    "research/experiments/critical_radius_birth_dynamics/gate_c_candidate_bundle_manifest_v2_6_v0_1.json",
    "BUNDLE_FILE_MANIFEST.txt",
    "SHA256SUMS",
)
REQUIRED_BUNDLE_README_TEXT = (
    "PrimeClock v2.6 Gate C Candidate",
    "THEOREM_NOTE.md",
    "not a public theorem release",
    "not a DOI artifact",
    "public release registry",
)
FORBIDDEN_BUNDLE_PATH_TEXT = (
    "release/public/release_registry.json",
    "CITATION.cff",
    "review_packages",
    "public_theorem_release_manifest_v2_5",
    "public_theorem_release_workflow_v2_5",
)


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_bundle_root(path: Path) -> bool:
    return (
        (path / "BUNDLE_FILE_MANIFEST.txt").is_file()
        and (path / "SHA256SUMS").is_file()
        and (path / "THEOREM_NOTE.md").is_file()
    )


def load_manifest(repo_root: Path, failures: list[str]) -> dict[str, object]:
    path = repo_root / MANIFEST_REL
    if not path.is_file():
        failures.append(f"missing Gate C candidate manifest: {MANIFEST_REL}")
        return {}
    text = path.read_text(encoding="utf-8")
    for phrase in FORBIDDEN_MANIFEST_TEXT:
        if phrase in text:
            failures.append(f"manifest contains forbidden public-release reference {phrase!r}")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        failures.append(f"manifest is not valid JSON: {exc}")
        return {}
    if not isinstance(data, dict):
        failures.append("manifest must be a JSON object")
        return {}
    return data


def require_manifest(data: dict[str, object], repo_root: Path, failures: list[str]) -> None:
    expected_scalars = {
        "candidate_id": "prc_v2_6_single_gap_proof_candidate",
        "gate": "gate_c_candidate",
        "gate_r_status": "closed_primary_candidate",
        "base_public_release": "v2.5.0-prc-public-theorem",
        "public_release": False,
    }
    for key, expected in expected_scalars.items():
        if data.get(key) != expected:
            failures.append(f"manifest {key} must be {expected!r}")

    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict):
        failures.append("manifest artifacts must be an object")
    else:
        for key, expected in EXPECTED_ARTIFACTS.items():
            if artifacts.get(key) != expected:
                failures.append(f"manifest artifact {key} must be {expected!r}")
            elif key == "bundle_profile":
                continue
            elif key == "bundle_name":
                continue
            elif not (repo_root / expected).is_file():
                failures.append(f"manifest artifact does not exist: {expected}")

    boundaries = data.get("boundaries")
    if not isinstance(boundaries, dict):
        failures.append("manifest boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                failures.append(f"manifest boundary {key} must be true")

    reproducibility = data.get("reproducibility_decision")
    if not isinstance(reproducibility, dict):
        failures.append("manifest reproducibility_decision must be an object")
    else:
        expected = {
            "primary_artifact": "proof_note",
            "minimal_support_csv": "not_required_for_this_proof_note_candidate",
            "candidate_bundle_zip": "required_for_gate_c_candidate",
            "ci_or_pr_checkpoint": "defer_until_user_requests_checkpoint",
        }
        for key, value in expected.items():
            if reproducibility.get(key) != value:
                failures.append(f"manifest reproducibility decision {key} must be {value!r}")


def run_theorem_checker(repo_root: Path, failures: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, str(repo_root / THEOREM_CHECKER_REL)],
        cwd=repo_root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        failures.append("single-gap theorem note checker failed")
        if result.stdout:
            failures.append(result.stdout.strip())
        if result.stderr:
            failures.append(result.stderr.strip())


def run_bundle_builder_check(bundle_root: Path, failures: list[str]) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(bundle_root / EXPECTED_ARTIFACTS["bundle_builder"]),
            "--profile",
            EXPECTED_ARTIFACTS["bundle_profile"],
            "--check",
            str(bundle_root),
        ],
        cwd=bundle_root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        failures.append("candidate bundle self-check failed")
        if result.stdout:
            failures.append(result.stdout.strip())
        if result.stderr:
            failures.append(result.stderr.strip())


def verify_sha256sums(bundle_root: Path, failures: list[str]) -> None:
    hash_manifest = bundle_root / "SHA256SUMS"
    if not hash_manifest.is_file():
        failures.append("Gate C candidate bundle missing SHA256SUMS")
        return
    seen_paths: set[str] = set()
    for line_number, line in enumerate(hash_manifest.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            expected, relative_path = line.split("  ", 1)
        except ValueError:
            failures.append(f"invalid SHA256SUMS line {line_number}: {line!r}")
            continue
        target = safe_bundle_path(bundle_root, relative_path, f"SHA256SUMS line {line_number}", failures)
        if target is None:
            continue
        if not target.is_file():
            failures.append(f"SHA256SUMS references missing file: {relative_path}")
            continue
        seen_paths.add(relative_path)
        if sha256(target) != expected:
            failures.append(f"SHA256SUMS hash mismatch for {relative_path}")
    actual_files = {
        path.relative_to(bundle_root).as_posix()
        for path in bundle_root.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    }
    for relative_path in sorted(actual_files - seen_paths):
        failures.append(f"bundle file missing from SHA256SUMS: {relative_path}")
    for relative_path in sorted(seen_paths - actual_files):
        failures.append(f"SHA256SUMS contains unexpected file: {relative_path}")


def safe_bundle_path(
    bundle_root: Path,
    raw_relative_path: str,
    context: str,
    failures: list[str],
) -> Path | None:
    if "\\" in raw_relative_path:
        failures.append(f"unsafe path in {context}: {raw_relative_path}")
        return None
    pure_path = PurePosixPath(raw_relative_path)
    if pure_path.is_absolute() or any(part in {"", ".", ".."} for part in pure_path.parts):
        failures.append(f"unsafe path in {context}: {raw_relative_path}")
        return None
    target = (bundle_root / Path(*pure_path.parts)).resolve()
    try:
        target.relative_to(bundle_root.resolve())
    except ValueError:
        failures.append(f"unsafe path escapes bundle root in {context}: {raw_relative_path}")
        return None
    return target


def check_bundle_root(bundle_root: Path, failures: list[str]) -> None:
    if not bundle_root.is_dir():
        failures.append(f"missing Gate C candidate bundle directory: {bundle_root}")
        return
    for relative in REQUIRED_BUNDLE_FILES:
        if not (bundle_root / relative).is_file():
            failures.append(f"Gate C candidate bundle missing file: {relative}")
    for path in bundle_root.rglob("*"):
        relative = path.relative_to(bundle_root).as_posix()
        for phrase in FORBIDDEN_BUNDLE_PATH_TEXT:
            if phrase in relative:
                failures.append(f"Gate C candidate bundle contains forbidden path {phrase!r}")
    note = bundle_root / EXPECTED_ARTIFACTS["canonical_note"]
    theorem_note = bundle_root / "THEOREM_NOTE.md"
    if note.is_file() and theorem_note.is_file() and sha256(note) != sha256(theorem_note):
        failures.append("Gate C candidate bundle THEOREM_NOTE.md does not match canonical note")
    readme = bundle_root / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        for phrase in REQUIRED_BUNDLE_README_TEXT:
            if phrase not in text:
                failures.append(f"Gate C candidate bundle README missing {phrase!r}")
    verify_sha256sums(bundle_root, failures)
    run_theorem_checker(bundle_root, failures)
    run_bundle_builder_check(bundle_root, failures)


def check_bundle_zip(zip_path: Path, failures: list[str]) -> None:
    if not zip_path.is_file():
        failures.append(f"missing Gate C candidate ZIP: {zip_path}")
        return
    try:
        archive = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile as exc:
        failures.append(f"Gate C candidate ZIP is invalid: {exc}")
        return
    with archive:
        bad_member = archive.testzip()
        if bad_member is not None:
            failures.append(f"Gate C candidate ZIP CRC check failed for {bad_member}")
        infos = [info for info in archive.infolist() if not info.is_dir()]
        names = [info.filename for info in infos]
        top_levels = {PurePosixPath(name).parts[0] for name in names if PurePosixPath(name).parts}
        if len(top_levels) != 1:
            failures.append("Gate C candidate ZIP must contain exactly one top-level directory")
            return
        root_name = next(iter(top_levels))
        if root_name != EXPECTED_ARTIFACTS["bundle_name"]:
            failures.append(f"Gate C candidate ZIP top-level directory must be {EXPECTED_ARTIFACTS['bundle_name']!r}")
        expected_names = {
            f"{root_name}/{relative}"
            for relative in REQUIRED_BUNDLE_FILES
        }
        expected_names.update({f"{root_name}/README.md", f"{root_name}/THEOREM_NOTE.md", f"{root_name}/VERIFY.md"})
        actual_names = set(names)
        for name in sorted(expected_names - actual_names):
            failures.append(f"Gate C candidate ZIP missing bundle path {name}")
        for name in sorted(actual_names - expected_names):
            failures.append(f"Gate C candidate ZIP contains unexpected file {name}")
        for name in names:
            pure_path = PurePosixPath(name)
            if pure_path.is_absolute() or any(part in {"", ".", ".."} for part in pure_path.parts):
                failures.append(f"Gate C candidate ZIP contains unsafe path {name!r}")
            for phrase in FORBIDDEN_BUNDLE_PATH_TEXT:
                if phrase in name:
                    failures.append(f"Gate C candidate ZIP contains forbidden path {phrase!r}")
        if failures:
            return
        with tempfile.TemporaryDirectory(prefix="prc-v26-zip-check-") as temp_dir:
            temp_root = Path(temp_dir)
            for info in infos:
                target = safe_bundle_path(temp_root, info.filename, "ZIP member", failures)
                if target is None:
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, target.open("wb") as handle:
                    shutil.copyfileobj(source, handle)
            if failures:
                return
            extracted_root = temp_root / root_name
            check_bundle_root(extracted_root, failures)


def check_reproducible_zip(repo_root: Path, failures: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="prc-v26-repro-") as temp_dir:
        temp_root = Path(temp_dir)
        zip_paths: list[Path] = []
        for label in ("a", "b"):
            out_dir = temp_root / label
            result = subprocess.run(
                [
                    sys.executable,
                    str(repo_root / EXPECTED_ARTIFACTS["bundle_builder"]),
                    "--profile",
                    EXPECTED_ARTIFACTS["bundle_profile"],
                    "--out",
                    str(out_dir),
                    "--zip",
                ],
                cwd=repo_root,
                check=False,
                text=True,
                capture_output=True,
            )
            if result.returncode != 0:
                failures.append(f"deterministic ZIP build {label} failed")
                if result.stdout:
                    failures.append(result.stdout.strip())
                if result.stderr:
                    failures.append(result.stderr.strip())
                return
            zip_paths.append(out_dir / f"{EXPECTED_ARTIFACTS['bundle_name']}.zip")
        first, second = zip_paths
        if not first.is_file() or not second.is_file():
            failures.append("deterministic ZIP build did not produce both ZIP files")
            return
        if sha256(first) != sha256(second):
            failures.append("deterministic ZIP check failed: repeated builds differ")


def check_negative_cases(bundle_root: Path, zip_path: Path, failures: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="prc-v26-negative-") as temp_dir:
        temp_root = Path(temp_dir)

        broken_bundle = temp_root / "broken-bundle"
        shutil.copytree(bundle_root, broken_bundle)
        bad_note = "# Broken note\n\nThis intentionally lacks the required proof-note structure.\n"
        (broken_bundle / "THEOREM_NOTE.md").write_text(bad_note, encoding="utf-8")
        (broken_bundle / EXPECTED_ARTIFACTS["canonical_note"]).write_text(
            bad_note,
            encoding="utf-8",
        )
        bundle_failures: list[str] = []
        check_bundle_root(broken_bundle, bundle_failures)
        if not bundle_failures:
            failures.append("negative check failed: broken bundle note was accepted")

        with zipfile.ZipFile(zip_path) as archive:
            root_name = PurePosixPath(
                next(name for name in archive.namelist() if not name.endswith("/"))
            ).parts[0]
            bad_zip = temp_root / "bad-note.zip"
            with zipfile.ZipFile(bad_zip, "w", compression=zipfile.ZIP_DEFLATED) as output:
                for info in archive.infolist():
                    data = archive.read(info.filename)
                    if info.filename == f"{root_name}/THEOREM_NOTE.md":
                        data = b"# Broken note\n"
                    output.writestr(info, data)
        zip_failures: list[str] = []
        check_bundle_zip(bad_zip, zip_failures)
        if not zip_failures:
            failures.append("negative check failed: modified ZIP theorem note was accepted")

        extra_zip = temp_root / "extra-file.zip"
        with zipfile.ZipFile(zip_path) as archive, zipfile.ZipFile(
            extra_zip,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as output:
            for info in archive.infolist():
                output.writestr(info, archive.read(info.filename))
            output.writestr(f"{root_name}/EXTRA.txt", "unexpected\n")
        extra_failures: list[str] = []
        check_bundle_zip(extra_zip, extra_failures)
        if not extra_failures:
            failures.append("negative check failed: ZIP with extra file was accepted")

        traversal_zip = temp_root / "traversal.zip"
        with zipfile.ZipFile(traversal_zip, "w", compression=zipfile.ZIP_DEFLATED) as output:
            output.writestr("../evil", "bad\n")
        traversal_failures: list[str] = []
        check_bundle_zip(traversal_zip, traversal_failures)
        if not traversal_failures:
            failures.append("negative check failed: ZIP path traversal was accepted")


def check_root_readme(repo_root: Path, failures: list[str]) -> None:
    readme = repo_root / "README.md"
    text = readme.read_text(encoding="utf-8")
    if is_bundle_root(repo_root):
        for phrase in REQUIRED_BUNDLE_README_TEXT:
            if phrase not in text:
                failures.append(f"Gate C candidate bundle README missing {phrase!r}")
        return
    for phrase in FORBIDDEN_README_TEXT:
        if phrase in text:
            failures.append(f"root README contains internal Gate C candidate phrase {phrase!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", type=Path)
    parser.add_argument("--zip", type=Path)
    parser.add_argument(
        "--zip-only",
        action="store_true",
        help="validate only the ZIP artifact, without checking the current working tree",
    )
    parser.add_argument("--reproducible-zip", action="store_true")
    parser.add_argument("--negative-tests", action="store_true")
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    failures: list[str] = []

    if args.zip_only:
        if args.zip is None:
            failures.append("--zip-only requires --zip")
        if args.bundle_root is not None:
            failures.append("--zip-only must not be combined with --bundle-root")
        if args.reproducible_zip:
            failures.append("--zip-only must not be combined with --reproducible-zip")
        if args.negative_tests:
            failures.append("--zip-only must not be combined with --negative-tests")
        if args.zip is not None:
            check_bundle_zip(args.zip.resolve(), failures)
    else:
        manifest = load_manifest(repo_root, failures)
        if manifest:
            require_manifest(manifest, repo_root, failures)
        check_root_readme(repo_root, failures)
        if args.bundle_root is not None:
            check_bundle_root(args.bundle_root.resolve(), failures)
        elif is_bundle_root(repo_root):
            check_bundle_root(repo_root, failures)
        else:
            run_theorem_checker(repo_root, failures)
        if args.zip is not None:
            check_bundle_zip(args.zip.resolve(), failures)
        if args.reproducible_zip:
            check_reproducible_zip(repo_root, failures)
        if args.negative_tests:
            if args.bundle_root is None or args.zip is None:
                failures.append("--negative-tests requires --bundle-root and --zip")
            else:
                check_negative_cases(args.bundle_root.resolve(), args.zip.resolve(), failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_6_gate_c_candidate: "
        "checks=9, failed=0, gate_c=candidate_ready, public_theorem=defer, "
        "artifact_integrity=passed, proof_note_hygiene=passed, "
        "mathematical_verification=not_claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
