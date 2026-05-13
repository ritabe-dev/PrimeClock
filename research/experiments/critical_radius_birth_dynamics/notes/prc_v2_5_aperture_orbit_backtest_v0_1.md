# PRC v2.5 Aperture-Orbit Historical Calibration

This source-only note records a historical calibration for the v2.5
aperture-orbit predictor.

## Purpose

The B8 aperture-orbit probe is exploratory. To avoid treating it as a B8-only
post-hoc selector, this calibration checks whether the same separator pattern is
visible in the already-known B5/B6/B7 transition families.

This is not out-of-sample prediction. B5/B6/B7 are historical calibration and a
regression guard.

## Historical scopes

The canonical exact source is the v2.4 phase-gate diagnostics.

```text
B4 -> B5 families = 208
B5 -> B6 families = 2274
B6 -> B7 families = 29520
```

The checked close/birth families are:

```text
B4 -> B5 close = 14
B5 -> B6 close = 42
B6 -> B7 close = 714
total = 770
```

In every historical scope:

```text
close rows have phase rank 1
close rows have positive signed phase margin
non-close rows have no positive signed phase margin
non-birth close rows = 0
```

## Capacity false positives

Capacity remains a broad gate rather than a theorem-level separator.

```text
B4 -> B5 capacity non-close = 14
B5 -> B6 capacity non-close = 182
B6 -> B7 capacity non-close = 2234
total capacity non-close = 2430
```

Thus capacity admits many false positives, while the signed aperture-orbit
margin separates the checked close lift.

## B8 comparison

The B8 control layer is still source-only:

```text
B8 sibling close rows = 32
B8 sibling non-birth rows = 576
B8 matched non-birth rows = 64
B8 matched positive-margin non-birth rows = 0
k8 sample rows = 200
```

The k=8 sample is used only as calibration, not recall.

## Interpretation

The safe readout is:

```text
aperture-orbit separation is stable across B5/B6/B7 historical calibration
and the current source-only B8 controls.
```

This strengthens the predictor as a Gate R diagnostic. It does not create a
public B8 claim.

## Non-claims

- No B8 full graph is generated.
- No out-of-sample prediction claim is made from B5/B6/B7.
- No public B8 theorem, candidate ZIP, GitHub Release, or Zenodo path changes.
- Capacity plus phase remains a foundation, not the headline theorem by itself.
