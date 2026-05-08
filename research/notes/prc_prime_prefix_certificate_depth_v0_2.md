# PRC Prime-Prefix Certificate Depth v0.2

This note connects the exact residue filtration `C_k` to the existing
exact-certified complete-covering values.

The guiding question is:

```text
complete-covering N は、どの小素数prefix C_k によって既に証明されるのか。
```

This keeps complete covering as a boundary/certificate case of the finite
prime residue-cell covering hierarchy, not as the main PRC axis by itself.

## Definition

Let

```text
M_k = prod_{i<=k} p_i
C_k = {r in Z/M_kZ : union_{i<=k} I_{p_i}(r) = T}
```

For an exact complete-covering value `N`, define:

```text
k_cert(N) = min{k : p_k <= N and N mod M_k in C_k}
P_cert(N) = p_{k_cert(N)}
```

If no such `k` is found in the checked range, the row is marked:

```text
certificate_status = no_prefix_certificate_within_max_k
```

This does not mean no certificate exists. It only means the current generated
filtration through `max_k=7` did not certify it.

## Generated Artifacts

Command:

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-certificates \
  --complete-source data/summaries/prc_combined_runs_2_1000000.csv \
  --max-k 7 \
  --out data/summaries/prc_prime_prefix_certificate_depth_v0_2.csv \
  --summary-out data/summaries/prc_prime_prefix_certificate_depth_summary_v0_2.csv
```

Outputs:

```text
data/summaries/prc_prime_prefix_certificate_depth_v0_2.csv
data/summaries/prc_prime_prefix_certificate_depth_summary_v0_2.csv
```

The input complete source is the exact-certified run table for
`2 <= N <= 1,000,000`.

## Summary

| status | k | prime | count | share |
|---|---:|---:|---:|---:|
| prefix certificate | 4 | 7 | 9,522 | 0.403971 |
| prefix certificate | 5 | 11 | 6,061 | 0.257138 |
| prefix certificate | 6 | 13 | 1,398 | 0.059310 |
| prefix certificate | 7 | 17 | 1,396 | 0.059225 |
| no prefix certificate within max_k | - | - | 5,194 | 0.220356 |

Thus, within `max_k=7`, `18,377 / 23,571` complete-covering values have a
shallow prime-prefix certificate, and `5,194` remain uncertified by the current
filtration.

## Reading

The main observation is not that complete covering has been explained. The
safer reading is:

```text
many complete-covering values are already forced by small-prime residue cells.
```

The `k=4` rows are exactly the `C_4={2,208} mod 210` stratum. These are marked
as `trivial_c4_certificate=True` in the detail CSV. The `k=5..7` rows show
additional finite residue strata born when primes `11`, `13`, and `17` are
added.

The remaining `no_prefix_certificate_within_max_k` rows are the important next
object. They may be certified at `k>=8`, or they may require a different
description than shallow prime-prefix certificates.

## Non-Claims

- v0.2 does not claim a law for complete-covering values.
- v0.2 does not claim `max_k=7` is enough for all complete-covering values.
- v0.2 does not claim anything about `N>10^6`.
- v0.2 does not turn anti-clustering into the main PRC axis.
- v0.2 only connects existing exact-certified complete values to the finite
  exact `C_k` filtration already generated.

## Next Step

The natural next step is a guarded `k=8` feasibility check. Since
`M_8=9,699,690`, this should be treated as a primorial-scale scan and kept
behind the existing `--allow-large-k` guardrail.
