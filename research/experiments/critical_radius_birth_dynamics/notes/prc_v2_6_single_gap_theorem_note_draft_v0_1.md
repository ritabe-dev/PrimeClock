# PRC v2.6 Single-Gap Theorem-Note Draft v0.1

## Goal

Purpose: state the clean source-only Gate R proof candidate behind the v2.6
special-point and single-gap route, while keeping the v2.5 public theorem
release fixed.

Current readiness is about 85-90%. The remaining work is about 0.5 slice:
review the residual component boundary bridge and decide whether this note is a
local Gate R checkpoint.

## Setup

Work on the circle `R/Z`. The old prefix contains `2,3,...,p_k`, and
`q=p_{k+1}` is the next odd prime. Old clouds are closed arcs. The old residual
set is their open complement.

For a q-remainder `a`, write the new q-cloud as

```text
I_q(a) = [(a - 1/2)/q, (a + 1/2)/q].
```

When an interval crosses the cut at `0/1`, choose a local circular
representative or split at the cut. Endpoint equality is not strict
containment.

## Lemma 1: Special Endpoint Spacing

For the old prefix up to `p_k`:

```text
dist(0, nearest old endpoint) >= 1/(2p_k)
dist(1/2, nearest old endpoint other than 1/2) >= 1/p_k.
```

Reason: odd-prime arc endpoints have the form `odd/(2p)`. Endpoints are the
union of old arc boundaries; composite placement does not create new endpoints.
Near `0`, the smallest odd numerator gives distance `1/(2p)`. Near `1/2`, the
nearest distinct odd numerators are `p-2` and `p+2`, giving distance `1/p`.
Taking the largest old prime gives the displayed lower bounds.

## Lemma 2: Residual Component Boundary

If a special side at `0` or `1/2` is old-uncovered, the adjacent residual
component extends until the nearest old endpoint on that side. Inside an open
arc with no old endpoint, the covered/uncovered state cannot change.

If the special side is old-covered, no residual component is based at that
covered side. A new q-cloud placed on the covered side has no old residual
component there to close.

## Lemma 3: Forbidden Special Remainders

For `q=p_{k+1}`, the remainders

```text
0, (q-1)/2, (q+1)/2
```

cannot produce birth.

For `a=0`, the q-cloud reaches distance `1/(2q)` from `0`. If `0` is
old-covered, there is no residual component based at `0`. If `0` is
old-uncovered, Lemmas 1 and 2 give an adjacent residual component reaching at
least `1/(2p_k)`. Since `q>p_k`,

```text
1/(2q) < 1/(2p_k),
```

so the q-cloud is too short to contain that residual component.

For `a=(q-1)/2` and `a=(q+1)/2`, the q-cloud touches `1/2` from one side and
reaches distance `1/q`. The same covered/uncovered dichotomy applies at the
central side, and

```text
1/q < 1/p_k.
```

Thus the central q-cloud is too short to contain the adjacent old residual
component.

## Lemma 4: Central Endpoint Obstruction

If an old odd-prime endpoint and a new q-endpoint coincide, then the common
point is `1/2`.

Indeed, an equality

```text
m/(2p) = n/(2q)
```

with `p` and `q` distinct odd primes implies `mq=np`. Since `gcd(p,q)=1`, `p`
divides `m` and `q` divides `n`; the only endpoint numerators in range force
`m=p`, `n=q`, hence the point is `1/2`.

The only new q-clouds with endpoint `1/2` are the two central clouds. Lemma 3
shows that those clouds cannot close the adjacent old residual component.
Therefore endpoint-touch birth is obstructed.

## Lemma 5: Single-Gap Grid Containment

For a fixed old residual component `G=(L,R)` and a fixed q-remainder `a`, strict
containment is exactly

```text
G subset I_q(a)
(a - 1/2)/q < L
R < (a + 1/2)/q
qR - 1/2 < a < qL + 1/2.
```

The interval for `a` has width `1 - q(R-L)`. Thus capacity is only the size
condition `q(R-L)<1`; actual birth also requires the actual integer remainder
`a` to lie strictly inside the open q-grid interval.

## Checked Support

The committed B4->B5, B5->B6, and B6->B7 audits support, but do not prove
beyond checked scopes:

```text
in checked scopes, Close(row) => parent residual set is single-gap
strict q-grid containment matches close rows
capacity false positives are q-grid misses
endpoint-touch rows are zero
```

Mod 6 ancestry and k=2 multi-gap dilution remain diagnostics only.

## Gate R Boundary

`source_theorem_note=promote_candidate`

`single_gap_grid_containment_lemma=promote_candidate`

`close_iff_grid_containment_general_theorem=defer`

`all_births_single_gap_general_theorem=defer`

`capacity_general_separator=reject`

`mod6_theorem=defer`

`public_theorem=defer`

Decision: continue Gate R source-only research under local-only review. The
next step is to review whether the Residual Component Boundary Lemma is tight
enough for a local theorem-note checkpoint.

## Non-claims

This note makes no public theorem claim, no DOI claim, no GitHub Release claim,
no B8 theorem claim, no B8 full graph claim, no general predictor claim, and no
asymptotic law claim.
