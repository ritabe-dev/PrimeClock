# PRC v2.5 Breakthrough Diagnostics

This source-only note records the aggressive v2.5 push beyond the residual
dynamics seed.

## Question

The terminal signed phase margin is a perfect checked separator, but by itself
it is still a terminal diagnostic.  The v2.5 breakthrough question is whether
prefix residual dynamics can explain which lineages become margin-positive.

## Diagnostics Added

- Prefix-only grammar removes the final transition label and compares close,
  near-miss, non-close, and capacity-nonclose lineages by earlier residual
  history.
- Margin genesis records prefix scores next to the terminal margin, explicitly
  separating predictor-like features from the final separator.
- Close/near-miss counterfactual rows compare siblings from the same parent
  residual state.
- Refined obstruction buckets split broad phase failure into sibling-dominated,
  split-history, underreach, and wrong-side failures.
- B8 targeted probe tests only the top source-only B7 high-potential parents;
  it is not a full B8 graph and not a public claim.

## Initial Readout

The prefix-only grammar has real enrichment pockets, but it is not yet a
replacement for signed phase margin.  The close-vs-near-miss counterfactual is
stronger: every checked pair shares prefix transition and component-delta
history while the final margin gap separates the close sibling from the
near-miss sibling.

The first B8 targeted probe is negative: the top 200 source-only B7 parents
selected by capacity/width produce no close rows in the checked 19-lift probe.
That is useful negative evidence against capacity-only selection, not evidence
against B8 births or residual dynamics.

The aperture-orbit recovery probe changes the selector.  It keeps the
capacity-top rows as a negative baseline, then selects additional parents by
aperture tension, near-zero margin, orbit diversity, and deterministic hash
controls.  In this source-only probe, the aperture-frontier group finds 32 B8
geometry close rows while the capacity baseline remains at 0.  A follow-up
overlap audit independently recomputes exact k=7/k=8 covering status for these
32 rows; all 32 are B8 births in the checked source-only probe.

## Gate R Implication

v2.5 should remain source-only for now.  The next candidate-level question is
not whether phase margin separates close rows; it does.  The sharper question
is whether aperture-orbit tension can be validated against independently
recomputed B8 birth evidence at broader scope without turning into a
terminal-label restatement.
