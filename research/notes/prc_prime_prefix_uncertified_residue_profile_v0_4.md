# PRC Prime-Prefix Uncertified Residue Profile v0.4

This note profiles the complete-covering values that remain without a
prime-prefix certificate after the guarded `k=8` extension.

The purpose is diagnostic. It does not claim these values are non-certifiable;
it only describes the residual class left by the current checked filtration.

## Input

Input certificate table:

```text
data/summaries/prc_prime_prefix_certificate_depth_k8_v0_3.csv
```

Rows with:

```text
certificate_status = no_prefix_certificate_within_max_k
```

are profiled against the exact covered residue set `C_8`.

## Command

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-uncertified-residues \
  --certificates data/summaries/prc_prime_prefix_certificate_depth_k8_v0_3.csv \
  --max-k 8 \
  --allow-large-k \
  --out data/summaries/prc_prime_prefix_uncertified_residue_profile_v0_4.csv \
  --summary-out data/summaries/prc_prime_prefix_uncertified_residue_summary_v0_4.csv \
  --mod210-out data/summaries/prc_prime_prefix_uncertified_mod210_summary_v0_4.csv
```

## Outputs

```text
data/summaries/prc_prime_prefix_uncertified_residue_profile_v0_4.csv
data/summaries/prc_prime_prefix_uncertified_residue_summary_v0_4.csv
data/summaries/prc_prime_prefix_uncertified_mod210_summary_v0_4.csv
```

The detail table records, for each uncertified `N`, its residue modulo `M_8`,
the nearest residue in `C_8`, the source depth of that nearest covered residue,
and the circular distance in residue units.

## Overall Summary

| metric | value |
|---|---:|
| uncertified count | 4,495 |
| checked max k | 8 |
| checked max prime | 19 |
| residue modulus `M_8` | 9,699,690 |
| unique mod 210 classes | 98 |
| nearest distance median | 25 |
| nearest distance p90 | 56 |
| nearest distance p99 | 90 |
| nearest distance max | 97 |

The distances are residue distances modulo `M_8`, not arc distances on the
circle. They measure proximity to the finite certificate set `C_8`, not
analytic closeness to complete covering.

## Top mod 210 Classes

| mod 210 | count | share | median nearest distance | max distance |
|---:|---:|---:|---:|---:|
| 111 | 209 | 0.046496 | 37 | 97 |
| 4 | 204 | 0.045384 | 2 | 2 |
| 99 | 197 | 0.043826 | 37 | 97 |
| 206 | 185 | 0.041157 | 2 | 2 |
| 118 | 162 | 0.036040 | 26 | 90 |

The strongest immediate pattern is that the remaining uncertified values are
not spread across all modulo-210 classes: only `98` classes occur, and several
classes dominate. Some high-count classes, such as `4` and `206`, are very
close to `C_8` in residue distance, while classes such as `111` and `99` have
larger nearest-distance profiles.

## Reading

The conservative reading is:

```text
the residual complete-covering class after C_8 is structured enough to profile
before attempting C_9.
```

This supports the hierarchy program because the remaining cases are no longer
just a flat list of complete-covering integers. They have wheel-residue and
nearest-certificate geometry that can be inspected directly.

## Non-Claims

- v0.4 does not claim the nearest `C_8` residue explains why an `N` is complete.
- v0.4 does not claim the `98` modulo-210 classes are stable asymptotically.
- v0.4 does not claim `C_9` is unnecessary.
- v0.4 does not use non-complete controls yet.

## Next Step

Before a full `k=9` scan, compare these `4,495` rows against matched
non-complete controls using the same residue profile. That would separate
"ordinary proximity to `C_8`" from a property specific to exact complete-covering
values.
