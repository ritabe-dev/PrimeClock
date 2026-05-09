# A finite prime-prefix residue-covering certificate for PRC

Version: v2.0
Date: 2026-05-09 JST

## Abstract

For the first `k` primes `p_1,...,p_k`, let `M_k=prod_{i<=k}p_i`. Each residue
`r in Z/M_kZ` chooses one closed arc of length `1/p_i`, centered at
`(r mod p_i)/p_i`, for every prime in the prefix. This note studies the finite
set `C_k` of residues for which those arcs cover the circle.

The sets `C_k` form a lifted monotone filtration over primorial residue rings:
covered residues lift to covered residues at the next prime, and the new
covered residues form a birth layer `B_k`. The first nonempty layer is
`C_4={2,208} mod 210`. At `k=5`, `C_5` has `36` covered residues, split into
`22` inherited lifts and `14` births in `7` reflection pairs. The claims in
this note are finite certificate statements backed by exact rational CSVs, a
package verifier, and a standard-library standalone checker. They are not
claims about asymptotic prime distribution.

## 1. Introduction

Prime Reciprocal Covering (PRC) places, for each prime `p`, a circle arc of
length `1/p` centered at the reciprocal phase `{N/p}`. Since

```text
{N/p} = (N mod p) / p,
```

the first `k` prime arcs depend only on the residue class of `N` modulo the
primorial `M_k`. This turns the prefix-covering question into a finite
residue-ring problem.

The purpose of this note is deliberately small: define this finite object and
record two auditable certificate results:

```text
C_4 = {2,208} mod 210,
B_5 = {118,448,542,778,849,872,1108,
       1202,1438,1461,1532,1768,1862,2192} mod 2310.
```

The visualization that motivated PRC is not used as proof. All theorem-level
claims here are finite and checked with rational interval arithmetic.

## 2. Definition of `C_k`

Let

```text
p_1=2, p_2=3, ...
M_k = prod_{i<=k} p_i.
```

For a residue `r in Z/M_kZ`, define

```text
I_p(r) = [(r mod p)/p - 1/(2p), (r mod p)/p + 1/(2p)] in R/Z.
```

The residue `r mod p` is represented in `{0,...,p-1}`. If the interval crosses
`0`, it is interpreted as the corresponding wrapped subset of the torus
`R/Z`.

Define

```text
U_k(r) = union_{i<=k} I_{p_i}(r),
C_k = {r in Z/M_kZ : U_k(r)=R/Z}.
```

The sets `C_k` live in different residue rings. The word filtration means a
lifted filtration through the natural maps

```text
pi_{k,k-1}: Z/M_kZ -> Z/M_{k-1}Z.
```

Set

```text
Lift_k(C_{k-1}) = pi_{k,k-1}^{-1}(C_{k-1}),
B_k = C_k \ Lift_k(C_{k-1}).
```

The set `B_k` is the birth layer: residues not already covered by the first
`k-1` primes, but covered after adding the `k`-th prime.

## 3. Closed arcs and endpoint convention

The arcs in this note are closed. This matters for exact coverage, although it
does not change measures. The base covered class `r=2 mod 210` uses endpoint
touching at `1/2`:

```text
p=5: [3/10,1/2]
p=3: [1/2,5/6]
```

CSV fields named as open gaps give boundary endpoints of uncovered open
intervals. Since the covering arcs are closed, a gap boundary point may be
covered. The certified uncovered point is the rational `witness_point` lying
strictly inside an open gap.

## 4. Lift monotonicity

If `r in C_k`, then every lift of `r` to `Z/M_{k+1}Z` belongs to `C_{k+1}`.
Indeed, every lift has the same residues modulo `p_1,...,p_k`, so its first
`k` arcs are identical. Those arcs already cover `R/Z`, and the new
`p_{k+1}` arc cannot uncover any point.

Thus

```text
Lift_{k+1}(C_k) subset C_{k+1}.
```

## 5. Density monotonicity

Let

```text
alpha_k = |C_k| / M_k.
```

For `k>=2`,

```text
|Lift_k(C_{k-1})| = p_k |C_{k-1}|,
M_k = p_k M_{k-1},
alpha_k = alpha_{k-1} + |B_k| / M_k.
```

Therefore `alpha_k` is nondecreasing. The meaningful finite questions are how
births occur, whether births eventually stop, and how large the monotone limit
becomes. This note does not claim an asymptotic law.

## 6. Reflection symmetry

Reflection of the circle gives an exact symmetry:

```text
r in C_k  =>  -r mod M_k in C_k.
```

The map `x -> -x` sends the selected closed arc for residue `r mod p` to the
selected closed arc for `-r mod p`. This explains the pair
`C_4={2,208}` and the reflection pairing in `B_5`.

## 7. Theorem: `C_4={2,208} mod 210`

**Theorem.** For the prime prefix `{2,3,5,7}` with closed arcs on `R/Z`,

```text
C_4 = {2,-2} = {2,208} mod 210.
```

**Positive residues.** For `r=2`, the selected arcs are

```text
p=2: [0,1/4] union [3/4,1]
p=3: [1/2,5/6]
p=5: [3/10,1/2]
p=7: [3/14,5/14]
```

They cover the circle by the chain

```text
[0,1/4] overlaps [3/14,5/14],
[3/14,5/14] overlaps [3/10,1/2],
[3/10,1/2] touches [1/2,5/6],
[1/2,5/6] overlaps [3/4,1].
```

Thus `2 in C_4`. The residue `208=-2 mod 210` follows by reflection symmetry.

**Exclusions.** For every other residue modulo `210`, the row-level witness
CSV gives a rational `witness_point` strictly inside an open gap and outside
all four closed arcs. This proves the residue is not in `C_4`.

The theorem is audited by:

```text
data/summaries/prc_prime_prefix_c4_exclusion_witness_v1_6.csv
data/summaries/prc_prime_prefix_c4_exclusion_summary_v1_5.csv
```

The v1.6 witness file has `208` exclusion rows. The v1.5 summary compresses
those rows into `36` component/measure classes with complete residue lists. The
summary is a human-readable index; the row-level rational witnesses are the
certificate.

## 8. Proposition: the `B_5` birth layer

**Proposition.** At `k=5`, with new prime `11` and `M_5=2310`,

```text
|C_5| = 36,
|Lift_5(C_4)| = 22,
|B_5| = 14,
B_5 = {
  118, 448, 542, 778, 849, 872, 1108,
  1202, 1438, 1461, 1532, 1768, 1862, 2192
} mod 2310.
```

The birth residues form the following reflection pairs:

| birth pair | previous residue mod 210 | old gap | new `p=11` arc |
|---:|---:|---|---|
| 118 / 2192 | 118 / 92 | `7/10-3/4` and `1/4-3/10` | `15/22-17/22` / `5/22-7/22` |
| 448 / 1862 | 28 / 182 | `7/10-3/4` and `1/4-3/10` | `15/22-17/22` / `5/22-7/22` |
| 542 / 1768 | 122 / 88 | `1/4-3/10` and `7/10-3/4` | `5/22-7/22` / `15/22-17/22` |
| 778 / 1532 | 148 / 62 | `7/10-3/4` and `1/4-3/10` | `15/22-17/22` / `5/22-7/22` |
| 849 / 1461 | 9 / 201 | `1/6-3/14` and `11/14-5/6` | `3/22-5/22` / `17/22-19/22` |
| 872 / 1438 | 32 / 178 | `1/4-3/10` and `7/10-3/4` | `5/22-7/22` / `15/22-17/22` |
| 1108 / 1202 | 58 / 152 | `7/10-3/4` and `1/4-3/10` | `15/22-17/22` / `5/22-7/22` |

Each `B_5` birth is a strict single-gap closure: the first four prime arcs
leave exactly one old open gap, and the new closed `p=11` arc strictly contains
that gap. Six reflection pairs close a gap of length `1/20`; the pair
`849/1461` closes a gap of length `1/21`. No `B_5` closure uses endpoint
touching.

The proposition is audited by:

```text
data/summaries/prc_prime_prefix_ck_full_v1_1.csv
data/summaries/prc_prime_prefix_birth_witness_v1_5.csv
data/summaries/prc_prime_prefix_b5_birth_classification_v1_5.csv
data/summaries/prc_prime_prefix_b5_birth_pair_summary_v1_5.csv
```

## 9. Certificate architecture

The package has two verification paths.

The package verifier reads the public finite theorem CSVs and checks row
counts, residue-set completeness, closed-arc coverage, open-gap witnesses,
rational witness points, exact interval/fraction fields, the `C_4` summary
partition, the `B_5` classification table, the reflection-pair quotient, and
strict old-gap/new-arc containment:

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-verify-certificates \
  --out data/summaries/prc_prime_prefix_certificate_verification_v1_7.csv
```

Expected result:

```text
checks=14, failed=0
```

The standalone checker uses only the Python standard library and does not
import `prime_reciprocal_projection`:

```bash
cd research
python certificates/check_prime_prefix_c4_b5.py \
  --out data/summaries/prc_prime_prefix_certificate_standalone_verification_v1_8.csv
```

Expected result:

```text
checks=9, failed=0
```

For the full verifier contract, see `VERIFY_FINITE_C4_B5.md`.

## 10. Non-claims

- This note is scoped to finite `C_4/B_5` prime-prefix residue-covering
  certificates. Broader asymptotic, distributional, complete-PRC, and
  selected-window diagnostic questions are outside this release.
- This note does not use floating-point coverage checks for theorem-level
  claims.
- This note does not include the full historical PRC archive. Certificate
  depth, `k=8`, residual fragmentation, and C0 anti-clustering are context
  tracks in the full repository, not claims of this finite certificate note.
