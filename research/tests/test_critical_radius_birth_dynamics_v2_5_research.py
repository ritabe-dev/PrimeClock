from __future__ import annotations

import importlib.util
import subprocess
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

import pytest


EXPERIMENT_DIR = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "critical_radius_birth_dynamics"
)
REPO_ROOT = EXPERIMENT_DIR.parents[2]
WORKFLOW_ENGINE = REPO_ROOT / "scripts" / "verify_candidate_workflow.py"
V2_5_WORKFLOW_CONFIG = EXPERIMENT_DIR / "candidate_workflow_v2_5_v0_1.yml"

if str(EXPERIMENT_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_DIR))


def _load_module(module_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(module_name, EXPERIMENT_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v2_5_residual_dynamics = _load_module(
    "critical_radius_birth_dynamics_v2_5_residual_dynamics",
    "v2_5_residual_dynamics.py",
)
v2_5_lineage_grammar = _load_module(
    "critical_radius_birth_dynamics_v2_5_lineage_grammar",
    "v2_5_lineage_grammar.py",
)
v2_5_obstruction = _load_module(
    "critical_radius_birth_dynamics_v2_5_obstruction",
    "v2_5_obstruction_classification.py",
)
v2_5_feature_ablation = _load_module(
    "critical_radius_birth_dynamics_v2_5_feature_ablation",
    "v2_5_feature_ablation.py",
)
v2_5_margin_genesis = _load_module(
    "critical_radius_birth_dynamics_v2_5_margin_genesis",
    "v2_5_margin_genesis.py",
)
v2_5_prefix_grammar = _load_module(
    "critical_radius_birth_dynamics_v2_5_prefix_grammar",
    "v2_5_prefix_grammar.py",
)
v2_5_obstruction_refinement = _load_module(
    "critical_radius_birth_dynamics_v2_5_obstruction_refinement",
    "v2_5_obstruction_refinement.py",
)
v2_5_b8_probe = _load_module(
    "critical_radius_birth_dynamics_v2_5_b8_probe",
    "v2_5_b8_targeted_probe.py",
)
v2_5_b8_aperture_orbit = _load_module(
    "critical_radius_birth_dynamics_v2_5_b8_aperture_orbit",
    "v2_5_b8_aperture_orbit_probe.py",
)
v2_5_b8_control_calibration = _load_module(
    "critical_radius_birth_dynamics_v2_5_b8_control_calibration",
    "v2_5_b8_control_calibration.py",
)
v2_5_aperture_orbit_backtest = _load_module(
    "critical_radius_birth_dynamics_v2_5_aperture_orbit_backtest",
    "v2_5_aperture_orbit_backtest.py",
)
v2_5_exact_hull_obstruction = _load_module(
    "critical_radius_birth_dynamics_v2_5_exact_hull_obstruction",
    "v2_5_exact_hull_obstruction.py",
)


def test_v2_5_residual_dynamics_lineage_roles():
    rows = v2_5_residual_dynamics.read_residual_state_transition_csv()
    final_rows = [
        row for row in rows if row.layer_k == _child_k_from_scope(row.scope)
    ]
    roles = Counter(row.lineage_role for row in final_rows)

    assert roles["close"] == 770
    assert roles["capacity_nonclose"] > 0
    assert roles["near_miss"] > 0
    assert all(row.is_close and row.is_birth for row in final_rows if row.lineage_role == "close")
    assert all(not row.is_close for row in final_rows if row.lineage_role != "close")
    assert all(
        Fraction(row.phase_margin) > 0
        for row in final_rows
        if row.lineage_role == "close"
    )


def test_v2_5_lineage_grammar_has_comparable_groups():
    rows = v2_5_lineage_grammar.read_lineage_grammar_csv()
    roles = {row.lineage_role for row in rows}

    assert {"close", "nonclose", "near_miss", "capacity_nonclose"}.issubset(roles)
    assert any(row.diagnostic_role == "dominant" for row in rows)
    assert any(row.diagnostic_role == "rare" for row in rows)


def test_v2_5_obstruction_keeps_close_rows_clean():
    rows = v2_5_obstruction.read_obstruction_class_csv()
    counts = Counter(row.obstruction_class for row in rows)

    assert all(row.obstruction_class == "none" for row in rows if row.is_close)
    assert all(row.obstruction_class != "none" for row in rows if not row.is_close)
    assert counts["phase_obstruction"] > 0
    assert counts["near_miss_obstruction"] > 0


def test_v2_5_feature_ablation_records_residual_dynamics_comparison():
    rows = v2_5_feature_ablation.read_feature_ablation_csv()
    by_feature = {row.feature_set: row for row in rows if row.scope == "all"}

    assert by_feature["phase margin only"].top_k_hit_rate >= by_feature["width only"].top_k_hit_rate
    assert by_feature["phase margin only"].top_k_hit_rate >= by_feature["capacity only"].top_k_hit_rate
    assert by_feature["state + grammar + phase margin"].candidate_count == by_feature["width only"].candidate_count


def test_v2_5_prefix_grammar_excludes_terminal_close():
    rows = v2_5_prefix_grammar.read_prefix_lineage_grammar_csv()
    enrichment = v2_5_prefix_grammar.read_prefix_grammar_enrichment_csv()

    assert all("close" not in row.prefix_transition_sequence.split(">") for row in rows)
    assert any(Fraction(row.enrichment_ratio) > 1 for row in enrichment)


def test_v2_5_margin_genesis_counterfactual_pairs():
    rows = v2_5_margin_genesis.read_prefix_margin_genesis_csv()
    counterfactual = v2_5_margin_genesis.read_close_nearmiss_counterfactual_csv()

    assert sum(row.is_close for row in rows) == 770
    assert len(counterfactual) == 770
    assert all(row.prefix_sequence_match for row in counterfactual)
    assert all(row.prefix_component_delta_match for row in counterfactual)
    assert all(Fraction(row.margin_gap) > 0 for row in counterfactual)


def test_v2_5_refined_obstruction_is_not_single_bucket():
    rows = v2_5_obstruction_refinement.read_refined_obstruction_csv()
    nonclose = [row for row in rows if row.refined_obstruction != "none"]
    buckets = Counter(row.refined_obstruction for row in nonclose)

    assert all(row.refined_obstruction == "none" for row in rows if row.lineage_role == "close")
    assert len(buckets) >= 3
    assert buckets["unclassified"] == 0


def test_v2_5_b8_targeted_probe_is_bounded_source_only():
    rows = v2_5_b8_probe.read_b8_high_potential_probe_csv()
    parents = {row.parent_residue for row in rows}

    assert len(parents) == 200
    assert len(rows) == 200 * 19
    assert all(1 <= row.phase_rank <= 19 for row in rows)
    assert Counter(row.transition_label for row in rows)["trim"] > 0


def test_v2_5_b8_aperture_orbit_recovers_diverse_source_only_panel():
    rows = v2_5_b8_aperture_orbit.read_b8_aperture_orbit_probe_csv()
    failure = v2_5_b8_aperture_orbit.read_b8_failure_forensics_csv()
    summary = v2_5_b8_aperture_orbit.read_b8_aperture_orbit_summary_csv()
    birth_audit = v2_5_b8_aperture_orbit.read_b8_birth_overlap_audit_csv()
    parents = {row.parent_residue for row in rows}

    assert len(rows) == len(parents) * 19
    assert len({row.parent_residual_measure for row in rows}) > 1
    assert sum(row.is_close for row in rows) == sum(
        Fraction(row.phase_margin) > 0 for row in rows
    )
    assert sum(row.is_close for row in rows) > 0
    assert Counter(row.transition_label for row in failure)["close"] == 0
    assert {
        row.metric: row.value
        for row in summary
        if row.selection_group == "capacity_top_200"
    }["close_count"] == "0"
    assert len(birth_audit) == 32
    assert all(row.exact_b8_birth for row in birth_audit)
    assert all(row.parent_uncovered_exact for row in birth_audit)
    assert all(row.child_covered_exact for row in birth_audit)
    assert all(row.child_projects_to_parent for row in birth_audit)
    assert all(row.parent_gap_count_exact == 1 for row in birth_audit)
    assert all(row.child_gap_count_exact == 0 for row in birth_audit)


def test_v2_5_b8_control_calibration_adds_sibling_and_matched_controls():
    siblings = v2_5_b8_control_calibration.read_b8_sibling_control_csv()
    matched = v2_5_b8_control_calibration.read_b8_matched_nonbirth_control_csv()
    overlap = v2_5_b8_control_calibration.read_b8_control_overlap_audit_csv()
    summary = v2_5_b8_control_calibration.read_b8_control_calibration_summary_csv()
    by_parent = {}
    for row in siblings:
        by_parent.setdefault(row.parent_residue, []).append(row)

    assert len(by_parent) == 32
    assert all(len(rows) == 19 for rows in by_parent.values())
    assert all(
        sum(row.sibling_role == "birth_close" for row in rows) == 1
        for rows in by_parent.values()
    )
    assert all(
        Fraction(row.phase_margin) > 0
        for row in siblings
        if row.sibling_role == "birth_close"
    )
    assert all(
        Fraction(row.phase_margin) <= 0
        for row in siblings
        if row.sibling_role == "sibling_nonbirth"
    )
    assert len(matched) == 64
    assert all(row.control_capacity_pass for row in matched)
    assert all(Fraction(row.control_phase_margin) <= 0 for row in matched)
    assert all(not row.control_child_covered_exact for row in matched)
    assert len({row.control_parent_residual_measure for row in matched}) > 1
    assert len({row.control_reflection_orbit for row in matched}) > 1
    assert len(overlap) == 200
    assert all(row.calibration_role == "sample_overlap_only_not_recall" for row in overlap)
    assert {
        row.metric: row.value
        for row in summary
    }["k8_sample_rows"] == "200"


def test_v2_5_aperture_orbit_backtest_calibrates_historical_scopes():
    scope_rows = v2_5_aperture_orbit_backtest.read_aperture_orbit_backtest_scope_csv()
    b8_rows = v2_5_aperture_orbit_backtest.read_aperture_orbit_backtest_b8_comparison_csv()
    by_scope = {row.scope: row for row in scope_rows}
    b8 = {(row.cohort, row.metric): row.value for row in b8_rows}

    assert by_scope["B4_to_B5_full"].family_count == 208
    assert by_scope["B5_to_B6_full"].family_count == 2274
    assert by_scope["B6_to_B7_full"].family_count == 29520
    assert sum(row.close_count for row in scope_rows) == 770
    assert sum(row.capacity_nonclose_families for row in scope_rows) == 2430
    assert all(row.separator_status == "stable_separator" for row in scope_rows)
    assert all(row.close_phase_rank_1_count == row.close_count for row in scope_rows)
    assert all(row.nonclose_positive_margin_count == 0 for row in scope_rows)
    assert b8[("B8_sibling_control", "birth_close_count")] == "32"
    assert b8[("B8_sibling_control", "sibling_nonbirth_positive_margin_count")] == "0"
    assert b8[("B8_matched_nonbirth_control", "matched_positive_margin_count")] == "0"
    assert b8[("B8_sample_calibration", "k8_sample_rows")] == "200"


def test_v2_5_exact_hull_obstruction_supports_single_gap_precursor():
    summary = v2_5_exact_hull_obstruction.read_exact_hull_obstruction_summary_csv()
    families = v2_5_exact_hull_obstruction.read_exact_hull_obstruction_family_csv()
    by_scope = {row.scope: row for row in summary}

    assert by_scope["B4_to_B5_full"].multi_component_family_count == 65
    assert by_scope["B5_to_B6_full"].multi_component_family_count == 913
    assert by_scope["B6_to_B7_full"].multi_component_family_count == 13785
    assert all(
        row.multi_component_family_count == row.hull_obstructed_multi_count
        for row in summary
    )
    assert all(row.multi_component_close_count == 0 for row in summary)
    assert sum(row.single_component_close_count for row in summary) == 770
    assert all(row.b8_checked_close_single_gap_count == 32 for row in summary)
    assert all(
        row.old_component_count == 1
        for row in families
        if row.close_lift_count > 0
    )


def test_v2_5_source_only_hygiene_passes():
    required_full_repo_inputs = [
        EXPERIMENT_DIR / "candidate_bundle_manifest_v0_1.json",
        REPO_ROOT / "release" / "public" / "release_config.json",
        REPO_ROOT / "scripts" / "build_public_release.py",
    ]
    if any(not path.exists() for path in required_full_repo_inputs):
        pytest.skip(
            "source-only-hygiene is a full repo v2.5 -> v2.3/public non-leak "
            "guard, not a ZIP reviewer command"
        )

    result = subprocess.run(
        [
            sys.executable,
            str(WORKFLOW_ENGINE),
            "--config",
            str(V2_5_WORKFLOW_CONFIG),
            "source-only-hygiene",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_v2_5_research_review_closes_gate_r():
    result = subprocess.run(
        [
            sys.executable,
            str(WORKFLOW_ENGINE),
            "--config",
            str(V2_5_WORKFLOW_CONFIG),
            "research-review",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "candidate research review gate passed" in result.stdout


def _child_k_from_scope(scope: str) -> int:
    if scope.startswith("B5"):
        return 5
    if scope.startswith("B6"):
        return 6
    if scope.startswith("B7"):
        return 7
    raise ValueError(f"unsupported scope: {scope}")
