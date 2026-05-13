# PRC v2.5 Reviewer Glossary

Status: candidate-included reviewer aid for Gate P dry-run. This note does not
authorize a public release.

## Terms

- `capacity`: the new prime arc is wide enough to cover a checked single
  residual component. Capacity is necessary in the checked close rows, but it
  leaves many false positives.
- `phase margin`: the exact signed containment margin between the old residual
  component and the new prime arc. Positive margin is treated as a finite exact
  signed containment certificate in checked transition rows, not as an
  independent general predictor.
- `aperture tension`: the same final alignment geometry recorded from the
  aperture-orbit selection viewpoint. It should not be read as an independent
  feature from phase margin.
- `close`: the residual set is empty after adding the new prime arc.
- `birth`: a history event where the parent residue was not covered before the
  new prime layer and the child residue is covered after it.
- `near-miss`: a sibling lift or matched control that remains non-close while
  staying close enough to compare against a close row.
- `source-only`: excluded from public release artifacts.
- `candidate-included`: included in this internal v2.5 candidate bundle for
  review and reproducibility.
- `stress control`: selected diagnostic evidence used to challenge the checked
  mechanism. It is not coverage, recall, holdout validation, or a public theorem.

## Obstruction Buckets

- `sibling_dominated`: a non-close sibling loses within a family where a
  different sibling is the close or stronger phase-rank lift.
- `split_history`: prefix residual dynamics produce a component history that
  remains non-close in the checked row.
- `underreach`: the final arc is aligned in the relevant aperture direction but
  the signed containment margin remains non-positive.
- `wrong_side`: the final arc is on the wrong side of the residual component
  aperture in the checked geometry.

These buckets are operational finite diagnostics. They summarize checked
failure modes and do not claim a layer-general causal taxonomy.
