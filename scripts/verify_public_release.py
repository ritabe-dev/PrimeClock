#!/usr/bin/env python3
"""Run the config-driven public release verification path."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from release_config import load_release_config


def run(command: list[str], cwd: Path) -> None:
    print("+ " + " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path, help="Output parent directory")
    parser.add_argument("--zip", action="store_true", help="Also build a zip archive")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    config = load_release_config(repo_root)
    release_root = args.out.resolve() / config["bundle_name"]

    run([sys.executable, "scripts/check_release_versions.py"], cwd=repo_root)
    run([sys.executable, "scripts/update_public_hashes.py", "--check"], cwd=repo_root)

    build_command = [
        sys.executable,
        "scripts/build_public_release.py",
        "--out",
        str(args.out.resolve()),
    ]
    if args.zip:
        build_command.append("--zip")
    run(build_command, cwd=repo_root)
    run([sys.executable, "scripts/check_public_release.py", str(release_root)], cwd=repo_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
