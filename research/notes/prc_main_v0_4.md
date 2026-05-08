# PRC Main v0.4: Matched Branch Fill-In Cohorts

v0.4 asks whether certified complete-covering values have visibly different
cumulative branch fill-in depth from matched controls.

This is a comparison experiment, not an explanation of complete covering.

## Cohort Rule

Complete source:

```text
data/summaries/prc_combined_runs_2_1000000.csv
```

Range and selection:

```text
1000 <= N <= 1000000
12 log-spaced N-bins
up to 3 certified complete values per bin
```

Within each log bin, seeds are chosen closest to the log-center of the bin.
Each complete seed receives three controls:

```text
local_mod6_control:
  non-complete N within seed +/- 250, same N mod 6, nearest to seed

band_mod6_control:
  non-complete N in the same log bin, same N mod 6, nearest to bin log-center

band_ordinary_control:
  non-complete N in the same log bin, nearest to bin log-center
```

If any control is missing, the seed is excluded. In the v0.4 run, no seeds were
excluded.

## Commands

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill-cohorts \
  --complete-source data/summaries/prc_combined_runs_2_1000000.csv \
  --start 1000 \
  --stop 1000000 \
  --bin-count 12 \
  --max-per-bin 3 \
  --local-radius 250 \
  --out data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv

python -m prime_reciprocal_projection.cli covering-branch-fill-cohort-summary \
  --manifest data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv \
  --max-branch 1000 \
  --summary-out data/summaries/prc_branch_fill_cohort_summary_v0_4.csv \
  --checkpoint-out data/summaries/prc_branch_fill_cohort_checkpoints_v0_4.csv

python -m prime_reciprocal_projection.cli covering-branch-fill-cohort-figures \
  --summary data/summaries/prc_branch_fill_cohort_summary_v0_4.csv \
  --checkpoints data/summaries/prc_branch_fill_cohort_checkpoints_v0_4.csv \
  --out figures/v0
```

The summary generation took about `413s` in the recorded local run. That is
acceptable for v0.4, but too slow for scaling to all complete values without
further optimization.

## Outputs

```text
data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv
data/summaries/prc_branch_fill_cohort_summary_v0_4.csv
data/summaries/prc_branch_fill_cohort_checkpoints_v0_4.csv
figures/v0/prc_branch_fill_cohort_k_depth_v0_4.png
figures/v0/prc_branch_fill_cohort_residual_v0_4.png
figures/v0/prc_branch_fill_cohort_checkpoint_fill_v0_4.png
figures/v0/prc_branch_fill_cohort_manifest.json
```

## First Reading

The v0.4 cohort has:

```text
eligible complete seeds: 36
excluded seeds: 0
summary rows: 144
checkpoint rows: 3744
```

Median diagnostics by cohort:

| cohort | rows | median K50 | K50 censored | K90 censored | median residual at K=1000 | median A_full |
|---|---:|---:|---:|---:|---:|---:|
| complete | 36 | 234 | 3 | 33 | 0.371519 | 0.000000 |
| local_mod6_control | 36 | 211 | 3 | 32 | 0.339959 | 0.037586 |
| band_mod6_control | 36 | 160 | 1 | 33 | 0.331501 | 0.043835 |
| band_ordinary_control | 36 | 195 | 0 | 30 | 0.331959 | 0.057117 |

The important observation is negative/conservative: complete values do not
look like simple early-fill cases in this v0.4 cohort. Their median residual at
`K=1000` is slightly higher than the three control groups, and `K90/K99` are
mostly censored for every group.

This does not mean complete values are slower in general. It only means that
the current matched sample does not support the easy story that exact complete
covering is explained by unusually fast low-branch fill-in.

## Non-Claims

- v0.4 does not claim complete-covering values are slower or faster in general.
- v0.4 does not claim the 36 seeds are representative of all complete values.
- v0.4 does not explain why `A_full(N)=0`.
- v0.4 does not use the controls as a probabilistic null model.
- v0.4 does not extend the search beyond `N<=10^6`.

## Next Reading Question

The next useful question is whether complete values differ not by early branch
speed, but by the structure of the final residual gaps after a deep common
prefix such as `K=1000`.
