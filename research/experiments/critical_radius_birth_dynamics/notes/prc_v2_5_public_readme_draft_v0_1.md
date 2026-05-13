# PRC v2.5 Public README Draft

Status: Gate P public-facing README draft. This document is a draft for scoped public theorem review; not a release.

## What Is Proved

PRC v2.5 is framed as a finite exact aperture-orbit separator theorem for the
recorded complete transition scopes `B4->B5`, `B5->B6`, and `B6->B7`.

In those checked finite scopes, positive signed aperture-orbit margin exactly
separates checked close rows from checked non-close rows. Capacity alone leaves
many false positives, so capacity is reported as a comparison rather than as the
theorem's universe. The margin is a terminal containment certificate, not a
general predictor.

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
| Checked lift rows | 533,690 |
| Close rows | 770 |
| Birth rows | 770 |
| Positive-margin rows | 770 |
| Non-close rows | 532,920 |
| Non-close positive-margin rows | 0 |
| Capacity non-close families | 2,430 |
| Capacity non-close lift rows | 52,566 |
| Capacity non-close positive-margin lift rows | 0 |
| Endpoint-touch rows | 0 |
| Minimum close positive margin | `1/221` |
| Maximum non-close margin | `-1/221` |
| `B4->B5` exact-hull obstructed multi-component families | 65 |
| `B5->B6` exact-hull obstructed multi-component families | 913 |
| `B6->B7` exact-hull obstructed multi-component families | 13,785 |

All 770 close rows are birth rows in these scopes.

B8 stress-control counts are intentionally not included in this public theorem
review bundle.

## How To Reproduce

This bundle is not the full research Python package. Its shortest ZIP-standalone
review path audits the committed finite certificate artifacts without installing
the research package:

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_5_public_theorem_integrity.py
```

`PyYAML` is not needed for the ZIP-standalone audit above. It is needed only for
the optional workflow wrapper:

```bash
python3 -m pip install PyYAML
```

```bash
python3 scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/public_theorem_workflow_v2_5_v0_1.yml \
  public-theorem-review
```

## Limitations

The result is a finite exact signed containment certificate for checked scopes.
It is intentionally narrower than a predictive theory. The public-safe theorem
does not use B8 as coverage evidence and does not make claims about all future
layers.

This audit does not independently regenerate the full PRC transition universe
from first principles.
