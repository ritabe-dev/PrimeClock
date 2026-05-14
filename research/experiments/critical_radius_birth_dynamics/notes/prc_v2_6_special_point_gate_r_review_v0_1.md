# PRC v2.6 Special Point Gate R Review v0.1

## Goal

Purpose: review whether the v2.6 special-point route is ready to move from a
source-only proof-candidate package toward a focused theorem note. The current
objective is Gate R review, not publication. The v2.5 public theorem release
remains closed and unchanged. Current completion is about 95% for Gate R review
readiness, with about 0.5 slice remaining before a theorem-note promotion,
defer, or negative diagnostic decision.

## Lemma Candidates

`Forbidden Special Remainder Lemma`: continue as a proof candidate. The target
claim is that the remainders `0`, `(q-1)/2`, and `(q+1)/2` cannot produce birth
for the transition from old prefix `2,3,...,p_k` to the next odd prime
`q=p_{k+1}`.

`Central Endpoint Obstruction Lemma`: continue as a proof candidate. The target
claim is that endpoint-touch birth is forced to the central point `1/2`, where
the central `q`-arc is too short to contain the adjacent old residual gap.

`3 mod 6 ancestry`: diagnostic only. It may explain why interior single-gap
ancestry becomes enriched in later checked scopes, but it is not a theorem and
not a predictor.

## Proof Obligations

The main unresolved obligation is to prove the nearest old endpoint lower bounds
without relying on finite audit tables:

- near `0`, nearest old endpoint distance is at least `1/(2p_k)`;
- near `1/2`, nearest old endpoint other than `1/2` is at least `1/p_k`;
- endpoint centralization must be stated on the circle, with `0/1` handled as a
  cut representation of the same circular point;
- odd-prime endpoint coincidences must be separated from the `p=2` half-circle
  convention.

## Finite Audit Support

The committed v2.6 source-only summaries support continuing the route:

- special remainders have zero positive-margin rows, zero close rows, and zero
  birth rows in the checked scopes;
- endpoint-touch rows and endpoint-touch birth rows are zero;
- all 770 checked birth rows are strict single-gap rows;
- mod 6 enrichment is asymmetric: `B4->B5` is weak or non-supportive, while
  `B5->B6` and `B6->B7` show enrichment.

## Gaps

The route is not yet a public theorem. The finite audit supports the candidates,
but the proof still needs standalone endpoint-distance arguments. If those
arguments cannot be made independent of the checked finite artifacts, the
correct Gate R outcome is theorem-note defer.

## Gate R Decision

Gate R decision: continue special-point obstruction as a theorem-note candidate,
with `public_theorem=defer`, `mod6_theorem=defer`, and
`b8_theorem=reject_for_v2_6_gate_r`.

Next action: write a focused theorem-note draft only after the endpoint-distance
proof obligations are resolved or clearly bounded.

## Non-claims

This v2.6 Gate R review makes no public claim, no DOI claim, no B8 theorem, no
B8 full graph, no general predictor, and no asymptotic law. It does not modify
the closed v2.5 public theorem release.
