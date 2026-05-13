# PRC v2.5 Exact Hull Obstruction

This source-only note records an exact diagnostic for the single-gap precursor
pattern.

## Purpose

The informal intuition is that a new prime arc cannot close multiple separated
residual components at once.  This note does not claim the full general theorem.
It checks the exact circular hull obstruction in the current B5/B6/B7
historical scopes and records the B8 source-only close rows as a supporting
single-gap check.

## Diagnostic

For each parent residual set, compute the shortest circular arc that contains
all old residual components:

```text
minimum covering hull length
```

If the parent has more than one residual component and this hull is longer than
the new prime arc width `1/q`, then a single new `q`-arc cannot cover all old
components.  Such a parent is hull-obstructed for complete close.

## Checked results

```text
B4 -> B5 multi-component families = 65
B4 -> B5 hull-obstructed multi-component families = 65
B4 -> B5 multi-component close families = 0

B5 -> B6 multi-component families = 913
B5 -> B6 hull-obstructed multi-component families = 913
B5 -> B6 multi-component close families = 0

B6 -> B7 multi-component families = 13,785
B6 -> B7 hull-obstructed multi-component families = 13,785
B6 -> B7 multi-component close families = 0
```

All checked historical close rows have a single residual component precursor:

```text
B5/B6/B7 historical close rows = 770
single-gap precursor close rows = 770
```

The source-only B8 controls agree with the same pattern:

```text
B8 audited close rows = 32
B8 audited close rows with parent gap count 1 = 32
```

## Interpretation

The safe claim is:

```text
In the checked scopes, multi-component parent residual sets are exact-hull
obstructed, and every checked close row has a single-gap precursor.
```

This supports the aperture-orbit separator by explaining why close candidates
are naturally reduced to single-component aperture tests.

## Non-claims

- This is not yet a general no-multi-gap-birth theorem.
- It does not prove the obstruction for all prime-prefix layers.
- It does not generate a B8 full graph.
- It does not change public release or Zenodo behavior.
