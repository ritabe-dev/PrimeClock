# PRC v2.6 Special Point Theorem-Note Candidate v0.1

## Definitions

Purpose: promote the v2.6 special point obstruction line to a source-only theorem-note candidate while keeping the v2.5 public theorem release fixed. Current readiness is about 95-98%, with about 0.3-0.5 slice remaining before a Gate R checkpoint decision.

Let the old prime prefix contain `2,3,...,p_k`, and let `q=p_{k+1}` be the next odd prime. For an odd prime `p`, an arc endpoint has the form `odd/(2p)`, equivalently `(2a-1)/(2p)` or `(2a+1)/(2p)` on the circle.

The circular points `0` and `1` are the same point. The `p=2` half-circle boundary is kept separate from the odd-prime endpoint lattice.

## Special Endpoint Spacing Lemma

Lemma candidate: for the old prefix up to `p_k`, no old endpoint lies within distance `< 1/(2p_k)` of `0`, and no old endpoint other than `1/2` lies within distance `< 1/p_k` of `1/2`.

Reason: old endpoints are the union of the individual odd-prime endpoint sets `odd/(2p)`. Composite placement does not generate new endpoints, because endpoints are inherited from arc boundaries rather than created by adding, intersecting, or combining endpoint locations.

Near `0`, the closest old endpoint for a fixed odd prime `p` is `1/(2p)` or `1 - 1/(2p)`. Across `p<=p_k`, the closest possible distance is therefore `1/(2p_k)`.

Near `1/2`, the endpoint `1/2=p/(2p)` is allowed for an odd prime `p`. The nearest distinct odd numerator is `p-2` or `p+2`, so the closest noncentral endpoint distance for that `p` is `2/(2p)=1/p`. Across `p<=p_k`, the closest possible distance is therefore `1/p_k`.

## Residual Component Boundary Lemma

Lemma candidate: if a special point side at `0` or `1/2` is not covered by the old clouds, then the old residual component adjacent to that side extends until the nearest old endpoint on that side.

This is a topological boundary statement about a union of closed circular arcs. Inside a connected interval containing no old endpoint and no old cloud interior boundary, the old-covered/uncovered state is constant. Therefore an uncovered special side remains in the same residual component until the next old endpoint.

The covered-special-side case is handled separately in `prc_v2_6_residual_component_boundary_bridge_v0_1.md`: if the relevant special side is old-covered, there is no old residual component based at that covered special point to close.

This closes the residual-gap containment bridge at theorem-note candidate level: the old residual component adjacent to the uncovered special side has length at least the special endpoint spacing lower bound.

## Forbidden Special Remainder Lemma

Lemma candidate: for `q=p_{k+1}`, the remainders `a=0`, `a=(q-1)/2`, and `a=(q+1)/2` cannot produce birth.

If the relevant special side is already old-covered, there is no old residual component wholly inside the special `q` arc. If it is old-uncovered, the residual component extends to the next old endpoint. The special `q` arc is too short:

```text
1/(2q) < 1/(2p_k)
1/q < 1/p_k
```

Thus the special `q` arc cannot contain the whole adjacent old residual component.

## Central Endpoint Obstruction Lemma

Lemma candidate: endpoint-touch birth cannot occur for the new odd prime `q`.

If an old odd-prime endpoint and a new odd-prime endpoint coincide, the coprime endpoint equation forces the common point to be `1/2`. The only new `q` arcs with endpoint `1/2` are the central arcs for `a=(q-1)/2` and `a=(q+1)/2`.

By the residual component boundary lemma and the special endpoint spacing lemma, the adjacent old residual component reaches at least distance `1/p_k` from `1/2`, while the central `q` arc reaches only distance `1/q`. Since `q>p_k`, endpoint-touch birth is structurally obstructed.

## Remaining Risks

This is a source-only theorem-note candidate, not a public theorem. The remaining Gate R risk is to review the standalone residual component boundary bridge and decide whether its covered-side and uncovered-side cases are tight enough for theorem-note promotion.

The `3 mod 6 ancestry` route remains diagnostic only. It may help explain productive interior single-gap ancestry, but it is not used as a theorem claim.

## Non-claims

`source_theorem_note=promote_candidate`

`public_theorem=defer`

`b8_theorem=reject_for_v2_6_gate_r`

`mod6_theorem=defer`

`pr_policy=local_first_until_checkpoint`

This v2.6 Gate R note makes no public release claim, no DOI claim, no GitHub Release claim, no B8 theorem, no B8 full graph claim, no general predictor claim, and no asymptotic law claim.
