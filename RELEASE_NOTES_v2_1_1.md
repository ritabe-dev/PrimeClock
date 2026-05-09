# PRC Finite Theorem Bundle v2.1.1 Release Notes

Release date: 2026-05-09 JST

## Purpose

This release preserves the narrow `C_k/C_4/B_5` finite theorem package after
GitHub-Zenodo preservation was enabled for `ritabe-dev/PrimeClock`.

The mathematical content is the same narrow finite certificate artifact as
v2.1.0: it is a finite Prime Reciprocal Covering certificate bundle, not the
full historical PRC archive.

## DOI

The archived v2.1.1 release DOI is:

```text
10.5281/zenodo.20091723
```

## Included

- `prc_finite_certificate_note_v2_0.md`, the theorem note centered on:
  - the prime-prefix residue-covering filtration `C_k`;
  - closed-arc endpoint convention;
  - lift monotonicity, density monotonicity, and reflection symmetry;
  - `C_4={2,208} mod 210`;
  - the `B_5` birth layer with 14 births in 7 reflection pairs;
  - the CSV/checker certificate architecture.
- `claims_finite_c4_b5.md`, the narrow claim registry for this release.
- `VERIFY_FINITE_C4_B5.md`, the verifier contract.
- `CITATION.cff`, pointing at the public GitHub repository, v2.1.1 release URL,
  and Zenodo DOI.
- `LICENSE`, using the MIT License.
- Existing public finite-theorem CSVs through the v1.8 standalone verification
  output.

## Not Included

- No `B_6` export or classification.
- No new `k=8` or complete-covering analysis.
- No certificate-depth, modulo-210, branch-uniform, or residual-fragmentation
  diagnostics.
- No arXiv submission.
- No broad related-work rewrite.
- No claim of a new prime-distribution theorem or asymptotic law.

## Expected Verification Results

From `research/`:

```text
focused pytest: 39 passed
package verifier: checks=14, failed=0
standalone checker: checks=9, failed=0
```

The full source repository validation at release-prep time passed:

```text
ruff: pass
full pytest: 193 passed
npm run build: pass
```

## Difference from v2.1.0

v2.1.1 keeps the same finite theorem scope and public CSV artifacts as v2.1.0,
but is issued after enabling Zenodo preservation for the public GitHub
repository so that Zenodo can archive the release and mint a DOI.
