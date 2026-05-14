# PRC v2.6 Special Point Theorem-Note Decision v0.1

## Goal

Purpose: decide whether the v2.6 special-point obstruction line is ready to promote into a source-only theorem note candidate, while keeping any public theorem claim deferred.

Current status: v2.5 public theorem release protection remains 100%; v2.6 source-only theorem-note candidate readiness is about 95-98%; after this local decision artifact, the remaining work is about 0.3-0.5 slice focused on tightening the residual component boundary wording.

## Candidate Lemmas

`Central Endpoint Obstruction Lemma`: promote to source-only theorem-note candidate. Endpoint centralization and length obstruction can be written from endpoint lattice spacing plus the residual component boundary lemma.

`Forbidden Special Remainder Lemma`: promote to source-only theorem-note candidate. The residual-gap containment bridge is handled at candidate level by the residual component boundary lemma: if the special side is uncovered, the residual component extends to the next old endpoint; if it is covered, there is no old residual component on that special side to close.

`3 mod 6 ancestry`: diagnostic only. It may explain where productive interior single-gap ancestry concentrates, but it is not a theorem claim.

## Endpoint-Distance Bridge

The endpoint-distance proof obligation supports these candidate facts:

- near `0`, the closest old odd-prime endpoint is at distance `1/(2p_k)`;
- near `1/2`, the closest old odd-prime endpoint other than `1/2` is at distance `1/p_k`;
- since `q>p_k`, the special `q` arcs are shorter than those adjacent old endpoint distances.

The bridge is now a theorem-note candidate rather than a blocker. The endpoint lattice calculation gives the special spacing, and the residual component boundary lemma gives the topological step from nearest endpoint spacing to old residual component length.

## Promote-Defer Decision

Decision: promote source-only theorem-note candidate while deferring any public theorem.

`source_theorem_note=promote_candidate`

`next=formalize_theorem_note_candidate`

`public_theorem=defer`

`b8_theorem=reject_for_v2_6_gate_r`

`mod6_theorem=defer`

`pr_policy=local_first_until_checkpoint`

The safe next step is a source-only theorem-note candidate, not a public theorem note and not another PR.

## Proof Gaps

Remaining proof gaps:

- tighten the residual component boundary lemma wording so it cannot be read as relying on checked finite scopes;
- keep `0/1` circular cut behavior explicit;
- keep `p=2` half-circle boundary behavior separate from odd-prime endpoint lattice facts;
- keep source-only theorem-note promotion separate from public theorem promotion.

## Non-claims

This source-only Gate R decision makes no public theorem claim, no DOI claim, no GitHub Release claim, no B8 theorem, no B8 full graph claim, no general predictor claim, and no asymptotic law claim.

PR #6 remains a draft checkpoint candidate. It should not be merged or updated until this local branch becomes a coherent Gate R checkpoint.
