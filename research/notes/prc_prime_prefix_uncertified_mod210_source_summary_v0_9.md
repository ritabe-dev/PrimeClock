# PRC Prime-Prefix Mod-210 Source Summary v0.9

## Purpose

v0.8 expanded the top modulo-210 classes into individual seed/control rows.
v0.9 compresses those rows by:

```text
mod 210 class
cohort role
nearest C_k source depth
```

The goal is to see which `C_k` layer the selected classes sit near. This keeps
the project aligned with the main finite residue-covering hierarchy: we are not
trying to explain complete covering directly, but to understand how the
remaining rows sit relative to the exact prefix filtration.

## Command

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-uncertified-class-source-summary \
  --detail data/summaries/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.csv \
  --out data/summaries/prc_prime_prefix_uncertified_mod210_class_source_summary_v0_9.csv
```

## Output

```text
data/summaries/prc_prime_prefix_uncertified_mod210_class_source_summary_v0_9.csv
```

The output has `93` data rows.

## First Reading

For the complete rows in the top selected classes:

| mod 210 | main source-depth pattern |
|---:|---|
| 111 | mostly near `C_5`; 137/209 rows have nearest source `k=5` |
| 4 | entirely near `C_4`; 204/204 rows have nearest source `k=4` |
| 99 | mostly near `C_5`; 142/197 rows have nearest source `k=5` |
| 206 | entirely near `C_4`; 185/185 rows have nearest source `k=4` |
| 118 | mixed, centered on `C_5`; 81/162 rows have nearest source `k=5` |
| 88 | mixed, centered on `C_5`; 82/153 rows have nearest source `k=5` |
| 201 | almost entirely near `C_4`; 148/152 rows have nearest source `k=4` |
| 62 | mixed, centered on `C_5`; 75/151 rows have nearest source `k=5` |

This suggests the top classes are not homogeneous:

- `4`, `206`, and `201` are essentially shallow `C_4`-adjacent classes.
- `111` and `99` are high-count classes mostly adjacent to `C_5`.
- `118`, `88`, and `62` are more distributed across source depths.

## Interpretation

This is a better stopping point than immediately trying `k=9`.

The remaining uncertified rows are not simply "far from `C_8`". Several large
classes are close to very shallow source layers (`C_4` or `C_5`) after lifting
to `M_8`. That makes the next conceptual question:

```text
Which lifted shallow C_k boundaries keep producing near-misses at deeper
prefixes?
```

That question belongs to the prime-prefix residue filtration itself, so it is
better aligned with the main research goal than more C0 run forensics.

## Next Step

Two viable next moves:

1. **Lift-boundary reading**: inspect classes `4`, `206`, `201`, `111`, and
   `99` as lifted neighborhoods of shallow `C_4`/`C_5` residues.
2. **Discrete residue null**: build a null that preserves prime residue-cell
   discreteness and compare these source-depth patterns.

For the next small slice, the lift-boundary reading is cheaper and clearer.

## Non-Claims

- This does not claim `C_4` or `C_5` explains complete covering.
- This does not claim `k=9` is unnecessary.
- This does not establish an asymptotic law for source-depth profiles.
