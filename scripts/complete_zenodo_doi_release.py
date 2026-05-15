#!/usr/bin/env python3
"""Complete a registry-managed Zenodo DOI release end to end."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from finalize_version_doi import DOI_RE, update_registered_files
from release_registry import REGISTRY_PATH, load_release_registry, release_entry, save_release_registry


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def python_executable(repo_root: Path) -> str:
    venv_python = repo_root / "research" / ".venv" / "bin" / "python"
    if venv_python.is_file():
        return str(venv_python)
    result = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        cwd=repo_root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        common_dir = Path(result.stdout.strip())
        if not common_dir.is_absolute():
            common_dir = repo_root / common_dir
        primary_worktree_python = common_dir.parent / "research" / ".venv" / "bin" / "python"
        if primary_worktree_python.is_file():
            return str(primary_worktree_python)
    return sys.executable


def scripts_dir() -> Path:
    return Path(__file__).resolve().parent


def deterministic_github_release_url(tag: str) -> str:
    return f"https://github.com/ritabe-dev/PrimeClock/releases/tag/{tag}"


def asset_path(repo_root: Path, entry: dict[str, Any]) -> Path:
    return repo_root / "review_packages" / entry["asset_name"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], *, cwd: Path, capture_json: bool = False) -> Any:
    print("+ " + " ".join(command), flush=True)
    result = subprocess.run(command, cwd=cwd, check=False, text=True, capture_output=True)
    if result.stdout and not capture_json:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    if capture_json:
        return json.loads(result.stdout)
    return result.stdout


def planned_files(entry: dict[str, Any]) -> list[str]:
    return sorted(
        set(
            [REGISTRY_PATH.as_posix(), "README.md", "VERSION_MAP.md", "SHA256SUMS"]
            + entry["readme_paths"]
            + entry["release_notes_paths"]
            + entry["citation_paths"]
            + [entry["manifest_path"]]
            + [f"review_packages/{entry['asset_name']}"]
        )
    )


def print_plan(repo_root: Path, entry: dict[str, Any], version_doi: str) -> None:
    print(f"release_id: {entry['release_id']}")
    print(f"version DOI: {version_doi}")
    print(f"GitHub Release: {deterministic_github_release_url(entry['tag'])}")
    print(f"release asset: review_packages/{entry['asset_name']}")
    print("planned file updates:")
    for relative_path in planned_files(entry):
        print(f"  {relative_path}")
    if entry.get("bundle_profile"):
        print("bundle rebuild:")
        print(
            "  "
            f"{python_executable(repo_root)} "
            "research/experiments/critical_radius_birth_dynamics/candidate_bundle.py "
            f"--profile {entry['bundle_profile']} --out review_packages --zip"
        )
    else:
        print("bundle rebuild: no registry bundle_profile; legacy/manual release")
    print("GitHub release refresh:")
    print(f"  gh release edit {entry['tag']} --notes-file {entry['release_notes_primary']}")
    print(
        f"  gh release upload {entry['tag']} "
        f"review_packages/{entry['asset_name']} --clobber"
    )


def validate_registered_assigned_state(
    repo_root: Path,
    registry_path: Path,
    release_id: str,
    version_doi: str,
    *,
    python: str,
) -> None:
    run(
        [
            python,
            str(scripts_dir() / "check_release_doi_integrity.py"),
            "--repo-root",
            str(repo_root),
            "--registry",
            str(registry_path),
            "--release-id",
            release_id,
        ],
        cwd=repo_root,
    )

    registry = load_release_registry(repo_root, registry_path)
    entry = release_entry(registry, release_id)
    if entry["doi_state"] != "assigned":
        raise SystemExit(f"{release_id}: doi_state is not assigned")
    if entry["zenodo_version_doi"] != version_doi:
        raise SystemExit(
            f"{release_id}: registry DOI {entry['zenodo_version_doi']!r} "
            f"does not match requested DOI {version_doi!r}"
        )


def rebuild_bundle(repo_root: Path, entry: dict[str, Any], *, python: str) -> str:
    if not entry.get("bundle_profile"):
        raise SystemExit(
            f"{entry['release_id']}: registry bundle_profile is required for automated DOI completion"
        )
    run(
        [
            python,
            str(
                repo_root
                / "research/experiments/critical_radius_birth_dynamics/candidate_bundle.py"
            ),
            "--profile",
            entry["bundle_profile"],
            "--out",
            "review_packages",
            "--zip",
        ],
        cwd=repo_root,
    )
    path = asset_path(repo_root, entry)
    if not path.is_file():
        raise SystemExit(f"{entry['release_id']}: expected rebuilt asset missing: {path}")
    return sha256_file(path)


def save_asset_sha(
    repo_root: Path,
    registry_path: Path,
    release_id: str,
    asset_sha: str,
) -> dict[str, Any]:
    registry = load_release_registry(repo_root, registry_path)
    entry = release_entry(registry, release_id)
    entry["release_asset_sha256"] = asset_sha
    save_release_registry(registry, repo_root, registry_path)
    return entry


def publish_github_release(repo_root: Path, entry: dict[str, Any]) -> None:
    run(
        ["gh", "release", "edit", entry["tag"], "--notes-file", entry["release_notes_primary"]],
        cwd=repo_root,
    )
    run(
        [
            "gh",
            "release",
            "upload",
            entry["tag"],
            str(asset_path(repo_root, entry)),
            "--clobber",
        ],
        cwd=repo_root,
    )


def verify_remote_state(repo_root: Path, entry: dict[str, Any], version_doi: str) -> None:
    release = run(
        ["gh", "release", "view", entry["tag"], "--json", "body,assets,url,tagName"],
        cwd=repo_root,
        capture_json=True,
    )
    if release["url"] != deterministic_github_release_url(entry["tag"]):
        raise SystemExit(f"{entry['release_id']}: unexpected GitHub Release URL {release['url']}")
    if version_doi not in release["body"]:
        raise SystemExit(f"{entry['release_id']}: GitHub Release body missing DOI {version_doi}")

    expected_digest = f"sha256:{entry['release_asset_sha256']}"
    matching_assets = [asset for asset in release["assets"] if asset["name"] == entry["asset_name"]]
    if len(matching_assets) != 1:
        raise SystemExit(f"{entry['release_id']}: GitHub Release asset not found exactly once")
    if matching_assets[0].get("digest") != expected_digest:
        raise SystemExit(
            f"{entry['release_id']}: remote asset digest {matching_assets[0].get('digest')} "
            f"does not match {expected_digest}"
        )

    readme = run(
        ["gh", "api", "repos/ritabe-dev/PrimeClock/readme", "-H", "Accept: application/vnd.github.raw"],
        cwd=repo_root,
    )
    for needle in [entry["release_id"], version_doi, entry["asset_name"]]:
        if needle not in readme:
            raise SystemExit(f"{entry['release_id']}: GitHub main README missing {needle!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, help="Repository root to update")
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH, help="Release registry path")
    parser.add_argument("--release-id", required=True, help="Registered release id to complete")
    parser.add_argument("--version-doi", required=True, help="Zenodo version DOI")
    parser.add_argument("--execute", action="store_true", help="Write local DOI updates")
    parser.add_argument("--publish-github", action="store_true", help="Update GitHub Release notes and asset")
    parser.add_argument("--verify-remote", action="store_true", help="Verify GitHub Release and main README")
    parser.add_argument(
        "--dry-run-validate",
        action="store_true",
        help="Validate an already-assigned DOI release without writing files",
    )
    args = parser.parse_args()

    if not DOI_RE.fullmatch(args.version_doi):
        print(f"invalid Zenodo DOI: {args.version_doi}")
        return 1
    if (args.publish_github or args.verify_remote) and not args.execute:
        print("--publish-github and --verify-remote require --execute")
        return 1

    repo_root = args.repo_root.resolve() if args.repo_root else repo_root_from_script()
    registry_path = args.registry
    registry = load_release_registry(repo_root, registry_path)
    entry = release_entry(registry, args.release_id)
    python = python_executable(repo_root)

    print_plan(repo_root, entry, args.version_doi)
    if args.dry_run_validate:
        validate_registered_assigned_state(
            repo_root,
            registry_path,
            args.release_id,
            args.version_doi,
            python=python,
        )
        print("complete_zenodo_doi_release: dry_run_validate=passed")
        return 0
    if not args.execute:
        print("dry-run: pass --execute to update local release files")
        return 0

    entry["doi_state"] = "assigned"
    entry["zenodo_version_doi"] = args.version_doi
    save_release_registry(registry, repo_root, registry_path)
    update_registered_files(repo_root, entry, args.version_doi)

    run([python, str(scripts_dir() / "render_public_surface.py"), "--write"], cwd=repo_root)
    asset_sha = rebuild_bundle(repo_root, entry, python=python)
    entry = save_asset_sha(repo_root, registry_path, args.release_id, asset_sha)
    run([python, str(scripts_dir() / "update_public_hashes.py")], cwd=repo_root)

    validate_registered_assigned_state(
        repo_root,
        registry_path,
        args.release_id,
        args.version_doi,
        python=python,
    )
    run(
        [
            python,
            str(scripts_dir() / "verify_public_release_execution_preflight.py"),
            "--release-id",
            args.release_id,
        ],
        cwd=repo_root,
    )

    if args.publish_github:
        publish_github_release(repo_root, entry)
    if args.verify_remote:
        verify_remote_state(repo_root, entry, args.version_doi)

    print(
        "complete_zenodo_doi_release: "
        f"release_id={args.release_id}, doi={args.version_doi}, asset_sha256={asset_sha}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
