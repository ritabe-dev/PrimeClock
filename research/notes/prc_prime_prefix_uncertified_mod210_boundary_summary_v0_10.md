# PRC Prime-Prefix Modulo-210 Boundary Summary v0.10

## Purpose

This note reads the selected modulo-210 classes from v0.8/v0.9 as neighborhoods
of shallow covered residue anchors.

The v0.9 source-depth table answered:

```text
Which C_k layer is the nearest covered residue coming from?
```

This v0.10 boundary table answers the next finite-filtration question:

```text
Within mod 210, which covered residue anchor is the selected class near?
```

This remains a main-line prime-prefix hierarchy diagnostic. It is not a new
complete-covering law and not a null model.

## Command

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-uncertified-class-boundary-summary \
  --detail data/summaries/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.csv \
  --out data/summaries/prc_prime_prefix_uncertified_mod210_class_boundary_summary_v0_10.csv
```

Output:

```text
data/summaries/prc_prime_prefix_uncertified_mod210_class_boundary_summary_v0_10.csv
```

The generated table has `414` data rows.

## First Reading

For complete rows in the selected classes:

| mod 210 | dominant boundary reading |
|---:|---|
| 4 | entirely near `C_4` anchor `2`, at signed delta `+2` |
| 206 | entirely near `C_4` anchor `208`, at signed delta `-2` |
| 201 | mostly near `C_4` anchor `208`, at signed delta `-7` |
| 111 | mostly spread across `C_5` anchors; largest anchors are `62` and `88` |
| 99 | mostly spread across `C_5` anchors; largest anchors are `148` and `122` |
| 118 | mixed, with a large `C_6` anchor at `99` and several `C_5` anchors |
| 88 | mixed, with visible `C_4` anchor `2` plus several `C_5` anchors |
| 62 | mixed, with visible `C_4` anchor `2` plus several `C_5` anchors |

The cleanest shallow-boundary cases are therefore:

```text
4   = 2   + 2 mod 210
206 = 208 - 2 mod 210
201 = 208 - 7 mod 210
```

The classes `111` and `99` are not single `C_4` boundary effects. They look
more like neighborhoods of the richer `C_5` lifted anchor set. Classes `118`,
`88`, and `62` are mixed and should not be summarized by one anchor.

## Interpretation

The useful object is no longer only the selected modulo-210 class. It is the
pair:

```text
(nearest covered source depth, nearest covered residue mod 210)
```

This suggests that the next exact object should be a lifted-boundary table:

```text
for each shallow covered residue a in C_k,
which mod 210 classes occur near lifts of a in C_8?
```

That is cheaper and more interpretable than jumping directly to a `k=9`
enumeration.

## Non-Claims

- This does not explain why a value is complete-covering.
- This does not claim that modulo `210` is sufficient.
- This does not claim that the selected classes are representative of all
  uncertified complete-covering values.
- This does not replace a discrete residue null model.
