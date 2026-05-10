# Near-Miss Birth Predictor v0.2

Status: internal experiment after the v2.2.4 finite `C_4/B_5` certificate
release.

## Purpose

The v0.1 artifacts introduced two exact views of the same finite process:

```text
lambda_k(r): how close a residue is to the covering threshold
R_k(r): the old residual open gaps before the next prime is added
```

The v0.2 question is narrower:

```text
When an uncovered residue is close to lambda=1/2, does it actually become a
birth parent at the next prime?
```

The answer is not determined by `lambda_k(r)` alone. The near-miss rank is a
useful candidate generator for small old gaps, but the birth decision is made
by q-grid phase: whether the next-prime center lands in the old gap's dual
containment window.

## Exact Predictor

For a near-miss parent residue `s mod M_k`, let `q=p_{k+1}`. A lift can be born
at level `k+1` exactly when some `q`-arc contains the whole old residual set:

```text
R_k(s) subset I_q(a)
```

Equivalently, each old gap defines a dual containment window for the next-prime
center `a/q`. A birth occurs only when a `q`-grid point lies in the intersection
of the required windows. Thus the finite predictor has two stages:

```text
stage 1: rank uncovered parents by lambda_k(s)-1/2
stage 2: keep only parents with q-grid phase inside the dual window
```

The second stage is the mechanism. It separates residues that are merely close
to the threshold from residues whose old gaps are aligned with the next prime
grid.

## Generated Results

For the top 20 near-miss residues at each level:

```text
k=4 near-misses: 13/20 are B_5 birth parents
k=5 near-misses: 19/20 are B_6 birth parents
```

The misses are informative:

```text
k=4 misses:
  rank 1: residue 99, lambda=5/9
  rank 2: residue 111, lambda=5/9
  rank 15: residue 3, lambda=3/5
  rank 17: residue 15, lambda=3/5
  rank 18: residue 21, lambda=3/5
  rank 19: residue 27, lambda=3/5
  rank 20: residue 33, lambda=3/5

k=5 miss:
  rank 18: residue 603, lambda=5/9
```

The gap-geometry table explains these misses as phase misses. Among the top 20
near-misses:

```text
k=4:
  one-gap parents with a containing q-remainder: 13
  one-gap parents without a containing q-remainder: 3
  two-gap parents without a containing q-remainder: 4

k=5:
  one-gap parents with a containing q-remainder: 19
  two-gap parents without a containing q-remainder: 1
```

So near-miss rank is useful but not sufficient. The sharper finite test is:

```text
near-miss candidate + q-grid phase in the dual containment window
```

For example, the top two `k=4` near-misses, residues `99` and `111`, have
`lambda=5/9` but no containing `q=11` remainder. Their old gap is close to
being small enough, yet the `11`-grid has no center in the needed dual window.
They are therefore phase misses, not counterexamples to the birth mechanism.

## Artifacts

```text
data/prc_prime_prefix_critical_radius_near_misses_k4_k5_v0_1.csv
data/prc_prime_prefix_near_miss_birth_parent_overlap_k4_k6_v0_1.csv
data/prc_prime_prefix_near_miss_gap_geometry_k4_k5_v0_1.csv
```

## What This Adds

This turns the previous observations into a finite workflow:

1. Use `lambda_k(r)` to find residues close to becoming covered.
2. Use q-grid phase in the dual containment window to decide which ones can
   birth at the next prime.
3. Treat non-birth near-misses as diagnostic examples, not failures of the
   framework.

This is the right bridge from the `lambda` spectrum to birth dynamics.

## Non-Claims

This note does not claim:

- that all near-misses become births;
- that near-miss rank predicts birth without q-grid phase and gap geometry;
- that all later births are single-gap births;
- an asymptotic law for the near-miss distribution.
