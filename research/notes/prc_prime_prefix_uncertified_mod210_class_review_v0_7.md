# PRC Prime-Prefix Uncertified Mod-210 Class Review v0.7

## Purpose

v0.6 produced the raw modulo-210 audit for the `4,495` complete-covering values
left uncertified after `C_8`. v0.7 pivots that audit into one row per
`mod 210` class so the next manual or model-based inspection has a stable
target list.

This is a review table, not a new null model and not a complete-covering
explanation.

## Command

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-uncertified-class-review \
  --audit data/summaries/prc_prime_prefix_uncertified_control_mod210_audit_v0_6.csv \
  --out data/summaries/prc_prime_prefix_uncertified_mod210_class_review_v0_7.csv
```

## Output

```text
data/summaries/prc_prime_prefix_uncertified_mod210_class_review_v0_7.csv
```

The table has `98` rows, one for each modulo-210 class occupied by the
uncertified complete rows.

## Priority Labels

The table compares two controls for each class:

- `local_mod210_control`: nearest local non-complete with the same mod-210
  class.
- `local_any_control`: nearest local non-complete without preserving mod 210.

`delta = complete_distance - control_distance`, so negative means the complete
row is closer to `C_8`.

Priority labels are descriptive:

| label | meaning |
|---|---|
| `large_class_mixed_direction` | at least 100 pairs and the two controls give different sign directions |
| `large_class_large_control_gap` | at least 100 pairs and the two controls differ strongly in median delta or smaller-rate |
| `large_class_baseline` | at least 100 pairs without a strong control disagreement |
| `small_class_mixed_direction` | fewer than 100 pairs but mixed control direction |
| `small_class` | smaller class without mixed direction |

## First Reading

Summary of the generated table:

| priority label | class count |
|---|---:|
| `large_class_mixed_direction` | 16 |
| `large_class_large_control_gap` | 1 |
| `large_class_baseline` | 1 |
| `small_class_mixed_direction` | 53 |
| `small_class` | 27 |

Top priority classes by pair count:

| mod 210 | max pairs | direction label | median delta vs mod210 | median delta vs any |
|---:|---:|---|---:|---:|
| 111 | 209 | `mod210_complete_smaller__any_complete_larger` | -12.0 | 1.0 |
| 4 | 204 | `mod210_tied__any_complete_larger` | 0.0 | 1.0 |
| 99 | 197 | `mod210_complete_larger__any_complete_smaller` | 6.0 | -1.0 |
| 206 | 185 | `mod210_tied__any_complete_smaller` | 0.0 | -1.0 |
| 118 | 162 | `mod210_tied__any_complete_larger` | 0.0 | 1.0 |
| 88 | 153 | `mod210_tied__any_complete_smaller` | 0.0 | -1.0 |
| 201 | 152 | `mod210_tied__any_complete_smaller` | 0.0 | -1.0 |
| 62 | 151 | `mod210_complete_smaller__any_complete_larger` | -7.0 | 1.0 |

The important pattern is not that complete rows are uniformly closer to `C_8`.
Rather, the direction often depends on whether the control preserves the
modulo-210 class. That reinforces the v0.5/v0.6 reading: this layer is mostly a
local wheel-residue diagnostic.

## Next Use

Use this table to choose one of two next moves:

1. Inspect a handful of large mixed-direction classes such as `111`, `99`,
   `62`, and `4` to see how their residues sit near `C_8`.
2. Build a stricter discrete residue null that preserves prime residue-cell
   structure more directly than the older branch-uniform null.

## Non-Claims

- This table does not explain why the remaining rows are complete-covering.
- This table does not justify `k=9` yet.
- This table does not establish a law for modulo-210 classes.
