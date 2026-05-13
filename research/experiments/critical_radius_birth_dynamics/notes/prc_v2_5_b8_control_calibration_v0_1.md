# PRC v2.5 B8 Control Calibration

This source-only note records the second control layer around the B8
aperture-orbit probe.

## Purpose

The B8 aperture-orbit probe found 32 exact B8 birth rows. This note does not
promote those rows to a public claim. It asks whether those rows survive three
stronger controls:

```text
selection bias
trivial phase sorting
sample coincidence
```

## Control layers

### Exact sibling control

For each of the 32 audited B8 birth parent families, all 19 lifts mod 19 are
recomputed from the same exact parent residual component.

```text
birth parent families = 32
sibling rows = 608
birth/close rows = 32
non-birth sibling rows = 576
```

The close lift is the only strict positive-margin lift in each checked family.
The remaining 18 sibling lifts are non-close controls from the same old gap.

### Matched non-birth control

For each audited B8 birth row, two non-birth controls are selected from other
parents with comparable capacity geometry.

```text
matched non-birth controls = 64
matched residual-measure buckets = 10
matched reflection-orbit buckets = 10
```

All matched controls are parent-uncovered, child-noncovered, capacity-pass, and
non-positive-margin rows.

### k=8 sample calibration

The older guarded k=8 birth sample contains 200 rows. It is a sample, not the
full set of 6,752 B8 births.

```text
k8 sample rows = 200
overlap with aperture-orbit 32 = 1
```

This is recorded only as sample calibration. It is not a recall estimate.

## Interpretation

The useful readout is that the 32 source-only B8 births are not merely isolated
positive rows:

```text
same-parent sibling controls fail phase;
matched capacity controls also fail phase;
the existing k=8 sample is used only as a calibration guard.
```

This keeps aperture-orbit as a plausible predictor, but it still does not make a
public B8 theorem.

## Non-claims

- No B8 full transition graph is generated.
- No recall or coverage claim is made from the 200-row k=8 sample.
- No candidate ZIP, GitHub Release, Zenodo path, or public claim changes.
- If later controls fail, v2.5 should pivot to obstruction classification.
