# PRC Main Roadmap

Objective: recast Prime Reciprocal Covering as a finite-`N` hierarchy of prime
residue-cell coverings, while preserving the older `A(N)`, residual
fragmentation, and `C0` work as classified layers of the same project.

## Current Main Frame

Main title:

```text
Prime Reciprocal Covering as a finite-N hierarchy of prime residue-cell coverings
素数剰余セルによる有限N円周被覆の階層構造
```

Residue-cell formulation:

```text
C_{p,r} = [(2r-1)/(2p), (2r+1)/(2p)] mod 1
I_p(N)  = C_{p, N mod p}
```

Endpoints do not affect measure-level statements. Exact theorem-level coverage
uses **closed arcs** and rational interval arithmetic rather than
floating-point zero tests.

The roadmap distinguishes three hierarchies:

- **Prime-prefix hierarchy**: `U_P(N)=union_{p<=P} I_p(N)`. This is the new
  main object.
- **Branch hierarchy**: `floor(N/p)=k`, used by the existing v0.3--v0.9 fill-in
  and null-model diagnostics.
- **Primorial / wheel hierarchy**: `Q_P=prod_{p<=P} p`, used for deterministic
  small-prime residue strata and certificate side cases.

Primary observables for the main line:

```text
U_P(N) = union_{p<=P} I_p(N)
A_P(N) = |T \ U_P(N)|
R_P(N) = T \ U_P(N)
```

Residual component count, gap quantiles, and max gap are diagnostics of
`R_P(N)`. Complete covering `C0(N)` and certificate depth are boundary outputs,
not replacements for the residual-set program.

## Prime-Prefix Profile v0.1

Goal: turn the main hierarchy `U_P(N)` into the next canonical descriptive
artifact.

Output:

- `data/summaries/prc_prime_prefix_profile_v0_1.csv`
- `notes/prc_prime_prefix_profile_v0_1.md`

Command:

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-profile \
  --n 1000 10000 100000 1000000 39069 372759 \
  --out data/summaries/prc_prime_prefix_profile_v0_1.csv
```

Current reading:

- `A_P(N)` is monotone decreasing by construction and is the primary profile.
- Component count, gap quantiles, and top-gap share describe the residual
  geometry of `R_P(N)`.
- `numeric_complete_prefix` is descriptive only. Exact certificate depth is a
  later phase.

## Prime-Prefix Residue Filtration v0.1

Goal: add the exact finite object behind prefix coverage. For the first `k`
primes,

```text
M_k = product_{i<=k} p_i
C_k = {r in Z/M_kZ : union_{i<=k} I_{p_i}(r) = T}
```

where

```text
I_p(r) = [(r mod p)/p - 1/(2p), (r mod p)/p + 1/(2p)] on T.
```

This is the exact primorial-residue version of the prime-prefix hierarchy.
Unlike the descriptive `numeric_complete_prefix` flag, membership in `C_k` is
a finite rational interval question.
The `C_k` are a lifted filtration over primorial residue rings, not nested
subsets of one fixed finite set:

```text
Lift_k(C_{k-1}) = pi_{k,k-1}^{-1}(C_{k-1})
B_k = C_k \ Lift_k(C_{k-1})
alpha_k = |C_k|/M_k = alpha_{k-1} + |B_k|/M_k.
```

So `alpha_k` is nondecreasing; the meaningful growth question is whether new
births eventually stop or continue.

Generated outputs:

- `notes/prc_mathematical_theme_prime_prefix_filtration_v0_1.md`
- `data/summaries/prc_prime_prefix_residue_covering_filtration_v0_1.csv`
- `data/summaries/prc_prime_prefix_residue_covering_birth_samples_v0_1.csv`

Command:

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-filtration \
  --max-k 7 \
  --birth-sample-limit 200 \
  --summary-out data/summaries/prc_prime_prefix_residue_covering_filtration_v0_1.csv \
  --birth-samples-out data/summaries/prc_prime_prefix_residue_covering_birth_samples_v0_1.csv
```

Current reading:

- Prefix coverage depends only on `N mod M_k`.
- If `r in C_k`, all lifts of `r` modulo `M_{k+1}` remain covered, so `C_k`
  forms a monotone lifted filtration.
- Coverage first appears at `k=4`, with `C_4={2,208} mod 210`.
- The current exact table reaches `k=7`, where `|C_7|=9384` modulo `510510`,
  including `714` new births at `p=17`.

The current implementation regenerates this table exactly through the CLI.

## v1.1 Finite Theorem Artifacts

Goal: pivot from selected modulo-210 diagnostics to a theorem-oriented finite
note around `C_k`, lift monotonicity, `C_4`, and `B_5/C_5`.

Deliverables:

- `notes/prc_prime_prefix_finite_note_v1_1.md`
- `data/summaries/prc_prime_prefix_ck_full_v1_1.csv`
- `data/summaries/prc_prime_prefix_birth_witness_v1_1.csv`
- `data/summaries/prc_prime_prefix_c4_exclusion_witness_v1_2.csv`
- `data/summaries/prc_prime_prefix_c4_exclusion_summary_v1_3.csv`
- `data/summaries/prc_prime_prefix_b5_birth_classification_v1_2.csv`
- `data/summaries/prc_prime_prefix_b5_birth_pair_summary_v1_4.csv`

Commands:

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-filtration-full \
  --max-k 5 \
  --out data/summaries/prc_prime_prefix_ck_full_v1_1.csv

python -m prime_reciprocal_projection.cli covering-prime-prefix-birth-witnesses \
  --k 5 \
  --out data/summaries/prc_prime_prefix_birth_witness_v1_1.csv

python -m prime_reciprocal_projection.cli covering-prime-prefix-exclusion-witnesses \
  --k 4 \
  --out data/summaries/prc_prime_prefix_c4_exclusion_witness_v1_2.csv

python -m prime_reciprocal_projection.cli covering-prime-prefix-exclusion-summary \
  --k 4 \
  --out data/summaries/prc_prime_prefix_c4_exclusion_summary_v1_3.csv

python -m prime_reciprocal_projection.cli covering-prime-prefix-birth-classification \
  --k 5 \
  --out data/summaries/prc_prime_prefix_b5_birth_classification_v1_2.csv

python -m prime_reciprocal_projection.cli covering-prime-prefix-birth-pair-summary \
  --k 5 \
  --out data/summaries/prc_prime_prefix_b5_birth_pair_summary_v1_4.csv
```

Current reading:

- `C_4={2,208} mod 210` is the first nonempty layer. The coverage chain for
  `r=2` uses closed-arc endpoint touching at `1/2`; `208` is its reflection.
- `C_5` has `36` residues: `22` inherited lifts from `C_4` and `14` births.
- The `B_5` witness table records the previous uncovered interval and the
  `p=11` arc that closes it. This is the next theorem-building object.
- The `C_4` exclusion witness table gives one uncovered rational gap for every
  residue outside `{2,208}`.
- The `C_4` exclusion summary compresses the 208 witnesses into 36
  component/measure classes: 22 one-gap classes covering 143 residues and 14
  two-gap classes covering 65 residues.
- The `B_5` classification table turns the witness rows into reflection-pair
  and parent-gap templates.
- The `B_5` pair summary compresses those `14` birth rows into `7`
  reflection-pair rows for the displayed finite theorem table.
- All `B_5` births are single-gap closures: six reflection pairs close length
  `1/20` gaps and one pair closes a length `1/21` gap, with no endpoint-touching
  closure.
- v0.9--v0.12 selected modulo-210 diagnostics are retained as appendix-style
  applications/diagnostics, not the main proof spine.

## v0.2 Prime-Prefix Certificate Depth

Goal: connect exact `C_k` membership to existing exact-certified
complete-covering values without turning `C0` into the main PRC axis.

Deliverables:

- `notes/prc_prime_prefix_certificate_depth_v0_2.md`
- `data/summaries/prc_prime_prefix_certificate_depth_v0_2.csv`
- `data/summaries/prc_prime_prefix_certificate_depth_summary_v0_2.csv`

Command:

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-certificates \
  --complete-source data/summaries/prc_combined_runs_2_1000000.csv \
  --max-k 7 \
  --out data/summaries/prc_prime_prefix_certificate_depth_v0_2.csv \
  --summary-out data/summaries/prc_prime_prefix_certificate_depth_summary_v0_2.csv
```

Current reading:

- `18,377 / 23,571` complete-covering values have a prefix certificate with
  `k<=7`.
- `5,194` values are not certified by the checked `C_k` range and remain the
  next target.
- `k=8` is intentionally behind the `--allow-large-k` primorial-scale guardrail.

## v0.3 Guarded k=8 Extension

Goal: test whether the next primorial-scale layer is feasible and whether it
materially reduces the uncertified complete-covering set.

Deliverables:

- `notes/prc_prime_prefix_k8_extension_v0_3.md`
- `data/summaries/prc_prime_prefix_residue_covering_filtration_k8_v0_3.csv`
- `data/summaries/prc_prime_prefix_residue_covering_birth_samples_k8_v0_3.csv`
- `data/summaries/prc_prime_prefix_certificate_depth_k8_v0_3.csv`
- `data/summaries/prc_prime_prefix_certificate_depth_summary_k8_v0_3.csv`

Current reading:

- `M_8=9,699,690`; local filtration generation completed in about 62 seconds.
- `|C_8|=185,048`, with `6,752` new birth residues at `p=19`.
- `k=8` certifies `699` additional complete-covering values.
- The uncertified group falls from `5,194` at `max_k=7` to `4,495` at
  `max_k=8`.
- Do not jump directly to `k=9`; `M_9=223,092,870`, so the next step should
  inspect the `4,495` remaining rows first.

## v0.4 Uncertified Residue Profile

Goal: inspect the `4,495` complete-covering values left uncertified after
`C_8` before attempting the much larger `k=9` scan. In the v1.1 framing, this
and v0.5--v0.12 are appendix-style diagnostics of selected complete rows, not
the main theorem spine.

Deliverables:

- `notes/prc_prime_prefix_uncertified_residue_profile_v0_4.md`
- `data/summaries/prc_prime_prefix_uncertified_residue_profile_v0_4.csv`
- `data/summaries/prc_prime_prefix_uncertified_residue_summary_v0_4.csv`
- `data/summaries/prc_prime_prefix_uncertified_mod210_summary_v0_4.csv`

Current reading:

- The `4,495` rows occupy `98` modulo-210 classes.
- Nearest distance to `C_8` has median `25`, p90 `56`, p99 `90`, and max `97`
  in residue units modulo `M_8`.
- The largest modulo-210 classes are `111`, `4`, `99`, `206`, and `118`.
- Some high-count classes are very near `C_8` in residue distance, while others
  have much larger nearest-distance profiles.
- The next useful experiment is a matched non-complete control profile, not an
  immediate jump to `k=9`.

## v0.5 Uncertified Control Profile

Goal: test whether the `C_8` nearest-distance profile is complete-specific or
also appears in local non-complete controls.

Deliverables:

- `notes/prc_prime_prefix_uncertified_control_profile_v0_5.md`
- `data/summaries/prc_prime_prefix_uncertified_control_profile_v0_5.csv`
- `data/summaries/prc_prime_prefix_uncertified_control_summary_v0_5.csv`
- `data/summaries/prc_prime_prefix_uncertified_control_pair_deltas_v0_5.csv`

Current reading:

- `local_mod210_control` has median distance `26`, compared with `25` for the
  complete rows.
- Paired `complete - local_mod210_control` median delta is `0`, with `1,310`
  ties over `4,475` pairs.
- `local_any_control` is also very close, with median distance `25`.
- Therefore nearest-distance to `C_8` is not yet a complete-specific
  explanation; it is mostly a local/wheel-residue diagnostic.

## v0.6 Uncertified Control Audit

Goal: split the v0.5 matched profile by seed modulo `210` and by the `C_k`
source depth of the nearest covered residue.

Deliverables:

- `notes/prc_prime_prefix_uncertified_control_audit_v0_6.md`
- `data/summaries/prc_prime_prefix_uncertified_control_mod210_audit_v0_6.csv`
- `data/summaries/prc_prime_prefix_uncertified_source_depth_summary_v0_6.csv`

Command:

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-uncertified-control-audit \
  --profile data/summaries/prc_prime_prefix_uncertified_control_profile_v0_5.csv \
  --mod210-out data/summaries/prc_prime_prefix_uncertified_control_mod210_audit_v0_6.csv \
  --source-depth-out data/summaries/prc_prime_prefix_uncertified_source_depth_summary_v0_6.csv
```

Current reading:

- The audit creates `196` modulo-210 rows and `15` source-depth rows.
- Source-depth composition is similar across complete and local controls.
- Some large modulo-210 classes have different paired directions, but the
  global conclusion remains unchanged: nearest distance to `C_8` is mostly a
  local/wheel diagnostic, not a standalone complete-covering explanation.

## v0.7 Modulo-210 Class Review

Goal: pivot the v0.6 audit into one row per modulo-210 class so the next manual
or null-model work has a stable target list.

Deliverables:

- `notes/prc_prime_prefix_uncertified_mod210_class_review_v0_7.md`
- `data/summaries/prc_prime_prefix_uncertified_mod210_class_review_v0_7.csv`

Command:

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-uncertified-class-review \
  --audit data/summaries/prc_prime_prefix_uncertified_control_mod210_audit_v0_6.csv \
  --out data/summaries/prc_prime_prefix_uncertified_mod210_class_review_v0_7.csv
```

Current reading:

- The table has `98` rows, one per occupied modulo-210 class.
- `16` large classes have mixed control direction, meaning the sign depends on
  whether the control preserves modulo `210`.
- The top priority classes include `111`, `4`, `99`, `206`, `118`, `88`, `201`,
  and `62`.
- This strengthens the view that this layer is a local wheel-residue diagnostic
  rather than a complete-covering explanation.

## v0.8 Modulo-210 Class Detail

Goal: expand the top v0.7 classes back into seed/control rows so the class
review can be inspected at the individual-residue level.

Deliverables:

- `notes/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.md`
- `data/summaries/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.csv`

Command:

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-uncertified-class-detail \
  --profile data/summaries/prc_prime_prefix_uncertified_control_profile_v0_5.csv \
  --class-review data/summaries/prc_prime_prefix_uncertified_mod210_class_review_v0_7.csv \
  --class-limit 8 \
  --out data/summaries/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.csv
```

Current reading:

- The detail table expands the top `8` classes: `111`, `4`, `99`, `206`,
  `118`, `88`, `201`, and `62`.
- It contains `4,227` rows: `1,413` complete rows, `1,413` nearest-any controls,
  and `1,401` same-modulo-210 controls.
- The table is meant for targeted inspection before either a stricter discrete
  residue null or a much larger `k=9` scan.

## v0.9 Modulo-210 Source Summary

Goal: compress the v0.8 selected-class detail table by class, cohort role, and
nearest `C_k` source depth.

Deliverables:

- `notes/prc_prime_prefix_uncertified_mod210_source_summary_v0_9.md`
- `data/summaries/prc_prime_prefix_uncertified_mod210_class_source_summary_v0_9.csv`

Command:

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-uncertified-class-source-summary \
  --detail data/summaries/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.csv \
  --out data/summaries/prc_prime_prefix_uncertified_mod210_class_source_summary_v0_9.csv
```

Current reading:

- `4`, `206`, and `201` are essentially shallow `C_4`-adjacent classes.
- `111` and `99` are high-count classes mostly adjacent to `C_5`.
- `118`, `88`, and `62` are more distributed but still centered on `C_5`.
- The next small step should inspect lifted shallow-boundary neighborhoods
  before attempting `k=9`.

## v0.10 Modulo-210 Boundary Summary

Goal: refine v0.9 by grouping the selected-class detail rows by the nearest
covered residue modulo `210`, not only by nearest `C_k` source depth.

Deliverables:

- `notes/prc_prime_prefix_uncertified_mod210_boundary_summary_v0_10.md`
- `data/summaries/prc_prime_prefix_uncertified_mod210_class_boundary_summary_v0_10.csv`

Command:

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-uncertified-class-boundary-summary \
  --detail data/summaries/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.csv \
  --out data/summaries/prc_prime_prefix_uncertified_mod210_class_boundary_summary_v0_10.csv
```

Current reading:

- `4`, `206`, and `201` are clean neighborhoods of the `C_4` anchors `2` and
  `208` modulo `210`.
- `111` and `99` are not single-boundary `C_4` effects; they spread across
  multiple `C_5` anchors.
- `118`, `88`, and `62` are mixed-anchor cases.
- The next exact target is a lifted-boundary table for shallow `C_k` anchors,
  not a raw larger primorial scan.

## v0.11 Modulo-210 Lift-Boundary Table

Goal: invert the selected-class boundary table and read selected modulo-210
classes as neighborhoods of shallow covered anchors.

Deliverables:

- `notes/prc_prime_prefix_uncertified_mod210_lift_boundary_v0_11.md`
- `data/summaries/prc_prime_prefix_uncertified_mod210_lift_boundary_v0_11.csv`

Command:

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-uncertified-lift-boundary \
  --detail data/summaries/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.csv \
  --source-max-k 5 \
  --out data/summaries/prc_prime_prefix_uncertified_mod210_lift_boundary_v0_11.csv
```

Current reading:

- `C_4` anchor `2` maps strongly to selected class `4`, with weaker
  neighborhoods at `62`, `88`, and `99`.
- `C_4` anchor `208` maps strongly to selected classes `206` and `201`, with a
  weaker neighborhood at `118`.
- `C_5` anchors `62`, `148`, `122`, and `88` explain the main selected
  `C_5`-adjacent classes `111`, `99`, `88`, and `118`.
- The next step should describe the anchor-neighborhood structure of `C_4` and
  `C_5` inside the `C_8` residue ring.

## v0.12 Modulo-210 Anchor Neighborhood in C8

Goal: classify selected modulo-210 classes directly inside the `C_8` residue
ring by nearest shallow covered anchor.

Deliverables:

- `notes/prc_prime_prefix_mod210_anchor_neighborhood_v0_12.md`
- `data/summaries/prc_prime_prefix_mod210_anchor_neighborhood_v0_12.csv`

Command:

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-mod210-anchor-neighborhood \
  --max-k 8 \
  --source-max-k 5 \
  --allow-large-k \
  --out data/summaries/prc_prime_prefix_mod210_anchor_neighborhood_v0_12.csv
```

Current reading:

- `4`, `206`, and `201` remain clean `C_4` boundary classes in the full `C_8`
  geometry.
- `111`, `99`, `118`, `88`, and `62` are mixed shallow-anchor neighborhoods.
- v0.11's apparent `C_5` dominance is partly an observed sample-weighting
  effect, not purely the geometry of the whole `C_8` residue ring.
- The next step should compare observed complete/control rows against this
  direct ring geometry within each anchor neighborhood.

## v0.3 Fixed Axis

Primary object:

```text
I_p(N) = [{N/p}-1/(2p), {N/p}+1/(2p)] on T
U_N    = union_{p<=N, p prime} I_p(N)
A(N)   = |T \ U_N|
```

Branch fill-in notation:

```text
B_k(N)      = {p prime : floor(N/p)=k}
U_{<=K}(N)  = union of arcs from branches 1..K
A_{<=K}(N)  = |T \ U_{<=K}(N)|
A_full(N)  = A(N)
```

Deliverables:

- `data/summaries/prc_branch_fill_v0_3.csv`
- `data/summaries/prc_branch_fill_summary_v0_3.csv`
- `figures/v0/prc_branch_fill_residual_v0_3.png`
- `figures/v0/prc_branch_fill_fraction_v0_3.png`
- `figures/v0/prc_branch_fill_manifest.json`
- `notes/prc_main_v0_3.md`

Commands:

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill \
  --n 1000 10000 100000 1000000 39069 372759 \
  --max-branch 1000 \
  --out data/summaries/prc_branch_fill_v0_3.csv

python -m prime_reciprocal_projection.cli covering-branch-fill-summary \
  --input data/summaries/prc_branch_fill_v0_3.csv \
  --out data/summaries/prc_branch_fill_summary_v0_3.csv

python -m prime_reciprocal_projection.cli covering-branch-fill-figures \
  --input data/summaries/prc_branch_fill_v0_3.csv \
  --out figures/v0
```

Validation:

```bash
python -m ruff check src tests
python -m pytest
```

## v0.4 Comparison Cohorts

Goal: test whether branch fill-in depth differs between complete-covering
values and controls.

Cohorts:

- exact-complete cohort from certified `N<=10^6` results
- local matched controls near each complete-covering value
- controls matched by log-N band and `N mod 6`
- band-center non-complete controls from the same broad range

Planned outputs:

- `data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv`
- `data/summaries/prc_branch_fill_cohort_summary_v0_4.csv`
- `data/summaries/prc_branch_fill_cohort_checkpoints_v0_4.csv`
- `figures/v0/prc_branch_fill_cohort_k_depth_v0_4.png`
- `figures/v0/prc_branch_fill_cohort_residual_v0_4.png`
- `figures/v0/prc_branch_fill_cohort_checkpoint_fill_v0_4.png`
- `notes/prc_main_v0_4.md`

Current v0.4 reading:

- 36 complete seeds were selected, 3 from each of 12 log-N bins.
- All seeds received all 3 matched controls.
- Complete values do not look like simple early-fill cases in this cohort;
  median residual at `K=1000` is slightly higher than the three control groups.
- This is an experiment-level observation, not a general explanation.

## v0.5/v0.6/v0.7 Modeling

Goal: compare the residual gap structure after the common branch prefix
`K=1000`, correct for prefix-exhausted small `N`, then use paired
complete-minus-control deltas and a focused residual-gap-count test to decide
which null/control model is worth building.

Current v0.5 outputs:

- `data/summaries/prc_branch_fill_residual_gaps_v0_5.csv`
- `figures/v0/prc_branch_fill_residual_gap_count_v0_5.png`
- `figures/v0/prc_branch_fill_residual_gap_shape_v0_5.png`
- `notes/prc_main_v0_5.md`

Current v0.6 outputs:

- `data/summaries/prc_residual_gap_pair_deltas_v0_6.csv`
- `data/summaries/prc_residual_gap_effect_summary_v0_6.csv`
- `figures/v0/prc_residual_gap_pair_delta_v0_6.png`
- `figures/v0/prc_residual_gap_effect_summary_v0_6.png`
- `notes/prc_main_v0_6.md`

Current v0.7 outputs:

- `data/summaries/prc_residual_gap_count_tests_v0_7.csv`
- `data/summaries/prc_residual_gap_secondary_direction_v0_7.csv`
- `figures/v0/prc_residual_gap_count_test_v0_7.png`
- `figures/v0/prc_residual_gap_count_ci_v0_7.png`
- `notes/prc_main_v0_7.md`

Current v0.5/v0.6/v0.7 reading:

- v0.5.1 excludes 3 prefix-exhausted seeds (`1258`, `1262`, `1329`) from the
  main reading, leaving 33 eligible seeds.
- Complete rows tend to have fewer residual components in paired v0.6
  comparisons.
- v0.7 shows the residual-gap-count signal is strongest against
  `band_ordinary_control`, but this role is a band-center non-complete control
  rather than a random control. The signal is weaker against local mod-6
  controls and not clear against band mod-6 controls.
- Top-gap dominance is mixed across control designs, so a simple "one dominant
  surviving gap" explanation is not yet supported.
- The next model should target residual component structure and matched nulls,
  not just total fill-in speed.

Candidate later models:

- independent random arcs with matched total residual measure
- branch-wise shuffled centers with fixed branch sizes
- local-window controls that preserve nearby prime-count fluctuations
- true seeded random non-complete controls, separate from current band-center
  controls

## v0.8 Cluster Audit

Goal: test whether the residual-gap-count signal survives seed clustering and
control reuse scrutiny before building a full null model.

Current v0.8 outputs:

- `data/summaries/prc_seed_cluster_audit_v0_8.csv`
- `data/summaries/prc_cluster_level_gap_count_direction_v0_8.csv`
- `data/summaries/prc_control_reuse_detail_v0_8.csv`
- `figures/v0/prc_cluster_level_gap_count_direction_v0_8.png`
- `figures/v0/prc_control_reuse_v0_8.png`
- `notes/prc_main_v0_8.md`

Current v0.8 reading:

- The 33 eligible seeds become 11 clusters with `cluster_radius=250`.
- `local_mod6_control` remains suggestive at cluster level: complete has fewer
  residual components in 9 of 11 clusters.
- `band_mod6_control` remains unclear.
- `band_ordinary_control` remains strong but is heavily reused and should stay
  a weak-control diagnostic.

## v0.9 Branch-Uniform Null

Goal: test whether the residual-gap-count signal survives a structure-preserving
null model, and return the main line to `A(N)` / residual structure rather than
selected complete values.

Current v0.9 outputs:

- `data/summaries/prc_branch_uniform_null_v0_9.csv`
- `data/summaries/prc_branch_uniform_null_summary_v0_9.csv`
- `figures/v0/prc_branch_uniform_null_percentile_v0_9.png`
- `figures/v0/prc_branch_uniform_null_deviation_v0_9.png`
- `notes/prc_main_v0_9.md`

Current v0.9 reading:

- The null preserves branch sizes and arc widths, then randomizes centers.
- All four cohorts have high median observed percentiles against this null:
  `0.929`, `0.949`, `0.957`, `0.962`.
- This does not support the idea that complete rows have absolutely low
  residual component count under random covering.
- The stronger observation is broad: PRC residual sets are more fragmented than
  branch-uniform random placements with the same widths.

## C0 / Anti-Clustering Subproblem

Goal: keep exact complete covering and anti-clustering as a forensic side track,
not as the main PRC axis.

Current status:

- `C0(N)=1` remains an important boundary event for `A(N)=0`.
- Consecutive-run and anti-clustering diagnostics are useful because they test
  how fragile complete coverage is under `N -> N+1`.
- These diagnostics do not replace the main `A(N)` / residual fragmentation
  program, and they should not be used to claim a complete-covering law.

Candidate later work:

- use the residue-cell formulation to separate deterministic wheel strata
- implement a discrete residue null that randomizes `r_p in {0,...,p-1}`
- compute `C0` autocorrelation for `h=1..100`
- compare the anti-clustering signal after `mod 30` and `mod 210` correction

## v1.0 / v1.1 Direction

Goal: consolidate the PRC research artifact into a short readable note, then
recast the next note around the finite residue-covering hierarchy without
adding another exploratory metric.

Current v1.0 output:

- `notes/prc_research_note_v1_0_ja.md`

Priority order:

1. make the finite residue-cell hierarchy the organizing frame
2. keep `A_P(N)`, residual components, and gap shape as the main diagnostics
3. explain the branch-uniform null as the first intentionally loose null
4. separate complete-vs-control observations from PRC-vs-null observations
5. list the next stricter nulls: discrete residue null, local branch-bucket
   shuffle, and arithmetic order-preserving controls
6. defer larger complete-cohort expansion, anti-clustering autocorrelation, and
   `N<=10^7` scan

Until v1.0, `residual_gap_count` should be treated as an exploratory
diagnostic, not as an explanation of `A(N)=0`.

Non-claims until v0.5:

- no claim that complete events are explained by branch fill-in speed
- no claim that the six v0.3 anchors are representative
- no claim that `K90/K99` has a stable asymptotic law
- no claim that v0.5/v0.6/v0.7 residual gap differences are a general law
- no claim that v0.7 p-values are confirmatory
- no claim that v0.8 cluster-level p-values are confirmatory
- no claim that the weak `band_ordinary_control` signal is robust
- no claim that branch-uniform null is the final null model
- no claim that high PRC residual fragmentation is asymptotic

## Canonical Data Scope

Tracked research data for this stage should stay limited to top-level summary
CSVs under `data/summaries/`. Nested block-scan directories are resume artifacts,
not canonical research outputs, unless a manifest is added later.
