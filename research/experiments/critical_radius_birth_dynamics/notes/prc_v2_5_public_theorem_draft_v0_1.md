# PRC v2.5 Public Theorem Draft

Status: Gate P theorem-preparation draft for scoped public theorem review.
This draft is not a release and does not authorize a GitHub Release, Zenodo
upload, DOI, or public B8 claim.

## Definitions

- `PRC prime-prefix residual-covering model`: the exact rational interval model
  used in the v2.5 candidate bundle to track residual sets under successive
  prime-prefix transition scopes.
- `Residual set R_k(r)`: the uncovered circular subset associated with a
  residue family after the recorded prefix through layer k.
- `U_{4->5}`, `U_{5->6}`, `U_{6->7}`: the finite row universes recorded for
  the complete checked transition scopes `B4->B5`, `B5->B6`, and `B6->B7`.
  Their union is the only universe used by the theorem draft.
- `row`: one recorded lift row in one of the finite universes.
- `Close(row)`: the row has empty child residual set after the next-prime arc.
- `Capacity(row)`: the row belongs to a capacity-admissible parent family in
  the recorded family audit.
- `NonClose(row)`: the row is checked and not close.
- `m(row)`: the exact signed aperture-orbit margin, computed as the signed
  rational containment margin between the parent residual aperture and the
  next-prime orbit arc in the checked row. Positive margin is used here as a
  terminal containment certificate, not a general predictor from prefix history
  alone.
- `Exact-hull obstruction`: the checked condition that a multi-component parent
  residual set has a circular hull too wide for a single next-prime arc to close
  all components at once.

## Finite Universe

The theorem draft is limited to the recorded complete transition scopes:

- `B4->B5`
- `B5->B6`
- `B6->B7`

The finite universe is `U = U_{4->5} union U_{5->6} union U_{6->7}`. It is
materialized by the public theorem review bundle as the recorded phase-gate
family audit, lift diagnostic audit, exact-hull family audit, and compact
public theorem summary table.

No `B8` full graph, unbounded layer family, asymptotic regime, or prime
distribution law is part of this theorem draft.

## Theorem

PRC v2.5 finite exact aperture-orbit separator theorem.

For the recorded complete transition scopes `B4->B5`, `B5->B6`, and `B6->B7`
under the PRC prime-prefix residual-covering model, positive signed
aperture-orbit margin exactly separates checked close rows from checked
non-close rows.

In predicate form, for every `row in U`:

- Primary separator: `Close(row) iff m(row) > 0`.
- Capacity comparison corollary: `Capacity(row) and NonClose(row) => m(row) <= 0`.

Equivalently, within these checked finite scopes, the signed aperture-orbit
margin is a finite exact terminal containment certificate. Capacity alone is not
a separator; it is retained as a false-positive comparison. This is not a
general predictor.

## Exhaustive Enumeration Certificate

The theorem is finite and audit-based. The enumeration certificate consists of:

- the committed phase-gate family and lift diagnostic CSV files for the
  recorded complete transition scopes;
- the exact-hull family audit and compact public theorem summary table;
- exact rational arithmetic in the helper and checker scripts;
- manifest-bound files in the v2.5 candidate bundle;
- checker assertions that audit row-level separator counts against the committed
  finite certificate artifacts.

The public claim, if later authorized, should state this as an exact finite
enumeration certificate rather than as a proof over all future layers.

The public theorem review checker does not independently regenerate the full PRC
transition universe from first principles. It audits the committed finite
certificate artifacts for the recorded scopes.

## Separator Audit

The separator audit fixes the following headline counts:

| Scope | Families | Lift rows | Close rows | Capacity non-close families | Capacity non-close lift rows | Non-close positive margin rows |
| --- | ---: | ---: | ---: | ---: |
| `B4->B5` | 208 | 2,288 | 14 | 14 | 294 | 0 |
| `B5->B6` | 2,274 | 29,562 | 42 | 182 | 2,870 | 0 |
| `B6->B7` | 29,520 | 501,840 | 714 | 2,234 | 49,402 | 0 |
| Total | 32,002 | 533,690 | 770 | 2,430 | 52,566 | 0 |

All 770 close rows are birth rows in these scopes. The finite theorem draft
depends on the row-level audit `Close(row) iff m(row) > 0`, the zero count in
the final column, and the capacity false-positive comparison.

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
python3 scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/public_theorem_workflow_v2_5_v0_1.yml \
  public-theorem-review
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
