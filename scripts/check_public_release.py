#!/usr/bin/env python3
"""Check that a generated public release bundle stays clean."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FORBIDDEN_PATH_PARTS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".uv-cache",
    ".venv",
    "__pycache__",
    "CSV_SUMMARY.md",
    "PROMPT.md",
    "dist",
    "node_modules",
    "review_packages",
}

FORBIDDEN_TEXT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bPROMPT\.md\b",
        r"\bCSV_SUMMARY\.md\b",
        r"\breview package\b",
        r"\bSuggested Review Prompt\b",
        r"\bChatGPT\b",
        r"\bCodex\b",
        r"\bClaude\b",
        r"\bCopilot\b",
        r"\bLLM\b",
        r"\blarge language model\b",
        r"\blanguage model\b",
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


def is_text_file(path: Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name in {"LICENSE"}


def check_paths(root: Path) -> list[str]:
    failures: list[str] = []
    for path in root.rglob("*"):
        relative_parts = path.relative_to(root).parts
        if path.name == ".DS_Store":
            failures.append(f"forbidden local metadata file: {path.relative_to(root)}")
        for part in relative_parts:
            if part in FORBIDDEN_PATH_PARTS:
                failures.append(f"forbidden path component {part}: {path.relative_to(root)}")
                break
        if path.suffix in {".zip", ".tar", ".tgz"} or path.name.endswith(".tar.gz"):
            failures.append(f"forbidden archive file: {path.relative_to(root)}")
    return failures


def check_text(root: Path) -> list[str]:
    failures: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or not is_text_file(path):
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_TEXT_PATTERNS:
            match = pattern.search(text)
            if match:
                failures.append(
                    f"forbidden text {match.group(0)!r} in {path.relative_to(root)}"
                )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release_root", type=Path)
    args = parser.parse_args()

    release_root = args.release_root.resolve()
    if not release_root.is_dir():
        raise SystemExit(f"Not a directory: {release_root}")

    failures = check_paths(release_root) + check_text(release_root)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"OK: {release_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
