# PRC Prime-Prefix k=8 Extension v0.3

This note records the first guarded extension of the exact prime-prefix
residue filtration beyond the default `max_k=7` range.

The goal is feasibility and certificate-depth refinement, not a new asymptotic
claim.

## Command

The `k=8` level is a primorial-scale scan:

```text
M_8 = 2*3*5*7*11*13*17*19 = 9,699,690
```

It is intentionally behind `--allow-large-k`.

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-filtration \
  --max-k 8 \
  --allow-large-k \
  --birth-sample-limit 200 \
  --summary-out data/summaries/prc_prime_prefix_residue_covering_filtration_k8_v0_3.csv \
  --birth-samples-out data/summaries/prc_prime_prefix_residue_covering_birth_samples_k8_v0_3.csv

python -m prime_reciprocal_projection.cli covering-prime-prefix-certificates \
  --complete-source data/summaries/prc_combined_runs_2_1000000.csv \
  --max-k 8 \
  --allow-large-k \
  --out data/summaries/prc_prime_prefix_certificate_depth_k8_v0_3.csv \
  --summary-out data/summaries/prc_prime_prefix_certificate_depth_summary_k8_v0_3.csv
```

The exploratory feasibility run completed locally in about 62 seconds for the
filtration generation.

## Filtration Result

| k | new prime | M_k | `|C_k|` | density | inherited | births |
|---:|---:|---:|---:|---:|---:|---:|
| 7 | 17 | 510,510 | 9,384 | 0.0183816 | 8,670 | 714 |
| 8 | 19 | 9,699,690 | 185,048 | 0.0190777 | 178,296 | 6,752 |

The increase from `k=7` to `k=8` is mostly inherited lifts, but `p=19` adds
`6,752` genuinely new birth residues.

## Certificate-Depth Update

Using the exact-certified complete-covering source for `2 <= N <= 1,000,000`:

| status | k | prime | count | share |
|---|---:|---:|---:|---:|
| prefix certificate | 4 | 7 | 9,522 | 0.403971 |
| prefix certificate | 5 | 11 | 6,061 | 0.257138 |
| prefix certificate | 6 | 13 | 1,398 | 0.059310 |
| prefix certificate | 7 | 17 | 1,396 | 0.059225 |
| prefix certificate | 8 | 19 | 699 | 0.029655 |
| no prefix certificate within max_k | - | - | 4,495 | 0.190700 |

Thus `k=8` certifies `699` additional complete-covering values. The
uncertified group falls from `5,194` at `max_k=7` to `4,495` at `max_k=8`.

## Reading

The conservative reading is:

```text
small-prime prefix certificates explain a large finite subset of complete
covering, but a nontrivial residual class remains after p=19.
```

This supports the finite hierarchy framing. It does not prove that every
complete-covering value eventually has a shallow certificate, nor does it make
anti-clustering the main axis.

## Next Step

The next useful step is not immediately `k=9`; `M_9=223,092,870`, so the scan
scale jumps by a factor of `23`. Before attempting that, inspect the `4,495`
uncertified rows under `max_k=8`:

- distribution of `N mod M_8`;
- proximity to `C_8` birth residues;
- whether uncertified rows concentrate in small wheel classes;
- comparison with non-complete controls using the same residue profile.
