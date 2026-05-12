from __future__ import annotations

import importlib.util
import hashlib
import subprocess
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path


EXPERIMENT_DIR = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "critical_radius_birth_dynamics"
)
REPO_ROOT = EXPERIMENT_DIR.parents[2]
WORKFLOW_ENGINE = REPO_ROOT / "scripts" / "verify_candidate_workflow.py"
V2_4_WORKFLOW_CONFIG = EXPERIMENT_DIR / "candidate_workflow_v2_4_v0_1.yml"


def _load_tools():
    spec = importlib.util.spec_from_file_location(
        "critical_radius_birth_dynamics_v2_4_tools",
        EXPERIMENT_DIR / "tools.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tools = _load_tools()


def _load_v2_4_pilot():
    spec = importlib.util.spec_from_file_location(
        "critical_radius_birth_dynamics_v2_4_pilot",
        EXPERIMENT_DIR / "v2_4_transition_pilot.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v2_4_pilot = _load_v2_4_pilot()


def _load_v2_4_genealogy():
    spec = importlib.util.spec_from_file_location(
        "critical_radius_birth_dynamics_v2_4_genealogy",
        EXPERIMENT_DIR / "v2_4_residual_genealogy.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v2_4_genealogy = _load_v2_4_genealogy()


def _load_v2_4_angle_aperture():
    spec = importlib.util.spec_from_file_location(
        "critical_radius_birth_dynamics_v2_4_angle_aperture",
        EXPERIMENT_DIR / "v2_4_angle_aperture_diagnostics.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v2_4_angle_aperture = _load_v2_4_angle_aperture()


def _load_v2_4_five_cycle():
    spec = importlib.util.spec_from_file_location(
        "critical_radius_birth_dynamics_v2_4_five_cycle",
        EXPERIMENT_DIR / "v2_4_five_cycle_synthesis.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v2_4_five_cycle = _load_v2_4_five_cycle()


def _load_v2_4_nonbirth_controls():
    spec = importlib.util.spec_from_file_location(
        "critical_radius_birth_dynamics_v2_4_nonbirth_controls",
        EXPERIMENT_DIR / "v2_4_nonbirth_controls.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v2_4_nonbirth_controls = _load_v2_4_nonbirth_controls()


def _load_v2_4_residual_lineage_atlas():
    spec = importlib.util.spec_from_file_location(
        "critical_radius_birth_dynamics_v2_4_residual_lineage_atlas",
        EXPERIMENT_DIR / "v2_4_residual_lineage_atlas.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v2_4_residual_lineage_atlas = _load_v2_4_residual_lineage_atlas()


def _load_v2_4_phase_gate_diagnostics():
    spec = importlib.util.spec_from_file_location(
        "critical_radius_birth_dynamics_v2_4_phase_gate_diagnostics",
        EXPERIMENT_DIR / "v2_4_phase_gate_diagnostics.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v2_4_phase_gate_diagnostics = _load_v2_4_phase_gate_diagnostics()


def _load_v2_4_gate_r_decision():
    spec = importlib.util.spec_from_file_location(
        "critical_radius_birth_dynamics_v2_4_gate_r_decision",
        EXPERIMENT_DIR / "v2_4_gate_r_decision.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v2_4_gate_r_decision = _load_v2_4_gate_r_decision()


def _load_candidate_workflow_engine():
    spec = importlib.util.spec_from_file_location(
        "primeclock_candidate_workflow_engine_v2_4",
        WORKFLOW_ENGINE,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


candidate_workflow_engine = _load_candidate_workflow_engine()


def test_v2_4_birth_residual_genealogy_counts():
    rows = v2_4_genealogy.read_birth_residual_genealogy_csv()
    transition_counts = v2_4_genealogy.genealogy_transition_summary(rows)

    assert len(rows) == 5320
    assert sum(row.birth_k == 5 for row in rows) == 70
    assert sum(row.birth_k == 6 for row in rows) == 252
    assert sum(row.birth_k == 7 for row in rows) == 4998
    assert transition_counts["start"] == 770
    assert transition_counts[v2_4_pilot.TRANSITION_MISS] == 1294
    assert transition_counts[v2_4_pilot.TRANSITION_TRIM] == 1354
    assert transition_counts[v2_4_pilot.TRANSITION_SPLIT] == 566
    assert transition_counts[v2_4_pilot.TRANSITION_PARTIAL_CLOSE] == 566
    assert transition_counts[v2_4_pilot.TRANSITION_CLOSE] == 770


def test_v2_4_k2_gap_width_bias_is_width_corrected():
    rows = v2_4_angle_aperture.read_k2_gap_width_bias_csv()
    by_residue = {row.residue_mod_6: row for row in rows}

    assert len(rows) == 6
    assert by_residue[3].residual_width == "1/6"
    assert by_residue[3].covered_width == "5/6"
    assert by_residue[3].birth_lineage_count == 556
    assert by_residue[3].observed_over_uniform == "1668/385"
    assert by_residue[3].observed_over_residual_weighted == "3336/385"
    assert by_residue[3].observed_over_covered_weighted == "6672/1925"
    assert by_residue[3].observed_over_inverse_width_weighted == "14456/5775"
    assert not by_residue[3].zero_point_in_residual
    assert by_residue[1].zero_point_in_residual
    assert by_residue[5].zero_point_in_residual


def test_v2_4_lineage_measure_bias_separates_width_from_angle():
    rows = v2_4_angle_aperture.read_lineage_measure_bias_csv()
    by_key = {(row.layer_k, row.population): row for row in rows}

    assert by_key[(2, "all_residues")].average_residual_measure == "1/3"
    assert by_key[(2, "all_residues")].target_sector_share_of_residual == "1/6"
    assert by_key[(2, "birth_lineage")].average_residual_measure == "59/308"
    assert by_key[(2, "birth_lineage")].target_sector_share_of_residual == "112/177"
    assert by_key[(4, "all_residues")].average_residual_measure == "8/35"
    assert by_key[(4, "all_residues")].target_sector_share_of_residual == "1/6"
    assert by_key[(4, "birth_lineage")].average_residual_measure == "2441/40425"
    assert by_key[(4, "birth_lineage")].target_sector_share_of_residual == "1730/2441"


def test_v2_4_final_aperture_margins_are_positive_for_checked_births():
    rows = v2_4_angle_aperture.read_final_aperture_margin_csv()
    by_birth = Counter(row.birth_k for row in rows)

    assert len(rows) == 770
    assert by_birth == Counter({5: 14, 6: 42, 7: 714})
    assert all(row.prefinal_gap_count == 1 for row in rows)
    assert all(Fraction(row.aperture_margin) > 0 for row in rows)
    assert all(Fraction(row.containment_margin) > 0 for row in rows)
    assert Counter(row.prefinal_gap_width for row in rows if row.birth_k == 5) == {
        "1/20": 12,
        "1/21": 2,
    }


def test_v2_4_angle_aperture_diagnostics_recompute_committed_rows():
    assert [
        v2_4_angle_aperture.row_signature(row)
        for row in v2_4_angle_aperture.read_k2_gap_width_bias_csv()
    ] == [
        v2_4_angle_aperture.row_signature(row)
        for row in v2_4_angle_aperture.build_k2_gap_width_bias_rows()
    ]
    assert [
        v2_4_angle_aperture.row_signature(row)
        for row in v2_4_angle_aperture.read_lineage_measure_bias_csv()
    ] == [
        v2_4_angle_aperture.row_signature(row)
        for row in v2_4_angle_aperture.build_lineage_measure_bias_rows()
    ]
    assert [
        v2_4_angle_aperture.row_signature(row)
        for row in v2_4_angle_aperture.read_final_aperture_margin_csv()
    ] == [
        v2_4_angle_aperture.row_signature(row)
        for row in v2_4_angle_aperture.build_final_aperture_margin_rows()
    ]
    assert [
        v2_4_angle_aperture.row_signature(row)
        for row in v2_4_angle_aperture.read_q_grid_birth_phase_csv()
    ] == [
        v2_4_angle_aperture.row_signature(row)
        for row in v2_4_angle_aperture.build_q_grid_birth_phase_rows()
    ]
    assert [
        v2_4_angle_aperture.row_signature(row)
        for row in v2_4_angle_aperture.read_incremental_grid_phase_csv()
    ] == [
        v2_4_angle_aperture.row_signature(row)
        for row in v2_4_angle_aperture.build_incremental_grid_phase_rows()
    ]
    assert [
        v2_4_angle_aperture.row_signature(row)
        for row in v2_4_angle_aperture.read_birth_potential_score_csv()
    ] == [
        v2_4_angle_aperture.row_signature(row)
        for row in v2_4_angle_aperture.build_birth_potential_score_rows()
    ]
    assert [
        v2_4_angle_aperture.row_signature(row)
        for row in v2_4_angle_aperture.read_birth_potential_correlation_csv()
    ] == [
        v2_4_angle_aperture.row_signature(row)
        for row in v2_4_angle_aperture.build_birth_potential_correlation_rows()
    ]


def test_v2_4_incremental_grid_phase_tracks_one_prime_at_a_time():
    rows = v2_4_angle_aperture.read_incremental_grid_phase_csv()
    by_key = {
        (row.birth_k, row.layer_k, row.new_prime_remainder, row.transition_label): row
        for row in rows
    }

    assert by_key[(7, 2, 0, "split")].row_count == 522
    assert by_key[(6, 2, 0, "split")].row_count == 32
    assert by_key[(5, 2, 0, "split")].row_count == 2
    assert by_key[(7, 3, 1, "partial_close")].row_count == 252
    assert by_key[(7, 3, 4, "partial_close")].row_count == 252
    assert by_key[(7, 7, 4, "close")].row_count == 199
    assert by_key[(7, 7, 13, "close")].row_count == 199


def test_v2_4_birth_potential_score_compares_width_hypotheses():
    score_rows = v2_4_angle_aperture.read_birth_potential_score_csv()
    correlation_rows = v2_4_angle_aperture.read_birth_potential_correlation_csv()
    by_key = {(row.model, row.residue): row for row in score_rows}
    by_model = {row.model: row for row in correlation_rows}

    assert len(score_rows) == 24
    assert len(correlation_rows) == 4
    assert by_key[("inverse_width", 3)].normalized_expected_count == "5775/26"
    assert by_key[("inverse_width", 3)].observed_birth_lineage_count == 556
    assert by_key[("inverse_width", 3)].observed_over_expected == "14456/5775"
    assert by_model["inverse_width"].pearson_correlation == "0.928735"
    assert by_model["covered_width"].pearson_correlation == "0.785851"
    assert by_model["uniform"].pearson_correlation == "0.000000"
    assert by_model["residual_width"].pearson_correlation == "-0.785851"
    assert by_model["inverse_width"].note == (
        "hypothesis diagnostic; does not exclude other mechanisms"
    )


def test_v2_4_five_cycle_scoreboard_recomputes_committed_rows():
    assert [
        v2_4_five_cycle.row_signature(row)
        for row in v2_4_five_cycle.read_hypothesis_scoreboard_csv()
    ] == [
        v2_4_five_cycle.row_signature(row)
        for row in v2_4_five_cycle.build_hypothesis_scoreboard_rows()
    ]
    assert [
        v2_4_five_cycle.row_signature(row)
        for row in v2_4_five_cycle.read_matched_control_csv()
    ] == [
        v2_4_five_cycle.row_signature(row)
        for row in v2_4_five_cycle.build_matched_control_rows()
    ]


def test_v2_4_five_cycle_scoreboard_keeps_hypotheses_separate():
    rows = v2_4_five_cycle.read_hypothesis_scoreboard_csv()
    matched_rows = v2_4_five_cycle.read_matched_control_csv()
    by_hypothesis = {row.hypothesis: row for row in rows}
    matched_by_group = {row.diagnostic_group: row for row in matched_rows}

    assert len(rows) == 26
    assert {row.cycle for row in rows} == {1, 2, 3, 4, 5}
    assert {
        row.status for row in rows
    } >= {"supported", "partial", "weak"}
    assert (
        by_hypothesis[
            "k=2 inverse_width potential predicts birth-lineage counts"
        ].value
        == "0.928735"
    )
    assert (
        by_hypothesis["inverse_width is useful but not sufficient"].value
        == "14456/5775"
    )
    assert (
        by_hypothesis["prime-zero side-gap creation is not all-birth explanation"].value
        == "0/770"
    )
    assert (
        by_hypothesis[
            "reflection-orbit symmetry survives the broad v2.4 diagnostics"
        ].value
        == "0"
    )
    assert (
        by_hypothesis[
            "genealogy paths form multiple grammars rather than one template"
        ].value
        == "23"
    )
    assert (
        by_hypothesis["final checked birth rows live on nonunit residue strata"].value
        == "770/770"
    )
    assert (
        by_hypothesis["final q-grid phase concentrates in reflected remainder pairs"].value
        == "398/714"
    )
    assert (
        by_hypothesis[
            "sibling-lift controls show close is phase-selective in scoped probes"
        ].value
        == "0/32002"
    )
    assert (
        by_hypothesis[
            "transition itinerary controls compare birth siblings against non-birth siblings"
        ].value
        == "birth=770;nonbirth=12068;nonbirth_sequences=23"
    )
    assert (
        by_hypothesis[
            "exact residual lineage atlas supports capacity gate plus sibling phase gate"
        ].value
        == "birth=770;nonbirth=12068;capacity_nonclose=40498;capacity_nonclose_families=2430"
    )
    assert (
        by_hypothesis[
            "signed phase-margin separation selects the closing sibling"
        ].value
        == "770/770;capacity_nonclose=2430"
    )
    assert (
        by_hypothesis[
            "Gate R decision table promotes signed phase-margin separation and demotes obvious mechanisms"
        ].value
        == "keep=1;support=3;weak=1"
    )
    assert matched_by_group["reflection_control"].observed_value == "0"
    assert matched_by_group["path_diversity_control"].observed_value == "23"
    assert matched_by_group["sibling_lift_control"].observed_value == "0/32002"
    assert matched_by_group["itinerary_nonbirth_control"].observed_value == "12068"
    assert matched_by_group["independent_phase_gate_control"].observed_value == "0"
    assert matched_by_group["gate_r_selection_control"].control_value == "weak"
    assert matched_by_group["gate_r_selection_control"].observed_value == "keep"
    assert (
        matched_by_group["non_claim_boundary"].observed_value
        == "early narrow residual potential + lineage survival + incremental q-grid phase alignment"
    )


def test_v2_4_five_cycle_note_and_figure_boundaries():
    note_text = v2_4_five_cycle.DEFAULT_SYNTHESIS_NOTE.read_text(encoding="utf-8")
    figure_path = v2_4_five_cycle.DEFAULT_SCOREBOARD_FIGURE

    assert "continue research" in note_text
    assert "Reflection symmetry is a guard" in note_text
    assert "genealogy paths are diverse" in note_text
    assert "No claim that width alone explains birth." in note_text
    assert "No claim that prime-zero side-gap creation explains all births." in note_text
    assert "The exact residual lineage atlas makes the current Gate R mechanism visible" in note_text
    assert "The independent phase-gate diagnostic makes that selection non-circular" in note_text
    assert "The Gate R decision table switches this line from exploration to selection" in note_text
    assert "B6->B7 full transition graph is source-only, not a public claim." in note_text
    assert figure_path.exists()
    assert figure_path.stat().st_size > 1000


def test_v2_4_phase_gate_diagnostics_recompute_committed_rows():
    lift_rows = v2_4_phase_gate_diagnostics.read_phase_gate_lift_diagnostics_csv()
    family_rows = v2_4_phase_gate_diagnostics.read_phase_gate_family_summary_csv()

    assert [
        v2_4_phase_gate_diagnostics.row_signature(row)
        for row in lift_rows
    ] == [
        v2_4_phase_gate_diagnostics.row_signature(row)
        for row in v2_4_phase_gate_diagnostics.build_phase_gate_lift_diagnostic_rows()
    ]
    assert [
        v2_4_phase_gate_diagnostics.row_signature(row)
        for row in family_rows
    ] == [
        v2_4_phase_gate_diagnostics.row_signature(row)
        for row in v2_4_phase_gate_diagnostics.build_phase_gate_family_summary_rows(
            lift_rows
        )
    ]


def test_v2_4_phase_gate_is_independent_geometry_not_close_label():
    lift_rows = v2_4_phase_gate_diagnostics.read_phase_gate_lift_diagnostics_csv()
    family_rows = v2_4_phase_gate_diagnostics.read_phase_gate_family_summary_csv()
    close_rows = [row for row in lift_rows if row.is_close]
    nonclose_rows = [row for row in lift_rows if not row.is_close]
    close_families = [row for row in family_rows if row.close_lift_count > 0]
    capacity_nonclose_families = [
        row for row in family_rows if row.capacity_pass and row.close_lift_count == 0
    ]

    assert len(lift_rows) == 533690
    assert len(family_rows) == 32002
    assert len(close_rows) == 770
    assert len(close_families) == 770
    assert len(capacity_nonclose_families) == 2430
    assert all(row.capacity_pass and row.phase_pass for row in close_rows)
    assert all(not row.phase_pass for row in nonclose_rows)
    assert all(row.phase_rank_desc == 1 for row in close_rows)
    assert all(row.nonbirth_close_count == 0 for row in family_rows)
    assert all(row.phase_pass_count == 0 for row in capacity_nonclose_families)
    assert all(
        row.phase_pass_count == row.close_lift_count == row.birth_lift_count == 1
        and row.phase_pass_remainders == row.close_remainders
        for row in close_families
    )


def test_v2_4_phase_gate_artifact_figure_exists():
    figure_path = v2_4_phase_gate_diagnostics.DEFAULT_PHASE_GATE_MARGIN_RANK_FIGURE

    assert figure_path.exists()
    assert figure_path.stat().st_size > 1000


def test_v2_4_gate_r_decision_table_recomputes_committed_rows():
    arithmetic_rows = v2_4_gate_r_decision.read_arithmetic_stratum_bias_csv()
    decision_rows = v2_4_gate_r_decision.read_gate_r_decision_table_csv()

    assert [
        v2_4_gate_r_decision.row_signature(row)
        for row in arithmetic_rows
    ] == [
        v2_4_gate_r_decision.row_signature(row)
        for row in v2_4_gate_r_decision.build_arithmetic_stratum_bias_rows()
    ]
    assert [
        v2_4_gate_r_decision.row_signature(row)
        for row in decision_rows
    ] == [
        v2_4_gate_r_decision.row_signature(row)
        for row in v2_4_gate_r_decision.build_gate_r_decision_rows(arithmetic_rows)
    ]


def test_v2_4_gate_r_decision_table_selects_arithmetic_bias():
    decision_rows = v2_4_gate_r_decision.read_gate_r_decision_table_csv()
    arithmetic_rows = v2_4_gate_r_decision.read_arithmetic_stratum_bias_csv()
    by_candidate = {row.candidate: row for row in decision_rows}
    parent_rows = {
        (row.scope, row.population, row.stratum): row
        for row in arithmetic_rows
        if row.diagnostic == "parent_gcd_capacity_conditioned"
    }
    reflection_rows = {
        (row.scope, row.stratum): row
        for row in arithmetic_rows
        if row.diagnostic == "close_reflection_pair_by_scope"
    }
    cross_rows = {
        (row.scope, row.stratum): row
        for row in arithmetic_rows
        if row.diagnostic == "close_child_gcd_reflection_pair_crosstab"
    }

    assert len(decision_rows) == 5
    assert by_candidate["capacity + phase gate"].decision == "weak"
    assert by_candidate["signed phase-margin separation theorem"].decision == "keep"
    assert (
        by_candidate["signed phase-margin separation theorem"].role
        == "headline theorem candidate"
    )
    assert by_candidate["sibling itinerary divergence"].decision == "support"
    assert by_candidate["width-normalized k2 r=3 lineage survival bias"].decision == "support"
    assert (
        by_candidate["width-normalized k2 r=3 lineage survival bias"].role
        == "arithmetic refinement"
    )
    assert by_candidate["reflection-paired final remainder bias"].decision == "support"
    assert by_candidate["reflection-paired final remainder bias"].role == "arithmetic refinement"
    assert parent_rows[("all", "capacity", "gcd=2")].family_count == 1590
    assert parent_rows[("all", "close", "gcd=3")].family_count == 440
    assert ("all", "close", "gcd=1") not in parent_rows
    k2_width_rows = {
        row.stratum: row
        for row in arithmetic_rows
        if row.diagnostic == "k2_width_normalized_lineage_survival"
    }
    k2_capacity_rows = {
        row.stratum: row
        for row in arithmetic_rows
        if row.diagnostic == "k2_capacity_conditioned_survival"
        and row.scope == "all"
    }
    assert k2_width_rows["r=3"].family_count == 556
    assert k2_width_rows["r=3"].close_rate == "14456/5775"
    assert k2_width_rows["r=2"].close_rate == "1339/1925"
    assert k2_width_rows["r=4"].close_rate == "1339/1925"
    assert k2_capacity_rows["r=3"].close_rate == "278/475"
    assert k2_capacity_rows["r=2"].close_rate == "103/1112"
    assert k2_capacity_rows["r=4"].close_rate == "103/1112"
    assert reflection_rows[("B4_to_B5_full", "3/8")].family_count == 12
    assert reflection_rows[("B5_to_B6_full", "3/10")].family_count == 32
    assert reflection_rows[("B6_to_B7_full", "4/13")].family_count == 398
    assert cross_rows[("B6_to_B7_full", "gcd=3;pair=4/13")].family_count == 316


def test_v2_4_birth_residual_genealogy_final_layers_close():
    rows = v2_4_genealogy.read_birth_residual_genealogy_csv()
    final_rows = v2_4_genealogy.final_birth_rows(rows)
    prefinal_rows = v2_4_genealogy.prefinal_rows(rows)
    birth_keys = {
        (row.k, row.residue)
        for row in tools.birth_dynamics_rows(min_k=5, max_k=7)
    }
    final_keys = {(row.birth_k, row.birth_residue) for row in final_rows}

    assert len(final_rows) == 770
    assert final_keys == birth_keys
    assert all(row.transition_label == v2_4_pilot.TRANSITION_CLOSE for row in final_rows)
    assert all(row.is_zero_residual_state for row in final_rows)
    assert all(row.residual_component_count > 0 for row in prefinal_rows)
    assert not any(row.is_zero_residual_state for row in prefinal_rows)


def test_v2_4_birth_residual_genealogy_prime_origin_is_diagnostic_only():
    rows = v2_4_genealogy.read_birth_residual_genealogy_csv()
    final_rows = v2_4_genealogy.final_birth_rows(rows)

    assert sum(row.origin_component_present for row in rows) == 576
    assert sum(row.zero_center_available for row in rows) == 4744
    assert v2_4_genealogy.non_coprime_birth_count(rows) == 770
    assert sum(row.birth_new_prime_remainder == 0 for row in final_rows) == 0


def test_v2_4_birth_residual_genealogy_recomputes_committed_rows():
    committed_rows = v2_4_genealogy.read_birth_residual_genealogy_csv()
    recomputed_rows = v2_4_genealogy.build_birth_residual_genealogy_rows(
        tools.birth_dynamics_rows(min_k=5, max_k=7)
    )
    committed_by_key = {
        v2_4_genealogy.genealogy_row_key(row): row for row in committed_rows
    }
    recomputed_by_key = {
        v2_4_genealogy.genealogy_row_key(row): row for row in recomputed_rows
    }

    assert committed_by_key.keys() == recomputed_by_key.keys()
    assert {
        key: v2_4_genealogy.genealogy_row_signature(row)
        for key, row in committed_by_key.items()
    } == {
        key: v2_4_genealogy.genealogy_row_signature(row)
        for key, row in recomputed_by_key.items()
    }


def test_v2_4_b5_transition_pilot_counts():
    rows = v2_4_pilot.read_b5_gap_close_transition_pilot_csv()
    summary = v2_4_pilot.b5_gap_close_transition_pilot_summary(rows)

    assert summary.total_rows == 2288
    assert summary.parent_count == 208
    assert summary.child_count == 2288
    assert summary.close_count == 14
    assert summary.not_close_count == 2274
    assert summary.birth_count == 14
    assert summary.birth_close_count == 14
    assert summary.birth_remaining_zero_count == 14
    assert summary.non_birth_close_count == 0
    assert summary.canonical_close_count == 14
    assert summary.canonical_partial_close_count == 22
    assert summary.canonical_split_count == 258
    assert summary.canonical_trim_count == 474
    assert summary.canonical_miss_count == 1520
    assert summary.trim_component_delta_zero_count == 474
    assert summary.trim_component_delta_positive_count == 0
    assert summary.close_to_zero_reflection_pair_count == 7
    assert summary.close_aperture_family_count == 4


def test_v2_4_b5_transition_pilot_recomputes_committed_geometry():
    committed_rows = v2_4_pilot.read_b5_gap_close_transition_pilot_csv()
    recomputed_rows = v2_4_pilot.recompute_b5_transition_pilot_rows(
        tools.birth_dynamics_rows(min_k=5, max_k=5)
    )
    committed_by_key = {
        v2_4_pilot.transition_row_key(row): row for row in committed_rows
    }
    recomputed_by_key = {
        v2_4_pilot.transition_row_key(row): row for row in recomputed_rows
    }

    assert committed_by_key.keys() == recomputed_by_key.keys()
    assert {
        key: v2_4_pilot.transition_row_geometry_signature(row)
        for key, row in committed_by_key.items()
    } == {
        key: v2_4_pilot.transition_row_geometry_signature(row)
        for key, row in recomputed_by_key.items()
    }
    assert all(v2_4_pilot.raw_gap_counts_match_intervals(row) for row in committed_rows)


def test_v2_4_transition_taxonomy_representative_rows():
    rows = v2_4_pilot.read_b5_gap_close_transition_pilot_csv()
    rows_by_parent_remainder = {
        (row.parent_residue, row.new_prime_remainder): row for row in rows
    }

    assert (
        v2_4_pilot.classify_canonical_transition(rows_by_parent_remainder[(9, 2)])
        == v2_4_pilot.TRANSITION_CLOSE
    )
    assert v2_4_pilot.is_zero_residual_state(rows_by_parent_remainder[(9, 2)])
    assert (
        v2_4_pilot.classify_canonical_transition(rows_by_parent_remainder[(12, 3)])
        == v2_4_pilot.TRANSITION_PARTIAL_CLOSE
    )
    assert (
        v2_4_pilot.classify_canonical_transition(rows_by_parent_remainder[(0, 3)])
        == v2_4_pilot.TRANSITION_TRIM
    )
    assert (
        v2_4_pilot.classify_canonical_transition(rows_by_parent_remainder[(0, 4)])
        == v2_4_pilot.TRANSITION_SPLIT
    )
    assert (
        v2_4_pilot.classify_canonical_transition(rows_by_parent_remainder[(0, 0)])
        == v2_4_pilot.TRANSITION_MISS
    )


def test_v2_4_component_attributes_use_circular_components():
    rows = v2_4_pilot.read_b5_gap_close_transition_pilot_csv()
    rows_by_parent_remainder = {
        (row.parent_residue, row.new_prime_remainder): row for row in rows
    }

    one_to_one_trim = rows_by_parent_remainder[(0, 3)]
    assert (
        v2_4_pilot.classify_canonical_transition(one_to_one_trim)
        == v2_4_pilot.TRANSITION_TRIM
    )
    assert v2_4_pilot.component_transition_stats(one_to_one_trim).component_delta == 0

    cut_at_zero_trim = rows_by_parent_remainder[(1, 1)]
    assert cut_at_zero_trim.old_gap_count == 1
    assert cut_at_zero_trim.remaining_gap_count == 2
    assert (
        v2_4_pilot.classify_canonical_transition(cut_at_zero_trim)
        == v2_4_pilot.TRANSITION_TRIM
    )
    mapping = v2_4_pilot.component_transition_mapping(cut_at_zero_trim)
    assert len(mapping["old_components"]) == 1
    assert len(mapping["remaining_components"]) == 1
    assert mapping["remaining_by_old"] == {0: (0,)}
    assert v2_4_pilot.component_transition_stats(cut_at_zero_trim).component_delta == 0

    true_split = rows_by_parent_remainder[(0, 4)]
    assert (
        v2_4_pilot.classify_canonical_transition(true_split)
        == v2_4_pilot.TRANSITION_SPLIT
    )
    split_mapping = v2_4_pilot.component_transition_mapping(true_split)
    assert split_mapping["remaining_by_old"] == {0: (0, 1)}
    assert v2_4_pilot.component_transition_stats(true_split).component_delta == 1


def test_v2_4_zero_residual_state_is_not_residue_zero():
    rows = v2_4_pilot.read_b5_gap_close_transition_pilot_csv()
    zero_residual_rows = [row for row in rows if v2_4_pilot.is_zero_residual_state(row)]

    assert zero_residual_rows
    assert all(row.remaining_gap_count == 0 for row in zero_residual_rows)
    assert all(row.parent_residue != 0 for row in zero_residual_rows)


def test_v2_4_prime_zero_obstruction_diagnostic():
    assert v2_4_pilot.prime_zero_obstruction_holds(11, [2, 3, 5, 7])
    assert not v2_4_pilot.prime_zero_obstruction_holds(11, [2, 3, 5, 7, 11])
    assert not v2_4_pilot.prime_zero_obstruction_holds(12, [2, 3, 5, 7])


def test_v2_4_b5_transition_pilot_has_eleven_lifts_per_parent():
    rows_by_parent = {}
    for row in v2_4_pilot.read_b5_gap_close_transition_pilot_csv():
        rows_by_parent.setdefault(row.parent_residue, []).append(row)

    assert len(rows_by_parent) == 208
    assert {len(rows) for rows in rows_by_parent.values()} == {11}
    assert {
        tuple(sorted(row.new_prime_remainder for row in rows))
        for rows in rows_by_parent.values()
    } == {tuple(range(11))}


def test_v2_4_b5_transition_pilot_aligns_with_v2_3_birth_dynamics():
    pilot_birth_keys = {
        (row.parent_residue, row.new_prime_remainder, row.child_residue)
        for row in v2_4_pilot.read_b5_gap_close_transition_pilot_csv()
        if row.is_b5_birth
    }
    birth_keys = {
        (row.parent_residue_mod_previous, row.new_prime_remainder, row.residue)
        for row in tools.birth_dynamics_rows(min_k=5, max_k=5)
    }

    assert pilot_birth_keys == birth_keys


def test_v2_4_b6_sanity_probe_counts():
    birth_rows = tools.birth_dynamics_rows(min_k=6, max_k=6)
    rows = v2_4_pilot.b6_birth_parent_transition_probe_rows(birth_rows)
    taxonomy_counts = v2_4_pilot.canonical_transition_summary(rows)

    assert len(rows) == 546
    assert len({row.parent_residue for row in rows}) == 42
    assert {len([row for row in rows if row.parent_residue == parent]) for parent in {row.parent_residue for row in rows}} == {13}
    assert taxonomy_counts[v2_4_pilot.TRANSITION_MISS] == 504
    assert taxonomy_counts[v2_4_pilot.TRANSITION_CLOSE] == 42
    assert taxonomy_counts[v2_4_pilot.TRANSITION_TRIM] == 0
    assert taxonomy_counts[v2_4_pilot.TRANSITION_SPLIT] == 0
    assert taxonomy_counts[v2_4_pilot.TRANSITION_PARTIAL_CLOSE] == 0


def test_v2_4_b6_sanity_probe_close_aligns_with_births():
    birth_rows = tools.birth_dynamics_rows(min_k=6, max_k=6)
    rows = v2_4_pilot.b6_birth_parent_transition_probe_rows(birth_rows)
    close_keys = {
        (row.parent_residue, row.new_prime_remainder, row.child_residue)
        for row in rows
        if v2_4_pilot.classify_canonical_transition(row)
        == v2_4_pilot.TRANSITION_CLOSE
    }
    birth_keys = {
        (row.parent_residue_mod_previous, row.new_prime_remainder, row.residue)
        for row in birth_rows
    }

    assert close_keys == birth_keys
    assert all(row.is_b5_birth for row in rows if row.remaining_gap_count == 0)


def test_v2_4_b5_to_b6_full_transition_graph_counts():
    rows = v2_4_pilot.read_b5_gap_close_transition_pilot_csv(
        v2_4_pilot.DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV
    )
    taxonomy_counts = v2_4_pilot.canonical_transition_summary(rows)
    delta_counts = Counter(
        (
            v2_4_pilot.classify_canonical_transition(row),
            v2_4_pilot.component_transition_stats(row).component_delta,
        )
        for row in rows
    )

    assert len(rows) == 29562
    assert len({row.parent_residue for row in rows}) == 2274
    assert {
        len([row for row in rows if row.parent_residue == parent])
        for parent in {row.parent_residue for row in rows}
    } == {13}
    assert taxonomy_counts[v2_4_pilot.TRANSITION_MISS] == 20442
    assert taxonomy_counts[v2_4_pilot.TRANSITION_TRIM] == 5610
    assert taxonomy_counts[v2_4_pilot.TRANSITION_SPLIT] == 3090
    assert taxonomy_counts[v2_4_pilot.TRANSITION_PARTIAL_CLOSE] == 378
    assert taxonomy_counts[v2_4_pilot.TRANSITION_CLOSE] == 42
    assert delta_counts[(v2_4_pilot.TRANSITION_MISS, 0)] == 20442
    assert delta_counts[(v2_4_pilot.TRANSITION_TRIM, 0)] == 5610
    assert delta_counts[(v2_4_pilot.TRANSITION_SPLIT, 1)] == 3090
    assert delta_counts[(v2_4_pilot.TRANSITION_PARTIAL_CLOSE, -1)] == 378
    assert delta_counts[(v2_4_pilot.TRANSITION_CLOSE, -1)] == 42


def test_v2_4_b5_to_b6_full_transition_graph_aligns_with_b6_births():
    rows = v2_4_pilot.read_b5_gap_close_transition_pilot_csv(
        v2_4_pilot.DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV
    )
    close_keys = {
        (row.parent_residue, row.new_prime_remainder, row.child_residue)
        for row in rows
        if v2_4_pilot.classify_canonical_transition(row)
        == v2_4_pilot.TRANSITION_CLOSE
    }
    birth_keys = {
        (row.parent_residue_mod_previous, row.new_prime_remainder, row.residue)
        for row in tools.birth_dynamics_rows(min_k=6, max_k=6)
    }

    assert close_keys == birth_keys
    assert all(
        row.is_b5_birth
        for row in rows
        if v2_4_pilot.classify_canonical_transition(row)
        == v2_4_pilot.TRANSITION_CLOSE
    )


def test_v2_4_b7_birth_parent_transition_probe_counts():
    rows = v2_4_pilot.read_b5_gap_close_transition_pilot_csv(
        v2_4_pilot.DEFAULT_B7_BIRTH_PARENT_TRANSITION_PROBE_CSV
    )
    taxonomy_counts = v2_4_pilot.canonical_transition_summary(rows)
    delta_counts = Counter(
        (
            v2_4_pilot.classify_canonical_transition(row),
            v2_4_pilot.component_transition_stats(row).component_delta,
        )
        for row in rows
    )

    assert len(rows) == 12138
    assert len({row.parent_residue for row in rows}) == 714
    assert {
        len([row for row in rows if row.parent_residue == parent])
        for parent in {row.parent_residue for row in rows}
    } == {17}
    assert taxonomy_counts[v2_4_pilot.TRANSITION_MISS] == 11424
    assert taxonomy_counts[v2_4_pilot.TRANSITION_CLOSE] == 714
    assert taxonomy_counts[v2_4_pilot.TRANSITION_TRIM] == 0
    assert taxonomy_counts[v2_4_pilot.TRANSITION_SPLIT] == 0
    assert taxonomy_counts[v2_4_pilot.TRANSITION_PARTIAL_CLOSE] == 0
    assert delta_counts[(v2_4_pilot.TRANSITION_MISS, 0)] == 11424
    assert delta_counts[(v2_4_pilot.TRANSITION_CLOSE, -1)] == 714


def test_v2_4_b7_birth_parent_transition_probe_aligns_with_b7_births():
    rows = v2_4_pilot.read_b5_gap_close_transition_pilot_csv(
        v2_4_pilot.DEFAULT_B7_BIRTH_PARENT_TRANSITION_PROBE_CSV
    )
    close_keys = {
        (row.parent_residue, row.new_prime_remainder, row.child_residue)
        for row in rows
        if v2_4_pilot.classify_canonical_transition(row)
        == v2_4_pilot.TRANSITION_CLOSE
    }
    birth_keys = {
        (row.parent_residue_mod_previous, row.new_prime_remainder, row.residue)
        for row in tools.birth_dynamics_rows(min_k=7, max_k=7)
    }

    assert close_keys == birth_keys
    assert all(
        row.is_b5_birth
        for row in rows
        if v2_4_pilot.classify_canonical_transition(row)
        == v2_4_pilot.TRANSITION_CLOSE
    )


def test_v2_4_b6_to_b7_full_transition_graph_aligns_with_b7_births():
    rows = v2_4_pilot.read_b5_gap_close_transition_pilot_csv(
        v2_4_pilot.DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV
    )
    taxonomy_counts = v2_4_pilot.canonical_transition_summary(rows)
    parent_counts = Counter(row.parent_residue for row in rows)
    close_keys = {
        (row.parent_residue, row.new_prime_remainder, row.child_residue)
        for row in rows
        if v2_4_pilot.classify_canonical_transition(row)
        == v2_4_pilot.TRANSITION_CLOSE
    }
    birth_keys = {
        (row.parent_residue_mod_previous, row.new_prime_remainder, row.residue)
        for row in tools.birth_dynamics_rows(min_k=7, max_k=7)
    }

    assert len(rows) == 501840
    assert len(parent_counts) == 29520
    assert set(parent_counts.values()) == {17}
    assert taxonomy_counts[v2_4_pilot.TRANSITION_MISS] == 363600
    assert taxonomy_counts[v2_4_pilot.TRANSITION_TRIM] == 78310
    assert taxonomy_counts[v2_4_pilot.TRANSITION_SPLIT] == 54490
    assert taxonomy_counts[v2_4_pilot.TRANSITION_PARTIAL_CLOSE] == 4726
    assert taxonomy_counts[v2_4_pilot.TRANSITION_CLOSE] == 714
    assert close_keys == birth_keys
    assert all(
        row.is_b5_birth
        for row in rows
        if v2_4_pilot.classify_canonical_transition(row)
        == v2_4_pilot.TRANSITION_CLOSE
    )


def test_v2_4_sibling_lift_phase_controls_cover_birth_and_nonbirth_families():
    rows = v2_4_nonbirth_controls.read_sibling_lift_phase_control_csv()
    scope_counts = Counter(row.scope for row in rows)

    assert len(rows) == 32002
    assert scope_counts == Counter(
        {
            "B4_to_B5_full": 208,
            "B5_to_B6_full": 2274,
            "B6_to_B7_full": 29520,
        }
    )
    assert all(row.close_lift_count == row.birth_lift_count for row in rows)
    assert sum(row.nonbirth_close_count for row in rows) == 0
    assert sum(row.birth_lift_count > 0 for row in rows) == 770
    assert sum(row.birth_lift_count == 0 for row in rows) == 31232
    assert [
        v2_4_nonbirth_controls.row_signature(row)
        for row in rows
    ] == [
        v2_4_nonbirth_controls.row_signature(row)
        for row in v2_4_nonbirth_controls.build_sibling_lift_phase_control_rows()
    ]


def test_v2_4_transition_itinerary_controls_compare_sibling_lifts():
    rows = v2_4_nonbirth_controls.read_transition_itinerary_control_csv()
    scope_counts = Counter(row.scope for row in rows)
    nonbirth_sequences = {
        row.transition_sequence for row in rows if not row.is_birth
    }

    assert len(rows) == 12838
    assert scope_counts == Counter(
        {
            "B5_birth_parent_siblings": 154,
            "B6_birth_parent_siblings": 546,
            "B7_birth_parent_siblings": 12138,
        }
    )
    assert sum(row.is_birth for row in rows) == 770
    assert sum(not row.is_birth for row in rows) == 12068
    assert all(row.is_close == row.is_birth for row in rows)
    assert len(nonbirth_sequences) == 23
    assert [
        v2_4_nonbirth_controls.row_signature(row)
        for row in rows
    ] == [
        v2_4_nonbirth_controls.row_signature(row)
        for row in v2_4_nonbirth_controls.build_transition_itinerary_control_rows()
    ]


def test_v2_4_residual_lineage_atlas_exposes_capacity_and_phase_controls():
    rows = v2_4_residual_lineage_atlas.read_residual_lineage_atlas_csv()
    summary_rows = v2_4_residual_lineage_atlas.read_residual_lineage_atlas_summary_csv()
    summary = {(row.metric, row.scope): row.value for row in summary_rows}
    final_rows = [
        row for row in rows if row.layer_k == int(row.scope[1])
    ]
    sibling_final = [
        row for row in final_rows if row.control_group == "birth_parent_sibling"
    ]
    capacity_final = [
        row for row in final_rows if row.control_group == "capacity_nonclose_control"
    ]

    assert len(rows) == 369824
    assert len(final_rows) == 53336
    assert sum(row.is_birth for row in sibling_final) == 770
    assert sum(not row.is_birth for row in sibling_final) == 12068
    assert len(capacity_final) == 40498
    assert all(row.is_close for row in sibling_final if row.is_birth)
    assert all(not row.is_close for row in final_rows if not row.is_birth)
    assert all(row.is_capacity_satisfied for row in capacity_final)
    assert summary[("capacity_gate_close_families", "all")] == "770"
    assert summary[("capacity_gate_nonclose_families", "all")] == "2430"
    assert [
        v2_4_residual_lineage_atlas.row_signature(row)
        for row in rows
    ] == [
        v2_4_residual_lineage_atlas.row_signature(row)
        for row in v2_4_residual_lineage_atlas.build_residual_lineage_atlas_rows()
    ]


def test_v2_4_b5_transition_pilot_checker_passes():
    result = subprocess.run(
        [
            sys.executable,
            "experiments/critical_radius_birth_dynamics/check_v2_4_b5_transition_pilot.py",
        ],
        cwd=REPO_ROOT / "research",
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert "check_v2_4_b5_transition_pilot: checks=13, failed=0" in result.stdout


def test_v2_4_b6_sanity_probe_checker_passes():
    result = subprocess.run(
        [
            sys.executable,
            "experiments/critical_radius_birth_dynamics/check_v2_4_b6_sanity_probe.py",
        ],
        cwd=REPO_ROOT / "research",
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert "check_v2_4_b6_sanity_probe: checks=6, failed=0" in result.stdout


def test_v2_4_b6_to_b7_full_transition_graph_checker_passes():
    result = subprocess.run(
        [
            sys.executable,
            "experiments/critical_radius_birth_dynamics/check_v2_4_b6_to_b7_full_transition_graph.py",
        ],
        cwd=REPO_ROOT / "research",
        check=True,
        capture_output=True,
        text=True,
        timeout=360,
    )

    assert (
        "check_v2_4_b6_to_b7_full_transition_graph: checks=7, failed=0"
        in result.stdout
    )


def test_v2_4_sibling_lift_controls_checker_passes():
    result = subprocess.run(
        [
            sys.executable,
            "experiments/critical_radius_birth_dynamics/check_v2_4_sibling_lift_controls.py",
        ],
        cwd=REPO_ROOT / "research",
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert "check_v2_4_sibling_lift_controls: checks=5, failed=0" in result.stdout


def test_v2_4_transition_itinerary_controls_checker_passes():
    result = subprocess.run(
        [
            sys.executable,
            "experiments/critical_radius_birth_dynamics/check_v2_4_transition_itinerary_controls.py",
        ],
        cwd=REPO_ROOT / "research",
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert (
        "check_v2_4_transition_itinerary_controls: checks=5, failed=0"
        in result.stdout
    )


def test_v2_4_residual_lineage_atlas_checker_passes():
    result = subprocess.run(
        [
            sys.executable,
            "experiments/critical_radius_birth_dynamics/check_v2_4_residual_lineage_atlas.py",
        ],
        cwd=REPO_ROOT / "research",
        check=True,
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert "check_v2_4_residual_lineage_atlas: checks=9, failed=0" in result.stdout


def test_v2_4_transition_graph_probe_checker_passes():
    result = subprocess.run(
        [
            sys.executable,
            "experiments/critical_radius_birth_dynamics/check_v2_4_transition_graph_probes.py",
        ],
        cwd=REPO_ROOT / "research",
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert "check_v2_4_transition_graph_probes: checks=13, failed=0" in result.stdout


def test_v2_4_birth_residual_genealogy_checker_passes():
    result = subprocess.run(
        [
            sys.executable,
            "experiments/critical_radius_birth_dynamics/check_v2_4_birth_residual_genealogy.py",
        ],
        cwd=REPO_ROOT / "research",
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert "check_v2_4_birth_residual_genealogy: checks=9, failed=0" in result.stdout


def test_v2_4_angle_aperture_diagnostics_checker_passes():
    result = subprocess.run(
        [
            sys.executable,
            "experiments/critical_radius_birth_dynamics/check_v2_4_angle_aperture_diagnostics.py",
        ],
        cwd=REPO_ROOT / "research",
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert "check_v2_4_angle_aperture_diagnostics: checks=13, failed=0" in result.stdout


def test_v2_4_five_cycle_research_synthesis_checker_passes():
    result = subprocess.run(
        [
            sys.executable,
            "experiments/critical_radius_birth_dynamics/check_v2_4_five_cycle_research_synthesis.py",
        ],
        cwd=REPO_ROOT / "research",
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert (
        "check_v2_4_five_cycle_research_synthesis: checks=7, failed=0"
        in result.stdout
    )


def test_v2_4_phase_gate_diagnostics_checker_passes():
    result = subprocess.run(
        [
            sys.executable,
            "experiments/critical_radius_birth_dynamics/check_v2_4_phase_gate_diagnostics.py",
        ],
        cwd=REPO_ROOT / "research",
        check=True,
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert "check_v2_4_phase_gate_diagnostics: checks=11, failed=0" in result.stdout


def test_v2_4_gate_r_decision_checker_passes():
    result = subprocess.run(
        [
            sys.executable,
            "experiments/critical_radius_birth_dynamics/check_v2_4_gate_r_decision.py",
        ],
        cwd=REPO_ROOT / "research",
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert "check_v2_4_gate_r_decision: checks=9, failed=0" in result.stdout


def test_v2_4_seed_is_not_in_v2_3_public_or_candidate_bundles():
    public_sources = [
        REPO_ROOT / "release" / "public" / "release_config.json",
        EXPERIMENT_DIR / "candidate_bundle_manifest_v0_1.json",
        EXPERIMENT_DIR / "manifest.yml",
    ]
    forbidden = "prc_v2_4_b5_gap_close_transition_pilot_v0_1.csv"

    for path in public_sources:
        assert forbidden not in path.read_text(encoding="utf-8")


def test_v2_4_source_only_hygiene_passes_current_config():
    config = candidate_workflow_engine.load_config(V2_4_WORKFLOW_CONFIG)

    candidate_workflow_engine.check_source_only_hygiene(config, repo_root=REPO_ROOT)


def test_v2_4_source_only_hygiene_rejects_candidate_manifest_reference(tmp_path, capsys):
    config = candidate_workflow_engine.load_config(V2_4_WORKFLOW_CONFIG)
    source_only = dict(config["source_only_research"])
    source_file = source_only["files"][0]
    manifest = tmp_path / "candidate_manifest.json"
    manifest.write_text(
        '{"root_file_map": [], "root_files": [], "research_files": ["'
        + source_file
        + '"], "research_dirs": []}',
        encoding="utf-8",
    )
    source_only["candidate_bundle_manifests"] = [str(manifest)]
    bad_config = dict(config)
    bad_config["source_only_research"] = source_only

    try:
        candidate_workflow_engine.check_source_only_hygiene(
            bad_config,
            repo_root=REPO_ROOT,
        )
    except SystemExit:
        output = capsys.readouterr().out
        assert "source-only research file is in candidate bundle sources" in output
    else:
        raise AssertionError("expected source-only hygiene failure")


def test_v2_4_source_only_hygiene_rejects_public_release_source(tmp_path, capsys):
    config = candidate_workflow_engine.load_config(V2_4_WORKFLOW_CONFIG)
    source_only = dict(config["source_only_research"])
    source_file = source_only["files"][1]
    release_config = tmp_path / "release_config.json"
    release_config.write_text('{"public_release": "2.3.0"}\n', encoding="utf-8")
    builder = tmp_path / "public_builder.py"
    builder.write_text(
        "ROOT_FILE_MAP = []\n"
        "RESEARCH_DIRS = []\n"
        "def root_files(config):\n"
        f"    return ['{source_file}']\n"
        "def research_files(config):\n"
        "    return []\n",
        encoding="utf-8",
    )
    source_only["public_release_config"] = str(release_config)
    source_only["public_release_builder"] = str(builder)
    bad_config = dict(config)
    bad_config["source_only_research"] = source_only

    try:
        candidate_workflow_engine.check_source_only_hygiene(
            bad_config,
            repo_root=REPO_ROOT,
        )
    except SystemExit:
        output = capsys.readouterr().out
        assert "source-only research file is in public release sources" in output
    else:
        raise AssertionError("expected source-only hygiene failure")


def test_v2_4_public_release_checker_rejects_v2_4_paths(tmp_path):
    release_root = tmp_path / "release"
    release_root.mkdir()
    readme = release_root / "README.md"
    readme.write_text(
        "public release bundle\n"
        "critical-radius\n"
        "gap-aperture\n",
        encoding="utf-8",
    )
    workflow = release_root / ".github" / "workflows" / "verify.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        "uses: actions/checkout@v6\n"
        "uses: actions/setup-python@v6\n"
        "run: python -m pytest tests/test_critical_radius_birth_dynamics_public.py -q\n"
        "run: python -m pytest tests/test_covering_prime_prefix_filtration.py -q\n"
        "run: python experiments/critical_radius_birth_dynamics/check_candidate.py\n"
        "run: python experiments/critical_radius_birth_dynamics/check_candidate_standalone.py\n"
        "run: python scripts/verify_public_release.py --out \"$RUNNER_TEMP/out\" --zip\n",
        encoding="utf-8",
    )
    v2_4_file = (
        release_root
        / "research"
        / "experiments"
        / "critical_radius_birth_dynamics"
        / "check_v2_4_b5_transition_pilot.py"
    )
    v2_4_file.parent.mkdir(parents=True)
    v2_4_file.write_text("# source-only v2.4 file\n", encoding="utf-8")
    manifest_lines = []
    for path in [readme, workflow, v2_4_file]:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_lines.append(f"{digest}  {path.relative_to(release_root).as_posix()}")
    (release_root / "SHA256SUMS").write_text(
        "\n".join(manifest_lines) + "\n",
        encoding="utf-8",
    )

    checker = REPO_ROOT / "scripts" / "check_public_release.py"
    result = subprocess.run(
        [sys.executable, str(checker), str(release_root)],
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 1
    assert "check_v2_4" in result.stdout
