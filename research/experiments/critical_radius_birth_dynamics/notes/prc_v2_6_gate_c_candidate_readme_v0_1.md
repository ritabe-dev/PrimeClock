# PrimeClock v2.6 Gate C Candidate

This bundle is an internal candidate artifact for the PRC v2.6 single-gap proof
note.

The main document is `THEOREM_NOTE.md`.

## What This Is

This is a reproducible candidate bundle. It contains the proof note, the
checker, the workflow, and the manifest needed to verify that the candidate is
well formed inside the repository.

## What This Is Not

This is not a public theorem release. It is not a DOI artifact, GitHub Release,
B8 theorem, predictor, or asymptotic-law claim. It is not registered in the
public release registry.

## Verify

Run:

```bash
python3 scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_6_v0_1.yml \
  v2-6-gate-c-candidate
```

The expected result is that the proof-note checker, Gate C candidate checker,
bundle self-check, and zip integrity check all pass.
