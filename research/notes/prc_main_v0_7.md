# PRC Main v0.7: Residual Gap Count Exploratory Test

v0.7 turns the v0.6 direction reading into a small exploratory paired test. The
primary metric is only:

```text
residual_gap_count
```

The comparison remains:

```text
delta = complete metric - control metric
```

Negative delta means the complete value has fewer residual components than its
matched control after the common `K=1000` prefix.

## Input

```text
data/summaries/prc_residual_gap_pair_deltas_v0_6.csv
```

The tested set is the same v0.6 eligible set: 33 seeds after excluding the
prefix-exhausted seeds `1258`, `1262`, and `1329`.

## Command

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill-residual-gap-count-test \
  --input data/summaries/prc_residual_gap_pair_deltas_v0_6.csv \
  --out data/summaries/prc_residual_gap_count_tests_v0_7.csv \
  --secondary-out data/summaries/prc_residual_gap_secondary_direction_v0_7.csv \
  --figures-out figures/v0
```

The recorded local run generated 3 primary test rows, 18 secondary direction
rows, and 2 figures in about `0.79s`.

v0.7.1 adds a light control-reuse audit so the p-values are not read as
confirmatory evidence.

## Outputs

```text
data/summaries/prc_residual_gap_count_tests_v0_7.csv
data/summaries/prc_residual_gap_secondary_direction_v0_7.csv
data/summaries/prc_residual_gap_control_reuse_audit_v0_7_1.csv
figures/v0/prc_residual_gap_count_test_v0_7.png
figures/v0/prc_residual_gap_count_ci_v0_7.png
figures/v0/prc_residual_gap_count_tests_manifest.json
```

## Test Definition

The sign test ignores ties and tests whether the complete row is smaller than
its matched control more often than chance under a `p=0.5` sign model.

The three control-role p-values receive Benjamini-Hochberg correction. The
bootstrap confidence interval is a percentile interval for the median paired
delta using 10,000 resamples and seed `1729`.

## Caveats

### Control Caveat

The CSV schema keeps the existing role name `band_ordinary_control`, but this
role is not a random ordinary control. It is a band-center non-complete control:
the non-complete value in the same log bin nearest the bin center. This is the
weakest control in v0.7 and should not be used as the headline result.

The harder controls are:

```text
local_mod6_control
band_mod6_control
```

The v0.7 signal is not clear under these harder controls.

### Post-Selection Caveat

`residual_gap_count` was selected after v0.6 inspected multiple residual
metrics. Therefore v0.7 is a discovery test, not a preregistered confirmation.
The p-values are exploratory p-values.

### Independence Caveat

The 33 pairs should not be treated as fully independent. Complete seeds can be
near each other in the same log bin, and band controls can be reused.

The control reuse audit is:

| control | pairs | unique controls | reused controls | excess reused pairs |
|---|---:|---:|---:|---:|
| local_mod6_control | 33 | 33 | 0 | 0 |
| band_mod6_control | 33 | 25 | 8 | 8 |
| band_ordinary_control | 33 | 16 | 11 | 17 |

The row-level bootstrap CI is also exploratory. A cluster/block bootstrap is a
v0.8 task.

## First Reading

| control | complete smaller | median delta | sign p | BH q | bootstrap median CI |
|---|---:|---:|---:|---:|---:|
| local_mod6_control | 22 / 33 | -11.0 | 0.0801 | 0.1202 | [-35.0, -2.0] |
| band_mod6_control | 19 / 31 non-tie | -9.0 | 0.2810 | 0.2810 | [-42.0, 3.0] |
| band_ordinary_control | 26 / 33 | -37.0 | 0.00132 | 0.00396 | [-51.0, -12.0] |

The v0.7.1 reading is intentionally conservative. Against the harder controls,
the signal is not confirmed: `local_mod6_control` is suggestive but not stable,
and `band_mod6_control` is unclear. The strongest numeric result appears only
against `band_ordinary_control`, the weakest and most reused control design.

This suggests that some of the signal may be entangled with log-band and
residue-class matching. The next step should not be a broad claim; it should be
a better null/control model and a cluster-robust confirmation path.

## Non-Claims

- v0.7 does not claim complete values generally have fewer residual components.
- v0.7 does not claim `residual_gap_count` explains complete covering.
- v0.7 does not use a random-arc null model.
- v0.7 does not expand beyond the 33 eligible v0.6 seeds.
- v0.7 does not treat secondary metrics as tested hypotheses.
- v0.7 does not treat row-level p-values or bootstrap intervals as
  confirmatory because the cohort has possible clustering and control reuse.
