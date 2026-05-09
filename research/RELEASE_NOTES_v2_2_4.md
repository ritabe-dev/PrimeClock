# PRC Finite Theorem Bundle v2.2.4 Release Notes

Release date: 2026-05-09 JST

Version DOI: pending Zenodo publication for the GitHub `v2.2.4` release.

Concept DOI: `10.5281/zenodo.20091722`

## Purpose

This release contains the narrow `C_k/C_4/B_5` finite certificate artifact for
Prime Reciprocal Covering. It is a release bundle for the finite theorem note,
CSV certificates, package verifier, and standard-library standalone checker.

This is a public hygiene patch release. It does not add new mathematical data or
new finite claims.

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

## Changes Since v2.2.3

- public release versioning remains config-driven through
  `release/public/release_config.json`;
- the public bundle README template is included in the generated bundle;
- focused pytest expected count is updated to `46 passed`;
- release guardrails reject private notes, local scratch paths, internal
  experiment paths, and candidate bundle artifacts;
- citation metadata is prepared for a v2.2.4 version DOI after Zenodo
  publication;
- README and version map clarify that the Python package keeps the historical
  `prime-reciprocal-projection` name while the finite theorem bundle is framed
  as Prime Reciprocal Covering.

## Not Included

- No `B_6` export or classification.
- No new `k=8` or complete-covering analysis.
- No v2.3 critical-radius or birth-dynamics candidate artifacts.
- No certificate-depth, modulo-210, branch-uniform, or residual-fragmentation
  diagnostics.
- No arXiv submission.
- No broad related-work rewrite.
- No broader asymptotic, distributional, or complete PRC claim.

## Expected Verification Results

From `research/`:

```text
focused pytest: 46 passed
package verifier: checks=14, failed=0
standalone checker: checks=9, failed=0
```
