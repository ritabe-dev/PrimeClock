# PRC Finite Theorem Bundle v2.2.1 Release Notes

Release date: 2026-05-09 JST

Version DOI: `10.5281/zenodo.20092329`

Concept DOI: `10.5281/zenodo.20091722`

## Purpose

This release contains the narrow `C_k/C_4/B_5` finite certificate artifact for
Prime Reciprocal Covering. It is a release bundle for the finite theorem note,
CSV certificates, package verifier, and standard-library standalone checker.
The historical PrimeClock React/Vite visualization remains in the source
repository as origin context and is not included in this release bundle.

## Included

- `prc_finite_certificate_note_v2_0.md`, the theorem note centered on:
  - the prime-prefix residue-covering filtration `C_k`;
  - closed-arc endpoint convention;
  - lift monotonicity, density monotonicity, and reflection symmetry;
  - `C_4={2,208} mod 210`;
  - the `B_5` birth layer with 14 births in 7 reflection pairs;
  - the CSV/checker certificate architecture.
- `claims_finite_c4_b5.md`, the narrow claim registry.
- `VERIFY_FINITE_C4_B5.md`, the verifier contract.
- Existing public finite-theorem CSVs through the v1.8 standalone verification
  output.
- `SHA256SUMS`, `VERSION_MAP.md`, and the GitHub Actions verification workflow
  in the release root.

## Not Included

- No `B_6` export or classification.
- No new `k=8` or complete-covering analysis.
- No certificate-depth, modulo-210, branch-uniform, or residual-fragmentation
  diagnostics.
- No arXiv submission.
- No broad related-work rewrite.
- No broader asymptotic, distributional, or complete PRC claim.

## Expected Verification Results

From `research/`:

```text
focused pytest: 41 passed
package verifier: checks=14, failed=0
standalone checker: checks=9, failed=0
```
