# PRC v2.5 External Reviewer Summary

Status: one-page reviewer summary for Gate P.  This note does not authorize a
public release.

## Definitions

- `capacity`: the old residual component is small enough that the next
  new-prime arc could cover it by width.
- `signed containment margin`: exact rational margin showing whether the
  new-prime arc strictly contains the relevant residual component.
- `close`: the residual set becomes empty after the transition.
- `birth`: the corresponding historical covering event.
- `stress control`: selected diagnostic evidence, not coverage, recall, or
  holdout validation.

## What Is Checked

The v2.5 candidate checks finite PRC transition scopes B4-to-B5, B5-to-B6, and
B6-to-B7.  In those checked finite scopes, capacity admits many false positives,
while positive signed aperture-orbit margin separates close lifts from capacity
non-close controls.

## What Is Not Claimed

This is not a public theorem, not a general predictor, not a B8 public theorem,
not B8 coverage, not B8 recall, not holdout validation, and not an asymptotic
law.  B8 remains a selected stress-control sample only.

## Exact Counts

- Historical close or birth rows: 770.
- Capacity non-close families: 2430.
- Non-close positive-margin rows: 0.
- Exact-hull obstructed multi-component families: 65 / 913 / 13785.
- B8 selected stress-control sample: 32 close rows, 576 sibling non-birth
  controls, 64 matched non-birth controls, k8 sample overlap = 1.

## Reproduction Commands

Run the candidate checks from the repository root:

```bash
research/.venv/bin/python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_5_v0_1.yml \
  candidate-integrity

research/.venv/bin/python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_5_v0_1.yml \
  gate-c

research/.venv/bin/python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_5_v0_1.yml \
  gate-p-readiness
```

## Limitations

The result is a finite exact signed containment certificate for checked finite
scopes.  It does not explain why all future layers should behave the same way,
and it should not be described as a general birth predictor.
