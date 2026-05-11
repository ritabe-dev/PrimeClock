#!/usr/bin/env python3
"""Detect and apply the Zenodo version DOI for the current public release."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from release_config import CONFIG_PATH, load_release_config


DEFAULT_PUBLIC_WORKTREE = Path(tempfile.gettempdir()) / "primeclock-public-release"
DEFAULT_BUILD_PARENT = Path(tempfile.gettempdir()) / "primeclock-public-doi-build"
DEFAULT_CHECK_PARENT = Path(tempfile.gettempdir()) / "primeclock-public-release-check"
DOI_PATTERN = re.compile(r"10\.5281/zenodo\.(\d+)")


def read_zenodo_page(concept_doi: str) -> str:
    url = f"https://zenodo.org/doi/{concept_doi}"
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8", "replace")


def extract_version_doi(text: str, concept_doi: str) -> str | None:
    for match in DOI_PATTERN.finditer(text):
        doi = match.group(0)
        if doi != concept_doi:
            return doi
    return None


def replace_pending_or_doi(text: str, version_doi: str) -> str:
    text = re.sub(
        r"Version DOI: pending Zenodo publication for the GitHub `v[\d.]+` release\.",
        f"Version DOI: `{version_doi}`",
        text,
    )
    text = re.sub(r"Version DOI: `10\.5281/zenodo\.\d+`", f"Version DOI: `{version_doi}`", text)
    text = re.sub(
        r"the v[\d.]+ version DOI is pending(?:\n)?Zenodo publication",
        f"the current version DOI is `{version_doi}`",
        text,
    )
    text = re.sub(r"\| Version DOI \| `10\.5281/zenodo\.\d+` \|", f"| Version DOI | `{version_doi}` |", text)
    text = re.sub(
        r"\| Version DOI \| pending Zenodo publication for the GitHub `v[\d.]+` release \|",
        f"| Version DOI | `{version_doi}` |",
        text,
    )
    return text


def update_citation(text: str, version_doi: str, concept_doi: str) -> str:
    return re.sub(r'doi: "10\.5281/zenodo\.\d+"', f'doi: "{concept_doi}"', text, count=1)


def update_files(repo_root: Path, version_doi: str) -> None:
    config_path = repo_root / CONFIG_PATH
    config = load_release_config(repo_root)
    concept_doi = config["zenodo_concept_doi"]

    config["zenodo_version_doi"] = version_doi
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    citation_path = repo_root / "CITATION.cff"
    citation_path.write_text(
        update_citation(citation_path.read_text(encoding="utf-8"), version_doi, concept_doi),
        encoding="utf-8",
    )

    for relative_path in [
        "README.md",
        "release/public/README.template.md",
        "VERSION_MAP.md",
        config["root_release_notes"],
        config["research_release_notes"],
    ]:
        path = repo_root / relative_path
        path.write_text(replace_pending_or_doi(path.read_text(encoding="utf-8"), version_doi), encoding="utf-8")


def run(command: list[str], cwd: Path) -> None:
    print("+ " + " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def commit_if_changed(cwd: Path, message: str) -> None:
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    if not status.stdout.strip():
        print(f"no git changes to commit in {cwd}")
        return
    run(["git", "add", "-A"], cwd)
    run(["git", "commit", "-m", message], cwd)


def sync_public_metadata(repo_root: Path, public_worktree: Path, build_parent: Path, config: dict[str, str]) -> None:
    release_root = build_parent / config["bundle_name"]
    release_zip = release_root.parent / f"{release_root.name}.zip"
    run([sys.executable, "scripts/verify_public_release.py", "--out", str(build_parent), "--zip"], repo_root)
    run(["git", "fetch", "origin", "main", "--tags"], public_worktree)
    run(["git", "switch", "--detach", "origin/main"], public_worktree)
    run(
        [
            "rsync",
            "-a",
            "--delete",
            "--exclude",
            ".git",
            f"{release_root}/",
            f"{public_worktree}/",
        ],
        repo_root,
    )
    run([sys.executable, "scripts/check_release_versions.py"], public_worktree)
    run([sys.executable, "scripts/update_public_hashes.py", "--check"], public_worktree)
    run(
        [
            sys.executable,
            "scripts/verify_public_release.py",
            "--out",
            str(DEFAULT_CHECK_PARENT),
            "--zip",
        ],
        public_worktree,
    )
    run(["git", "diff", "--check"], public_worktree)
    commit_if_changed(public_worktree, f"Add Zenodo DOI for PRC {config['public_tag']}")
    run(["git", "push", "origin", "HEAD:main"], public_worktree)
    run(["gh", "release", "edit", config["public_tag"], "--notes-file", str(public_worktree / config["root_release_notes"])], public_worktree)
    run(["gh", "release", "upload", config["public_tag"], str(release_zip), "--clobber"], public_worktree)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Update files and SHA256SUMS")
    parser.add_argument("--repo-root", type=Path, help="Repository root to update")
    parser.add_argument("--version-doi", help="Use this DOI instead of detecting from Zenodo")
    parser.add_argument("--html-file", type=Path, help="Read a saved Zenodo HTML page")
    parser.add_argument("--public-worktree", type=Path, default=DEFAULT_PUBLIC_WORKTREE)
    parser.add_argument("--build-parent", type=Path, default=DEFAULT_BUILD_PARENT)
    parser.add_argument(
        "--skip-public-sync",
        action="store_true",
        help="Only update source files; do not sync the public worktree or GitHub release",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    config = load_release_config(repo_root)
    concept_doi = config["zenodo_concept_doi"]

    if config["release_kind"] != "doi_release":
        print(f"refusing DOI finalization for release_kind={config['release_kind']}")
        return 1

    if args.version_doi:
        version_doi = args.version_doi
    else:
        html = args.html_file.read_text(encoding="utf-8") if args.html_file else read_zenodo_page(concept_doi)
        version_doi = extract_version_doi(html, concept_doi)

    if not version_doi:
        print(f"pending: no Zenodo version DOI found for {config['public_tag']}")
        return 0

    print(f"version DOI: {version_doi}")
    if not args.execute:
        print("dry-run: pass --execute to update citation metadata")
        return 0

    update_files(repo_root, version_doi)
    subprocess.run([sys.executable, "scripts/update_public_hashes.py"], cwd=repo_root, check=True)
    subprocess.run([sys.executable, "scripts/check_release_versions.py"], cwd=repo_root, check=True)
    commit_if_changed(repo_root, f"Add Zenodo DOI for PRC {config['public_tag']}")
    if not args.skip_public_sync:
        sync_public_metadata(repo_root, args.public_worktree.resolve(), args.build_parent.resolve(), load_release_config(repo_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
