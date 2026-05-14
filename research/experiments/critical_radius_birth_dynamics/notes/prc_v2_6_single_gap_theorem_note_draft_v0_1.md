# PRC v2.6 Single-Gap Theorem-Note Draft v0.1

## Goal

Purpose: integrate the v2.6 residual-gap and q-grid containment diagnostics into a source-only theorem-note draft while keeping the v2.5 public theorem release fixed.

Current readiness is about 98-99% for a Gate R theorem-note draft after this note and checker. The remaining work is about 0.2-0.3 slice focused on review and tightening, not on adding more diagnostic tables by default.

## Definitions

Let the old prime prefix contain `2,3,...,p_k`, and let `q=p_{k+1}` be the next odd prime. For a parent residue row, let the old residual set be the complement of the old closed prime clouds on the circle.

If the old residual set has exactly one connected component, choose a non-wrapping representative or split at `0/1` and write that single residual gap as `G=(L,R)`.

For the new q-remainder `a`, write the new q-cloud as:

```text
I_q(a) = [(a - 1/2)/q, (a + 1/2)/q]
```

Endpoint equality is kept separate from strict containment. Capacity means the size condition `q(R-L) < 1`; it is necessary for a single gap to fit inside a q-cloud, but it is not a separator by itself.

## General Lemma Candidates

The following are promoted as source-only theorem-note candidates:

| lemma | decision |
| --- | --- |
| Special Endpoint Spacing Lemma | promote_candidate |
| Residual Component Boundary Lemma | promote_candidate |
| Forbidden Special Remainder Lemma | promote_candidate |
| Central Endpoint Obstruction Lemma | promote_candidate |
| Single-Gap Grid Containment Lemma | promote_candidate |

The `Single-Gap Grid Containment Lemma` is a geometric lemma, not a global PRC birth theorem. For a fixed single residual gap `G=(L,R)` and a fixed q-cloud `I_q(a)`, strict containment is equivalent to:

```text
G subset I_q(a)
(a - 1/2)/q < L
R < (a + 1/2)/q
qR - 1/2 < a < qL + 1/2
```

The open interval for `a` has width `1 - q(R-L)`. Thus capacity is the positivity of that width, while q-grid alignment is the requirement that the actual integer remainder `a` lies strictly inside the interval.

## Checked-Scope Diagnostics

The checked finite scopes B4->B5, B5->B6, and B6->B7 support the route:

```text
single-gap required
capacity necessary
q-grid containment matches close rows in checked scopes
capacity false positives are grid misses in checked scopes
```

The committed audits record:

- strict q-grid containment rows match checked close rows with zero mismatches;
- grid endpoint-touch rows are zero;
- capacity false positives are single-gap rows whose actual q-remainder misses the strict containment interval;
- special remainders and central endpoint-touch remain governed by the special point obstruction candidate;
- mod 6 ancestry and k=2 multi-gap dilution remain explanatory diagnostics only.

## Promote-Defer Boundary

The theorem-note draft promotes geometric and topological lemmas, but defers global PRC equivalence claims:

| claim | decision |
| --- | --- |
| Special Endpoint Spacing Lemma | promote_candidate |
| Residual Component Boundary Lemma | promote_candidate |
| Forbidden Special Remainder Lemma | promote_candidate |
| Central Endpoint Obstruction Lemma | promote_candidate |
| Single-Gap Grid Containment Lemma | promote_candidate |
| Close(row) iff strict q-grid containment beyond checked scopes | defer |
| all births are single-gap beyond checked scopes | defer |
| capacity false positives are all grid misses beyond checked scopes | defer |
| mod 6 ancestry theorem | defer |
| k=2 multi-gap dilution theorem | defer |
| capacity as a general separator | reject |

This boundary is the central point of the draft. It lets v2.6 advance the clean geometric content while preventing the checked B4->B7 audits from being overstated as a general theorem.

## Proof Obligations

The remaining proof obligations are:

- make the circular representative or `0/1` splitting convention explicit in every containment statement;
- keep endpoint-touch equality out of strict containment;
- state the residual component boundary lemma without relying on finite CSV counts;
- distinguish `there exists an integer a in the open interval` from `the actual lift remainder a is aligned`;
- keep capacity as a necessary size filter rather than a separator;
- keep mod 6 ancestry and k=2 multi-gap dilution diagnostic-only.

## Gate R Decision

`theorem_note_draft=continue`

`source_theorem_note=promote_candidate`

`single_gap_grid_containment_lemma=promote_candidate`

`close_iff_grid_containment_general_theorem=defer`

`capacity_general_separator=reject`

`mod6_theorem=defer`

`public_theorem=defer`

Decision: continue v2.6 theorem-note drafting as source-only Gate R research. The next step is review and tightening of this draft, not Gate C, Gate P, DOI, GitHub Release, B8 theorem work, general predictor work, or asymptotic law work.

## Non-claims

This note makes no public theorem claim, no DOI claim, no GitHub Release claim, no B8 theorem claim, no B8 full graph claim, no general predictor claim, and no asymptotic law claim.

It does not modify the v2.5 public theorem release, the root README, VERSION_MAP, release registry, v2.5 release files, or the v2.3 hash-protected public README.

This remains Gate R source-only research.
