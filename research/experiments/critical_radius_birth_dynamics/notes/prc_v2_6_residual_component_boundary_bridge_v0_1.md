# PRC v2.6 Residual Component Boundary Bridge v0.1

## Goal

Purpose: tighten the bridge from special endpoint spacing to residual-gap non-containment for the v2.6 special point obstruction route.

This is a source-only Gate R proof-candidate note. It supports theorem-note drafting, but it is not a public theorem, not a DOI artifact, not a GitHub Release artifact, not a B8 theorem, not a B8 full graph claim, not a general predictor, and not an asymptotic law.

## Setup

Let the old covered set be a finite union of closed circular arcs on `R/Z`, and let the old residual set be its open complement. The boundary of each residual component is contained in the old endpoint set.

The circular points `0` and `1` are the same point. When a special-side argument crosses the cut at `0/1`, choose a local circular representative or split the argument at the cut.

## Covered Special Side

If the relevant special side is old-covered, then an old residual component cannot contain the special point on that side. A new special q-arc centered at or adjacent to that special point would have to cover a residual component whose boundary is away from the covered neighborhood, not a component based at the special point itself.

For the forbidden-special-remainder route, this means the covered-side case cannot create birth merely by placing a new q-arc on the already-covered special point. There is no old residual component wholly based at the covered special side to close.

## Uncovered Special Side

If the relevant special side is old-uncovered, then the residual component adjacent to that side extends until the nearest old endpoint on that side. Inside a connected interval with no old endpoint, the covered/uncovered state cannot change.

Combined with the special endpoint spacing lower bounds, the adjacent residual component reaches at least:

```text
1/(2p_k) from 0
1/p_k from 1/2
```

The corresponding special q-arcs reach only:

```text
1/(2q) from 0
1/q from 1/2
```

Since `q>p_k`, the special q-arc is too short to contain the adjacent old residual component.

## Gate R Decision

`residual_component_boundary_bridge=proof_candidate`

`covered_special_side=proof_candidate`

`uncovered_special_side=proof_candidate`

`public_theorem=defer`

Decision: continue the special point obstruction route as source-only Gate R proof work. The bridge is strong enough to guide theorem-note drafting, but public theorem promotion remains deferred.

## Non-claims

This bridge note makes no public theorem claim, no DOI claim, no GitHub Release claim, no B8 theorem claim, no B8 full graph claim, no general predictor claim, and no asymptotic law claim.
