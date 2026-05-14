# PRC v2.6 Special Point Theorem-Note Decision v0.1

## Goal

Purpose: decide whether the v2.6 special-point obstruction line is ready to promote into a source-only theorem note, or whether it should remain in Gate R until the residual-gap containment bridge is closed.

Current status: v2.5 public theorem release protection remains 100%; v2.6 endpoint-distance proof-obligation readiness is about 90-95%; after this local decision artifact, the remaining work is about 0.5 slice focused on the residual-gap containment bridge.

## Candidate Lemmas

`Central Endpoint Obstruction Lemma`: promote only as a theorem-note candidate if endpoint centralization and length obstruction are written without finite-scope dependence.

`Forbidden Special Remainder Lemma`: defer unless the residual-gap containment bridge is clean. The endpoint lattice bounds are promising, but the proof still needs to show that the adjacent old residual gap is governed by those nearest old endpoint bounds without relying on committed finite audit tables.

`3 mod 6 ancestry`: diagnostic only. It may explain where productive interior single-gap ancestry concentrates, but it is not a theorem claim.

## Endpoint-Distance Bridge

The endpoint-distance proof obligation supports these candidate facts:

- near `0`, the closest old odd-prime endpoint is at distance `1/(2p_k)`;
- near `1/2`, the closest old odd-prime endpoint other than `1/2` is at distance `1/p_k`;
- since `q>p_k`, the special `q` arcs are shorter than those adjacent old endpoint distances.

The unresolved bridge is not the endpoint lattice calculation. The unresolved bridge is proving, without finite-scope dependence, that the relevant old residual gap adjacent to `0` or `1/2` extends to the next old endpoint in the way the obstruction argument needs.

## Promote-Defer Decision

Decision: defer full theorem-note promotion.

`decision=defer_full_theorem_note`

`next=close_residual_gap_bridge`

`public_theorem=defer`

`b8_theorem=reject_for_v2_6_gate_r`

`mod6_theorem=defer`

`pr_policy=local_first_until_checkpoint`

The safe next step is a smaller residual-gap bridge note/checker, not a public theorem note and not another PR.

## Proof Gaps

Remaining proof gaps:

- prove the residual-gap containment bridge near `0` and `1/2` without using checked finite scopes as the argument;
- keep `0/1` circular cut behavior explicit;
- keep `p=2` half-circle boundary behavior separate from odd-prime endpoint lattice facts;
- decide whether the central endpoint lemma can be promoted independently while the forbidden special remainder lemma remains deferred.

## Non-claims

This source-only Gate R decision makes no public theorem claim, no DOI claim, no GitHub Release claim, no B8 theorem, no B8 full graph claim, no general predictor claim, and no asymptotic law claim.

PR #6 remains a draft checkpoint candidate. It should not be merged or updated until this local branch becomes a coherent Gate R checkpoint.

