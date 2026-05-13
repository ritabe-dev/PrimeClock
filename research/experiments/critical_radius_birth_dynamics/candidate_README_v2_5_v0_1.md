# PrimeClock PRC v2.5 Candidate Bundle

This is an internal candidate bundle for PrimeClock PRC v2.5.  It is a
candidate package, not a public release.

Version-line relationship:

```text
v2.3 public theorem -> v2.4 inherited source diagnostics -> v2.5 candidate mechanism -> Gate P public decision
```

The v2.5 candidate uses v2.4 transition and phase diagnostics as inherited
source support.  Those v2.4 diagnostics are included only to make this candidate
reproducible; they are not cited as public v2.4 results.

Terminology:

- `source-only` means public excluded.
- `candidate-included` means included in this internal candidate bundle.
- `candidate-excluded` means intentionally absent from this internal candidate bundle.
- `source_only_research.files` is the full-repo v2.5 artifact superset used by
  non-leak hygiene.
- `candidate_bundle_manifest_v2_5_v0_1.json` is the candidate-included subset
  packaged for reviewer ZIPs.
- `prc_v2_5_research_seed_note_v0_1.md` and
  `prc_v2_5_deferred_review_resolution_v0_1.md` are candidate-excluded internal
  planning notes.

## Claim

The candidate fixes a finite exact signed containment certificate for residual
dynamics.  Equivalently, the checked aperture-orbit margin is a terminal
containment certificate, not an independent general predictor:

```text
In checked PRC transition scopes, capacity admits many false positives, while
positive signed aperture-orbit margin separates close lifts from capacity
non-close controls.
```

The support lemma is:

```text
In checked scopes, multi-component parent residual sets are exact-hull
obstructed, and every checked close row has a single-gap precursor.
```

## Non-Claims

This candidate is based on the immutable v2.3.0 public release line and the
public-excluded v2.5 candidate diagnostics.  B8 is a selected stress-control
sample, not coverage, recall, or holdout validation.  The B8 stress-control
layer records `32` selected close rows, `576` sibling non-birth controls, and
`64` matched non-birth controls.  There is no B8 full graph, no B8 public
theorem, no asymptotic law, no general prediction theorem, and no public release
in this bundle.

## Checked Counts

- Historical B5/B6/B7 close or birth rows: `770`.
- Historical capacity non-close families: `2430`.
- Historical non-close positive-margin rows: `0`.
- Exact-hull obstructed multi-component families: `65 / 913 / 13785`.
- B8 selected stress-control sample: `32` close rows, `576` sibling non-birth
  controls, `64` matched non-birth controls, and `k8 sample overlap = 1`.

For reviewer terminology and compact count tables, see
`research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_reviewer_glossary_v0_1.md`
and
`research/experiments/critical_radius_birth_dynamics/data/prc_v2_5_gate_p_summary_tables_v0_1.csv`.

## Limitations

The certificate is checked only in the recorded finite transition scopes.  It
does not explain an asymptotic law, does not make B8 coverage claims, and does
not turn the B8 selected stress-control sample into public evidence.  The
obstruction bucket counts are finite diagnostics, not a layer-general causal
classification.

## Reviewer Setup

Use `research/.venv/bin/python` when reviewing from the repository checkout used
to build this candidate.  In a fresh environment, install the research package
before running workflow gates:

```bash
cd research && python -m pip install -e .
```

For a ZIP-only review, use this order:

```text
unzip -t -> candidate-integrity -> gate-c
```

The ZIP reviewer-facing workflow modes are `candidate-integrity`, `gate-c`, and
`bundle`.  The `quick` mode is full diagnostics; it may be slower and should be
run from the full repository or a prepared checkout with all diagnostic
artifacts present.  The `source-only-hygiene` mode is a full repo only v2.5 ->
v2.3/public non-leak guard; it is not a ZIP reviewer command and not the v2.5
candidate bundle manifest check.
This is intentionally the v2.3 candidate manifest and is only for the full repo
leak guard.

When building or checking this v2.5 candidate directly, pass the explicit
manifest:

```bash
research/.venv/bin/python research/experiments/critical_radius_birth_dynamics/candidate_bundle.py \
  --manifest research/experiments/critical_radius_birth_dynamics/candidate_bundle_manifest_v2_5_v0_1.json \
  --out /private/tmp/primeclock-v25-candidate-latest \
  --name PrimeClock-v2.5-candidate-latest \
  --zip
```

## Verify

From the repository root:

```bash
research/.venv/bin/python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_5_v0_1.yml \
  candidate-integrity

research/.venv/bin/python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_5_v0_1.yml \
  gate-c
```

The Gate C core is `candidate-integrity` plus candidate bundle build/check.
The `quick` gate remains the v2.5 full diagnostics path and is intentionally
separate from the ZIP reviewer path and Gate C core.
