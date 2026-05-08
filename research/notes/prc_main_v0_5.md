# PRC Main v0.5: Residual Gap Structure

v0.5 follows the v0.4 result that complete-covering values are not explained
by obviously faster early branch fill-in. The new question is:

```text
After the common prefix U_{<=1000}(N), do complete values have a different
residual gap structure from matched controls?
```

This is still a comparison experiment. It is not a proof or explanation of
complete covering.

## Metric Definition

For each v0.4 cohort row, compute the uncovered intervals after adding all
branches `1..1000`.

The v0.5 row records:

```text
max_possible_branch = floor(N/2)
prefix_exhausts_all_branches
seed_analysis_eligible
residual_uncovered_measure
residual_gap_count
residual_gap_max
residual_gap_p50, residual_gap_p90, residual_gap_p99
residual_gap_entropy
residual_top_gap_share
residual_gap_near_zero_count
```

`residual_gap_entropy` is normalized Shannon entropy over positive gap lengths.
`residual_top_gap_share` is the largest residual gap divided by total residual
uncovered measure. `residual_gap_near_zero_count` uses the v0.5 default
threshold `1e-6`.

`max_possible_branch=floor(N/2)` is the largest branch index that can contain a
prime. If `max_branch >= max_possible_branch`, then the `K=1000` prefix is not a
prefix experiment anymore: it already contains every branch. In that case
`prefix_exhausts_all_branches=True`.

The main v0.5.1 reading uses only seeds where all four roles are non-exhausted.
If any role for a seed exhausts all branches, all four rows for that seed are
marked `seed_analysis_eligible=False`.

## Commands

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill-residual-gaps \
  --manifest data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv \
  --summary data/summaries/prc_branch_fill_cohort_summary_v0_4.csv \
  --max-branch 1000 \
  --near-zero-threshold 1e-6 \
  --out data/summaries/prc_branch_fill_residual_gaps_v0_5.csv \
  --figures-out figures/v0
```

The recorded local run took about `3.53s`, because it computes only the common
prefix gap list and reuses the v0.4 summary CSV for `A_full(N)` and
`exact_complete`.

## Outputs

```text
data/summaries/prc_branch_fill_residual_gaps_v0_5.csv
figures/v0/prc_branch_fill_residual_gap_count_v0_5.png
figures/v0/prc_branch_fill_residual_gap_shape_v0_5.png
figures/v0/prc_branch_fill_residual_gaps_manifest.json
```

## First Reading

The raw v0.5 cohort has 144 rows: 36 complete rows and 36 rows in each of the
three control groups.

The v0.5.1 prefix-censoring correction excludes 3 seeds from the main reading:

```text
1258, 1262, 1329
```

For these seeds, `K=1000` exhausts all branches for at least one role. The main
analysis therefore uses 33 eligible seeds and 132 eligible rows.

Median diagnostics on the 132 eligible rows:

| cohort | gap count | max gap | p90 gap | entropy | top gap share | near-zero gaps | residual measure |
|---|---:|---:|---:|---:|---:|---:|---:|
| complete | 1592.0 | 0.001555 | 0.000504 | 0.947004 | 0.004218 | 3.0 | 0.363894 |
| local_mod6_control | 1644.0 | 0.001805 | 0.000505 | 0.946324 | 0.005154 | 4.0 | 0.358907 |
| band_mod6_control | 1566.0 | 0.001771 | 0.000470 | 0.947887 | 0.005354 | 5.0 | 0.370041 |
| band_ordinary_control | 1620.0 | 0.001531 | 0.000464 | 0.951086 | 0.004384 | 5.0 | 0.349276 |

The conservative reading is weaker than the raw v0.5 table suggested. Complete
values still have a smaller median largest residual gap than the local and
band-mod6 controls, but not smaller than the ordinary band controls. The
top-gap-share signal is also mixed. Entropy remains very similar across all
groups, so there is no broad collapse into a highly uneven gap distribution.

The useful next step is therefore paired, seed-wise comparison rather than
reading unpaired cohort medians. That is v0.6.

## Non-Claims

- v0.5 does not claim complete-covering values generally have smaller residual
  max gaps.
- v0.5 does not claim residual gap shape explains exact complete covering.
- v0.5 does not use a probabilistic null model.
- v0.5 does not expand the cohort beyond the v0.4 36 complete seeds.
- v0.5.1 excludes prefix-exhausted seeds from the main reading, but it does not
  discard the raw rows from the CSV.
