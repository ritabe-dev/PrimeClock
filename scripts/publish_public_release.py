#!/usr/bin/env python3
"""Prepare or publish the clean public release bundle.

The default mode is a dry run. Network writes only happen with --execute.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from release_config import load_release_config


DEFAULT_PUBLIC_WORKTREE = Path(tempfile.gettempdir()) / "primeclock-public-release"
DEFAULT_BUILD_PARENT = Path(tempfile.gettempdir()) / "primeclock-public-publish-build"
DEFAULT_CHECK_PARENT = Path(tempfile.gettempdir()) / "primeclock-public-release-check"


def run(command: list[str], cwd: Path, *, execute: bool) -> None:
    prefix = "+" if execute else "DRY-RUN:"
    print(f"{prefix} ({cwd}) {' '.join(command)}", flush=True)
    if execute:
        subprocess.run(command, cwd=cwd, check=True)


def run_checked(command: list[str], cwd: Path) -> None:
    print(f"+ ({cwd}) {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def require_tool(name: str) -> None:
    if not shutil.which(name):
        raise SystemExit(f"required tool not found on PATH: {name}")


def preflight_execute_tools(*, allow_github_release: bool) -> None:
    for tool in ["git", "rsync"]:
        require_tool(tool)
    if allow_github_release:
        require_tool("gh")


def sync_bundle(source: Path, target: Path, *, execute: bool) -> None:
    command = [
        "rsync",
        "-a",
        "--delete",
        "--exclude",
        ".git",
        f"{source}/",
        f"{target}/",
    ]
    run(command, Path.cwd(), execute=execute)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Perform git push/tag/release writes")
    parser.add_argument("--public-worktree", type=Path, default=DEFAULT_PUBLIC_WORKTREE)
    parser.add_argument("--build-parent", type=Path, default=DEFAULT_BUILD_PARENT)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    config = load_release_config(repo_root)
    tag = config["public_tag"]
    bundle_name = config["bundle_name"]
    allow_github_release = config["allow_github_release"]
    zenodo_expected = config["zenodo_expected"]
    public_worktree = args.public_worktree.resolve()
    build_parent = args.build_parent.resolve()
    release_root = build_parent / bundle_name
    release_zip = release_root.parent / f"{release_root.name}.zip"

    print(f"release: {tag}", flush=True)
    print(
        "mode: execute"
        if args.execute
        else "mode: dry-run: local checks run, mutating release steps previewed",
        flush=True,
    )
    print(f"release kind: {config['release_kind']}", flush=True)
    print(f"GitHub Release: {'yes' if allow_github_release else 'no'}", flush=True)
    print(f"Zenodo target: {'yes' if zenodo_expected else 'no'}", flush=True)

    if args.execute:
        preflight_execute_tools(allow_github_release=allow_github_release)
        if not public_worktree.is_dir():
            raise SystemExit(f"public worktree does not exist: {public_worktree}")

    run_checked([sys.executable, "scripts/check_release_versions.py"], repo_root)
    run_checked([sys.executable, "scripts/update_public_hashes.py", "--check"], repo_root)
    run_checked(
        [
            sys.executable,
            "scripts/verify_public_release.py",
            "--out",
            str(build_parent),
            "--zip",
        ],
        repo_root,
    )
    if not release_zip.is_file():
        raise SystemExit(f"missing release asset: {release_zip}")

    run(["git", "fetch", "origin", "main", "--tags"], public_worktree, execute=args.execute)
    run(["git", "switch", "--detach", "origin/main"], public_worktree, execute=args.execute)
    sync_bundle(release_root, public_worktree, execute=args.execute)

    run([sys.executable, "scripts/check_release_versions.py"], public_worktree, execute=args.execute)
    run([sys.executable, "scripts/update_public_hashes.py", "--check"], public_worktree, execute=args.execute)
    run(
        [
            sys.executable,
            "scripts/verify_public_release.py",
            "--out",
            str(DEFAULT_CHECK_PARENT),
            "--zip",
        ],
        public_worktree,
        execute=args.execute,
    )
    run(["git", "diff", "--check"], public_worktree, execute=args.execute)

    if allow_github_release:
        commit_message = f"Release PRC finite certificate bundle {tag}"
    else:
        commit_message = f"Sync PRC public bundle {tag}"
    run(["git", "add", "-A"], public_worktree, execute=args.execute)
    run(["git", "commit", "-m", commit_message], public_worktree, execute=args.execute)
    run(["git", "push", "origin", "HEAD:main"], public_worktree, execute=args.execute)
    if not allow_github_release:
        print(
            "skipping tag and GitHub Release because release_kind is maintenance_sync",
            flush=True,
        )
        return 0

    run(["git", "tag", "-a", tag, "-m", f"PRC finite theorem bundle {tag}"], public_worktree, execute=args.execute)
    run(["git", "push", "origin", tag], public_worktree, execute=args.execute)

    release_title = f"PRC finite theorem bundle {tag}"
    notes_file = public_worktree / config["root_release_notes"]
    run(
        [
            "gh",
            "release",
            "create",
            tag,
            str(release_zip),
            "--title",
            release_title,
            "--notes-file",
            str(notes_file),
            "--latest",
        ],
        public_worktree,
        execute=args.execute,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
