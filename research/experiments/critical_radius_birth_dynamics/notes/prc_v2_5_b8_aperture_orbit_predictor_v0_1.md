# PRC v2.5 B8 Aperture-Orbit Predictor

This source-only note records the first recovery step after the negative B8
capacity-top probe.

## Core idea

The first B8 targeted probe selected parents by capacity and residual width. It
collapsed to one geometry: `capacity_nonclose`, residual measure `4/77`, and
best margin `-3/209`. That made it a useful negative baseline, but not a strong
upper-layer predictor.

The replacement diagnostic treats B8 as an aperture-orbit problem. Prefix
residual dynamics creates candidate gaps; the next question is whether the
`q=19` lift orbit places an arc center inside the exact containment aperture.

## Source-only readout

The existing `capacity_top_200` baseline is preserved:

```text
parents = 200
lifts = 3800
miss = 3400
trim = 400
close = 0
best parent margin = -3/209 for every selected parent
distinct parent residual measures = 1
```

The aperture-orbit selection is broader:

```text
deduped selected parents = 767
probe rows = 14573
distinct parent residual measures = more than one
positive aperture / positive margin / close rows = 32
```

Within `aperture_frontier_top_400`:

```text
parents = 400
rows = 7600
close rows = 32
positive margin rows = 32
distinct parent residual measures = 25
```

## B8 birth overlap audit

The 32 close rows were checked independently against the exact covering
predicate:

```text
audit rows = 32
parent uncovered at k=7 = 32
child covered at k=8 = 32
child projects to parent mod M_7 = 32
exact B8 birth = 32
```

This audit does not build the B8 full graph.  It verifies only that the 32
source-only close rows found by the aperture-orbit probe satisfy the finite B8
birth condition.

## Interpretation

This does not establish a public B8 theorem. It shows that the previous
capacity selector was too homogeneous, while aperture-orbit selection finds
source-only B8 births in the checked probe.

The safe research statement is:

```text
capacity / width is a weak B8 baseline;
aperture-orbit tension is a stronger source-only selector.
```

## Follow-up control

The follow-up control layer compares these 32 audited B8 births against exact
same-parent sibling lifts, matched capacity non-birth controls, and the existing
200-row guarded k=8 birth sample as calibration only. Those controls are
recorded in `prc_v2_5_b8_control_calibration_v0_1.md`.

## Non-claims

- No B8 full graph is generated.
- No public B8 claim is made.
- No candidate ZIP, GitHub Release, or Zenodo path is changed.
- The 32 checked B8 births are not promoted to public release claims.
