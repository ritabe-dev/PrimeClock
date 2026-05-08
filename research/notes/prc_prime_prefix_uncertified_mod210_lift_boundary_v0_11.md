# PRC Prime-Prefix Modulo-210 Lift-Boundary Table v0.11

## Purpose

This artifact inverts the v0.10 boundary summary.

Instead of asking which covered anchor each selected class is near, it asks:

```text
For each shallow covered anchor, which selected modulo-210 classes appear
around it?
```

The default table keeps nearest source depths `k <= 5`. This is intentionally
smaller than a `k=9` enumeration and stays focused on the finite prime-prefix
hierarchy.

## Command

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-uncertified-lift-boundary \
  --detail data/summaries/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.csv \
  --source-max-k 5 \
  --out data/summaries/prc_prime_prefix_uncertified_mod210_lift_boundary_v0_11.csv
```

Output:

```text
data/summaries/prc_prime_prefix_uncertified_mod210_lift_boundary_v0_11.csv
```

The generated table has `140` data rows.

## First Reading

For complete rows, the largest shallow-anchor neighborhoods are:

| source | anchor mod 210 | selected class | signed delta | row count |
|---|---:|---:|---:|---:|
| `C_4` | 2 | 4 | +2 | 204 |
| `C_4` | 208 | 206 | -2 | 185 |
| `C_4` | 208 | 201 | -7 | 148 |
| `C_5` | 62 | 111 | +49 | 49 |
| `C_5` | 148 | 99 | -49 | 46 |
| `C_4` | 2 | 62 | +60 | 37 |
| `C_4` | 2 | 88 | +86 | 26 |
| `C_5` | 122 | 99 | -23 | 26 |
| `C_5` | 88 | 111 | +23 | 23 |

The cleanest interpretation is:

- `C_4` anchor `2` dominates class `4`, but also contributes visible
  neighborhoods at `62`, `88`, and `99`.
- `C_4` anchor `208` dominates classes `206` and `201`, with a smaller
  contribution toward `118`.
- `C_5` anchor `62` points strongly toward class `111`.
- `C_5` anchor `148` points strongly toward class `99`.
- `C_5` anchor `122` splits toward `99`, `88`, and `118`.

## Interpretation

The selected modulo-210 classes are not arbitrary labels. Several are readable
as low-depth anchor neighborhoods in the lifted finite residue filtration.

The most stable exact object to pursue next is therefore:

```text
anchor-neighborhood structure of C_4 and C_5 inside the C_8 residue ring
```

This is still a descriptive finite-`N` artifact. It does not explain complete
covering, but it gives a much clearer target for the next exact table than a
raw `k=9` scan.

## Non-Claims

- This does not claim that `C_4` or `C_5` determines complete covering.
- This does not claim that modulo `210` is the final wheel level.
- This does not claim that the selected classes are representative of all
  uncertified complete-covering values.
- This does not replace a discrete residue null model.
