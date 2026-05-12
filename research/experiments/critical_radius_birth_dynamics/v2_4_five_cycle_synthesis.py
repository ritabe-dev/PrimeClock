"""Source-only five-cycle synthesis helpers for PRC v2.4 Gate R."""

from __future__ import annotations

import csv
import math
import os
import tempfile
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_HYPOTHESIS_SCOREBOARD_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_hypothesis_scoreboard_v0_1.csv"
)
DEFAULT_MATCHED_CONTROL_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_matched_control_diagnostics_v0_1.csv"
)
DEFAULT_SYNTHESIS_NOTE = (
    EXPERIMENT_DIR / "notes" / "prc_v2_4_five_cycle_research_synthesis_v0_1.md"
)
DEFAULT_R3_FACTOR_FORENSICS_NOTE = (
    EXPERIMENT_DIR / "notes" / "prc_v2_4_r3_residual_factor_forensics_v0_1.md"
)
DEFAULT_SCOREBOARD_FIGURE = (
    EXPERIMENT_DIR / "figures" / "v2_4" / "prc_v2_4_hypothesis_scoreboard_v0_1.png"
)


@dataclass(frozen=True)
class HypothesisScoreboardRow:
    cycle: int
    role: str
    hypothesis: str
    metric: str
    value: str
    status: str
    classification: str
    failure_mode: str


@dataclass(frozen=True)
class MatchedControlDiagnosticRow:
    diagnostic_group: str
    control_key: str
    observed_key: str
    control_value: str
    observed_value: str
    interpretation: str


def build_hypothesis_scoreboard_rows() -> list[HypothesisScoreboardRow]:
    """Build a broad five-angle source-only hypothesis scoreboard."""
    from v2_4_angle_aperture_diagnostics import (
        read_birth_potential_correlation_csv,
        read_birth_potential_score_csv,
        read_final_aperture_margin_csv,
        read_incremental_grid_phase_csv,
        read_q_grid_birth_phase_csv,
    )
    from v2_4_residual_genealogy import (
        final_birth_rows,
        read_birth_residual_genealogy_csv,
    )
    from v2_4_nonbirth_controls import (
        read_sibling_lift_phase_control_csv,
        read_transition_itinerary_control_csv,
    )
    from v2_4_residual_lineage_atlas import (
        read_residual_lineage_atlas_summary_csv,
    )
    from v2_4_phase_gate_diagnostics import (
        read_phase_gate_family_summary_csv,
    )
    from v2_4_gate_r_decision import read_gate_r_decision_table_csv
    from v2_4_transition_pilot import (
        DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV,
        DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV,
        DEFAULT_B5_TRANSITION_PILOT_CSV,
        TRANSITION_CLOSE,
        TRANSITION_MISS,
        TRANSITION_PARTIAL_CLOSE,
        TRANSITION_SPLIT,
        TRANSITION_TRIM,
        canonical_transition_summary,
        read_b5_gap_close_transition_pilot_csv,
    )

    score_rows = read_birth_potential_score_csv()
    correlations = {row.model: row for row in read_birth_potential_correlation_csv()}
    incremental_rows = read_incremental_grid_phase_csv()
    genealogy_rows = read_birth_residual_genealogy_csv()
    final_rows = final_birth_rows(genealogy_rows)
    margin_rows = read_final_aperture_margin_csv()
    q_grid_rows = read_q_grid_birth_phase_csv()
    b5_rows = read_b5_gap_close_transition_pilot_csv(DEFAULT_B5_TRANSITION_PILOT_CSV)
    b56_rows = read_b5_gap_close_transition_pilot_csv(
        DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV
    )
    b67_rows = read_b5_gap_close_transition_pilot_csv(
        DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV
    )
    sibling_rows = read_sibling_lift_phase_control_csv()
    itinerary_rows = read_transition_itinerary_control_csv()
    atlas_summary = {
        (row.metric, row.scope): row.value
        for row in read_residual_lineage_atlas_summary_csv()
    }
    phase_gate_rows = read_phase_gate_family_summary_csv()
    gate_r_decision_rows = read_gate_r_decision_table_csv()

    r3_inverse = next(
        row for row in score_rows if row.model == "inverse_width" and row.residue == 3
    )
    k2_b7_split = next(
        row
        for row in incremental_rows
        if row.birth_k == 7
        and row.layer_k == 2
        and row.new_prime_remainder == 0
        and row.transition_label == "split"
    )
    max_reflection_imbalance = max(
        abs(row.row_count - row.reflected_row_count) for row in incremental_rows
    )
    sequence_counts = _lineage_sequence_counts(genealogy_rows)
    top_sequence, top_sequence_count = sequence_counts.most_common(1)[0]
    b56_counts = canonical_transition_summary(b56_rows)
    b67_counts = canonical_transition_summary(b67_rows)
    b5_counts = canonical_transition_summary(b5_rows)
    b7_aperture_min = min(
        Fraction(row.aperture_margin) for row in margin_rows if row.birth_k == 7
    )
    b7_containment_min = min(
        Fraction(row.containment_margin) for row in margin_rows if row.birth_k == 7
    )
    b7_q_top = _top_q_grid_pair_share(q_grid_rows, birth_k=7)
    entropy_b7 = _transition_entropy(
        row.transition_label for row in genealogy_rows if row.birth_k == 7
    )
    final_nonunit_count = sum(row.residue_gcd_with_modulus > 1 for row in final_rows)
    sibling_nonbirth_close_count = sum(row.nonbirth_close_count for row in sibling_rows)
    sibling_family_count = len(sibling_rows)
    itinerary_birth_count = sum(row.is_birth for row in itinerary_rows)
    itinerary_nonbirth_count = sum(not row.is_birth for row in itinerary_rows)
    itinerary_nonbirth_sequence_count = len(
        {row.transition_sequence for row in itinerary_rows if not row.is_birth}
    )
    phase_gate_close_families = [
        row for row in phase_gate_rows if row.close_lift_count > 0
    ]
    phase_gate_capacity_nonclose_families = [
        row
        for row in phase_gate_rows
        if row.capacity_pass and row.close_lift_count == 0
    ]
    phase_gate_ranked_close_families = sum(
        row.phase_pass_count == row.close_lift_count == row.birth_lift_count == 1
        and row.phase_pass_remainders == row.close_remainders
        for row in phase_gate_close_families
    )
    decision_counts = Counter(row.decision for row in gate_r_decision_rows)

    rows = [
        HypothesisScoreboardRow(
            cycle=1,
            role="Data Auditor",
            hypothesis="reflection-orbit symmetry survives the broad v2.4 diagnostics",
            metric="max_incremental_reflection_imbalance",
            value=str(max_reflection_imbalance),
            status="supported",
            classification="candidate constraint",
            failure_mode="symmetry is a consistency check, not a causal mechanism",
        ),
        HypothesisScoreboardRow(
            cycle=1,
            role="Skeptical Reviewer",
            hypothesis="future birth filtering breaks rotation but not reflection symmetry",
            metric="incremental_grid_phase_rows",
            value=str(len(incremental_rows)),
            status="supported",
            classification="diagnostic only",
            failure_mode="does not identify which reflected pair will close",
        ),
        HypothesisScoreboardRow(
            cycle=1,
            role="Data Auditor",
            hypothesis="all final checked birth rows close after a recorded residual history",
            metric="final_close_count",
            value=str(sum(row.transition_label == "close" for row in final_rows)),
            status="supported",
            classification="candidate claim candidate",
            failure_mode="finite B5/B6/B7 only",
        ),
        HypothesisScoreboardRow(
            cycle=1,
            role="Hypothesis Miner",
            hypothesis="final checked birth rows live on nonunit residue strata",
            metric="final_gcd_greater_than_one",
            value=f"{final_nonunit_count}/{len(final_rows)}",
            status="supported",
            classification="diagnostic only",
            failure_mode="nonunit gcd may be necessary-looking but is not sufficient",
        ),
        HypothesisScoreboardRow(
            cycle=2,
            role="Hypothesis Miner",
            hypothesis="genealogy paths form multiple grammars rather than one template",
            metric="distinct_transition_sequences",
            value=str(len(sequence_counts)),
            status="supported",
            classification="diagnostic only",
            failure_mode="too many paths can weaken a compact candidate story",
        ),
        HypothesisScoreboardRow(
            cycle=2,
            role="Experiment Designer",
            hypothesis="dominant B7 lineage grammar is informative but not universal",
            metric="top_sequence_count",
            value=f"{top_sequence_count}/770",
            status="partial",
            classification="diagnostic only",
            failure_mode=top_sequence,
        ),
        HypothesisScoreboardRow(
            cycle=2,
            role="Data Auditor",
            hypothesis="B7 genealogy has mixed transition entropy",
            metric="B7_transition_entropy_bits",
            value=_format_float(entropy_b7),
            status="partial",
            classification="future work",
            failure_mode="entropy summarizes diversity but does not explain it",
        ),
        HypothesisScoreboardRow(
            cycle=3,
            role="Experiment Designer",
            hypothesis="local transition dynamics remain rich away from final birth rows",
            metric="B5_to_B6_full_counts",
            value=(
                f"miss={b56_counts[TRANSITION_MISS]};"
                f"trim={b56_counts[TRANSITION_TRIM]};"
                f"split={b56_counts[TRANSITION_SPLIT]};"
                f"partial_close={b56_counts[TRANSITION_PARTIAL_CLOSE]};"
                f"close={b56_counts[TRANSITION_CLOSE]}"
            ),
            status="supported",
            classification="diagnostic only",
            failure_mode="B5->B6 full graph cannot be extrapolated to full B6->B7",
        ),
        HypothesisScoreboardRow(
            cycle=3,
            role="Skeptical Reviewer",
            hypothesis="B6->B7 full transition graph is source-only and must not be overread",
            metric="B6_to_B7_full_counts",
            value=(
                f"miss={b67_counts[TRANSITION_MISS]};"
                f"trim={b67_counts[TRANSITION_TRIM]};"
                f"split={b67_counts[TRANSITION_SPLIT]};"
                f"partial_close={b67_counts[TRANSITION_PARTIAL_CLOSE]};"
                f"close={b67_counts[TRANSITION_CLOSE]}"
            ),
            status="supported",
            classification="non-claim boundary",
            failure_mode="B6->B7 full graph is source-only, not a public claim",
        ),
        HypothesisScoreboardRow(
            cycle=3,
            role="Data Auditor",
            hypothesis="B5 pilot already contains all five primary transition labels",
            metric="B5_taxonomy_counts",
            value=(
                f"miss={b5_counts[TRANSITION_MISS]};"
                f"trim={b5_counts[TRANSITION_TRIM]};"
                f"split={b5_counts[TRANSITION_SPLIT]};"
                f"partial_close={b5_counts[TRANSITION_PARTIAL_CLOSE]};"
                f"close={b5_counts[TRANSITION_CLOSE]}"
            ),
            status="supported",
            classification="diagnostic only",
            failure_mode="taxonomy richness is not by itself a theorem",
        ),
        HypothesisScoreboardRow(
            cycle=4,
            role="Hypothesis Miner",
            hypothesis="final aperture margins are positive but layer-dependent",
            metric="B7_min_aperture_margin",
            value=str(b7_aperture_min),
            status="supported",
            classification="candidate claim candidate",
            failure_mode="margin positivity explains close feasibility, not lineage selection",
        ),
        HypothesisScoreboardRow(
            cycle=4,
            role="Data Auditor",
            hypothesis="containment margins stay positive in checked final closes",
            metric="B7_min_containment_margin",
            value=str(b7_containment_min),
            status="supported",
            classification="candidate claim candidate",
            failure_mode="finite margins are not asymptotic stability",
        ),
        HypothesisScoreboardRow(
            cycle=4,
            role="Experiment Designer",
            hypothesis="final q-grid phase concentrates in reflected remainder pairs",
            metric="B7_top_reflection_pair_share",
            value=b7_q_top,
            status="partial",
            classification="diagnostic only",
            failure_mode="phase concentration needs controls against parent selection",
        ),
        HypothesisScoreboardRow(
            cycle=4,
            role="Skeptical Reviewer",
            hypothesis="sibling-lift controls show close is phase-selective in scoped probes",
            metric="nonbirth_close_families",
            value=f"{sibling_nonbirth_close_count}/{sibling_family_count}",
            status="supported",
            classification="diagnostic only",
            failure_mode="family controls do not by themselves explain phase selection",
        ),
        HypothesisScoreboardRow(
            cycle=4,
            role="Experiment Designer",
            hypothesis="transition itinerary controls compare birth siblings against non-birth siblings",
            metric="birth_nonbirth_itinerary_rows",
            value=(
                f"birth={itinerary_birth_count};"
                f"nonbirth={itinerary_nonbirth_count};"
                f"nonbirth_sequences={itinerary_nonbirth_sequence_count}"
            ),
            status="supported",
            classification="diagnostic only",
            failure_mode="itinerary controls are scoped to checked birth-parent families",
        ),
        HypothesisScoreboardRow(
            cycle=4,
            role="Synthesis Writer",
            hypothesis="exact residual lineage atlas supports capacity gate plus sibling phase gate",
            metric="lineage_atlas_counts",
            value=(
                f"birth={atlas_summary[('birth_sibling_final_lifts', 'all')]};"
                f"nonbirth={atlas_summary[('nonbirth_sibling_final_lifts', 'all')]};"
                f"capacity_nonclose={atlas_summary[('capacity_nonclose_final_lifts', 'all')]};"
                f"capacity_nonclose_families={atlas_summary[('capacity_gate_nonclose_families', 'all')]}"
            ),
            status="supported",
            classification="candidate claim candidate",
            failure_mode="capacity gate is necessary-looking but not sufficient",
        ),
        HypothesisScoreboardRow(
            cycle=4,
            role="Data Auditor",
            hypothesis="signed phase-margin separation selects the closing sibling",
            metric="phase_pass_close_family_alignment",
            value=(
                f"{phase_gate_ranked_close_families}/{len(phase_gate_close_families)};"
                f"capacity_nonclose={len(phase_gate_capacity_nonclose_families)}"
            ),
            status="supported",
            classification="candidate claim candidate",
            failure_mode="phase margin is finite B5/B6/B7 geometry, not an asymptotic law",
        ),
        HypothesisScoreboardRow(
            cycle=5,
            role="Skeptical Reviewer",
            hypothesis="inverse_width is useful but not sufficient",
            metric="inverse_width_r3_observed_over_expected",
            value=r3_inverse.observed_over_expected,
            status="partial",
            classification="non-claim boundary",
            failure_mode="do not claim width alone explains birth",
        ),
        HypothesisScoreboardRow(
            cycle=5,
            role="Skeptical Reviewer",
            hypothesis="prime-zero side-gap creation is not all-birth explanation",
            metric="final_new_prime_remainder_zero",
            value="0/770",
            status="supported",
            classification="non-claim boundary",
            failure_mode="prime-zero remains local diagnostic only",
        ),
        HypothesisScoreboardRow(
            cycle=5,
            role="Synthesis Writer",
            hypothesis="Gate R story should remain continue research",
            metric="decision",
            value="continue research",
            status="partial",
            classification="future work",
            failure_mode="broad exploration found diagnostics, not one locked candidate claim",
        ),
        HypothesisScoreboardRow(
            cycle=5,
            role="Synthesis Writer",
            hypothesis="Gate R decision table promotes signed phase-margin separation and demotes obvious mechanisms",
            metric="decision_counts",
            value=(
                f"keep={decision_counts['keep']};"
                f"support={decision_counts['support']};"
                f"weak={decision_counts['weak']}"
            ),
            status="supported",
            classification="Gate R selection",
            failure_mode="decision table is still source-only and does not change Gate R automatically",
        ),
    ]
    for model in ("uniform", "residual_width", "covered_width", "inverse_width"):
        if model == "inverse_width":
            status = "supported"
        elif model == "covered_width":
            status = "partial"
        else:
            status = "weak"
        rows.append(
            HypothesisScoreboardRow(
                cycle=5,
                role="Hypothesis Miner",
                hypothesis=f"k=2 {model} potential predicts birth-lineage counts",
                metric="pearson_correlation",
                value=correlations[model].pearson_correlation,
                status=status,
                classification="diagnostic only",
                failure_mode="width-family scores are controls, not sole causes",
            )
        )
    rows.append(
        HypothesisScoreboardRow(
            cycle=3,
            role="Experiment Designer",
            hypothesis="incremental p=3 remainder 0 split is an early ancestor signal",
            metric="B7 k2 split row_count",
            value=str(k2_b7_split.row_count),
            status="supported",
            classification="diagnostic only",
            failure_mode="incremental phase needs lineage survival to become explanatory",
        )
    )
    return sorted(rows, key=lambda row: (row.cycle, row.role, row.hypothesis))


def build_matched_control_rows() -> list[MatchedControlDiagnosticRow]:
    """Build broad false-positive/false-negative controls for Gate R."""
    from v2_4_angle_aperture_diagnostics import (
        read_birth_potential_score_csv,
        read_incremental_grid_phase_csv,
    )
    from v2_4_residual_genealogy import (
        final_birth_rows,
        read_birth_residual_genealogy_csv,
    )
    from v2_4_nonbirth_controls import (
        read_sibling_lift_phase_control_csv,
        read_transition_itinerary_control_csv,
    )
    from v2_4_phase_gate_diagnostics import read_phase_gate_family_summary_csv
    from v2_4_gate_r_decision import read_gate_r_decision_table_csv

    score_rows = read_birth_potential_score_csv()
    genealogy_rows = read_birth_residual_genealogy_csv()
    final_rows = final_birth_rows(genealogy_rows)
    incremental_rows = read_incremental_grid_phase_csv()
    sibling_rows = read_sibling_lift_phase_control_csv()
    itinerary_rows = read_transition_itinerary_control_csv()
    phase_gate_rows = read_phase_gate_family_summary_csv()
    gate_r_decision_rows = read_gate_r_decision_table_csv()
    by_candidate = {row.candidate: row for row in gate_r_decision_rows}
    by_residue = {
        row.residue: row for row in score_rows if row.model == "inverse_width"
    }
    max_reflection_imbalance = max(
        abs(row.row_count - row.reflected_row_count) for row in incremental_rows
    )
    return [
        MatchedControlDiagnosticRow(
            diagnostic_group="equal_occurrence_k2",
            control_key="all residues occur with baseline probability 1/6",
            observed_key="r=3 mod 6",
            control_value="1/6",
            observed_value=by_residue[3].occurrence_probability,
            interpretation="occurrence alone cannot explain concentration",
        ),
        MatchedControlDiagnosticRow(
            diagnostic_group="same_width_neighbors",
            control_key="r=2 and r=4, width 1/4",
            observed_key="r=3, width 1/6",
            control_value=f"{by_residue[2].observed_birth_lineage_count}+{by_residue[4].observed_birth_lineage_count}",
            observed_value=str(by_residue[3].observed_birth_lineage_count),
            interpretation="narrower residual state is much more enriched",
        ),
        MatchedControlDiagnosticRow(
            diagnostic_group="wide_zero_side_controls",
            control_key="r=1 and r=5 contain 0-side residual",
            observed_key="r=3 side gaps do not contain 0",
            control_value=f"{by_residue[1].observed_birth_lineage_count}+{by_residue[5].observed_birth_lineage_count}",
            observed_value=str(by_residue[3].observed_birth_lineage_count),
            interpretation="0-side presence is not sufficient for later birth lineage concentration",
        ),
        MatchedControlDiagnosticRow(
            diagnostic_group="model_failure",
            control_key="inverse_width expected for r=3",
            observed_key="observed r=3 count",
            control_value=by_residue[3].normalized_expected_count,
            observed_value=str(by_residue[3].observed_birth_lineage_count),
            interpretation="width is useful but still underpredicts r=3",
        ),
        MatchedControlDiagnosticRow(
            diagnostic_group="reflection_control",
            control_key="reflected incremental rows",
            observed_key="maximum count imbalance",
            control_value="expected 0 under reflection symmetry",
            observed_value=str(max_reflection_imbalance),
            interpretation="reflection symmetry survives conditioning and should be a guard",
        ),
        MatchedControlDiagnosticRow(
            diagnostic_group="path_diversity_control",
            control_key="single genealogy template",
            observed_key="distinct transition sequences",
            control_value="1",
            observed_value=str(len(_lineage_sequence_counts(genealogy_rows))),
            interpretation="birth lineages are not one repeated path",
        ),
        MatchedControlDiagnosticRow(
            diagnostic_group="prime_zero_control",
            control_key="final new-prime remainder zero",
            observed_key="checked final birth rows",
            control_value="would support prime-zero all-birth story",
            observed_value=(
                f"{sum(row.birth_new_prime_remainder == 0 for row in final_rows)}/"
                f"{len(final_rows)}"
            ),
            interpretation="prime-zero remains local diagnostic only",
        ),
        MatchedControlDiagnosticRow(
            diagnostic_group="sibling_lift_control",
            control_key="non-birth close inside sibling families",
            observed_key="geometric close families outside checked births",
            control_value="would reveal close/birth mismatch",
            observed_value=f"{sum(row.nonbirth_close_count for row in sibling_rows)}/{len(sibling_rows)}",
            interpretation="final phase is selective inside current sibling-lift family scopes",
        ),
        MatchedControlDiagnosticRow(
            diagnostic_group="itinerary_nonbirth_control",
            control_key="birth-only itinerary sample",
            observed_key="non-birth sibling itinerary rows",
            control_value="would miss sibling phase controls",
            observed_value=str(sum(not row.is_birth for row in itinerary_rows)),
            interpretation="non-birth siblings share history but fail at final phase",
        ),
        MatchedControlDiagnosticRow(
            diagnostic_group="independent_phase_gate_control",
            control_key="capacity-satisfied non-close families",
            observed_key="phase_pass without close",
            control_value=str(
                sum(row.capacity_pass and row.close_lift_count == 0 for row in phase_gate_rows)
            ),
            observed_value=str(
                sum(
                    row.phase_pass_count > 0 and row.close_lift_count == 0
                    for row in phase_gate_rows
                )
            ),
            interpretation="signed phase margin separates phase gate from the close label",
        ),
        MatchedControlDiagnosticRow(
            diagnostic_group="gate_r_selection_control",
            control_key="capacity + phase as headline",
            observed_key="signed phase-margin theorem candidate",
            control_value=by_candidate["capacity + phase gate"].decision,
            observed_value=by_candidate["signed phase-margin separation theorem"].decision,
            interpretation="selection table promotes the separator and demotes arithmetic diagnostics to refinements",
        ),
        MatchedControlDiagnosticRow(
            diagnostic_group="non_claim_boundary",
            control_key="width-only explanation",
            observed_key="accepted story",
            control_value="rejected",
            observed_value="early narrow residual potential + lineage survival + incremental q-grid phase alignment",
            interpretation="other mechanisms remain active hypotheses",
        ),
    ]


def write_five_cycle_artifacts(
    *,
    scoreboard_path: str | Path = DEFAULT_HYPOTHESIS_SCOREBOARD_CSV,
    matched_control_path: str | Path = DEFAULT_MATCHED_CONTROL_CSV,
    note_path: str | Path = DEFAULT_SYNTHESIS_NOTE,
    figure_path: str | Path = DEFAULT_SCOREBOARD_FIGURE,
) -> None:
    scoreboard_rows = build_hypothesis_scoreboard_rows()
    matched_rows = build_matched_control_rows()
    write_dataclass_csv(scoreboard_rows, scoreboard_path, HypothesisScoreboardRow)
    write_dataclass_csv(matched_rows, matched_control_path, MatchedControlDiagnosticRow)
    write_synthesis_note(scoreboard_rows, matched_rows, note_path)
    write_scoreboard_figure(scoreboard_rows, figure_path)


def read_hypothesis_scoreboard_csv(
    path: str | Path = DEFAULT_HYPOTHESIS_SCOREBOARD_CSV,
) -> list[HypothesisScoreboardRow]:
    return _read_dataclass_csv(path, HypothesisScoreboardRow)


def read_matched_control_csv(
    path: str | Path = DEFAULT_MATCHED_CONTROL_CSV,
) -> list[MatchedControlDiagnosticRow]:
    return _read_dataclass_csv(path, MatchedControlDiagnosticRow)


def row_signature(row: object) -> tuple[object, ...]:
    return tuple(getattr(row, field) for field in row.__dataclass_fields__)


def write_dataclass_csv(rows: Iterable[object], output_path: str | Path, row_type: type) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(row_type.__dataclass_fields__.keys())
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def write_synthesis_note(
    scoreboard_rows: list[HypothesisScoreboardRow],
    matched_rows: list[MatchedControlDiagnosticRow],
    output_path: str | Path,
) -> None:
    lines = [
        "# PRC v2.4 Five-Cycle Research Synthesis v0.1",
        "",
        "Status: source-only Gate R synthesis. This is not a candidate package, public release, or public claim.",
        "",
        "## Purpose",
        "",
        "Run five cycles from five different hypothesis angles: reflection orbit, genealogy grammar, transition dynamics, aperture/phase robustness, and negative controls.",
        "",
        "## Cycle Summary",
        "",
    ]
    for cycle in range(1, 6):
        lines.append(f"### Cycle {cycle}")
        for row in [item for item in scoreboard_rows if item.cycle == cycle]:
            lines.append(
                f"- {row.role}: {row.hypothesis}; {row.metric}={row.value}; status={row.status}; class={row.classification}."
            )
        lines.append("")
    lines.extend(
        [
            "## Matched Controls",
            "",
        ]
    )
    for row in matched_rows:
        lines.append(
            f"- {row.diagnostic_group}: {row.control_key} -> {row.control_value}; {row.observed_key} -> {row.observed_value}; {row.interpretation}."
        )
    lines.extend(
        [
            "",
            "## Synthesis",
            "",
            "The strongest current finite story is: early narrow residual potential + lineage survival + incremental q-grid phase alignment.",
            "",
            "The broader exploration rejects a single-cause story. Reflection symmetry is a guard, genealogy paths are diverse, B5-to-B6 transition dynamics are richer than final birth rows, aperture margins are positive, and inverse-width remains useful but incomplete.",
            "",
            "The inverse-width score underpredicts `r=3 mod 6`, so width alone is explicitly not a claim.",
            "",
            "The `p=3` remainder-0 split is an early ancestor signal in checked birth lineages. It should be read incrementally, not as a final-q histogram.",
            "",
            "The exact residual lineage atlas makes the current Gate R mechanism visible: all checked close families pass the single-component capacity gate, but 2430 capacity-satisfied families still do not close. That keeps sibling phase selection as a necessary part of the story.",
            "",
            "The independent phase-gate diagnostic makes that selection non-circular: signed containment margin is computed before reading the close/birth label, and only the closing sibling has positive phase margin in checked B5/B6/B7 families.",
            "",
            "The Gate R decision table switches this line from exploration to selection. It keeps signed phase-margin separation as the headline theorem candidate, while treating width-normalized k2 r=3 lineage survival and reflection-paired final remainder concentration as arithmetic refinements.",
            "",
            "## Decision",
            "",
            "continue research",
            "",
            "## Non-Claims",
            "",
            "- No B8 data.",
            "- No public v2.4 release.",
            "- No GitHub Release or Zenodo publication.",
            "- No broad theorem for all births.",
            "- No claim that width alone explains birth.",
            "- No claim that prime-zero side-gap creation explains all births.",
            "- B6->B7 full transition graph is source-only, not a public claim.",
            "",
        ]
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def write_scoreboard_figure(
    scoreboard_rows: list[HypothesisScoreboardRow],
    output_path: str | Path,
) -> None:
    if "MPLCONFIGDIR" not in os.environ:
        os.environ["MPLCONFIGDIR"] = str(
            Path(tempfile.gettempdir()) / "primeclock-matplotlib"
        )
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    correlation_rows = [
        row
        for row in scoreboard_rows
        if row.metric == "pearson_correlation"
    ]
    status_counts: dict[str, int] = {}
    for row in scoreboard_rows:
        status_counts[row.status] = status_counts.get(row.status, 0) + 1

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)
    axes[0].bar(
        [
            row.hypothesis.replace("k=2 ", "").replace(
                " potential predicts birth-lineage counts",
                "",
            )
            for row in correlation_rows
        ],
        [float(row.value) for row in correlation_rows],
        color=["#999999", "#e41a1c", "#4daf4a", "#2b8cbe"],
    )
    axes[0].set_title("Width-model control correlations")
    axes[0].set_ylabel("Pearson correlation")
    axes[0].tick_params(axis="x", rotation=18)
    axes[0].grid(axis="y", alpha=0.25)

    labels = sorted(status_counts)
    axes[1].bar(labels, [status_counts[label] for label in labels], color="#767676")
    axes[1].set_title("Five-cycle hypothesis statuses")
    axes[1].set_ylabel("scoreboard rows")
    axes[1].grid(axis="y", alpha=0.25)
    fig.suptitle("PRC v2.4 five-cycle research synthesis")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def _lineage_sequence_counts(rows: Iterable[object]) -> Counter[str]:
    rows_by_lineage: dict[tuple[int, int], list[object]] = {}
    for row in rows:
        rows_by_lineage.setdefault((row.birth_k, row.birth_residue), []).append(row)
    return Counter(
        ">".join(
            row.transition_label for row in sorted(lineage, key=lambda item: item.layer_k)
        )
        for lineage in rows_by_lineage.values()
    )


def _transition_entropy(labels: Iterable[str]) -> float:
    counts = Counter(labels)
    total = sum(counts.values())
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def _top_q_grid_pair_share(rows: Iterable[object], *, birth_k: int) -> str:
    subset = [row for row in rows if row.birth_k == birth_k]
    total = sum(row.birth_count for row in subset)
    top = max(subset, key=lambda row: row.reflection_pair_count)
    return f"{top.reflection_pair_count}/{total}"


def _format_float(value: float) -> str:
    return f"{value:.6f}"


def _read_dataclass_csv(path: str | Path, row_type: type):
    int_fields = {"cycle"}
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for raw_row in csv.DictReader(handle):
            values = dict(raw_row)
            for field in int_fields:
                if field in values:
                    values[field] = int(values[field])
            rows.append(row_type(**values))
    return rows
