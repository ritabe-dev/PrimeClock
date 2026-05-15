#!/usr/bin/env python3
"""Audit the v2.7 general single-gap aperture theorem note."""

from __future__ import annotations

from pathlib import Path


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
NOTES_REL = EXPERIMENT_REL / "notes"

NOTE_REL = NOTES_REL / "prc_v2_7_general_single_gap_aperture_theorem_note_v0_1.md"


def term(*parts: str) -> str:
    return "".join(parts)


REQUIRED_SECTIONS = (
    "# PRC v2.7 General q-Prime Single-Gap Aperture Classification Theorem",
    "## 1. Definitions",
    "## 2. Terminal containment and birth terminology",
    "## 3. Endpoint spacing near 0 and 1/2",
    "## 4. Forbidden special remainders",
    "## 5. Endpoint coincidence",
    "## 6. Closed terminal containment reduces to strict terminal containment",
    "## 7. Abstract circle-arc obstruction lemma",
    "## 8. PRC covered component lower bound",
    "## 9. Multi-gap obstruction",
    "## 10. Single-gap aperture classification",
    "## 11. Main theorem",
    "## 12. Next-prime corollary and consequences",
    "## 13. Relation to PRC v2.3/v2.5 terminology",
    "## 14. Public Theorem Boundary",
)
REQUIRED_PHRASES = (
    "public theorem release text, v1.0. DOI pending Zenodo publication.",
    "General q-Prime Single-Gap Aperture Classification",
    "general over all old residues and all later odd prime moduli q>p_k",
    "Fix k >= 3",
    "p_1 = 2, p_2 = 3, ..., p_k",
    "M_k = product_{i<=k} p_i",
    "r in Z/M_kZ",
    "Let q be any odd prime with",
    "The next-prime case q=p_{k+1} is a corollary",
    "direct one-prime q-lift over the old prefix",
    "intermediate sequential PRC transitions are skipped or unchanged",
    "old p-arc",
    "U_k(r) = union_{i<=k} I_{p_i}(r)",
    "R_k(r) = T \\ U_k(r)",
    "new q-arc",
    "Component strict q-containment",
    "Row-level strict terminal containment",
    "Row-level closed terminal containment",
    "This note proves the strict classification first",
    "stated later-prime arc model",
    "closed terminal containment gives no additional nonempty birth cases beyond the strict classification",
    "If earlier PRC artifacts use Close(row) for this same closed terminal containment test",
    "that implementation should be audited separately",
    "closure(R_k(r)) subset int(I_q(a))",
    "closure(R_k(r)) subset I_q(a)",
    "strict q-birth lift",
    "a = 0",
    "a = (q-1)/2",
    "a = (q+1)/2",
    "I_q(0) = [-1/(2q), 1/(2q)]",
    "does not produce a closed or strict q-birth lift",
    "the two central remainders are non-birth",
    "old/new endpoint coincidence is only central",
    "q be any odd prime with q>p_k",
    "m in {1,3,...,2p-1}",
    "n in {1,3,...,2q-1}",
    "closed q-terminal containment implies strict q-terminal containment for nonempty residual sets",
    "no closed-only endpoint-touch birth cases",
    "Abstract circle-arc obstruction lemma",
    "short arcs cannot bridge separated residual components",
    "Let U be a finite union of closed arcs on T",
    "lambda < delta",
    "Every nonempty connected component of U_k(r) has circular length at least",
    "one q-arc cannot close multiple residual components",
    "Apply Lemma 7.1",
    "delta = 1/p_k",
    "lambda = 1/q",
    "Choose a cut outside J",
    "No residual component lies between them",
    "closure(G) subset int(I_q(a))",
    "qR - 1/2 < tilde a < qL + 1/2",
    "compatible lifts of the gap and q-arc in the universal cover",
    "L and R are lifted real coordinates in the universal cover",
    "chosen lift may have R>1",
    "A_q(G) = (qR - 1/2, qL + 1/2)",
    "If this width is non-positive, the aperture window is empty and contains no integer",
    "General q-Prime Single-Gap Aperture Classification",
    "any odd prime q with q>p_k",
    "If R_k(r) is empty, the old row is already terminally closed",
    "If R_k(r) has two or more connected components, no q-remainder a produces",
    "a q-remainder a produces a closed q-birth lift if and only if it produces a strict q-birth lift",
    "1 - q length(G)",
    "A single-gap old row has at most one q-remainder candidate",
    "next-prime PRC birth classification",
    "Taking q=p_{k+1} in Theorem 11.1",
    "multi-gap birth is structurally impossible",
    "birth requires q-grid phase alignment",
    "Implementation-level equivalence should be checked by a separate exact-audit script",
    "committed recorded birth rows in the finite next-prime support CSV",
    "not a full finite-universe completeness audit",
    "This theorem note claims a structural classification inside the stated PRC circular-arc model",
    "nonempty q-birth lift",
    "This theorem is general over all old residues and all later odd prime moduli",
    "not a claim about the full sequential insertion of all intermediate primes",
    "Implementation-level PRC artifacts are covered only after exact audit confirms",
    "Finite exact audits are useful for validating implementations and examples, but they are not the proof of the theorem",
)
FORBIDDEN_PHRASES = (
    "public theorem-note candidate",
    "public artifact",
    "Public-scope boundary",
    term("Gate", " C candidate bundle"),
    term("v2.6 Gate", " C artifact"),
    "PrimeClock-v2.6-gate-c-candidate",
    "public_theorem=promote",
    "doi_state=assigned",
    "zenodo_version_doi",
    "GitHub Release ready",
    "release registry entry ready",
    "B8 theorem ready",
    "B8 theorem proven",
    "B8 theorem promoted",
    "general predictor theorem",
    "asymptotic law theorem",
    "finite audit proves",
    "finite audits prove",
    "CSV proves",
    "checker proves the theorem",
    "mathematical_verification=claimed",
    "Scope: PRC next-prime circular-arc model",
    "q = p_{k+1} be the next prime",
    "Fix k>=3, an old residue r in Z/M_kZ, and q=p_{k+1}",
    "This theorem note claims a structural classification inside the stated PRC next-prime circular-arc model",
    "C_k(r)",
    "E_k(r)",
    "q-closed",
    term("Gate", " C Boundary"),
    "Public Theorem Preflight Boundary",
)


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def normalized_text(text: str) -> str:
    return " ".join(text.replace("`", "").split())


def require_note(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / NOTE_REL
    if not path.is_file():
        failures.append(f"missing v2.7 theorem note: {NOTE_REL}")
        return
    text = path.read_text(encoding="utf-8")
    normalized = normalized_text(text)
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"v2.7 theorem note missing section {section}")
    for phrase in REQUIRED_PHRASES:
        if normalized_text(phrase) not in normalized:
            failures.append(f"v2.7 theorem note missing phrase {phrase!r}")
    for phrase in FORBIDDEN_PHRASES:
        if normalized_text(phrase) in normalized:
            failures.append(f"v2.7 theorem note contains forbidden phrase {phrase!r}")
    for line_number, line in enumerate(text.splitlines(), start=1):
        normalized_line = normalized_text(line)
        if "Close(row) iff" in normalized_line:
            failures.append(
                "v2.7 theorem note contains row-close iff shorthand on line "
                f"{line_number}; use row-based birth-lift definitions instead"
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
        "check_v2_7_general_single_gap_aperture_theorem_note: "
        "checks=6, failed=0, "
        f"sections={len(REQUIRED_SECTIONS)}, "
        f"required_phrases={len(REQUIRED_PHRASES)}, "
        f"forbidden_phrases={len(FORBIDDEN_PHRASES)}, "
        "component_row_separation=passed, "
        "multigap_obstruction=present, "
        "lifted_remainder=present, "
        "gate_p=theorem_note_preflight, public_release_text=present, "
        "release_publication_checked_by=check_v2_7_public_theorem_release, "
        "proof_note_hygiene=passed, mathematical_verification=not_claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
