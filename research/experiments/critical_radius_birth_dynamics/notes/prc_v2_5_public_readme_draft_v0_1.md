# PRC v2.5 Public README Draft

Status: Gate P public-facing README draft. This document is a draft for scoped
public theorem review only. It does not authorize a public release.

## What Is Proved

PRC v2.5 is framed as a finite exact aperture-orbit separator theorem for the
recorded complete transition scopes `B4->B5`, `B5->B6`, and `B6->B7`.

In those checked finite scopes, capacity alone leaves many false positives, but
positive signed aperture-orbit margin exactly separates checked close lifts from
capacity-admissible non-close controls. The margin is a terminal containment
certificate, not a general predictor.

The support lemma is that checked multi-component parent residual sets are
exact-hull obstructed, and every checked close row has a single-gap precursor.

## What Is Not Proved

- no B8 theorem
- no B8 full graph
- no asymptotic law
- no general predictor
- no coverage, recall, or holdout validation for B8
- no prime distribution theorem
- no claim that the separator automatically extends beyond the recorded
  complete transition scopes

B8 selected stress-control only. The B8 selected rows remain appendix or
stress-control material and are not part of the theorem.

## Exact Counts

| Metric | Count |
| --- | ---: |
| Historical close or birth rows | 770 |
| Capacity non-close families | 2,430 |
| Non-close positive-margin rows | 0 |
| `B4->B5` exact-hull obstructed multi-component families | 65 |
| `B5->B6` exact-hull obstructed multi-component families | 913 |
| `B6->B7` exact-hull obstructed multi-component families | 13,785 |
| B8 selected close rows | 32 |
| B8 sibling non-birth controls | 576 |
| B8 matched non-birth controls | 64 |

The B8 counts are stress-control diagnostics only.

## How To Reproduce

Install the research package from the repository root:

```bash
cd research
python -m pip install -e .
cd ..
```

Run the reviewer-facing checks:

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

## Limitations

The result is a finite exact signed containment certificate for checked scopes.
It is intentionally narrower than a predictive theory. The public-safe theorem
does not use B8 as coverage evidence and does not make claims about all future
layers.
