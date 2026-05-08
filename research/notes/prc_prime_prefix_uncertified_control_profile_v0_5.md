# PRC Prime-Prefix Uncertified Control Profile v0.5

This note compares the `C_8`-uncertified complete-covering rows against local
non-complete controls using the same nearest-`C_8` residue profile.

The purpose is to check whether the v0.4 residue-distance pattern is specific
to complete-covering values or is also present in nearby ordinary values.

## Inputs

```text
data/summaries/prc_prime_prefix_uncertified_residue_profile_v0_4.csv
data/summaries/prc_combined_runs_2_1000000.csv
```

The first file supplies the `4,495` complete-covering values left uncertified
after `max_k=8`. The second file supplies the full exact-certified complete set
used to avoid selecting complete values as controls.

## Control Rules

For each uncertified complete seed `N`, select:

```text
complete_uncertified: N itself
local_mod210_control: nearest non-complete M within N±250 and M == N mod 210
local_any_control: nearest non-complete M within N±250
```

Ties are resolved by smaller `M`. Missing controls are omitted rather than
filled.

## Command

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-uncertified-controls \
  --uncertified-profile data/summaries/prc_prime_prefix_uncertified_residue_profile_v0_4.csv \
  --complete-source data/summaries/prc_combined_runs_2_1000000.csv \
  --start 2 \
  --stop 1000000 \
  --local-radius 250 \
  --max-k 8 \
  --allow-large-k \
  --out data/summaries/prc_prime_prefix_uncertified_control_profile_v0_5.csv \
  --summary-out data/summaries/prc_prime_prefix_uncertified_control_summary_v0_5.csv \
  --pair-deltas-out data/summaries/prc_prime_prefix_uncertified_control_pair_deltas_v0_5.csv
```

## Outputs

```text
data/summaries/prc_prime_prefix_uncertified_control_profile_v0_5.csv
data/summaries/prc_prime_prefix_uncertified_control_summary_v0_5.csv
data/summaries/prc_prime_prefix_uncertified_control_pair_deltas_v0_5.csv
```

## Cohort Summary

| cohort | rows | unique N | unique mod 210 | median distance | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| complete_uncertified | 4,495 | 4,495 | 98 | 25 | 56 | 90 | 97 |
| local_mod210_control | 4,475 | 4,465 | 98 | 26 | 60 | 97 | 100 |
| local_any_control | 4,495 | 4,495 | 100 | 25 | 57 | 91 | 98 |

`local_mod210_control` is missing for 20 seeds under the current radius.

## Paired Direction

For `circular_residue_distance`, using `complete - control`:

| control | pairs | median delta | complete smaller | complete larger | ties |
|---|---:|---:|---:|---:|---:|
| local_mod210_control | 4,475 | 0 | 1,654 | 1,511 | 1,310 |
| local_any_control | 4,495 | 1 | 2,201 | 2,273 | 21 |

## Reading

The v0.5 control check does **not** support a strong claim that uncertified
complete-covering values are uniquely close to `C_8`. The hard
`local_mod210_control` has nearly the same distance distribution, with median
delta `0` and many ties. The weaker `local_any_control` is also very close.

The conservative reading is:

```text
the C_8-nearest-distance profile is largely a local/wheel-residue feature,
not yet a complete-specific explanation.
```

This is useful: it prevents over-reading the v0.4 residue-distance pattern and
points the next step away from pure nearest-distance claims.

## Next Step

The next useful comparison is not a larger `k` by default. Better next targets:

- inspect mod-210 classes where complete and controls diverge most;
- compare source depth of nearest `C_8` residue;
- add a stricter discrete residue null for the same profile;
- only then decide whether `k=9` is worth the compute.
