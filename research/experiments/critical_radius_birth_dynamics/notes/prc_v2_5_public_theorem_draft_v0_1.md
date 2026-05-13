# PRC v2.5 Public Theorem Draft

Status: Gate P theorem-preparation draft. This draft does not authorize a
public release, GitHub Release, Zenodo upload, DOI, or public B8 claim.

## Definitions

- `PRC prime-prefix residual-covering model`: the exact rational interval model
  used in the v2.5 candidate bundle to track residual sets under successive
  prime-prefix transition scopes.
- `Residual set R_k(r)`: the uncovered circular subset associated with a
  residue family after the recorded prefix through layer k.
- `Lift`: a child residue row obtained from a recorded parent family by the
  next-prime grid action in the checked transition scope.
- `Close lift`: a checked lift whose child residual set is empty after the
  next-prime arc is applied.
- `Capacity-admissible non-close control`: a checked non-close family or lift
  whose residual width passes the capacity screen but does not close.
- `Signed aperture-orbit margin`: the exact signed containment margin between
  the parent residual aperture and the next-prime orbit arc in the checked row.
  Positive margin is used here as a terminal containment certificate, not a
  general predictor from prefix history alone.
- `Exact-hull obstruction`: the checked condition that a multi-component parent
  residual set has a circular hull too wide for a single next-prime arc to close
  all components at once.

## Finite Universe

The theorem draft is limited to the recorded complete transition scopes:

- `B4->B5`
- `B5->B6`
- `B6->B7`

The finite universe is the committed v2.5 candidate audit universe for those
recorded complete transition scopes. It includes the checked close lifts,
birth rows, capacity-admissible non-close controls, and exact-hull support rows
listed in the candidate manifest and verified by the v2.5 checkers.

No `B8` full graph, unbounded layer family, asymptotic regime, or prime
distribution law is part of this theorem draft.

## Theorem

PRC v2.5 finite exact aperture-orbit separator theorem.

For the recorded complete transition scopes `B4->B5`, `B5->B6`, and `B6->B7`
under the PRC prime-prefix residual-covering model, every checked close lift
has positive signed aperture-orbit margin, and every checked
capacity-admissible non-close control has non-positive signed aperture-orbit
margin.

Equivalently, within these checked finite scopes, capacity alone is not a
separator, while the signed aperture-orbit margin is a finite exact terminal
containment certificate. This is not a general predictor.

## Exhaustive Enumeration Certificate

The theorem is finite and audit-based. The enumeration certificate consists of:

- the committed transition and phase diagnostic CSV files for the recorded
  complete transition scopes;
- exact rational arithmetic in the helper and checker scripts;
- manifest-bound files in the v2.5 candidate bundle;
- checker assertions that recompute or re-audit the headline counts against the
  committed artifacts.

The public claim, if later authorized, should state this as an exact finite
enumeration certificate rather than as a proof over all future layers.

## Separator Audit

The separator audit fixes the following headline counts:

| Scope | Families | Close or birth rows | Capacity non-close families | Non-close positive margin rows |
| --- | ---: | ---: | ---: | ---: |
| `B4->B5` | 208 | 14 | 14 | 0 |
| `B5->B6` | 2,274 | 42 | 182 | 0 |
| `B6->B7` | 29,520 | 714 | 2,234 | 0 |
| Total | 32,002 | 770 | 2,430 | 0 |

The finite theorem draft depends on the zero count in the final column and on
the exact positive-margin audit for all 770 checked close or birth rows.

## Support Lemma

Within the same checked finite scopes, every checked close row has a single-gap
precursor, and checked multi-component parent residual sets are exact-hull
obstructed.

| Scope | Exact-hull obstructed multi-component families |
| --- | ---: |
| `B4->B5` | 65 |
| `B5->B6` | 913 |
| `B6->B7` | 13,785 |

This support lemma explains why the public theorem draft is framed around
single-gap terminal containment rather than multi-gap closure.

## B8 Non-Claim

B8 selected stress-control only.

The v2.5 candidate includes audited B8 selected stress-control rows, but B8 is
not part of the theorem. The B8 rows are not coverage, recall, holdout
validation, a B8 theorem, or evidence for an asymptotic law. They should remain
appendix or stress-control material unless a later slice builds and audits a B8
full transition universe.

## Reproduction

Reviewer-facing Gate C and Gate P dry-run commands:

```bash
python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_5_v0_1.yml \
  candidate-integrity

python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_5_v0_1.yml \
  gate-c

python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_5_v0_1.yml \
  gate-p-readiness
```

The public theorem claim should not be reduced to "the scripts pass." The claim
is the finite exact enumeration certificate plus the exact signed containment
audit in the recorded complete transition scopes.

## Limitations

- This is a checked finite-scopes theorem draft, not a public release decision.
- It is not a general predictor.
- It is not a B8 theorem.
- It is not an asymptotic law.
- It does not claim coverage, recall, or holdout validation for B8.
- It does not explain all future residual dynamics; it fixes the public-safe
  v2.5 theorem boundary for Gate P review.
