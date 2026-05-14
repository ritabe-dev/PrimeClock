# PRC v2.6 Single-Gap Grid Containment Diagnostic v0.1

## Goal

Purpose: add a source-only v2.6 Gate R diagnostic that audits whether PRC birth in the checked B4->B5, B5->B6, and B6->B7 transition scopes is exactly captured by single-gap q-grid containment. Current diagnostic readiness is about 95% after this note and checker. The v2.5 public theorem release remains protected.

This is not a theorem claim, predictor claim, public theorem claim, DOI claim, GitHub Release claim, B8 theorem claim, B8 full graph claim, or asymptotic law claim.

## Definitions

For a parent residue row, let the old residual set be the complement of the old closed prime clouds. If it has exactly one connected component, write that single gap as `G=(L,R)`.

For the new prime `q` and new remainder `a`, write the new q-cloud as:

```text
I_q(a) = [(a - 1/2)/q, (a + 1/2)/q]
```

All arithmetic in the checker is exact rational arithmetic. Circular wrap is handled by splitting arcs at `0/1`.

## Single-Gap Grid Containment

In the non-wrapping single-gap representative, strict birth containment is:

```text
G subset I_q(a)
```

Equivalently:

```text
(a - 1/2)/q < L
R < (a + 1/2)/q
qR - 1/2 < a < qL + 1/2
```

The open interval for the integer `a` has width `1 - q(R-L)`. Thus `q(R-L) < 1` is the capacity condition, while the integer position of `a` inside that interval is the q-grid alignment condition.

## Capacity vs Grid Alignment

Capacity is a necessary size test, not a separator by itself. The checked scopes contain capacity false positives: rows where the old uncovered measure is small enough but the q-grid remainder is not aligned to contain the old residual gap.

The diagnostic separates these roles:

- single-gap structure chooses the correct kind of parent residual set;
- capacity tests whether the gap could fit in a q-cloud;
- q-grid alignment tests whether the actual new remainder contains the gap.

## Forbidden Remainders

The special remainders `0`, `(q-1)/2`, and `(q+1)/2` remain governed by the v2.6 special point obstruction candidate. They are not promoted here to a public theorem.

This diagnostic is compatible with the special point story: forbidden remainders are excluded structurally, while ordinary rows are audited by exact q-grid containment.

## Endpoint-Touch Strictness

Endpoint equality is not counted as strict containment. The checker separates strict containment from endpoint-touch containment. In the checked scopes, grid endpoint-touch rows are `0`, matching the existing endpoint obstruction finite support.

## Checked-Scope Audit

The committed `prc_v2_6_single_gap_grid_containment_summary_v0_1.csv` records:

- `B4_to_B5_full`: `14` grid strict containment rows, `14` close rows, `0` mismatches.
- `B5_to_B6_full`: `42` grid strict containment rows, `42` close rows, `0` mismatches.
- `B6_to_B7_full`: `714` grid strict containment rows, `714` close rows, `0` mismatches.

Across these checked scopes, strict single-gap q-grid containment matches close rows exactly in the committed finite diagnostics. Capacity remains a false-positive filter only.

## Gate R Decision

`diagnostic=continue`

`single_gap_grid_containment=continue`

`capacity=false_positive_filter_only`

`public_theorem=defer`

Decision: continue single-gap q-grid containment as the central v2.6 Gate R diagnostic route.

## Non-claims

This note makes no theorem claim, no predictor claim, no public theorem claim, no DOI claim, no GitHub Release claim, no B8 theorem claim, no B8 full graph claim, and no asymptotic law claim.

It audits committed checked finite scopes only and does not claim automatic extension beyond B4->B5, B5->B6, and B6->B7.
