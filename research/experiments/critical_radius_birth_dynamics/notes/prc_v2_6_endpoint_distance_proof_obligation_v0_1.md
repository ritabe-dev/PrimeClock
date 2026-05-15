# PRC v2.6 Endpoint-Distance Proof Obligation v0.1

## Definitions

Purpose: decide whether the v2.6 special-point lemmas can move from finite audit evidence toward theorem-note drafting by replacing the open nearest-old-endpoint obligation with a general endpoint lattice argument.

Current status: v2.5 public theorem release protection remains 100%; this v2.6 source-only Gate R slice is about 90-95% ready after this note and checker, with about 0.5 slice remaining before theorem-note promote/defer review.

Let the old prime prefix contain `2,3,...,p_k`, and let `q=p_{k+1}` be the next odd prime. A prime cloud for an odd prime `p` has endpoints

```text
(2a-1)/(2p), (2a+1)/(2p)
```

for residue `a mod p`, interpreted on the circle. Equivalently, the old odd-prime endpoint lattice for `p` is the set of odd residues over `2p`.

The circular points `0` and `1` are the same point. The notation `0/1` is only a cut representation, not two geometric points.

## Endpoint Lattice Near 0

For an old odd prime `p`, the closest endpoint to `0` occurs at distance `1/(2p)` from either side of the circular cut. Since the largest old odd prime is `p_k`, the closest old odd-prime endpoint to `0` across the old prefix is at distance

```text
1/(2p_k).
```

This is the candidate lower bound needed for the `a=0` special remainder: no old odd-prime endpoint can lie closer to `0` than `1/(2p_k)`.

## Endpoint Lattice Near 1/2

For an old odd prime `p`, an endpoint equals `1/2` when its odd numerator equals `p`. The nearest distinct old odd-prime endpoints are therefore at numerator distance `2` from `p`, giving circular distance

```text
2/(2p) = 1/p.
```

Since the largest old odd prime is `p_k`, the closest old odd-prime endpoint to `1/2`, other than `1/2` itself, is at distance

```text
1/p_k.
```

This is the candidate lower bound needed for central endpoint obstruction.

## p=2 Boundary

The prime `2` is not part of the odd-prime endpoint lattice above. It contributes the half-circle boundary convention that makes `1/2` a special point of the old prefix geometry.

This note keeps the `p=2` boundary separate from odd-prime endpoint coincidences. The `1/2` point is allowed as the central special point, but distances to the next old odd-prime endpoint are controlled by the odd-prime lattice.

## Implication For Special q-arcs

For `q>p_k`, the special `q` arcs are shorter than the adjacent old endpoint gaps:

```text
1/(2q) < 1/(2p_k)
1/q < 1/p_k
```

The first inequality is the near-`0` bound for the `a=0` arc. The second inequality is the central bound for the two central remainders `(q-1)/2` and `(q+1)/2`, whose `q` arcs touch `1/2` from one side.

The proof candidate is:

1. If the special point is already covered by an old cloud, the special `q` arc does not create a new birth gap at that point.
2. If the special point is not covered by an old cloud, the nearest old endpoint gap adjacent to that special point is longer than the corresponding special `q` arc.
3. Therefore the special `q` arc is too short to contain the adjacent old residual gap.

This supports the `Forbidden Special Remainder Lemma` and the `Central Endpoint Obstruction Lemma` as proof candidates, not public theorems.

## Remaining Risks

The endpoint-distance lattice bounds look general, but the bridge from endpoint spacing to residual-gap containment still has to be written without silently assuming a finite audit table.

Open proof obligations:

- show that the old residual gap adjacent to `0` or `1/2` must extend to the next old endpoint when the special point is not old-covered;
- keep circular cut handling at `0/1` explicit;
- keep `p=2` boundary behavior separate from odd-prime endpoint coincidence;
- show that endpoint-touch centralization does not depend on checked finite scopes only.

## Gate R Decision

`proof_status=candidate`

`public_theorem=defer`

`b8_theorem=reject_for_v2_6_gate_r`

Decision: continue endpoint-distance proof formalization. The endpoint lattice lower bounds are strong enough for theorem-note drafting review, but not yet enough for a public theorem, DOI, GitHub Release, B8 theorem, B8 full graph claim, general predictor, or asymptotic law.
