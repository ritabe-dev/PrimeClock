# PRC Prime-Prefix Modulo-210 Anchor Neighborhood v0.12

## Purpose

This artifact moves from the v0.11 sample-derived lift-boundary table to a
direct exact table on the `C_8` residue ring.

For selected modulo-210 classes, it scans residues modulo `M_8` in that class,
excludes residues already covered by `C_8`, and classifies each remaining
residue by its nearest shallow covered anchor with source depth `k <= 5`.

This separates two questions:

```text
Geometry question:
  Which shallow anchors are near a modulo-210 class inside the C_8 ring?

Sample question:
  Which of those neighborhoods are actually visited by the observed complete
  and control rows?
```

v0.12 answers the geometry question. v0.11 answers the sample question.

## Command

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-mod210-anchor-neighborhood \
  --max-k 8 \
  --source-max-k 5 \
  --allow-large-k \
  --out data/summaries/prc_prime_prefix_mod210_anchor_neighborhood_v0_12.csv
```

Output:

```text
data/summaries/prc_prime_prefix_mod210_anchor_neighborhood_v0_12.csv
```

The generated table has `47` data rows.

## First Reading

The three clean `C_4` cases remain clean in the full `C_8` geometry:

| target mod 210 | dominant shallow anchor | share |
|---:|---|---:|
| 4 | `C_4` anchor `2`, signed delta `+2` | `1.0` |
| 206 | `C_4` anchor `208`, signed delta `-2` | `1.0` |
| 201 | `C_4` anchor `208`, signed delta `-7` | `1.0` |

For the mixed classes, the direct ring geometry is more symmetric than the
observed sample:

| target mod 210 | largest direct-geometry anchor | share |
|---:|---|---:|
| 111 | `C_4` anchor `208`, signed delta `-97` | `0.1827` |
| 99 | `C_4` anchor `2`, signed delta `+97` | `0.1827` |
| 118 | `C_4` anchor `208`, signed delta `-90` | `0.2000` |
| 88 | `C_4` anchor `2`, signed delta `+86` | `0.3000` |
| 62 | `C_4` anchor `2`, signed delta `+60` | `0.4000` |

The remaining mass is split across several `C_5` anchors in equal-size blocks.
For example, class `111` has many `C_5` anchor blocks with share `0.0913`;
class `118` has several `C_5` blocks with share `0.1`.

## Interpretation

v0.12 shows that the selected classes have a simple exact geometry relative to
shallow anchors:

- `4`, `206`, and `201` are genuinely clean `C_4` boundary classes.
- `111`, `99`, `118`, `88`, and `62` have mixed shallow-anchor geometry.
- The apparent dominance of particular `C_5` anchors in v0.11 is not purely a
  geometric fact of the whole `C_8` ring. It is partly a sample/complete-control
  weighting effect.

That makes the next useful question sharper:

```text
Within each shallow-anchor neighborhood, which actual N-values are selected,
and is that selection explained by local residue constraints beyond mod 210?
```

This is a better next step than increasing `k` again.

## Non-Claims

- This does not explain complete covering.
- This does not claim that `mod 210` is sufficient.
- This does not claim that the observed sample is uniform inside these
  neighborhoods.
- This does not replace a discrete residue null model.
