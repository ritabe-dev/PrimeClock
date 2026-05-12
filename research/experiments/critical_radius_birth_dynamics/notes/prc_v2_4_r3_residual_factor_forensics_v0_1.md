# PRC v2.4 r=3 Residual Factor Forensics v0.1

Status: source-only explanatory note for the v2.4 Gate R line. This is not a
public release claim.

## Question

After giving `r=3 mod 6` the favorable narrow-hole correction, why does it
still appear at about `2.5x`?

## Short Answer

The factor is not a visual estimate. It is the exact checked ratio

```text
observed_birth_lineage_count / inverse_width_expected_count
= 556 / (5775/26)
= 14456/5775
= 2.503203...
```

The number comes from the `k=2` birth-lineage population across checked
`B5/B6/B7` births. The favorable correction is the `inverse_width` model: a
narrower residual hole receives larger expected mass before the ratio is
computed.

## Evidence Chain

### 1. Population

The denominator model is fitted over the `770` checked birth-lineage rows at
layer `k=2`.

In `prc_v2_4_birth_potential_score_v0_1.csv`, `r=3` has:

```text
layer_k=2
model=inverse_width
residue=3
residual_width=1/6
normalized_expected_count=5775/26
observed_birth_lineage_count=556
observed_over_expected=14456/5775
```

The same value is repeated in the Gate R arithmetic table as the
`k2_width_normalized_lineage_survival` diagnostic:

```text
stratum=r=3
family_count=556
lift_count=770
close_rate=14456/5775
observed_share=5775/26
note=width=1/6;inverse_width_expected=5775/26
```

### 2. Why the expected count is `5775/26`

At `k=2`, the modulus is `2 * 3 = 6`. The residual widths by residue are:

```text
r=0: 1/2
r=1: 5/12
r=2: 1/4
r=3: 1/6
r=4: 1/4
r=5: 5/12
```

The narrow-hole correction uses inverse residual width:

```text
r=0: 2
r=1: 12/5
r=2: 4
r=3: 6
r=4: 4
r=5: 12/5
total inverse weight = 104/5
```

So the corrected expected count for `r=3` is:

```text
770 * 6 / (104/5)
= 770 * 30 / 104
= 5775/26
= 222.115384...
```

This already gives `r=3` the largest expected count because `1/6` is the
narrowest residual width.

### 3. Where the remaining `2.5x` comes from

The observed count is `556`, so after the favorable correction:

```text
556 / (5775/26)
= 556 * 26 / 5775
= 14456/5775
= 2.503203...
```

For comparison, the uncorrected uniform baseline is:

```text
expected_uniform_count = 770 / 6 = 385/3
observed_over_uniform = 556 / (385/3) = 1668/385 = 4.332467...
```

Thus inverse-width correction explains part of the raw concentration:

```text
4.332467 / 2.503203 = 1.730769...
```

but leaves the checked residual factor `14456/5775`.

## Control Interpretation

This factor should be presented as a lineage-survival signal, not as proof that
width alone explains birth.

- Same occurrence: every `k=2` residue starts with occurrence probability `1/6`.
- Same-width neighbors do not explain it: `r=2` and `r=4` have wider `1/4`
  residual holes and only `103 + 103` birth-lineage rows, while `r=3` has `556`.
- Zero-side controls do not explain it: `r=1` and `r=5` contain the zero-side
  residual but have only `4 + 4` rows, while `r=3` does not contain the zero side.
- Capacity conditioning sharpens the story: in the all-scope capacity table,
  `r=3` has `556/950 = 278/475` close rate, while the symmetric neighbors have
  `103/1112`.

## Presentation-Grade Claim Boundary

Safe phrasing:

```text
In the checked B5/B6/B7 source-only v2.4 data, the k=2 residue r=3 remains
enriched by 14456/5775 = 2.503x even after the inverse-width narrow-hole
correction. The factor is the observed 556 r=3 birth-lineage rows divided by
the inverse-width expected count 5775/26. This is evidence for a
width-normalized lineage-survival bias, not a standalone width-only mechanism.
```

Unsafe phrasing:

```text
The narrow hole explains the birth concentration.
```

The current Gate R synthesis rejects that statement. Width is useful, but the
remaining factor is exactly the part still requiring lineage-survival and phase
alignment explanation.
