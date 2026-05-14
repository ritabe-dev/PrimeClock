# PRC v2.6 Special Point Obstruction Gate R Note v0.1

## Definitions

Purpose: start v2.6 from the special-point obstruction mechanism while keeping
the v2.5 public theorem release fixed. The mathematical direction is about
90% clear as a lemma candidate, and the source-only Gate R artifact is about
1 slice from a stable starter state.

Let `q=p_{k+1}` be the next odd prime after the old prefix whose largest prime
is `p_k`. A prime `p` contributes the closed circular arc centered at `a/p`
with radius `1/(2p)`. A birth occurs when the old residual open set `R_k(s)` is
contained in the new `q`-arc.

The special points are `0` and `1/2`. The value `0/1 is a cut representation`
of the same circular point, not two different geometric endpoints.

## Endpoint Lattice Facts

Old prime-cloud endpoints have the form `(2b +/- 1)/(2p)`. New `q`-arc
endpoints have the same form with denominator `2q`.

Near `0`, the nearest old endpoint distance is at least 1/(2p_k). Near `1/2`,
the nearest old endpoint other than 1/2 is at least 1/p_k. Since `q>p_k`, the
special `q`-arcs have radius or one-sided central length too small to reach the
next old endpoint from those special points.

If an endpoint of an old odd-prime cloud and an endpoint of the new odd-prime
`q` cloud coincide, the common point is forced to be `1/2`: from
`u/(2p)=v/(2q)` with coprime odd primes `p<q`, the in-range odd endpoint
numerators force `u=p` and `v=q`.

## Forbidden Special Remainder Lemma

Lemma candidate: for the transition from `p_k` to `q=p_{k+1}`, the remainders
`a=0`, `a=(q-1)/2`, and `a=(q+1)/2` cannot produce birth.

This is not proved by endpoint-touch alone. The `a=0` arc wraps around the
circular point `0`, while the central two remainders are the one-sided arcs
adjacent to `1/2`. In each case, either the old prefix already covers the
special side, so there is no old residual gap wholly inside the new special
arc, or the adjacent old endpoint is farther away than the new `q` arc can
reach. Thus the special arc cannot contain the entire old residual open set.

The checked v2.5 finite scopes support this lemma candidate: the special
remainders occur as checked lift rows and capacity candidates, but they never
have positive phase margin, close rows, or birth rows.

## Central Endpoint Obstruction Lemma

Lemma candidate: endpoint-touch birth cannot occur. If endpoint-touch were to
occur between an old odd-prime cloud and the new `q` cloud, the endpoint lattice
forces the touch point to be `1/2`. The only new `q` arcs with endpoint `1/2`
are the central arcs for `a=(q-1)/2` and `a=(q+1)/2`.

On either side of `1/2`, any adjacent old residual gap has its next old endpoint
at distance at least `1/p_k`, while the central `q` arc extends only `1/q`.
Because `q>p_k`, the central `q` arc is too short to contain the whole adjacent
old residual gap. Therefore endpoint-touch birth is structurally obstructed.

The checked v2.5 finite scopes support this candidate: all 770 close/birth rows
are strict single-gap births, and the phase diagnostics record zero endpoint
touch rows.

## Relation To 3 Mod 6 Ancestry

The mod 6 ancestry diagnostic is a downstream research question, not a theorem.
The working idea is that `p=2` and `p=3` suppress the special points `0` and
`1/2` early, so later birth-producing gaps may be biased toward interior
single-gap ancestry.

The current data must be read asymmetrically: `B4->B5` is weak or
non-supportive for `mod 6 = 3`, while `B5->B6` and `B6->B7` show strong
`mod 6 = 3` enrichment among close rows. This supports a mod 6 ancestry
diagnostic, not a public theorem, not a general predictor, and not an
asymptotic law.

## Non-claims

This v2.6 Gate R note is source-only research. It is not a public theorem, not
a DOI artifact, not a GitHub Release, not a B8 theorem, not a B8 full graph, not
a general predictor, and not an asymptotic law. It does not modify the v2.5
public theorem release.

## Gate R Decision

Gate R should continue the `special point obstruction` route if the source-only
checker confirms:

- no special-remainder close or birth rows in the checked finite scopes;
- no endpoint-touch birth rows in the checked finite scopes;
- all checked close/birth rows remain strict single-gap rows;
- `B4->B5` remains weak for `mod 6 = 3`, while later checked scopes show
  enrichment.

The next decision after this starter is whether the two special-point lemmas can
be written as a formal v2.6 theorem note independent of the finite v2.5 audit.
