# PRC v2.5 Theorem Candidate Note

## Main Claim

In checked PRC transition scopes, capacity admits many false positives, while
positive signed aperture-orbit margin separates close lifts from capacity
non-close controls.  This is a finite exact signed containment certificate: the
margin is a terminal certificate for the checked transition rows, not an
independent general predictor.

The checked historical scopes are B4->B5, B5->B6, and B6->B7 transition
families.  Across these scopes, the historical close or birth count is `770`,
capacity non-close families total `2430`, and historical non-close
positive-margin rows total `0`.

## Support Claim

In checked scopes, multi-component parent residual sets are exact-hull
obstructed, and every checked close row has a single-gap precursor.

The checked multi-component obstruction counts are:

```text
B4->B5: 65
B5->B6: 913
B6->B7: 13785
```

The checked close rows have single-gap precursors in the historical scopes.
The selected B8 stress-control close rows also have single-gap precursors.

## B8 Stress Control

B8 is used only as source-only selected stress-control evidence.  The selected
aperture-orbit probe audits `32` B8 close rows, `576` sibling non-birth
controls, and `64` matched non-birth controls.  The B8 200-row sample overlap
is `1`.  These counts are not coverage, recall, or holdout validation, and the
aperture-frontier selection is phase-margin-related; the B8 evidence is not a
proof that the separator generalizes.

## Claim Boundary

This v2.5 candidate has no B8 full graph, no B8 public theorem, no asymptotic
law, no general prediction theorem, and no public release.  It is an internal
candidate line for external review before any Gate P decision.

## Diagnostic Value

The useful Gate P framing is not that phase margin is a broad predictor.  The
useful finite diagnostics are:

- capacity alone leaves many false positives;
- close and near-miss rows can share prefix history before the final phase;
- exact-hull obstruction keeps checked close rows in the single-gap precursor
  case;
- obstruction buckets summarize checked failure modes without claiming a
  layer-general causal taxonomy.
