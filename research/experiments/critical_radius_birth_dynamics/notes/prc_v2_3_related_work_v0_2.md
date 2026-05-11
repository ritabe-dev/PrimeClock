# PRC v2.3 Related Work v0.2

Status: public v2.3.0 related-work boundary note.

## Purpose

This note fixes the terminology boundary for the v2.3.0 critical-radius and
birth-dynamics release. It does not claim that the weighted max-min form is a
new optimization problem. It records how the release should be described
relative to nearby existing problems.

## Critical Radius and Weighted 1-Center Problems

The v2.3.0 project term is `critical radius`:

```text
lambda_k(r) = inf { lambda >= 0 :
  union_{i<=k} I_{p_i}^{(lambda)}(r) = R/Z }.
```

The equivalent expression

```text
lambda_k(r) = max_x min_{i<=k} p_i d_T(x, c_{p_i}(r))
```

is used as a finite max-min interpretation. It is close in shape to weighted
one-center and minimax location problems, where one optimizes a maximum weighted
distance to a finite set of sites. The v2.3.0 release does not claim novelty for
that optimization viewpoint. Its specific object is the exact rational spectrum
induced by prime-prefix residue centers on `R/Z`.

Useful references for terminology context:

- Donald W. Hearn and James Vijay, "Efficient Algorithms for the (Weighted)
  Minimum Circle Problem," Operations Research 30(4):777-795, 1982.
  DOI: 10.1287/opre.30.4.777.
- Nimrod Megiddo, "The Weighted Euclidean 1-Center Problem," Mathematics of
  Operations Research 8(4):498-504, 1983. DOI: 10.1287/moor.8.4.498.

## Covering Systems and Circle-Arc Covering

The v2.3.0 release uses residue classes, moduli, and a covering condition, so it
is adjacent in vocabulary to covering systems of congruences. It is not a claim
about classical covering systems of the integers. Here, each finite residue
class determines a finite family of closed arcs on the circle, and the theorem
claim is checked by exact rational enumeration.

The interval-union part is also elementary but important: each finite check is
about union and residual gaps of closed circular arcs with rational endpoints.
The public package treats this as an exact finite certificate computation,
not as a new circle-covering algorithm.

## Birth Dynamics Boundary

The birth containment identity is internal to the PRC finite setup:

```text
r in B_{k+1}
iff
parent s notin C_k and R_k(s) subset I_q^{(1/2)}(r).
```

This identity is a structural restatement of adding the next prime arc. The
finite result in v2.3 is narrower:

```text
B_5, B_6, and B_7 are unique strict single-gap births in the checked finite data.
```

The release does not claim that all future births are single-gap births.

## Public Wording

Use this wording in v2.3.0 public material:

```text
The critical-radius spectrum is a project-defined finite invariant. Its
weighted max-min expression is related to weighted one-center/minimax location
problems, but no novelty is claimed for that general optimization viewpoint.
The contribution here is the exact rational certificate for the prime-prefix
residue-covering instances and the finite B_5/B_6/B_7 birth classification.
```
