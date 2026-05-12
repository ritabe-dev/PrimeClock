# PRC v2.4 Five-Cycle Research Synthesis v0.1

Status: source-only Gate R synthesis. This is not a candidate package, public release, or public claim.

## Purpose

Run five cycles from five different hypothesis angles: reflection orbit, genealogy grammar, transition dynamics, aperture/phase robustness, and negative controls.

## Cycle Summary

### Cycle 1
- Data Auditor: all final checked birth rows close after a recorded residual history; final_close_count=770; status=supported; class=candidate claim candidate.
- Data Auditor: reflection-orbit symmetry survives the broad v2.4 diagnostics; max_incremental_reflection_imbalance=0; status=supported; class=candidate constraint.
- Hypothesis Miner: final checked birth rows live on nonunit residue strata; final_gcd_greater_than_one=770/770; status=supported; class=diagnostic only.
- Skeptical Reviewer: future birth filtering breaks rotation but not reflection symmetry; incremental_grid_phase_rows=169; status=supported; class=diagnostic only.

### Cycle 2
- Data Auditor: B7 genealogy has mixed transition entropy; B7_transition_entropy_bits=2.490887; status=partial; class=future work.
- Experiment Designer: dominant B7 lineage grammar is informative but not universal; top_sequence_count=216/770; status=partial; class=diagnostic only.
- Hypothesis Miner: genealogy paths form multiple grammars rather than one template; distinct_transition_sequences=23; status=supported; class=diagnostic only.

### Cycle 3
- Data Auditor: B5 pilot already contains all five primary transition labels; B5_taxonomy_counts=miss=1520;trim=474;split=258;partial_close=22;close=14; status=supported; class=diagnostic only.
- Experiment Designer: incremental p=3 remainder 0 split is an early ancestor signal; B7 k2 split row_count=522; status=supported; class=diagnostic only.
- Experiment Designer: local transition dynamics remain rich away from final birth rows; B5_to_B6_full_counts=miss=20442;trim=5610;split=3090;partial_close=378;close=42; status=supported; class=diagnostic only.
- Skeptical Reviewer: B6->B7 full transition graph is source-only and must not be overread; B6_to_B7_full_counts=miss=363600;trim=78310;split=54490;partial_close=4726;close=714; status=supported; class=non-claim boundary.

### Cycle 4
- Data Auditor: containment margins stay positive in checked final closes; B7_min_containment_margin=1/221; status=supported; class=candidate claim candidate.
- Data Auditor: signed phase-margin separation selects the closing sibling; phase_pass_close_family_alignment=770/770;capacity_nonclose=2430; status=supported; class=candidate claim candidate.
- Experiment Designer: final q-grid phase concentrates in reflected remainder pairs; B7_top_reflection_pair_share=398/714; status=partial; class=diagnostic only.
- Experiment Designer: transition itinerary controls compare birth siblings against non-birth siblings; birth_nonbirth_itinerary_rows=birth=770;nonbirth=12068;nonbirth_sequences=23; status=supported; class=diagnostic only.
- Hypothesis Miner: final aperture margins are positive but layer-dependent; B7_min_aperture_margin=24/2431; status=supported; class=candidate claim candidate.
- Skeptical Reviewer: sibling-lift controls show close is phase-selective in scoped probes; nonbirth_close_families=0/32002; status=supported; class=diagnostic only.
- Synthesis Writer: exact residual lineage atlas supports capacity gate plus sibling phase gate; lineage_atlas_counts=birth=770;nonbirth=12068;capacity_nonclose=40498;capacity_nonclose_families=2430; status=supported; class=candidate claim candidate.

### Cycle 5
- Hypothesis Miner: k=2 covered_width potential predicts birth-lineage counts; pearson_correlation=0.785851; status=partial; class=diagnostic only.
- Hypothesis Miner: k=2 inverse_width potential predicts birth-lineage counts; pearson_correlation=0.928735; status=supported; class=diagnostic only.
- Hypothesis Miner: k=2 residual_width potential predicts birth-lineage counts; pearson_correlation=-0.785851; status=weak; class=diagnostic only.
- Hypothesis Miner: k=2 uniform potential predicts birth-lineage counts; pearson_correlation=0.000000; status=weak; class=diagnostic only.
- Skeptical Reviewer: inverse_width is useful but not sufficient; inverse_width_r3_observed_over_expected=14456/5775; status=partial; class=non-claim boundary.
- Skeptical Reviewer: prime-zero side-gap creation is not all-birth explanation; final_new_prime_remainder_zero=0/770; status=supported; class=non-claim boundary.
- Synthesis Writer: Gate R decision table promotes signed phase-margin separation and demotes obvious mechanisms; decision_counts=keep=1;support=3;weak=1; status=supported; class=Gate R selection.
- Synthesis Writer: Gate R story should remain continue research; decision=continue research; status=partial; class=future work.

## Matched Controls

- equal_occurrence_k2: all residues occur with baseline probability 1/6 -> 1/6; r=3 mod 6 -> 1/6; occurrence alone cannot explain concentration.
- same_width_neighbors: r=2 and r=4, width 1/4 -> 103+103; r=3, width 1/6 -> 556; narrower residual state is much more enriched.
- wide_zero_side_controls: r=1 and r=5 contain 0-side residual -> 4+4; r=3 side gaps do not contain 0 -> 556; 0-side presence is not sufficient for later birth lineage concentration.
- model_failure: inverse_width expected for r=3 -> 5775/26; observed r=3 count -> 556; width is useful but still underpredicts r=3.
- reflection_control: reflected incremental rows -> expected 0 under reflection symmetry; maximum count imbalance -> 0; reflection symmetry survives conditioning and should be a guard.
- path_diversity_control: single genealogy template -> 1; distinct transition sequences -> 23; birth lineages are not one repeated path.
- prime_zero_control: final new-prime remainder zero -> would support prime-zero all-birth story; checked final birth rows -> 0/770; prime-zero remains local diagnostic only.
- sibling_lift_control: non-birth close inside sibling families -> would reveal close/birth mismatch; geometric close families outside checked births -> 0/32002; final phase is selective inside current sibling-lift family scopes.
- itinerary_nonbirth_control: birth-only itinerary sample -> would miss sibling phase controls; non-birth sibling itinerary rows -> 12068; non-birth siblings share history but fail at final phase.
- independent_phase_gate_control: capacity-satisfied non-close families -> 2430; phase_pass without close -> 0; signed phase margin separates phase gate from the close label.
- gate_r_selection_control: capacity + phase as headline -> weak; signed phase-margin theorem candidate -> keep; selection table promotes the separator and demotes arithmetic diagnostics to refinements.
- non_claim_boundary: width-only explanation -> rejected; accepted story -> early narrow residual potential + lineage survival + incremental q-grid phase alignment; other mechanisms remain active hypotheses.

## Synthesis

The strongest current finite story is: early narrow residual potential + lineage survival + incremental q-grid phase alignment.

The broader exploration rejects a single-cause story. Reflection symmetry is a guard, genealogy paths are diverse, B5-to-B6 transition dynamics are richer than final birth rows, aperture margins are positive, and inverse-width remains useful but incomplete.

The inverse-width score underpredicts `r=3 mod 6`, so width alone is explicitly not a claim.

The `p=3` remainder-0 split is an early ancestor signal in checked birth lineages. It should be read incrementally, not as a final-q histogram.

The exact residual lineage atlas makes the current Gate R mechanism visible: all checked close families pass the single-component capacity gate, but 2430 capacity-satisfied families still do not close. That keeps sibling phase selection as a necessary part of the story.

The independent phase-gate diagnostic makes that selection non-circular: signed containment margin is computed before reading the close/birth label, and only the closing sibling has positive phase margin in checked B5/B6/B7 families.

The Gate R decision table switches this line from exploration to selection. It keeps signed phase-margin separation as the headline theorem candidate, while treating width-normalized k2 r=3 lineage survival and reflection-paired final remainder concentration as arithmetic refinements.

## Decision

continue research

## Non-Claims

- No B8 data.
- No public v2.4 release.
- No GitHub Release or Zenodo publication.
- No broad theorem for all births.
- No claim that width alone explains birth.
- No claim that prime-zero side-gap creation explains all births.
- B6->B7 full transition graph is source-only, not a public claim.
