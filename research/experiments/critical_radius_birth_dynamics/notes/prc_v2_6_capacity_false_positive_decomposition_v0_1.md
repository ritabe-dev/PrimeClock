# PRC v2.6 Capacity False-Positive Decomposition v0.1

## Goal

Purpose: add a source-only v2.6 Gate R diagnostic explaining why capacity is not a separator. The diagnostic decomposes capacity-passing non-close rows in the checked B4->B5, B5->B6, and B6->B7 transition scopes.

Current diagnostic readiness is about 95-98% after this note and checker. The v2.5 public theorem release remains protected.

## Capacity Is Not A Separator

Capacity is a necessary size filter: if a parent residual gap is too large for the new `q` cloud, birth cannot occur. But capacity alone does not locate the gap in the `q` grid.

The v2.6 single-gap grid containment diagnostic therefore treats capacity as a preliminary filter and q-grid containment as the exact checked-scope separator.

## False-Positive Decomposition

The committed `prc_v2_6_capacity_false_positive_decomposition_summary_v0_1.csv` records capacity-passing non-close rows. In every checked scope, all capacity false positives are single-gap rows:

- `B4->B5`: capacity non-close `294`, single-gap capacity non-close `294`, multi-gap capacity non-close `0`.
- `B5->B6`: capacity non-close `2870`, single-gap capacity non-close `2870`, multi-gap capacity non-close `0`.
- `B6->B7`: capacity non-close `49402`, single-gap capacity non-close `49402`, multi-gap capacity non-close `0`.

This means the capacity false positives are not explained by multi-gap parent obstruction. They are single-gap rows whose new remainder does not strictly contain the old residual gap.

## Special Remainder Subset

Special remainders are a visible subset of the capacity false positives:

- `B4->B5`: special remainder subset `84`.
- `B5->B6`: special remainder subset `672`.
- `B6->B7`: special remainder subset `8844`.

These rows are compatible with the v2.6 special point obstruction candidate. They do not exhaust the false positives.

## Ordinary Grid Misalignment

Most capacity false positives are ordinary non-special q-grid misses:

- `B4->B5`: ordinary grid miss `210`.
- `B5->B6`: ordinary grid miss `2198`.
- `B6->B7`: ordinary grid miss `40558`.

The checker also records `grid_strict_containment_nonclose_rows = 0` in every checked scope. Thus, within the committed finite diagnostics, once strict q-grid containment holds, the row is close; capacity-passing non-close rows are grid misses.

## Link To Single-Gap Containment

The central explanatory route is:

```text
single-gap required
capacity necessary
q-grid containment sufficient in checked scopes
capacity false positives are grid misses
```

This diagnostic strengthens the single-gap q-grid containment route by showing that capacity false positives survive the single-gap filter but fail the grid-position filter.

## Gate R Decision

`diagnostic=continue`

`capacity=false_positive_filter_only`

`capacity_false_positive_decomposition=continue`

`single_gap_grid_containment=continue`

`public_theorem=defer`

Decision: continue capacity false-positive decomposition as a Gate R diagnostic only.

## Non-claims

This note makes no theorem claim, no predictor claim, no public theorem claim, no DOI claim, no GitHub Release claim, no B8 theorem claim, no B8 full graph claim, and no asymptotic law claim.

It audits committed checked finite scopes only and does not claim automatic extension beyond B4->B5, B5->B6, and B6->B7.
