# PRC Main v0.9: Branch-Uniform Null Model

v0.9 adds the first structure-preserving null model for the PRC main line.
The goal is to compare the observed `K=1000` residual component count against a
randomized covering process that preserves branch sizes and prime arc widths.

This is not a test that `residual_gap_count` explains complete covering. It is
a check of whether the observed PRC residual structure is unusual relative to a
simple branch-wise random placement model.

## Null Model

For each observed row, keep:

```text
N
max_branch = 1000
the branch label floor(N/p) for each included prime
the arc radius 1/(2p)
```

Then replace each center `{N/p}` by an independent uniform random center on the
circle. The current v0.9 model is:

```text
branch_uniform
```

This preserves branch sizes and widths, but it does not preserve the arithmetic
phase structure of `{N/p}` inside each branch.

## Command

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill-null-model \
  --manifest data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv \
  --observed data/summaries/prc_branch_fill_residual_gaps_v0_5.csv \
  --model branch_uniform \
  --max-branch 1000 \
  --iterations 1000 \
  --seed 1729 \
  --out data/summaries/prc_branch_uniform_null_v0_9.csv \
  --summary-out data/summaries/prc_branch_uniform_null_summary_v0_9.csv \
  --figures-out figures/v0
```

The recorded local run generated 132 per-row summaries, 4 cohort summaries, and
2 figures in about `1162s`.

## Outputs

```text
data/summaries/prc_branch_uniform_null_v0_9.csv
data/summaries/prc_branch_uniform_null_summary_v0_9.csv
figures/v0/prc_branch_uniform_null_percentile_v0_9.png
figures/v0/prc_branch_uniform_null_deviation_v0_9.png
figures/v0/prc_branch_uniform_null_manifest.json
```

## First Reading

| cohort | rows | median observed percentile | median observed < null rate | below null p05 | above null p95 |
|---|---:|---:|---:|---:|---:|
| complete | 33 | 0.929 | 0.071 | 0 | 12 |
| local_mod6_control | 33 | 0.949 | 0.051 | 1 | 16 |
| band_mod6_control | 33 | 0.957 | 0.043 | 0 | 17 |
| band_ordinary_control | 33 | 0.962 | 0.038 | 0 | 18 |

This reverses the naive expectation behind the v0.7 reading. The complete rows
do not have unusually low `residual_gap_count` relative to the branch-uniform
null. Instead, all four cohorts have high observed percentiles.

The conservative reading is:

```text
PRC residual sets are more fragmented than branch-uniform random placements
with the same arc widths.
```

This appears to be a broad PRC-vs-null effect, not a complete-specific effect.

## Consequence for the Main Direction

v0.7/v0.8 remain useful, but their meaning changes:

- complete values can have fewer residual components than matched controls;
- nevertheless, both complete and control PRC rows tend to have more residual
  components than the branch-uniform null;
- therefore `residual_gap_count` should not be read as "complete values are
  unusually simple under random covering."

The better next question is:

```text
Why does the reciprocal phase structure fragment the remaining uncovered set
more than a branch-uniform placement?
```

For v1.0, this is more central than trying to make `residual_gap_count` explain
`A(N)=0`.

## Limitations

- The null model randomizes centers independently and may be too loose.
- It preserves branch sizes and widths, but not within-branch arithmetic order.
- The run is computationally expensive in the current pure Python
  implementation.
- This is still a finite cohort result on the existing 33 eligible seeds and
  matched controls.

## Non-Claims

- v0.9 does not claim a theorem about PRC.
- v0.9 does not claim complete covering is explained by residual component
  count.
- v0.9 does not claim the branch-uniform null is the final null model.
- v0.9 does not claim the observed high fragmentation is asymptotic.
