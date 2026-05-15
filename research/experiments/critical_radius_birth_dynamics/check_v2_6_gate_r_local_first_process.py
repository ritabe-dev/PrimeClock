#!/usr/bin/env python3
"""Audit v2.6 Gate R local-first process boundaries."""

from __future__ import annotations

from pathlib import Path

from check_v2_6_special_point_obstruction import repo_root_from_script


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
NOTES_REL = EXPERIMENT_REL / "notes"
NOTE_REL = NOTES_REL / "prc_v2_6_gate_r_local_first_process_v0_1.md"

REQUIRED_SECTIONS = (
    "## Purpose",
    "## Gate Policy",
    "## PR #6 Handling",
    "## Next Work",
    "## Non-claims",
)
REQUIRED_PHRASES = (
    "Gate R is local-first by default",
    "source-only note/checker",
    "local workflow",
    "no new PR or push unless the work has become a coherent Gate R checkpoint",
    "Gate C is PR/CI-first",
    "Gate P is PR/CI-first",
    "keep PR #6 open as a draft",
    "do not merge it yet",
    "update the existing PR only after the theorem-note promote/defer decision is clear",
    "v2.5 public theorem release protection remains 100%",
    "about 90-95%",
    "about 0.5 slice",
    "no public theorem claim",
    "no DOI claim",
    "no B8 theorem",
    "no general predictor claim",
    "no asymptotic law claim",
)


def require_note(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / NOTE_REL
    if not path.is_file():
        failures.append(f"missing local-first process note: {NOTE_REL}")
        return
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.replace("`", "").split())
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"local-first process note missing section {section}")
    for phrase in REQUIRED_PHRASES:
        normalized_phrase = " ".join(phrase.replace("`", "").split())
        if normalized_phrase not in normalized:
            failures.append(f"local-first process note missing phrase {phrase!r}")


def main() -> int:
    repo_root = repo_root_from_script()
    failures: list[str] = []
    require_note(repo_root, failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_6_gate_r_local_first_process: "
        "checks=5, failed=0, "
        "gate_r=local_first, "
        "pr_policy=checkpoint_only, "
        "pr6=draft_hold"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
