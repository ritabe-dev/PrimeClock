# Critical Radius Spectra and Birth Dynamics in Prime-Prefix Coverings

Status: internal-candidate.
Release eligibility: included in v2.3 candidate bundle, excluded from public release until promoted.

## 1. Introduction

The v2.2.4 public release gives a finite certificate package for the first
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

with an exact threshold spectrum `lambda_k(r)` and a birth mechanism stated as
gap-aperture windows against the next prime grid. The claims here are finite
and computationally certified; they are not asymptotic claims.

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
interpretation of the finite critical-radius threshold. In this draft,
`critical radius` is the project term; `weighted covering-radius` is only
descriptive shorthand for the max-min expression above. The implementation
computes the value exactly by evaluating weighted bisector candidates for
lifted center pairs and selecting a bottleneck point. The finite candidate-set
justification is recorded as an internal certificate lemma:

```text
notes/prc_weighted_bisector_candidate_lemma_v0_1.md
```

Important boundary: this draft does not use the naive adjacent-center formula
as a theorem. Adjacent data may be useful for certificates, but the theorem
candidate is the weighted covering-radius statement above.

Terminology boundary: this draft does not claim novelty for the phrase
`weighted covering-radius`, and it does not import any external covering-radius
theorem without citation. A separate internal terminology note records this
scope:

```text
notes/prc_weighted_covering_radius_terminology_v0_1.md
notes/prc_v2_3_related_work_v0_2.md
```

Relation to existing optimization language: the weighted max-min expression is
related to weighted one-center and minimax location problems, but v2.3 does not
claim novelty for that general optimization viewpoint. The contribution claimed
here is the exact rational certificate for the prime-prefix residue-covering
instances and the finite `B_5/B_6/B_7` birth classification.

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

## 5. Gap-Aperture Birth Formula

Let `q=p_{k+1}` and let `r mod M_{k+1}` be a lift of a parent residue
`s = r mod M_k`. Let

```text
R_k(s) = (R/Z) \ U_k(s)
```

be the old residual set before the new prime is added.

The birth containment identity is:

```text
r in B_{k+1}
iff
s notin C_k and R_k(s) subset I_q^(1/2)(r).
```

The right-hand side says that the parent was not covered at level `k`, but the
single new `q`-arc covers every old gap.

The gap-aperture form rewrites this containment as a finite count of admissible
next-prime remainders. If an old open gap is represented after cutting the
circle as

```text
G = (a,b) subset [0,1],
```

then a new `q`-arc with center `m/q` strictly contains this gap when its center
lies in the dual containment window

```text
b - 1/(2q) < m/q < a + 1/(2q)
```

after the same circle cut is used. Endpoint containment replaces the strict
inequalities by non-strict ones. For wrap-around gaps, the implementation first
splits the gap and arc into intervals in `[0,1]`; for multi-gap residual sets,
the same `m/q` must lie in the intersection of all dual windows. Thus the
number of birth lifts above a parent is exactly the number of `q`-grid centers
whose closed `q`-arc contains all old residual gaps. In short:

```text
old residual gap -> dual containment window -> q-grid remainder count -> birth
```

The experiment classifies births by two axes:

```text
strict vs endpoint containment
single-gap vs multi-gap residual set
```

The current finite evidence is:

```text
B_5: 14 unique strict single-gap births
B_6: 42 unique strict single-gap births
B_7: 714 unique strict single-gap births
```

Here `unique` means that each birth parent has exactly one old open gap, that
gap is strictly contained in the new `q`-arc, and exactly one admissible
`q`-remainder exists. The checked remainder is the row's
`new_prime_remainder` in the birth-dynamics CSV.

The same finite birth rows imply the covered-set growth recurrence

```text
|C_{k+1}| = p_{k+1}|C_k| + |B_{k+1}|.
```

Consequently,

```text
|C_6| = 13*36 + 42 = 510
|C_7| = 17*510 + 714 = 9384
```

These are finite checked results, not evidence for a general law that all
future births are unique or single-gap.

## 6. Near-Miss Discussion

The critical-radius spectrum gives a natural way to rank uncovered residues by
how close they are to the `1/2` threshold. However, near-miss rank alone is not
the birth mechanism.

The useful finite diagnostic is:

```text
near-miss candidate + q-grid phase in the dual containment window
```

Observed finite overlap:

```text
k=4 top-20 near-misses: 13 are B_5 birth parents
k=5 top-20 near-misses: 19 are B_6 birth parents
```

The misses are phase misses. A residue can be close to the threshold because
its old gap is small, but fail to have any next-prime `q`-grid center inside
the dual containment window. Thus near-miss rank controls a useful gap-size
candidate list; birth is decided by q-grid phase.

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

Internal checkers:

```text
check_candidate.py: checks=13, failed=0
check_candidate_standalone.py: checks=10, failed=0
```

The helper-based checker regenerates candidate rows from experiment code. The
standalone checker uses only the Python standard library, reads the committed
CSV artifacts, recomputes the k=4,5 critical-radius values from the definition,
and checks the candidate CSV SHA256 manifest plus the headline finite claims.

Internal candidate bundle:

```text
candidate_bundle.py -> PrimeClock-v2.3-candidate-v0.1
```

## 8. Future Work

The next direction is a v2.4 residual-gap transition graph, where each old gap
is classified as missed, trimmed, split, or closed by the next prime arc. That
future-work direction is not part of this v2.3 candidate. The no-multi-gap
birth idea is also kept as an internal lemma candidate rather than a theorem in
this draft. Active-prime taxonomy and any null model for q-grid phase are also
future work; v2.3 only records the finite spectrum, the gap-aperture birth
formula, and the checked unique strict single-gap layers.

## 9. Promotion Boundary

The internal promotion manifest fixes this draft's candidate scope:

```text
critical radius: k=4,5
birth dynamics: k=5,6,7
near-miss discussion: k=4,5
no B_8 or larger layers
```

Before promotion to a public v2.3 release bundle, this draft still needs:

1. conversion of `candidate_bundle_manifest_v0_1.json` into a `release/public`
   config with GitHub/Zenodo metadata.
2. the related-work decision kept fixed: use `critical radius` as the project
   term, and add formal covering-radius citations only if the public note leans
   on that external terminology.

## 10. Non-Claims

This draft does not claim:

- a general theorem that all births are single-gap births;
- that near-miss rank alone predicts births;
- an asymptotic law for `lambda_k`;
- a new theorem about prime distribution;
- an explanation of all complete PRC events;
- any change to the v2.2.4 public release.
