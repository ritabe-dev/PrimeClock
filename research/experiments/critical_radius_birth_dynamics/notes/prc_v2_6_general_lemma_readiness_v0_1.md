# PRC v2.6 General Lemma Readiness v0.1

## Goal

Purpose: decide how far the v2.6 finite diagnostics can be written as general lemma candidates while keeping global PRC theorem claims deferred.

Current readiness is about 95-98% for the special point obstruction lemmas and about 85-90% for the single-gap grid containment route. This note raises geometric facts to source-only theorem-note candidates, but it keeps checked-scope equivalence claims finite. The v2.5 public theorem release remains protected.

## Lemmas That Can Be General

The following are promoted as source-only general lemma candidates:

| lemma | decision |
| --- | --- |
| Special Endpoint Spacing Lemma | promote_candidate |
| Residual Component Boundary Lemma | promote_candidate |
| Forbidden Special Remainder Lemma | promote_candidate |
| Central Endpoint Obstruction Lemma | promote_candidate |
| Single-Gap Grid Containment Lemma | promote_candidate |

The `Single-Gap Grid Containment Lemma` is a geometric containment criterion, not a full PRC birth theorem. For a fixed single residual component `G=(L,R)` and q-cloud `I_q(a)`, strict containment is equivalent to:

```text
G subset I_q(a)
I_q(a) = [(a - 1/2)/q, (a + 1/2)/q]
qR - 1/2 < a < qL + 1/2
```

This statement is made after choosing a non-wrapping representative or splitting at `0/1`. The interval width is `1 - q(R-L)`, so capacity is the necessary condition that this width is positive. The actual integer `a` must still be aligned inside the open interval.

## Lemmas Still Checked-Scope

The following remain checked-scope diagnostics, not general theorem claims:

| claim | decision |
| --- | --- |
| Close(row) iff strict q-grid containment | defer |
| all births are single-gap | defer |
| capacity false positives are all grid misses | defer |
| mod 6 ancestry theorem | defer |
| k=2 multi-gap dilution theorem | defer |
| capacity general separator | reject |

The finite audits show exact agreement in B4->B5, B5->B6, and B6->B7, but this note does not claim automatic extension beyond those recorded complete transition scopes.

## Proof Obligations

The remaining proof obligations are:

- tighten the circular representative language for wrapping single gaps;
- keep endpoint equality separate from strict containment;
- show exactly when the PRC close/birth predicate is equivalent to residual containment, without using checked CSV counts as the proof;
- keep `integer a exists` separate from `the actual lift remainder a is aligned`;
- keep `mod 6 ancestry` and `k=2 multi-gap dilution` diagnostic-only.

These obligations are compatible with the current route:

```text
single-gap required
capacity necessary
q-grid containment sufficient in checked scopes
capacity false positives are grid misses
```

## Gate R Decision

`general_lemma_readiness=continue`

`single_gap_grid_containment_lemma=promote_candidate`

`close_iff_grid_containment_general_theorem=defer`

`capacity_general_separator=reject`

`mod6_theorem=defer`

`public_theorem=defer`

Decision: continue toward a source-only theorem-note candidate for the geometric lemmas, while deferring any public theorem or global PRC birth equivalence claim.

## Non-claims

This note makes no public theorem claim, no DOI claim, no GitHub Release claim, no B8 theorem claim, no B8 full graph claim, no general predictor claim, and no asymptotic law claim.

This remains Gate R source-only research.
