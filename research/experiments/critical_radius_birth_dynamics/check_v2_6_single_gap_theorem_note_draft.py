#!/usr/bin/env python3
"""Audit the v2.6 necessary-only proof note."""

from __future__ import annotations

from pathlib import Path


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
NOTES_REL = EXPERIMENT_REL / "notes"

NOTE_REL = NOTES_REL / "prc_v2_6_single_gap_theorem_note_draft_v0_1.md"
REQUIRED_SECTIONS = (
    "## Definitions",
    "## Special Endpoint Spacing Lemma",
    "## Residual Boundary Lemma",
    "## Forbidden Special Remainder Lemma",
    "## Central Endpoint Obstruction",
    "## Single-Gap Grid Containment Criterion",
    "## Boundary",
)
REQUIRED_PHRASES = (
    "old prime prefix is {p_1=2, p_2=3, ..., p_k}",
    "p_k >= 5",
    "closure(G) subset int(I_q(a))",
    "dist(0, nearest old endpoint) >= 1/(2p_k)",
    "dist(1/2, nearest old endpoint other than 1/2) >= 1/p_k",
    "combining old clouds does not create new endpoints",
    "The prime 2 endpoints are handled separately",
    "do not weaken the displayed bound",
    "finite union of closed arcs",
    "boundary is contained in the set of old cloud endpoints",
    "one-sided open interval adjacent to 0 or 1/2",
    "covered/uncovered state is constant",
    "contains no old residual component",
    "same old residual component continues",
    "0, (q-1)/2, (q+1)/2",
    "local representative (-1/2, 1/2)",
    "the q-cloud cannot reach that endpoint",
    "covered case contains no residual component",
    "uncovered case leaves part of the adjacent residual component outside",
    "the point is 1/2",
    "The p=2 endpoints are 1/4 and 3/4",
    "equality with 1/4 or 3/4 would require n=q/2 or n=3q/2",
    "impossible for odd q",
    "endpoint-touch birth is obstructed",
    "choose a local linear representative of R/Z",
    "both G and the relevant q-cloud are represented without crossing the chosen cut",
    "qR - 1/2 < a < qL + 1/2",
    "fixed-gap geometric criterion",
    "private source-only proof note",
    "no public theorem",
    "Close(row) equivalence remains checked-scope support only",
)
FORBIDDEN_PHRASES = (
    "Current readiness",
    "readiness",
    "remaining work",
    "slice",
    "old prefix contains",
    "PR #",
    "mod 6",
    "k=2",
    "capacity false-positive",
    "B8 feasibility",
    "public_theorem=promote",
    "doi_state=assigned",
    "zenodo_version_doi",
    "b8_theorem=promote",
    "general predictor theorem",
    "asymptotic law theorem",
    "G subset I_q(a)\niff",
)


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def require_note(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / NOTE_REL
    if not path.is_file():
        failures.append(f"missing single-gap theorem-note draft: {NOTE_REL}")
        return
    text = path.read_text(encoding="utf-8")
    normalized = " ".join(text.replace("`", "").split())
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"single-gap theorem-note draft missing section {section}")
    for phrase in REQUIRED_PHRASES:
        normalized_phrase = " ".join(phrase.replace("`", "").split())
        if normalized_phrase not in normalized:
            failures.append(f"single-gap theorem-note draft missing phrase {phrase!r}")
    for phrase in FORBIDDEN_PHRASES:
        normalized_phrase = " ".join(phrase.replace("`", "").split())
        if normalized_phrase in normalized:
            failures.append(f"single-gap theorem-note draft contains forbidden phrase {phrase!r}")
    for line_number, line in enumerate(text.splitlines(), start=1):
        normalized_line = " ".join(line.replace("`", "").split())
        if (
            "Close(row) iff strict q-grid containment" in normalized_line
            and "defer" not in normalized_line
        ):
            failures.append(
                "single-gap theorem-note draft contains undeferred global iff "
                f"language on line {line_number}"
            )


def main() -> int:
    repo_root = repo_root_from_script()
    failures: list[str] = []

    require_note(repo_root, failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "check_v2_6_single_gap_theorem_note_draft: "
        "checks=5, failed=0, "
        f"sections={len(REQUIRED_SECTIONS)}, "
        f"required_phrases={len(REQUIRED_PHRASES)}, "
        f"forbidden_phrases={len(FORBIDDEN_PHRASES)}, "
        "global_iff_guard=passed, "
        "theorem_note=necessary_only, public_theorem=defer, "
        "proof_note_hygiene=passed, mathematical_verification=not_claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
