# PRC v2.6 Special Point Lemma Draft v0.1

## Definitions

Purpose: formalize the v2.6 special-point obstruction route while keeping the
v2.5 public theorem release fixed. The current objective is a source-only Gate R
proof-candidate package, about 85-90% ready for focused review and about
0.5-1 slice from a Gate R decision on theorem-note promotion.

Let `q=p_{k+1}` be the next odd prime. The old prefix contains 2,3,...,p_k,
with `p_k<q`. A prime `p` contributes the closed circular arc
centered at `a/p` with radius `1/(2p)`. A birth candidate asks whether the old
residual open set `R_k(s)` is contained in the new `q`-arc for a residue
`a mod q`.

The special circular points are `0` and `1/2`. The text `0/1 is the same
circular point` as `0`; it is a cut representation, not a second geometric
endpoint.

## Endpoint Lattice Facts

Cloud endpoints have the form `(2a-1)/(2p)` and `(2a+1)/(2p)` on the circle.
For distinct odd primes `p<q`, an endpoint coincidence between a `p`-cloud and a
`q`-cloud is forced to the central point `1/2`. Equivalently, if
`u/(2p)=v/(2q)` with valid odd endpoint numerators and coprime odd primes, then
the in-range equality forces `u=p` and `v=q`.

Near `0`, the nearest old endpoint is at distance at least `1/(2p_k)`. Near
`1/2`, the nearest old endpoint other than `1/2` is at distance at least
`1/p_k`. Since `q>p_k`, the special `q`-arcs are too short to reach the next old
endpoint from these special points.

## Forbidden Special Remainder Proof Candidate

Candidate lemma: in the transition from `p_k` to `q=p_{k+1}`, the remainders
`a=0`, `a=(q-1)/2`, and `a=(q+1)/2` cannot produce birth.

The intended proof is by special-point obstruction. The `a=0` arc is centered at
the circular point `0`. The two central remainders are the one-sided arcs
adjacent to `1/2`. In each case, if the old prefix already covers the special
side, there is no old residual gap wholly inside the new special arc. If it does
not cover the special side, the next old endpoint is farther away than the new
`q`-arc can reach, so the new arc leaves residual gap outside itself. Thus the
whole old residual open set cannot be contained in the special `q`-arc.

This is a proof candidate, not yet a public theorem. The remaining obligation is
to write the old-endpoint distance lower bounds without relying on the finite
v2.5 audit tables.

## Central Endpoint Obstruction Proof Candidate

Candidate lemma: endpoint-touch birth cannot occur.

The endpoint lattice first centralizes any old odd-prime / new odd-prime
endpoint coincidence at `1/2`. The only new `q`-arcs with endpoint `1/2` are the
central arcs for `a=(q-1)/2` and `a=(q+1)/2`. On either side of `1/2`, an
adjacent old residual gap reaches at least to the next old endpoint, at distance
at least `1/p_k`, while the central `q`-arc extends only `1/q`. Since `q>p_k`,
the central `q`-arc is too short to contain the whole adjacent old residual gap.

This proof candidate explains why endpoint-touch rows are absent in the finite
audit without treating absence as random evidence.

## Proof Obligations

- Formalize the endpoint lattice centralization on the circle, including the
  cut-point convention at `0`.
- Prove the nearest-old-endpoint distance lower bounds around `0` and `1/2` for
  the old prefix `2,3,...,p_k`.
- Separate odd-prime endpoint coincidences from the `p=2` half-circle boundary
  convention.
- State exactly whether the lemma is about all birth candidates or only the
  PRC row universe used by the source-only v2.6 audit.

## Finite Audit Evidence

The committed v2.6 source-only summaries support the proof candidates in the
checked `B4->B5`, `B5->B6`, and `B6->B7` scopes:

- special remainders `0,(q-1)/2,(q+1)/2` have zero positive-margin rows, zero
  close rows, and zero birth rows;
- endpoint-touch rows and endpoint-touch birth rows are zero;
- all 770 checked birth rows are strict single-gap rows;
- `3 mod 6 ancestry diagnostic` remains explanatory only: `B4->B5` is weak or
  non-supportive, while `B5->B6` and `B6->B7` show enrichment.

## Non-claims

This v2.6 draft is source-only Gate R research. It is not a public theorem, not
a DOI artifact, not a GitHub Release, not a B8 theorem, not a B8 full graph, not
a general predictor, and not an asymptotic law. It does not modify the closed
v2.5 public theorem release.
