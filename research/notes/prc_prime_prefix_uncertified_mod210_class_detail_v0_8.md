# PRC Prime-Prefix Uncertified Mod-210 Class Detail v0.8

## Purpose

v0.7 ranked modulo-210 classes by how differently the controls behave. v0.8
expands the top classes back to seed/control rows so the comparison can be read
at the level of individual complete values and their controls.

This is a detail table for inspection. It is not a new claim and not a new null
model.

## Command

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-uncertified-class-detail \
  --profile data/summaries/prc_prime_prefix_uncertified_control_profile_v0_5.csv \
  --class-review data/summaries/prc_prime_prefix_uncertified_mod210_class_review_v0_7.csv \
  --class-limit 8 \
  --out data/summaries/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.csv
```

## Output

```text
data/summaries/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.csv
```

The output expands the top `8` ranked modulo-210 classes from v0.7:

```text
111, 4, 99, 206, 118, 88, 201, 62
```

It contains `4,227` data rows:

| role | rows |
|---|---:|
| `complete_uncertified` | 1,413 |
| `local_mod210_control` | 1,401 |
| `local_any_control` | 1,413 |

The slight deficit in `local_mod210_control` rows comes from seeds where no
same-modulo-210 non-complete control exists inside the local radius.

## How To Read

Each row keeps the selected class metadata and the underlying profile row:

- `selected_rank`, `seed_mod210`, `priority_label`, `direction_label`
- `seed_n`, `cohort_role`, `n`, `control_delta`
- `residue`, `nearest_covered_residue`
- `nearest_covered_source_k`, `nearest_covered_source_prime`
- `circular_residue_distance`
- `complete_circular_residue_distance`
- `distance_minus_complete`

`distance_minus_complete` is:

```text
row circular distance - complete row circular distance
```

So for controls:

- negative means the control is closer to `C_8` than the complete row.
- positive means the control is farther from `C_8` than the complete row.
- zero means they tie at this distance scale.

## First Reading

The first selected class, `mod210=111`, shows why the v0.7 direction label is
mixed:

```text
direction_label = mod210_complete_smaller__any_complete_larger
```

That means:

- against same-modulo-210 controls, complete rows tend to be closer to `C_8`.
- against nearest-any controls, complete rows tend to be farther from `C_8`.

This is exactly the kind of pattern that argues against treating nearest
distance to `C_8` as a complete-specific explanation. The comparison depends on
which local/wheel structure the control preserves.

## Next Use

Use this detail table for targeted inspection before attempting `k=9`.
Reasonable next targets are:

- `mod210=111`: largest mixed-direction class.
- `mod210=99`: large class where mod210-control and any-control signs disagree
  in the opposite direction.
- `mod210=62`: large mixed class with a sizeable median-delta gap.
- `mod210=4` / `206` / `201`: classes where same-mod210 controls often tie but
  nearest-any controls move in one direction.

## Non-Claims

- This detail table does not explain complete covering.
- This detail table does not imply that `mod210` alone controls the phenomenon.
- This detail table does not justify a `k=9` scan by itself.
