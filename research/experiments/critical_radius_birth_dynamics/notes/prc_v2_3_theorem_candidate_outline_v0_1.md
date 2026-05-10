# PRC v2.3 Theorem Candidate Outline

Status: internal theorem-candidate outline, not a public release.

## Purpose

This note organizes the current `critical_radius_birth_dynamics` experiment into
the smallest theorem-candidate shape that could later become a v2.3 public
candidate. It does not add new data. It selects the finite claims that are
already supported by the existing exact CSVs and tests.

The v2.2.4 public release remains the stable public artifact for the
`C_4/B_5` finite certificate package. The material below is internal research
until it is promoted through a separate release process.

## Candidate Structure

The v2.3 candidate should have three mathematical components:

```text
1. critical radius formula
2. C_k = { r : lambda_k(r) <= 1/2 }
3. birth containment identity
```

The near-miss predictor is useful experimental evidence, but it should remain
in the discussion section rather than become a headline theorem.

## Critical Radius Formula

For each prime `p` in the prefix and residue `r`, write

```text
c_p(r) = (r mod p)/p in R/Z.
```

For `lambda >= 0`, define the scaled closed arc

```text
I_p^(lambda)(r) =
  [c_p(r) - lambda/p, c_p(r) + lambda/p] in R/Z.
```

The critical radius is

```text
lambda_k(r) = inf { lambda >= 0 :
  union_{i<=k} I_{p_i}^(lambda)(r) = R/Z }.
```

Equivalently, it is the exact weighted covering radius

```text
lambda_k(r) = max_x min_{i<=k} p_i * d_T(x, c_{p_i}(r)),
```

where `d_T` is circular distance on `R/Z`.

The implementation computes this exactly by evaluating weighted bisector
candidates of lifted center pairs and choosing a bottleneck point. The candidate
note should not claim the naive adjacent-center formula as a theorem. Adjacent
center data may be reported only as part of a checked bottleneck certificate.

## Level-Set Proposition

The original covered-residue set is the `1/2` level set:

```text
C_k = { r : lambda_k(r) <= 1/2 }.
```

This follows directly from the definitions because the original PRC arcs have
radius `1/(2p)`.

The current finite checks are:

```text
C_4 = { r : lambda_4(r) <= 1/2 } = {2,208} mod 210
|{ r : lambda_5(r) <= 1/2 }| = |C_5| = 36.
```

The exact spectrum summary is:

```text
k=4: robust=0, endpoint=2, uncovered=208, nearest uncovered lambda=5/9
k=5: robust=2, endpoint=34, uncovered=2274, nearest uncovered lambda=7/13
```

Here `robust` means `lambda_k(r) < 1/2`, `endpoint` means
`lambda_k(r) = 1/2`, and `uncovered` means `lambda_k(r) > 1/2`.

## Birth Containment Identity

Let `q=p_{k+1}`. Let `r mod M_{k+1}` be a lift of parent residue
`s = r mod M_k`, and write

```text
R_k(s) = (R/Z) \ U_k(s)
```

for the old residual set before adding the new prime `q`.

Then a lift is a birth exactly when the parent is not already covered and the
old residual set is contained in the new `q`-arc:

```text
r in B_{k+1}
iff
s notin C_k and R_k(s) subset I_q(r).
```

This is the structural form of the birth definition. It reframes the birth
layer as old-gap containment rather than only full enumeration.

The current finite evidence is:

```text
B_5: 14 strict single-gap births
B_6: 42 strict single-gap births
B_7: 714 strict single-gap births
```

In these checked layers, every birth closes exactly one old open gap by strict
containment in the new prime arc. This is finite evidence only.

## Discussion Candidate

The near-miss predictor should be stated conservatively:

```text
near-miss candidate + containing next-prime remainder
```

Observed finite overlap:

```text
k=4 top-20 near-misses: 13 are B_5 birth parents
k=5 top-20 near-misses: 19 are B_6 birth parents
```

This suggests that `lambda_k(r)` is useful for finding likely birth parents, but
`lambda` rank alone is not sufficient. The old-gap geometry and available
next-prime remainders decide whether a near-miss actually births.

## Public-Candidate Boundary

Before this becomes a public v2.3 candidate, it needs:

1. a polished theorem/proposition note using the three components above;
2. a decision on whether v2.3 includes only `k<=7` birth dynamics;
3. a release manifest that keeps v2.2.4 unchanged.

The internal helper checker and standard-library standalone checker now cover
the promoted finite claims at the candidate-artifact level.

## Non-Claims

This outline does not claim:

- a general theorem that all births are single-gap births;
- that near-miss rank alone predicts births;
- an asymptotic law for `lambda_k`;
- a new theorem about prime distribution;
- any change to the v2.2.4 public release.
