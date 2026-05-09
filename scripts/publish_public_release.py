#!/usr/bin/env python3
"""Prepare or publish the clean public release bundle.

The default mode is a dry run. Network writes only happen with --execute.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from release_config import load_release_config


DEFAULT_PUBLIC_WORKTREE = Path("/private/tmp/primeclock-public-release")
DEFAULT_BUILD_PARENT = Path("/private/tmp/primeclock-public-publish-build")


def run(command: list[str], cwd: Path, *, execute: bool, mutating: bool = False) -> None:
    prefix = "+" if execute or not mutating else "DRY-RUN:"
    print(f"{prefix} ({cwd}) {' '.join(command)}")
    if execute or not mutating:
        subprocess.run(command, cwd=cwd, check=True)


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
    run(command, Path.cwd(), execute=execute, mutating=True)


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
    public_worktree = args.public_worktree.resolve()
    build_parent = args.build_parent.resolve()
    release_root = build_parent / bundle_name
    release_zip = release_root.parent / f"{release_root.name}.zip"

    print(f"release: {tag}")
    print(f"mode: {'execute' if args.execute else 'dry-run'}")

    run([sys.executable, "scripts/check_release_versions.py"], repo_root, execute=args.execute, mutating=True)
    run([sys.executable, "scripts/update_public_hashes.py", "--check"], repo_root, execute=args.execute, mutating=True)
    run(
        [
            sys.executable,
            "scripts/verify_public_release.py",
            "--out",
            str(build_parent),
            "--zip",
        ],
        repo_root,
        execute=args.execute,
        mutating=True,
    )

    if args.execute and not public_worktree.is_dir():
        raise SystemExit(f"public worktree does not exist: {public_worktree}")

    run(["git", "fetch", "origin", "main", "--tags"], public_worktree, execute=args.execute, mutating=True)
    run(["git", "switch", "--detach", "origin/main"], public_worktree, execute=args.execute, mutating=True)
    sync_bundle(release_root, public_worktree, execute=args.execute)

    run([sys.executable, "scripts/check_release_versions.py"], public_worktree, execute=args.execute, mutating=True)
    run([sys.executable, "scripts/update_public_hashes.py", "--check"], public_worktree, execute=args.execute, mutating=True)
    run(
        [
            sys.executable,
            "scripts/verify_public_release.py",
            "--out",
            "/private/tmp/primeclock-public-release-check",
            "--zip",
        ],
        public_worktree,
        execute=args.execute,
        mutating=True,
    )
    run(["git", "diff", "--check"], public_worktree, execute=args.execute, mutating=True)

    commit_message = f"Release PRC finite certificate bundle {tag}"
    run(["git", "add", "-A"], public_worktree, execute=args.execute, mutating=True)
    run(["git", "commit", "-m", commit_message], public_worktree, execute=args.execute, mutating=True)
    run(["git", "push", "origin", "HEAD:main"], public_worktree, execute=args.execute, mutating=True)
    run(["git", "tag", "-a", tag, "-m", f"PRC finite theorem bundle {tag}"], public_worktree, execute=args.execute, mutating=True)
    run(["git", "push", "origin", tag], public_worktree, execute=args.execute, mutating=True)

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
        mutating=True,
    )
    if not release_zip.is_file() and args.execute:
        raise SystemExit(f"missing release asset: {release_zip}")
    if not shutil.which("gh"):
        print("warning: gh CLI not found; --execute release creation will fail")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
