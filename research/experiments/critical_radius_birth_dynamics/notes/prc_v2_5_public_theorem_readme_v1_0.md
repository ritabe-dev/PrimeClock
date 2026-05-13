# PRC v2.5: Finite Aperture-Orbit Separator Theorem

Status: prepared public theorem README text, pending explicit release execution.
This file does not create a tag, GitHub Release, Zenodo upload, DOI, or public
B8 claim.

## What Is Proved

PRC v2.5 proves a finite exact aperture-orbit separator theorem for the recorded
complete transition scopes:

```text
B4->B5
B5->B6
B6->B7
```

Let `U` be the materialized finite universe of committed checked rows in these
three scopes.  For every committed checked row in `U`:

```text
Close(row) iff m(row) > 0
```

Here `m(row)` is the exact signed aperture-orbit containment margin.  It is a
terminal containment certificate for the checked finite rows, not a general
predictor from prefix history alone.

Capacity is retained as a false-positive comparison: capacity admits many
non-close rows, while positive signed margin separates the checked close rows
from checked non-close rows in `U`.

## Exact Counts

| Metric | Count |
| --- | ---: |
| Checked lift rows | 533,690 |
| Close rows | 770 |
| Birth rows | 770 |
| Positive-margin rows | 770 |
| Non-close rows | 532,920 |
| Non-close positive-margin rows | 0 |
| Capacity non-close lift rows | 52,566 |
| Capacity non-close positive-margin lift rows | 0 |
| Endpoint-touch rows | 0 |
| Minimum close positive margin | `1/221` |
| Maximum non-close margin | `-1/221` |

All close rows are birth rows in these checked scopes.

## How To Verify

From the repository root:

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_5_public_theorem_integrity.py
```

Expected result:

```text
check_v2_5_public_theorem_integrity: checks=9, failed=0
```

The verifier audits the committed finite certificate artifacts.  It does not
independently regenerate the full PRC transition universe from first principles.

## What Is Not Proved

- no B8 theorem;
- no B8 full graph;
- no general predictor;
- no asymptotic law;
- no coverage, recall, or holdout validation for B8;
- no automatic extension beyond `B4->B5`, `B5->B6`, and `B6->B7`.

## Citation

Do not cite a Zenodo DOI for this v2.5 theorem until a Zenodo archive exists.
Use the repository tag and GitHub Release metadata once a release is explicitly
created.
