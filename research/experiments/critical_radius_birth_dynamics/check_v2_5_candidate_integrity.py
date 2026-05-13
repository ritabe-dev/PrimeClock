#!/usr/bin/env python3
"""Verify PRC v2.5 candidate-package integrity."""

from __future__ import annotations

import argparse
import csv
import json
import tempfile
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[2]

THEOREM_NOTE = EXPERIMENT_DIR / "notes" / "prc_v2_5_theorem_candidate_note_v0_1.md"
RESEARCH_REVIEW_NOTE = (
    EXPERIMENT_DIR / "notes" / "prc_v2_5_research_review_note_v0_1.md"
)
CANDIDATE_README = EXPERIMENT_DIR / "candidate_README_v2_5_v0_1.md"
CANDIDATE_RESEARCH_README = EXPERIMENT_DIR / "candidate_research_README_v2_5_v0_1.md"
EXPERIMENT_README = EXPERIMENT_DIR / "README.md"
CANDIDATE_MANIFEST = EXPERIMENT_DIR / "candidate_bundle_manifest_v2_5_v0_1.json"
CANDIDATE_WORKFLOW = EXPERIMENT_DIR / "candidate_workflow_v2_5_v0_1.yml"
GATE_P_CHECKLIST_NOTE = (
    EXPERIMENT_DIR / "notes" / "prc_v2_5_gate_p_checklist_v0_1.md"
)
SCOPE_SUMMARY_CSV = (
    EXPERIMENT_DIR
    / "data"
    / "prc_v2_5_aperture_orbit_backtest_scope_summary_v0_1.csv"
)
B8_COMPARISON_CSV = (
    EXPERIMENT_DIR
    / "data"
    / "prc_v2_5_aperture_orbit_backtest_b8_comparison_v0_1.csv"
)
HULL_SUMMARY_CSV = (
    EXPERIMENT_DIR
    / "data"
    / "prc_v2_5_exact_hull_obstruction_summary_v0_1.csv"
)
DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_5_candidate_integrity_verification_v0_1.csv"
)

MAIN_CLAIM = (
    "In checked PRC transition scopes, capacity admits many false positives, "
    "while positive signed aperture-orbit margin separates close lifts from "
    "capacity non-close controls."
)
SUPPORT_CLAIM = (
    "In checked scopes, multi-component parent residual sets are exact-hull "
    "obstructed, and every checked close row has a single-gap precursor."
)
NONCLAIM_PHRASES = [
    "no B8 full graph",
    "no B8 public theorem",
    "no asymptotic law",
    "no general prediction theorem",
    "no public release",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    args = parser.parse_args()

    checks = verification_rows()
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_5_candidate_integrity: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows() -> list[dict[str, str]]:
    manifest = load_manifest()
    return [
        check_theorem_note_phrases(),
        check_research_review_decision(),
        check_candidate_readme_boundaries(),
        check_candidate_readme_dependency_terms(),
        check_candidate_readme_candidate_scope_terms(),
        check_candidate_readme_reviewer_setup(),
        check_source_only_hygiene_scope(),
        check_experiment_readme_reviewer_banner(),
        check_gate_p_checklist(),
        check_manifest_identity_and_allowlist(manifest),
        check_manifest_required_sources_exist(manifest),
        check_manifest_includes_reviewer_figures(manifest),
        check_historical_separator_counts(),
        check_b8_control_counts(),
        check_exact_hull_counts(),
    ]


def load_manifest() -> dict:
    return json.loads(CANDIDATE_MANIFEST.read_text(encoding="utf-8"))


def check_theorem_note_phrases() -> dict[str, str]:
    text = normalized_text(THEOREM_NOTE)
    required = [MAIN_CLAIM, SUPPORT_CLAIM, *NONCLAIM_PHRASES]
    missing = missing_phrases(text, required)
    return check_bool(
        "v2_5_theorem_note_claim_boundary_phrases",
        not missing,
        total=len(required),
        failed=len(missing),
    )


def check_research_review_decision() -> dict[str, str]:
    text = normalized_text(RESEARCH_REVIEW_NOTE)
    required = [
        "checked finite aperture-orbit separator",
        "source-only stress control",
        "checked support lemma",
        "package as candidate",
    ]
    missing = missing_phrases(text, required)
    return check_bool(
        "v2_5_research_review_gate_r_closed",
        not missing,
        total=len(required),
        failed=len(missing),
    )


def check_candidate_readme_boundaries() -> dict[str, str]:
    text = normalized_text(CANDIDATE_README) + "\n" + normalized_text(CANDIDATE_RESEARCH_README)
    required = [
        "internal candidate bundle",
        "candidate package",
        "not a public release",
        "v2.3.0",
        MAIN_CLAIM,
        SUPPORT_CLAIM,
        *NONCLAIM_PHRASES,
        "selected stress-control sample, not coverage",
        "finite exact signed containment certificate",
    ]
    missing = missing_phrases(text, required)
    return check_bool(
        "v2_5_candidate_readme_boundaries",
        not missing,
        total=len(required),
        failed=len(missing),
    )


def check_candidate_readme_dependency_terms() -> dict[str, str]:
    text = normalized_text(CANDIDATE_README) + "\n" + normalized_text(CANDIDATE_RESEARCH_README)
    required = [
        "v2.5 candidate uses v2.4 transition and phase diagnostics as inherited source support",
        "source-only means public excluded",
        "candidate-included means included in this internal candidate bundle",
        "candidate-excluded means intentionally absent from this internal candidate bundle",
        "v2.3 public theorem -> v2.4 inherited source diagnostics -> v2.5 candidate mechanism -> Gate P public decision",
    ]
    missing = missing_phrases(text, required)
    return check_bool(
        "v2_5_candidate_readme_dependency_terms",
        not missing,
        total=len(required),
        failed=len(missing),
    )


def check_candidate_readme_candidate_scope_terms() -> dict[str, str]:
    text = (
        normalized_text(CANDIDATE_README)
        + "\n"
        + normalized_text(CANDIDATE_RESEARCH_README)
    )
    required = [
        "source_only_research.files is the full-repo v2.5 artifact superset",
        "candidate_bundle_manifest_v2_5_v0_1.json is the candidate-included subset",
        "prc_v2_5_research_seed_note_v0_1.md",
        "prc_v2_5_deferred_review_resolution_v0_1.md",
        "candidate-excluded internal planning notes",
    ]
    missing = missing_phrases(text, required)
    return check_bool(
        "v2_5_candidate_readme_scope_terms",
        not missing,
        total=len(required),
        failed=len(missing),
    )


def check_candidate_readme_reviewer_setup() -> dict[str, str]:
    text = (
        normalized_text(CANDIDATE_README)
        + "\n"
        + normalized_text(CANDIDATE_RESEARCH_README)
    )
    required = [
        "cd research && python -m pip install -e .",
        "research/.venv/bin/python",
        "unzip -t -> candidate-integrity -> gate-c",
        "candidate-integrity",
        "gate-c",
        "bundle",
        "quick mode is full diagnostics",
        "full repository or a prepared checkout",
        "--manifest research/experiments/critical_radius_birth_dynamics/candidate_bundle_manifest_v2_5_v0_1.json",
    ]
    forbidden = [
        "unzip -t -> candidate-integrity -> gate-c -> quick optional",
        "reviewer-facing workflow modes are candidate-integrity, gate-c, quick, bundle, and source-only-hygiene",
        "External reviewers should use candidate-integrity, gate-c, quick, bundle, and source-only-hygiene",
    ]
    missing = missing_phrases(text, required)
    forbidden_found = [
        phrase for phrase in forbidden if phrase.lower() in text.lower()
    ]
    return check_bool(
        "v2_5_candidate_readme_reviewer_setup",
        not missing and not forbidden_found,
        total=len(required) + len(forbidden),
        failed=len(missing) + len(forbidden_found),
    )


def check_source_only_hygiene_scope() -> dict[str, str]:
    text = (
        normalized_text(CANDIDATE_README)
        + "\n"
        + normalized_text(CANDIDATE_RESEARCH_README)
        + "\n"
        + normalized_text(CANDIDATE_WORKFLOW)
    )
    required = [
        "full repo only v2.5 -> v2.3/public non-leak guard",
        "not the v2.5 candidate bundle manifest check",
        "not the v2.5 candidate manifest",
        "not a ZIP reviewer command",
        "This is intentionally the v2.3 candidate manifest and is only for the full repo leak guard",
    ]
    missing = missing_phrases(text, required)
    return check_bool(
        "v2_5_source_only_hygiene_scope",
        not missing,
        total=len(required),
        failed=len(missing),
    )


def check_experiment_readme_reviewer_banner() -> dict[str, str]:
    text = normalized_text(EXPERIMENT_README)
    required = [
        "PRC v2.5 candidate reviewer note",
        "legacy experiment index",
        "historical v2.3/v2.4 experiment context",
        "candidate_README_v2_5_v0_1.md",
        "not a public release",
    ]
    missing = missing_phrases(text, required)
    return check_bool(
        "v2_5_experiment_readme_reviewer_banner",
        not missing,
        total=len(required),
        failed=len(missing),
    )


def check_gate_p_checklist() -> dict[str, str]:
    text = normalized_text(GATE_P_CHECKLIST_NOTE)
    required = [
        "claim wording stable",
        "B8 boundary stable",
        "external reviewer can reproduce Gate C",
        "public README non-claims clear",
        "release metadata ready",
        "Zenodo DOI plan ready",
        "no B8 full graph",
        "no B8 public theorem",
        "does not authorize a public release",
        "selected stress-control sample, not coverage",
        "avoid general predictor wording",
        "finite exact aperture-orbit separator / certificate",
        "phase margin is an exact signed containment certificate, not a general predictor",
        "stress-control counts, not public evidence",
    ]
    missing = missing_phrases(text, required)
    return check_bool(
        "v2_5_gate_p_checklist_boundary",
        not missing,
        total=len(required),
        failed=len(missing),
    )


def check_manifest_includes_reviewer_figures(manifest: dict) -> dict[str, str]:
    sources = manifest_sources(manifest)
    required_sources = {
        "research/experiments/critical_radius_birth_dynamics/figures/v2_5/prc_v2_5_feature_ablation_v0_1.png",
        "research/experiments/critical_radius_birth_dynamics/figures/v2_5/prc_v2_5_margin_genesis_v0_1.png",
        "research/experiments/critical_radius_birth_dynamics/figures/v2_5/prc_v2_5_b8_aperture_orbit_heatmap_v0_1.png",
    }
    failures = sum(source not in sources for source in required_sources)
    failures += sum(not (REPO_ROOT / source).is_file() for source in required_sources)
    return check_bool(
        "v2_5_candidate_manifest_reviewer_figures",
        failures == 0,
        total=len(required_sources) * 2,
        failed=failures,
    )


def check_manifest_identity_and_allowlist(manifest: dict) -> dict[str, str]:
    allowed = set(manifest.get("allowed_path_markers", []))
    required_allowed = {"v2_5", "prc_v2_5", "check_v2_5", "v2_4", "prc_v2_4"}
    failures = 0
    failures += int(manifest.get("id") != "prc_v2_5_candidate_bundle_v0_1")
    failures += int(manifest.get("base_public_release") != "v2.3.0")
    failures += int(manifest.get("public_release") is not False)
    failures += int(not required_allowed.issubset(allowed))
    return check_bool(
        "v2_5_candidate_manifest_identity_allowlist",
        failures == 0,
        total=4,
        failed=failures,
    )


def check_manifest_required_sources_exist(manifest: dict) -> dict[str, str]:
    sources = manifest_sources(manifest)
    required_sources = {
        "research/experiments/critical_radius_birth_dynamics/candidate_README_v2_5_v0_1.md",
        "research/experiments/critical_radius_birth_dynamics/candidate_research_README_v2_5_v0_1.md",
        "research/experiments/critical_radius_birth_dynamics/candidate_bundle_manifest_v2_5_v0_1.json",
        "research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_5_v0_1.yml",
        "research/experiments/critical_radius_birth_dynamics/check_v2_5_candidate_integrity.py",
        "research/experiments/critical_radius_birth_dynamics/check_v2_5_gate_p_readiness.py",
        "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_theorem_candidate_note_v0_1.md",
        "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_candidate_fixed_note_v0_1.md",
        "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_gate_p_checklist_v0_1.md",
        "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_reviewer_glossary_v0_1.md",
        "research/experiments/critical_radius_birth_dynamics/data/prc_v2_5_aperture_orbit_backtest_scope_summary_v0_1.csv",
        "research/experiments/critical_radius_birth_dynamics/data/prc_v2_5_aperture_orbit_backtest_b8_comparison_v0_1.csv",
        "research/experiments/critical_radius_birth_dynamics/data/prc_v2_5_exact_hull_obstruction_summary_v0_1.csv",
        "research/experiments/critical_radius_birth_dynamics/data/prc_v2_5_gate_p_summary_tables_v0_1.csv",
    }
    failures = sum(source not in sources for source in required_sources)
    failures += sum(not (REPO_ROOT / source).is_file() for source in required_sources)
    return check_bool(
        "v2_5_candidate_manifest_required_sources",
        failures == 0,
        total=len(required_sources) * 2,
        failed=failures,
    )


def check_historical_separator_counts() -> dict[str, str]:
    rows = read_csv_dicts(SCOPE_SUMMARY_CSV)
    close_count = sum(int(row["close_count"]) for row in rows)
    birth_count = sum(int(row["birth_count"]) for row in rows)
    capacity_nonclose = sum(int(row["capacity_nonclose_families"]) for row in rows)
    nonclose_positive = sum(int(row["nonclose_positive_margin_count"]) for row in rows)
    nonbirth_close = sum(int(row["nonbirth_close_count"]) for row in rows)
    failures = 0
    failures += int(close_count != 770)
    failures += int(birth_count != 770)
    failures += int(capacity_nonclose != 2430)
    failures += int(nonclose_positive != 0)
    failures += int(nonbirth_close != 0)
    return check_bool(
        "v2_5_historical_aperture_orbit_counts",
        failures == 0,
        total=5,
        failed=failures,
    )


def check_b8_control_counts() -> dict[str, str]:
    values = {
        (row["cohort"], row["metric"]): row["value"]
        for row in read_csv_dicts(B8_COMPARISON_CSV)
    }
    expected = {
        ("B8_sibling_control", "birth_close_count"): "32",
        ("B8_sibling_control", "sibling_nonbirth_count"): "576",
        ("B8_sibling_control", "birth_close_positive_margin_count"): "32",
        ("B8_sibling_control", "sibling_nonbirth_positive_margin_count"): "0",
        ("B8_matched_nonbirth_control", "matched_nonbirth_count"): "64",
        ("B8_matched_nonbirth_control", "matched_positive_margin_count"): "0",
    }
    failures = sum(values.get(key) != value for key, value in expected.items())
    return check_bool(
        "v2_5_b8_stress_control_counts",
        failures == 0,
        total=len(expected),
        failed=failures,
    )


def check_exact_hull_counts() -> dict[str, str]:
    rows = {row["scope"]: row for row in read_csv_dicts(HULL_SUMMARY_CSV)}
    expected_multi = {
        "B4_to_B5_full": 65,
        "B5_to_B6_full": 913,
        "B6_to_B7_full": 13785,
    }
    failures = 0
    for scope, expected in expected_multi.items():
        row = rows.get(scope)
        failures += int(row is None)
        if row is None:
            continue
        failures += int(int(row["multi_component_family_count"]) != expected)
        failures += int(int(row["hull_obstructed_multi_count"]) != expected)
        failures += int(int(row["multi_component_close_count"]) != 0)
        failures += int(row["status"] != "checked_hull_obstruction")
        failures += int(int(row["b8_checked_close_single_gap_count"]) != 32)
    return check_bool(
        "v2_5_exact_hull_support_counts",
        failures == 0,
        total=len(expected_multi) * 5,
        failed=failures,
    )


def manifest_sources(manifest: dict) -> set[str]:
    sources = {entry["source"] for entry in manifest.get("root_file_map", [])}
    sources.update(manifest.get("root_files", []))
    sources.update(manifest.get("research_files", []))
    return sources


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalized_text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").replace("`", "").split())


def missing_phrases(text: str, required: list[str]) -> list[str]:
    normalized = text.lower()
    return [phrase for phrase in required if phrase.lower() not in normalized]


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
