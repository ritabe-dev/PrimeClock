# PRC v2.5 Candidate Research README

This research directory is the internal candidate package for PRC v2.5.  It is
not a public release.

## Version-Line Relationship

```text
v2.3 public theorem -> v2.4 inherited source diagnostics -> v2.5 candidate mechanism -> Gate P public decision
```

The v2.5 candidate uses v2.4 transition and phase diagnostics as inherited
source support.  The inherited v2.4 files are candidate-included for
reproducibility, but they remain source-only in the sense of public excluded.
They are not public v2.4 results.

Terminology:

- `source-only`: public excluded.
- `candidate-included`: included in this internal candidate bundle.
- `candidate-excluded`: intentionally absent from this internal candidate bundle.
- `source_only_research.files`: full-repo v2.5 artifact superset for non-leak
  hygiene.
- `candidate_bundle_manifest_v2_5_v0_1.json`: candidate-included subset for the
  reviewer ZIP.
- `prc_v2_5_research_seed_note_v0_1.md` and
  `prc_v2_5_deferred_review_resolution_v0_1.md`: candidate-excluded internal
  planning notes.

## Reviewer Setup

Use `research/.venv/bin/python` from the repository checkout when available.  In
a fresh environment, install the research package first:

```bash
cd research && python -m pip install -e .
```

For a ZIP-only review, the recommended path is:

```text
unzip -t -> candidate-integrity -> gate-c
```

ZIP reviewers should use `candidate-integrity`, `gate-c`, and `bundle`.  The
`quick` mode is full diagnostics; it may be slower and should be run from the
full repository or a prepared checkout with all diagnostic artifacts present.
Gate C core is `candidate-integrity` plus bundle build/check and focused pytest.
The `source-only-hygiene` mode is a full repo only v2.5 -> v2.3/public non-leak
guard, not a ZIP reviewer command and not the v2.5 candidate manifest.

When building or checking this v2.5 candidate directly, pass
`--manifest research/experiments/critical_radius_birth_dynamics/candidate_bundle_manifest_v2_5_v0_1.json`.

## Candidate Claim

In checked PRC transition scopes, the finite exact signed containment
certificate shows that capacity admits many false positives, while positive
signed aperture-orbit margin separates close lifts from capacity non-close
controls.  The margin is a terminal containment certificate, not an independent
general predictor.

## Support Claim

In checked scopes, multi-component parent residual sets are exact-hull
obstructed, and every checked close row has a single-gap precursor.

## Checked Counts

- Historical B5/B6/B7 close or birth rows: `770`.
- Historical capacity non-close families: `2430`.
- Historical non-close positive-margin rows: `0`.
- B8 selected stress-control sample, not coverage, recall, or holdout
  validation: `32` close rows.  This is a stress-control count, not public
  evidence for B8 coverage.
- B8 sibling non-birth controls: `576`.
- B8 matched non-birth controls: `64`.
- k8 sample overlap: `1`.
- Exact-hull obstructed multi-component families: `65 / 913 / 13785`.

## Boundary

B8 remains selected stress-control evidence, not coverage.  This candidate
makes no B8 full graph claim, no B8 public theorem, no asymptotic law, and no
general prediction theorem.  Public release and DOI decisions belong to a later
Gate P.  Obstruction buckets are finite diagnostics, not a layer-general causal
classification.
