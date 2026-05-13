#!/usr/bin/env python3
"""Verify PRC v2.5 Gate P dry-run wording and reviewer aids."""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).resolve().parent

CANDIDATE_README = EXPERIMENT_DIR / "candidate_README_v2_5_v0_1.md"
CANDIDATE_RESEARCH_README = EXPERIMENT_DIR / "candidate_research_README_v2_5_v0_1.md"
THEOREM_NOTE = EXPERIMENT_DIR / "notes" / "prc_v2_5_theorem_candidate_note_v0_1.md"
GATE_P_CHECKLIST = EXPERIMENT_DIR / "notes" / "prc_v2_5_gate_p_checklist_v0_1.md"
GLOSSARY_NOTE = EXPERIMENT_DIR / "notes" / "prc_v2_5_reviewer_glossary_v0_1.md"
MATH_FRAMING_NOTE = (
    EXPERIMENT_DIR / "notes" / "prc_v2_5_gate_p_mathematical_framing_v0_1.md"
)
EXTERNAL_SUMMARY_NOTE = (
    EXPERIMENT_DIR / "notes" / "prc_v2_5_external_reviewer_summary_v0_1.md"
)
PUBLIC_THEOREM_DRAFT = (
    EXPERIMENT_DIR / "notes" / "prc_v2_5_public_theorem_draft_v0_1.md"
)
PUBLIC_README_DRAFT = (
    EXPERIMENT_DIR / "notes" / "prc_v2_5_public_readme_draft_v0_1.md"
)
PUBLICATION_PLAN_NOTE = (
    EXPERIMENT_DIR / "notes" / "prc_v2_5_publication_plan_v0_1.md"
)
PUBLIC_THEOREM_README_V1 = (
    EXPERIMENT_DIR / "notes" / "prc_v2_5_public_theorem_readme_v1_0.md"
)
PUBLIC_THEOREM_RELEASE_NOTES_V1 = (
    EXPERIMENT_DIR / "notes" / "prc_v2_5_public_theorem_release_notes_v1_0.md"
)
SUMMARY_CSV = EXPERIMENT_DIR / "data" / "prc_v2_5_gate_p_summary_tables_v0_1.csv"
DECISION_TABLE_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_gate_p_decision_table_v0_1.csv"
)
DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_5_gate_p_readiness_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    args = parser.parse_args()

    checks = verification_rows()
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_5_gate_p_readiness: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows() -> list[dict[str, str]]:
    return [
        check_certificate_wording(),
        check_b8_boundary(),
        check_obstruction_boundary(),
        check_reviewer_glossary(),
        check_summary_counts(),
        check_zip_reviewer_path(),
        check_gate_p_default(),
        check_mathematical_framing_note(),
        check_external_reviewer_summary(),
        check_gate_p_decision_table(),
        check_public_theorem_draft(),
        check_public_readme_draft(),
        check_publication_plan_note(),
        check_public_theorem_readme_v1(),
        check_public_theorem_release_notes_v1(),
    ]


def check_certificate_wording() -> dict[str, str]:
    text = combined_text(CANDIDATE_README, CANDIDATE_RESEARCH_README, THEOREM_NOTE)
    required = [
        "finite exact signed containment certificate",
        "terminal containment certificate",
        "not an independent general predictor",
        "capacity alone leaves many false positives",
    ]
    forbidden = ["A general predictor for prime-prefix births"]
    return phrase_check("v2_5_gate_p_certificate_wording", text, required, forbidden)


def check_b8_boundary() -> dict[str, str]:
    text = combined_text(CANDIDATE_README, CANDIDATE_RESEARCH_README, THEOREM_NOTE, GATE_P_CHECKLIST)
    required = [
        "selected stress-control sample",
        "not coverage, recall, or holdout validation",
        "k8 sample overlap",
        "B8 evidence is not a proof that the separator generalizes",
        "no B8 full graph",
        "no B8 public theorem",
    ]
    forbidden: list[str] = []
    return phrase_check("v2_5_gate_p_b8_boundary", text, required, forbidden)


def check_obstruction_boundary() -> dict[str, str]:
    text = combined_text(GATE_P_CHECKLIST, GLOSSARY_NOTE, THEOREM_NOTE)
    required = [
        "sibling_dominated",
        "split_history",
        "underreach",
        "wrong_side",
        "finite diagnostics",
        "not a layer-general causal taxonomy",
    ]
    return phrase_check("v2_5_gate_p_obstruction_boundary", text, required, [])


def check_reviewer_glossary() -> dict[str, str]:
    text = normalized_text(GLOSSARY_NOTE)
    required = [
        "capacity",
        "phase margin",
        "aperture tension",
        "close",
        "birth",
        "near-miss",
        "source-only",
        "candidate-included",
        "stress control",
    ]
    return phrase_check("v2_5_gate_p_reviewer_glossary", text, required, [])


def check_summary_counts() -> dict[str, str]:
    rows = read_csv_dicts(SUMMARY_CSV)
    values = {
        (row["section"], row["scope"], row["metric"]): row["value"]
        for row in rows
    }
    expected = {
        ("historical_totals", "all", "close_or_birth_rows"): "770",
        ("historical_totals", "all", "capacity_nonclose_families"): "2430",
        ("historical_totals", "all", "nonclose_positive_margin_rows"): "0",
        ("exact_hull", "B4_to_B5_full", "hull_obstructed_multi_component_families"): "65",
        ("exact_hull", "B5_to_B6_full", "hull_obstructed_multi_component_families"): "913",
        ("exact_hull", "B6_to_B7_full", "hull_obstructed_multi_component_families"): "13785",
        ("B8_stress_control", "selected_panel", "selected_close_rows"): "32",
        ("B8_stress_control", "selected_panel", "sibling_nonbirth_controls"): "576",
        ("B8_stress_control", "selected_panel", "matched_nonbirth_controls"): "64",
        ("B8_stress_control", "selected_panel", "k8_sample_overlap"): "1",
    }
    failures = sum(values.get(key) != value for key, value in expected.items())
    return check_bool(
        "v2_5_gate_p_summary_counts",
        failures == 0,
        total=len(expected),
        failed=failures,
    )


def check_zip_reviewer_path() -> dict[str, str]:
    text = combined_text(CANDIDATE_README, CANDIDATE_RESEARCH_README)
    required = [
        "unzip -t -> candidate-integrity -> gate-c",
        "ZIP reviewer-facing workflow modes are candidate-integrity, gate-c, and bundle",
        "quick mode is full diagnostics",
        "source-only-hygiene mode is a full repo only",
    ]
    forbidden = [
        "unzip -t -> candidate-integrity -> gate-c -> quick optional",
        "source-only-hygiene` mode is a v2.5 -> v2.3/public non-leak guard",
    ]
    return phrase_check("v2_5_gate_p_zip_reviewer_path", text, required, forbidden)


def check_gate_p_default() -> dict[str, str]:
    text = combined_text(GATE_P_CHECKLIST)
    required = [
        "does not authorize a public release",
        "default Gate P decision remains not ready",
        "release metadata ready",
        "Zenodo DOI plan ready",
    ]
    return phrase_check("v2_5_gate_p_default_not_ready", text, required, [])


def check_mathematical_framing_note() -> dict[str, str]:
    text = normalized_text(MATH_FRAMING_NOTE)
    required = [
        "finite exact signed containment certificate",
        "not a public theorem",
        "not a general predictor",
        "checked finite scopes",
        "B8 is a selected stress-control sample only",
        "not coverage, recall, holdout validation",
        "exact-hull obstruction is supporting structure",
        "public theorem decision remains not ready",
    ]
    return phrase_check("v2_5_gate_p_mathematical_framing", text, required, [])


def check_external_reviewer_summary() -> dict[str, str]:
    text = normalized_text(EXTERNAL_SUMMARY_NOTE)
    required = [
        "Definitions",
        "What Is Checked",
        "What Is Not Claimed",
        "Exact Counts",
        "Reproduction Commands",
        "Limitations",
        "not a public theorem",
        "not a general predictor",
        "B8 remains a selected stress-control sample only",
        "Historical close or birth rows: 770",
        "Capacity non-close families: 2430",
        "Non-close positive-margin rows: 0",
    ]
    return phrase_check("v2_5_gate_p_external_summary", text, required, [])


def check_gate_p_decision_table() -> dict[str, str]:
    rows = read_csv_dicts(DECISION_TABLE_CSV)
    values = {row["candidate"]: row["decision"] for row in rows}
    expected = {
        "finite certificate": "ready",
        "public theorem": "ready for scoped finite theorem review",
        "B8 generalization": "defer",
        "general predictor": "reject for v2.5",
        "asymptotic law": "reject for v2.5",
    }
    failures = sum(values.get(key) != value for key, value in expected.items())
    return check_bool(
        "v2_5_gate_p_decision_table",
        failures == 0,
        total=len(expected),
        failed=failures,
    )


def check_public_theorem_draft() -> dict[str, str]:
    text = normalized_text(PUBLIC_THEOREM_DRAFT)
    required = [
        "Definitions",
        "Finite Universe",
        "Theorem",
        "Exhaustive Enumeration Certificate",
        "Separator Audit",
        "Support Lemma",
        "B8 Non-Claim",
        "Reproduction",
        "Limitations",
        "finite exact aperture-orbit separator theorem",
        "recorded complete transition scopes",
        "terminal containment certificate",
        "B8 selected stress-control only",
        "not a general predictor",
    ]
    forbidden = ["The separator generalizes to B8"]
    return phrase_check("v2_5_public_theorem_draft", text, required, forbidden)


def check_public_readme_draft() -> dict[str, str]:
    text = normalized_text(PUBLIC_README_DRAFT)
    required = [
        "What Is Proved",
        "What Is Not Proved",
        "Exact Counts",
        "How To Reproduce",
        "Limitations",
        "finite exact aperture-orbit separator theorem",
        "terminal containment certificate",
        "not a general predictor",
        "no B8 theorem",
        "no asymptotic law",
        "B8 selected stress-control only",
    ]
    forbidden = ["A general predictor for prime-prefix births"]
    return phrase_check("v2_5_public_readme_draft", text, required, forbidden)


def check_publication_plan_note() -> dict[str, str]:
    text = normalized_text(PUBLICATION_PLAN_NOTE)
    required = [
        "repo tag + release notes + public theorem README + verifier command",
        "v2.5.0-prc-public-theorem",
        "PRC v2.5: finite aperture-orbit separator theorem",
        "PrimeClock-v2.5-public-theorem-review-v0.1.zip",
        "PrimeClock-v2.5-public-theorem-v1.0.zip",
        "B4->B5, B5->B6, and B6->B7 recorded complete transition scopes",
        "Close(row) iff m(row) > 0",
        "not a general predictor",
        "not a B8 theorem",
        "not an asymptotic law",
        "Do not write a DOI into README or release notes until the DOI exists",
        "release/public/release_config.json remains the v2.3.0 release config",
    ]
    forbidden = [
        "upload this plan to Zenodo now",
        "create the GitHub Release now",
    ]
    return phrase_check("v2_5_publication_plan", text, required, forbidden)


def check_public_theorem_readme_v1() -> dict[str, str]:
    text = normalized_text(PUBLIC_THEOREM_README_V1)
    required = [
        "public theorem README text for v2.5.0-prc-public-theorem",
        "finite exact aperture-orbit separator theorem",
        "B4->B5",
        "B5->B6",
        "B6->B7",
        "Close(row) iff m(row) > 0",
        "not a general predictor",
        "Checked lift rows",
        "533,690",
        "Non-close positive-margin rows",
        "0",
        "check_v2_5_public_theorem_integrity: checks=9, failed=0",
        "does not independently regenerate the full PRC transition universe from first principles",
        "no B8 theorem",
        "no asymptotic law",
        "10.5281/zenodo.20154561",
        "release-specific CITATION.cff",
    ]
    forbidden = [
        "B8 full graph is included",
        "general predictor theorem",
    ]
    return phrase_check("v2_5_public_theorem_readme_v1", text, required, forbidden)


def check_public_theorem_release_notes_v1() -> dict[str, str]:
    text = normalized_text(PUBLIC_THEOREM_RELEASE_NOTES_V1)
    required = [
        "release notes text for v2.5.0-prc-public-theorem",
        "PRC v2.5: finite aperture-orbit separator theorem",
        "v2.5.0-prc-public-theorem",
        "Close(row) iff m(row) > 0",
        "finite exact terminal containment certificate",
        "not a general predictor",
        "check_v2_5_public_theorem_integrity: checks=9, failed=0",
        "checked lift rows 533690",
        "non-close positive-margin rows 0",
        "B8 theorem",
        "B8 full graph",
        "general predictor",
        "asymptotic law",
        "Version DOI: 10.5281/zenodo.20154561",
        "release-specific CITATION.cff",
    ]
    forbidden = [
        "B8 theorem is proved",
        "general predictor is proved",
    ]
    return phrase_check(
        "v2_5_public_theorem_release_notes_v1",
        text,
        required,
        forbidden,
    )


def combined_text(*paths: Path) -> str:
    return "\n".join(normalized_text(path) for path in paths)


def normalized_text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").replace("`", "").split())


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def phrase_check(
    name: str,
    text: str,
    required: list[str],
    forbidden: list[str],
) -> dict[str, str]:
    normalized = text.lower()
    missing = [phrase for phrase in required if phrase.lower() not in normalized]
    forbidden_found = [
        phrase for phrase in forbidden if phrase.lower() in normalized
    ]
    failed = len(missing) + len(forbidden_found)
    return check_bool(
        name,
        failed == 0,
        total=len(required) + len(forbidden),
        failed=failed,
    )


def check_bool(name: str, passed: bool, *, total: int, failed: int) -> dict[str, str]:
    return {
        "check": name,
        "total": str(total),
        "passed": str(max(total - failed, 0)),
        "failed": str(failed),
        "status": "pass" if passed else "fail",
    }


def write_checks(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["check", "total", "passed", "failed", "status"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
