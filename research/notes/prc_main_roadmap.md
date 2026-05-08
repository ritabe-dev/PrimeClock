# PRC Main Roadmap

Objective: keep Prime Reciprocal Covering focused on reproducible covering
metrics, not on selected-number interpretation.

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

## v0.9 Direction

Goal: test whether the residual-gap-count signal survives a structure-preserving
null model.

Priority order:

1. branch-wise shuffled centers with fixed branch sizes
2. local branch-bucket shuffled centers if full branch shuffling is too loose
3. cluster-level statistic against the shuffled null
4. larger local/mod-6 matched complete cohort
5. true seeded random controls

Until v0.9, `residual_gap_count` should be treated as an exploratory
diagnostic, not as an explanation of `A(N)=0`.

Non-claims until v0.5:

- no claim that complete events are explained by branch fill-in speed
- no claim that the six v0.3 anchors are representative
- no claim that `K90/K99` has a stable asymptotic law
- no claim that v0.5/v0.6/v0.7 residual gap differences are a general law
- no claim that v0.7 p-values are confirmatory
- no claim that v0.8 cluster-level p-values are confirmatory
- no claim that the weak `band_ordinary_control` signal is robust

## Canonical Data Scope

Tracked research data for this stage should stay limited to top-level summary
CSVs under `data/summaries/`. Nested block-scan directories are resume artifacts,
not canonical research outputs, unless a manifest is added later.
