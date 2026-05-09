# Critical Radius Spectra and Birth Dynamics in Prime-Prefix Coverings

Status: internal public-candidate theorem-note draft, not a public release.

## 1. Introduction

The v2.2.3 public release gives a finite certificate package for the first
nontrivial prime-prefix covering layers:

```text
C_4 = {2,208} mod 210,
|C_5| = 36,
|B_5| = 14.
```

This draft keeps that public release fixed and develops the next internal
research layer. The goal is to replace a purely binary view of residues,

```text
r in C_k or r notin C_k,
```

with an exact threshold spectrum `lambda_k(r)` and a birth mechanism stated in
terms of old residual gaps. The claims here are finite and computationally
certified; they are not asymptotic claims.

## 2. Prime-Prefix Covering

Let `p_1,...,p_k` be the first `k` primes and

```text
M_k = product_{i<=k} p_i.
```

For a residue `r mod M_k`, set

```text
c_p(r) = (r mod p)/p in R/Z.
```

The original PRC prefix arc at prime `p` is the closed arc of radius `1/(2p)`
around `c_p(r)`. The covered-residue set is

```text
C_k = { r mod M_k : union_{i<=k} I_{p_i}(r) = R/Z }.
```

The sets are understood over the primorial inverse system: `C_k` and `C_{k+1}`
live in different residue rings, and monotonicity is through lifted residue
classes.

## 3. Critical Radius

For `lambda >= 0`, define the scaled closed arc

```text
I_p^(lambda)(r) =
  [c_p(r) - lambda/p, c_p(r) + lambda/p] in R/Z.
```

Define the critical radius

```text
lambda_k(r) = inf { lambda >= 0 :
  union_{i<=k} I_{p_i}^(lambda)(r) = R/Z }.
```

Equivalently,

```text
lambda_k(r) = max_x min_{i<=k} p_i * d_T(x, c_{p_i}(r)),
```

where `d_T` is circular distance on `R/Z`. This is a weighted covering-radius
formula. The implementation computes it exactly by evaluating weighted bisector
candidates for lifted center pairs and selecting a bottleneck point.

Important boundary: this draft does not use the naive adjacent-center formula
as a theorem. Adjacent data may be useful for certificates, but the theorem
candidate is the weighted covering-radius statement above.

## 4. Level-Set Proposition

Because the original PRC arcs have radius `1/(2p)`, the original covered set is
the `1/2` level set:

```text
C_k = { r : lambda_k(r) <= 1/2 }.
```

The current exact finite checks give:

```text
C_4 = { r : lambda_4(r) <= 1/2 } = {2,208} mod 210
|{ r : lambda_5(r) <= 1/2 }| = |C_5| = 36.
```

The spectrum separates covered residues into robust and endpoint cases:

```text
robust:   lambda_k(r) < 1/2
endpoint: lambda_k(r) = 1/2
uncovered: lambda_k(r) > 1/2
```

The generated finite summary is:

```text
k=4: robust=0, endpoint=2, uncovered=208, nearest uncovered lambda=5/9
k=5: robust=2, endpoint=34, uncovered=2274, nearest uncovered lambda=7/13
```

Thus the first nonempty layer `C_4` is entirely endpoint-critical, while `C_5`
already contains two robust covered residues.

## 5. Birth Containment

Let `q=p_{k+1}` and let `r mod M_{k+1}` be a lift of a parent residue
`s = r mod M_k`. Let

```text
R_k(s) = (R/Z) \ U_k(s)
```

be the old residual set before the new prime is added.

The birth condition is exactly old-gap containment:

```text
r in B_{k+1}
iff
s notin C_k and R_k(s) subset I_q^(1/2)(r).
```

The right-hand side says that the parent was not covered at level `k`, but the
single new `q`-arc covers every old gap. This turns birth enumeration into a
finite residual-gap classification problem.

The experiment classifies births by two axes:

```text
strict vs endpoint containment
single-gap vs multi-gap residual set
```

The current finite evidence is:

```text
B_5: 14 strict single-gap births
B_6: 42 strict single-gap births
B_7: 714 strict single-gap births
```

This is evidence for a simple early birth mechanism, not a theorem that all
future births are single-gap births.

## 6. Near-Miss Discussion

The critical-radius spectrum gives a natural way to rank uncovered residues by
how close they are to the `1/2` threshold. However, near-miss rank alone is not
the birth mechanism.

The useful finite diagnostic is:

```text
near-miss candidate + containing next-prime remainder
```

Observed finite overlap:

```text
k=4 top-20 near-misses: 13 are B_5 birth parents
k=5 top-20 near-misses: 19 are B_6 birth parents
```

The misses are explained by old-gap geometry: a residue can be close to the
threshold but fail to have any next-prime remainder whose arc contains its old
residual set.

## 7. Certificate Artifacts

The current draft is supported by the internal experiment artifacts:

```text
data/prc_prime_prefix_critical_radius_k4_k5_v0_1.csv
data/prc_prime_prefix_critical_radius_summary_v0_1.csv
data/prc_prime_prefix_critical_radius_near_misses_k4_k5_v0_1.csv
data/prc_prime_prefix_near_miss_birth_parent_overlap_k4_k6_v0_1.csv
data/prc_prime_prefix_near_miss_gap_geometry_k4_k5_v0_1.csv
data/prc_prime_prefix_birth_threshold_crossing_k5_k7_v0_1.csv
data/prc_prime_prefix_birth_dynamics_k5_k7_v0_1.csv
data/prc_prime_prefix_birth_dynamics_summary_v0_1.csv
data/prc_v2_3_candidate_verification_v0_1.csv
```

The implementation and tests remain under `research/experiments`; this is not
yet a public release bundle.

Internal checker:

```text
check_candidate.py: checks=11, failed=0
```

Internal candidate bundle:

```text
candidate_bundle.py -> PrimeClock-v2.3-candidate-v0.1
```

## 8. Promotion Boundary

The internal promotion manifest fixes this draft's candidate scope:

```text
critical radius: k=4,5
birth dynamics: k=5,6,7
near-miss discussion: k=4,5
no B_8 or larger layers
```

Before promotion to a public v2.3 release bundle, this draft still needs:

1. review of the weighted covering-radius statement against nearby covering
   radius terminology.

## 9. Non-Claims

This draft does not claim:

- a general theorem that all births are single-gap births;
- that near-miss rank alone predicts births;
- an asymptotic law for `lambda_k`;
- a new theorem about prime distribution;
- an explanation of all complete PRC events;
- any change to the v2.2.3 public release.
