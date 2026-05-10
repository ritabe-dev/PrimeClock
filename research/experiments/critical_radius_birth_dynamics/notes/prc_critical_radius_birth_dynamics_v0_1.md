# Critical Radius Spectra and Birth Dynamics v0.1

Status: internal experiment after the v2.2.4 finite `C_4/B_5` certificate
release.

## Purpose

The v2.2.4 public artifact proves and verifies a narrow finite certificate:

```text
C_4 = {2,208} mod 210,
|C_5| = 36,
|B_5| = 14.
```

This experiment keeps that release fixed and asks the next structural question:

```text
How do residues cross the covering threshold, and what geometric mechanism
creates birth residues?
```

The two new observables are:

```text
lambda_k(r): exact critical radius threshold
B_k birth type: old residual gap containment by the new prime arc
```

## Critical Radius

For a residue `r mod M_k`, set

```text
c_p(r) = (r mod p) / p
I_p^(lambda)(r) = [c_p(r)-lambda/p, c_p(r)+lambda/p].
```

Then

```text
lambda_k(r) = inf { lambda >= 0 :
  union_{i<=k} I_{p_i}^{(lambda)}(r) = R/Z }.
```

The original finite covering set is the `1/2` level set:

```text
C_k = { r : lambda_k(r) <= 1/2 }.
```

The implementation computes `lambda_k(r)` exactly as the maximum of the
weighted lower envelope

```text
max_x min_i p_i d_T(x, c_{p_i}(r)).
```

It does not use the raw adjacent-center formula as a theorem-level shortcut.

## Generated Spectrum Summary

```text
k=4: robust=0, endpoint=2, uncovered=208, nearest uncovered lambda=5/9
k=5: robust=2, endpoint=34, uncovered=2274, nearest uncovered lambda=7/13
```

Interpretation:

- `C_4` is entirely endpoint-critical.
- `C_5` already contains two robust covered residues.
- The `B_5` robust birth pair is `849/1461`, with `lambda_5=4/9`.
- The other six `B_5` reflection pairs land exactly at `lambda_5=1/2`.
- Threshold-crossing rows now cover `B_5`, `B_6`, and `B_7`, so all early
  birth layers can be read as parent `lambda>1/2` to child `lambda<=1/2`
  transitions.
- The near-miss table lists the closest uncovered `k=4,5` residues above
  `lambda=1/2`; it is a candidate generator, not a claim about later levels.
- The near-miss parent-overlap table records whether those near-miss residues
  actually produce birth lifts at the next prime level.
- The near-miss gap-geometry table records the old open gaps and the next-prime
  remainders whose arcs contain them, separating ranking from mechanism.

## Birth Dynamics

Let `q=p_{k+1}` and let `s` be the parent residue modulo `M_k`. The old
residual set is

```text
R_k(s) = R/Z \ U_k(s).
```

A lift becomes a birth exactly when the new `q`-arc covers the old residual set:

```text
r in B_{k+1}
iff
s notin C_k and R_k(s) subset I_q(r mod q).
```

The v0.1 experiment classifies births as:

```text
strict_single_gap_birth
endpoint_single_gap_birth
strict_multi_gap_birth
endpoint_multi_gap_birth
```

Generated finite summary:

```text
B_5: 14 unique strict single-gap births
B_6: 42 unique strict single-gap births
B_7: 714 unique strict single-gap births
```

This is finite evidence for a simple early birth mechanism; it is not a general
unique single-gap theorem for all levels.

In short: this is not a general theorem for all levels.

## Artifacts

```text
data/prc_prime_prefix_critical_radius_k4_k5_v0_1.csv
data/prc_prime_prefix_critical_radius_summary_v0_1.csv
data/prc_prime_prefix_critical_radius_near_misses_k4_k5_v0_1.csv
data/prc_prime_prefix_near_miss_birth_parent_overlap_k4_k6_v0_1.csv
data/prc_prime_prefix_near_miss_gap_geometry_k4_k5_v0_1.csv
data/prc_prime_prefix_birth_threshold_crossing_k5_v0_1.csv
data/prc_prime_prefix_birth_threshold_crossing_k5_k7_v0_1.csv
data/prc_prime_prefix_birth_dynamics_k5_k7_v0_1.csv
data/prc_prime_prefix_birth_dynamics_summary_v0_1.csv
```

## Next Questions

The next useful steps are deliberately finite:

1. Use `prc_near_miss_birth_predictor_v0_2.md` as the current predictor note.
2. Test whether the same two-stage predictor remains useful beyond `k=5`.
3. Search for the first multi-gap birth without brute-forcing `k=9`.
4. Decide whether the v0.1 sandbox is mature enough to promote into a v2.3
   public candidate.

## Non-Claims

This experiment does not claim:

- an asymptotic law for `lambda_k`;
- a general theorem that all births are single-gap births;
- a new prime-distribution theorem;
- an explanation of all complete PRC events.
