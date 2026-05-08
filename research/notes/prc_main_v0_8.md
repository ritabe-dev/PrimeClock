# PRC Main v0.8: Cluster-Robust Control Audit

v0.8 audits the v0.7 `residual_gap_count` signal against two risks:

```text
seed clustering
control reuse
```

The goal is not to confirm a theorem. The goal is to decide whether the
`residual_gap_count` diagnostic is still worth testing with a stronger null
model.

## Input

```text
data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv
data/summaries/prc_residual_gap_pair_deltas_v0_6.csv
```

The tested metric remains:

```text
residual_gap_count
```

The eligible set is the same v0.6/v0.7 set: 33 seeds after excluding the
prefix-exhausted seeds `1258`, `1262`, and `1329`.

## Command

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill-cluster-audit \
  --manifest data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv \
  --deltas data/summaries/prc_residual_gap_pair_deltas_v0_6.csv \
  --metric residual_gap_count \
  --cluster-radius 250 \
  --cluster-out data/summaries/prc_seed_cluster_audit_v0_8.csv \
  --direction-out data/summaries/prc_cluster_level_gap_count_direction_v0_8.csv \
  --reuse-out data/summaries/prc_control_reuse_detail_v0_8.csv \
  --figures-out figures/v0
```

The recorded local run generated 33 seed-cluster rows, 3 cluster-direction rows,
74 control-reuse detail rows, and 2 figures in about `0.50s`.

## Outputs

```text
data/summaries/prc_seed_cluster_audit_v0_8.csv
data/summaries/prc_cluster_level_gap_count_direction_v0_8.csv
data/summaries/prc_control_reuse_detail_v0_8.csv
figures/v0/prc_cluster_level_gap_count_direction_v0_8.png
figures/v0/prc_control_reuse_v0_8.png
figures/v0/prc_cluster_audit_manifest.json
```

## Cluster Definition

Seeds are clustered within each log bin. In sorted `seed_n` order, a new cluster
starts when the distance from the previous seed is greater than the configured
cluster radius.

For v0.8:

```text
cluster_radius = 250
```

The 33 eligible seeds become 11 clusters. In this cohort each cluster has 3
seeds.

For each cluster and control role, v0.8 takes the median paired delta in the
cluster, then runs the sign summary over clusters rather than over seed rows.

```text
delta = complete residual_gap_count - control residual_gap_count
negative delta = complete has fewer residual components
```

The sign-test p-value is still exploratory. It is now cluster-level, but the
cluster construction itself was chosen after earlier exploration.

## First Reading

| control | clusters | complete smaller clusters | median cluster delta | sign p |
|---|---:|---:|---:|---:|
| local_mod6_control | 11 | 9 | -24.0 | 0.0654 |
| band_mod6_control | 11 | 6 | -27.0 | 0.5078 |
| band_ordinary_control | 11 | 10 | -37.0 | 0.0117 |

The conservative reading is:

- `local_mod6_control` remains suggestive after cluster aggregation, but it is
  not a confirmatory result.
- `band_mod6_control` remains unclear.
- `band_ordinary_control` remains strong, but it is the weakest control design
  and has heavy reuse, so it should not be the headline.

This means the v0.7 signal is not obviously just a single-row artifact, but it
is also not strong enough under hard controls to become a claim.

## Control Reuse

| control | pairs | unique controls | reused controls | reused pairs |
|---|---:|---:|---:|---:|
| local_mod6_control | 33 | 33 | 0 | 0 |
| band_mod6_control | 33 | 25 | 8 | 16 |
| band_ordinary_control | 33 | 16 | 11 | 28 |

`local_mod6_control` has no control reuse in this cohort. The two band controls
reuse controls, especially `band_ordinary_control`.

This reinforces the v0.7.1 caveat: the strongest numeric result appears in the
least robust control role.

## Decision

v0.8 supports continuing, but only into a stricter null model. The next useful
step is:

```text
v0.9 branch-wise shuffled centers null
```

That null should preserve branch sizes and arc widths while randomizing centers
inside each branch or local branch bucket. The question should be:

```text
Is the observed complete-vs-control residual_gap_count direction unusual
relative to a structure-preserving shuffled baseline?
```

## Non-Claims

- v0.8 does not claim `residual_gap_count` explains exact complete covering.
- v0.8 does not claim the 11 clusters are independent experimental units in a
  confirmatory sense.
- v0.8 does not claim the `band_ordinary_control` signal is robust.
- v0.8 does not use a shuffled or random-arc null model yet.
- v0.8 does not expand the cohort beyond the v0.6/v0.7 33 eligible seeds.
