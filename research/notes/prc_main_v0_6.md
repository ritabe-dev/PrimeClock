# PRC Main v0.6: Paired Residual Gap Dominance

v0.6 follows the v0.5.1 correction. The goal is to compare complete values with
their matched controls seed by seed, after excluding seeds where `K=1000`
already exhausts all branches.

The comparison is:

```text
delta = complete metric - control metric
```

Negative delta means the complete value has a smaller metric than its matched
control.

## Inputs

```text
data/summaries/prc_branch_fill_residual_gaps_v0_5.csv
```

The input contains 144 raw rows. The paired analysis uses 33 eligible seeds and
excludes these prefix-exhausted seeds:

```text
1258, 1262, 1329
```

## Command

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill-residual-gap-pairs \
  --input data/summaries/prc_branch_fill_residual_gaps_v0_5.csv \
  --delta-out data/summaries/prc_residual_gap_pair_deltas_v0_6.csv \
  --summary-out data/summaries/prc_residual_gap_effect_summary_v0_6.csv \
  --figures-out figures/v0
```

The recorded local run generated 594 paired delta rows and 18 effect-summary
rows in about `0.50s`.

## Outputs

```text
data/summaries/prc_residual_gap_pair_deltas_v0_6.csv
data/summaries/prc_residual_gap_effect_summary_v0_6.csv
figures/v0/prc_residual_gap_pair_delta_v0_6.png
figures/v0/prc_residual_gap_effect_summary_v0_6.png
figures/v0/prc_residual_gap_pairs_manifest.json
```

## First Reading

Each control role has 33 eligible pairs.

For `residual_gap_count`, complete rows are smaller more often than controls:

| control | median delta | complete smaller |
|---|---:|---:|
| local_mod6_control | -11.0 | 22 / 33 |
| band_mod6_control | -9.0 | 19 / 33 |
| band_ordinary_control | -37.0 | 26 / 33 |

For `residual_gap_max`, the signal is present but weaker:

| control | median delta | complete smaller |
|---|---:|---:|
| local_mod6_control | -0.0000382 | 20 / 33 |
| band_mod6_control | -0.00000162 | 17 / 33 |
| band_ordinary_control | -0.0000210 | 19 / 33 |

For `residual_top_gap_share`, the result is mixed:

| control | median delta | complete smaller |
|---|---:|---:|
| local_mod6_control | -0.0000768 | 19 / 33 |
| band_mod6_control | 0.00000682 | 15 / 33 |
| band_ordinary_control | 0.0000122 | 16 / 33 |

The most stable v0.6 observation is not "complete values have one smaller
dominant gap." It is closer to: in this matched cohort, complete values tend to
leave fewer residual components after the `K=1000` prefix, while top-gap
dominance itself is not consistently lower across all control designs.

## Non-Claims

- v0.6 does not claim complete-covering values generally have fewer residual
  gaps.
- v0.6 does not claim residual gap count explains complete covering.
- v0.6 does not use bootstrap confidence intervals.
- v0.6 does not use a null model.
- v0.6 does not expand beyond the existing 36-seed v0.4 cohort.
