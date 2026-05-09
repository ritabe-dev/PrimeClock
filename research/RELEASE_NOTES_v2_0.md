# PRC Finite Theorem Bundle v2.0 Release Notes

Release date: 2026-05-09 JST

## Purpose

This release prepares the `C_k/C_4/B_5` finite theorem package for external
review, citation, and later archival release. It is a narrow finite-certificate
bundle, not the full historical PRC archive.

## Included

- `prc_finite_certificate_note_v2_0.md`, a short theorem note centered on:
  - the prime-prefix residue-covering filtration `C_k`;
  - closed-arc endpoint convention;
  - lift monotonicity, density monotonicity, and reflection symmetry;
  - `C_4={2,208} mod 210`;
  - the `B_5` birth layer with 14 births in 7 reflection pairs;
  - the CSV/checker certificate architecture.
- `claims_finite_c4_b5.md`, the narrow claim registry for this release.
- `VERIFY_FINITE_C4_B5.md`, the verifier contract.
- `CITATION.cff`, a DOI-free citation metadata file for the local release.
- `LICENSE`, using the MIT License for the software and accompanying
  documentation in the release bundle.
- Existing public finite-theorem CSVs through the v1.8 standalone verification
  output.

## Not Included

- No `B_6` export or classification.
- No new `k=8` or complete-covering analysis.
- No GitHub release, Zenodo DOI registration, or arXiv submission.
- No broad related-work rewrite.
- No claim of a new prime-distribution theorem or asymptotic law.

## Expected Verification Results

From `research/`:

```text
focused pytest: 39 passed
package verifier: checks=14, failed=0
standalone checker: checks=9, failed=0
```

The full source repository validation at release-prep time should also pass:

```text
ruff: pass
full pytest: 193 passed
npm run build: pass
```

## Difference from v1.10

v2.0 turns the same finite certificate material into a release-ready bundle by
adding a standalone theorem note, citation metadata, and release notes while
keeping the mathematical scope unchanged.

## v2.1 Packaging Cleanup

The v2.1 bundle keeps the same mathematical scope and finite CSV artifacts as
v2.0, but tightens the release package:

- adds `LICENSE`;
- points the root and research README files at the narrow `C_k/C_4/B_5`
  artifact first;
- removes older v1.1 and historical theme notes from the sendable zip;
- keeps certificate-depth, `k=8`, modulo-210, branch-uniform, and
  residual-fragmentation material in the full repository only.
