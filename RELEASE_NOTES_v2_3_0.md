# PrimeClock / PRC v2.3.0 Release Notes

Version DOI: `10.5281/zenodo.20119473`
Concept DOI: `10.5281/zenodo.20091722`.

## Summary

This release promotes the v2.3 Prime Reciprocal Covering critical-radius and
birth-dynamics candidate to a public finite artifact. It keeps the v2.2.4
`C_4/B_5` certificate line intact and adds the checked v2.3 finite mechanism:
critical-radius spectra for `k=4,5`, gap-aperture birth dynamics for
`B_5/B_6/B_7`, and near-miss diagnostics for `k=4,5`.

## Public Claims

- `C_k` is the `1/2` level set of the exact critical-radius spectrum for the
  checked `k=4,5` layers.
- `C_4 = {2, 208}` modulo `210`.
- `C_5` has `36` covered residues.
- `B_5`, `B_6`, and `B_7` are unique strict single-gap births in the checked
  finite data.
- Near-miss rank is a diagnostic candidate generator; birth also depends on
  next-prime `q`-grid phase alignment through the gap-aperture window.

## Verification

The release includes exact rational CSV artifacts, helper verification, a
standard-library standalone audit, and focused pytest coverage for the v2.3
finite candidate.

Expected v2.3 checker summaries:

```text
check_v2_3_candidate: checks=13, failed=0
check_v2_3_candidate_standalone: checks=10, failed=0
```

## Non-Claims

This release does not claim a general theorem that all future births are
single-gap births. It does not include `B_8` or larger layers, asymptotic laws,
prime-distribution claims, null models, or residual-gap transition graphs.

## Scope Boundary

The v2.4 residual-gap transition graph idea and the no-multi-gap birth note
remain tracked internal future work and are not included in this public release
bundle.

Future work includes larger-layer spectra, static spectrum and gap-aperture
visual summaries, residual-gap transition graphs, null models, and broader
paper-preparation notes. These are not part of v2.3.0.
