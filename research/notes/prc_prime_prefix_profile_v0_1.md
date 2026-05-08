# PRC Prime-Prefix Residual Profile v0.1

Purpose: make the new main frame, **finite-`N` hierarchy of prime residue-cell
coverings**, visible as a reproducible CSV artifact.

This note is descriptive. It does not claim an asymptotic law, and the
`numeric_complete_prefix` column is not an exact certificate.

## Definition

For fixed `N`, each prime `p` selects the residue cell

```text
C_{p,r} = [(2r-1)/(2p), (2r+1)/(2p)] mod 1
I_p(N) = C_{p, N mod p}.
```

The prime-prefix hierarchy adds these cells in increasing prime order:

```text
U_P(N) = union_{p<=P} I_p(N)
A_P(N) = |T \ U_P(N)|
R_P(N) = T \ U_P(N).
```

`A_P(N)` must be nonincreasing as `P` grows. The residual component count,
maximum gap, gap quantiles, and top-gap share describe the shape of `R_P(N)`.

## Artifact

Generate:

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-profile \
  --n 1000 10000 100000 1000000 39069 372759 \
  --out data/summaries/prc_prime_prefix_profile_v0_1.csv
```

Output:

```text
data/summaries/prc_prime_prefix_profile_v0_1.csv
```

Current file has 125 data rows. The fixed checkpoints are:

```text
2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31,
47, 97, 199, 499, 997, 1999, 4999, 9973,
19997, 49999, 99991, 199999, 499979, 999983
```

Checkpoints with `P > N` are omitted.

## Columns

- `n`: fixed integer `N`.
- `p_prefix`: prime-prefix cutoff `P`.
- `prime_index`: number of primes `p <= P`.
- `prefix_width_sum`: `sum_{p<=P} 1/p`.
- `poisson_prefix_baseline`: `exp(-sum_{p<=P} 1/p)`.
- `product_prefix_baseline`: `prod_{p<=P}(1 - 1/p)`.
- `uncovered_measure`: `A_P(N)`.
- `uncovered_over_product_baseline`: `A_P(N) / product_prefix_baseline`.
- `baseline_delta`: `A_P(N) - product_prefix_baseline`.
- `log_uncovered_minus_log_product_baseline`: log ratio against product baseline.
- `component_count`: number of residual components.
- `max_gap`, `gap_p50`, `gap_p90`, `gap_p99`: residual gap shape.
- `top_gap_share`: largest gap divided by `A_P(N)`.
- `numeric_complete_prefix`: floating-point descriptive flag only.

Blank ratio/log-ratio cells mean the numerator or denominator was zero in a
place where a finite ratio would be misleading.

## Initial Reading

Summary from the generated CSV:

| N | rows | last P | first A_P | last A_P | last components | first numeric-complete checkpoint |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 16 | 997 | 0.500000 | 0.114647 | 19 | none |
| 10,000 | 19 | 9,973 | 0.500000 | 0.041923 | 49 | none |
| 39,069 | 20 | 19,997 | 0.500000 | 0.000000 | 0 | 29 |
| 100,000 | 22 | 99,991 | 0.500000 | 0.040222 | 346 | none |
| 372,759 | 23 | 199,999 | 0.500000 | 0.000000 | 0 | 11 |
| 1,000,000 | 25 | 999,983 | 0.500000 | 0.050069 | 3,308 | none |

The generic rows show the hierarchy clearly: as more small-to-large prime cells
are added, `A_P(N)` falls while the residual set often breaks into many more
pieces. For example, `N=1,000,000` ends with `A_P≈0.0501` and 3,308 residual
components at the full checkpoint.

The two selected complete-covering examples, `N=39,069` and `N=372,759`, show
early numeric prefix coverage at the coarse checkpoint level. This is useful
for choosing later certificate-depth questions, but v0.1 does not treat these
flags as exact mathematical certificates.

## Interpretation

This artifact shifts the main line away from asking only whether `A(N)=0`.
The stronger object is the whole path

```text
P -> R_P(N).
```

The next natural question is certificate depth: when a numeric prefix appears
to cover the circle, what is the smallest prime prefix that is exactly
certifiable with rational interval arithmetic? That belongs in the next phase,
not in this descriptive CSV.

## Validation

Current focused checks:

```bash
python -m pytest tests/test_covering_prime_prefix.py
python -m ruff check src/prime_reciprocal_projection/covering_prime_prefix.py \
  tests/test_covering_prime_prefix.py
```

The full validation gate remains:

```bash
python -m ruff check src tests
python -m pytest
UV_CACHE_DIR=.uv-cache .venv/bin/uv run pytest
npm run build
git diff --check
```
