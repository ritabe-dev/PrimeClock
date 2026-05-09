# PRC Finite Theorem Bundle v2.2.0 Release Notes

Release date: 2026-05-09 JST

## Purpose

This release publishes a clean-history public bundle for the narrow
`C_k/C_4/B_5` finite certificate artifact.

The mathematical content is the same finite Prime Reciprocal Covering
certificate artifact prepared in v2.1, but the public repository history and
release archive have been rebuilt from a clean tree.

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
- `DATA_FILES.md`, a compact guide to the finite certificate CSVs.
- `CITATION.cff`, pointing at the public GitHub repository and v2.2.0 release
  URL.
- `LICENSE`, using the MIT License.
- Existing public finite-theorem CSVs through the v1.8 standalone verification
  output.

## Not Included

- No `B_6` export or classification.
- No new `k=8` or complete-covering analysis.
- No certificate-depth, modulo-210, branch-uniform, or residual-fragmentation
  diagnostics.
- No PrimeClock React/Vite visualization files.
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

## Difference from v2.1.1

v2.2.0 keeps the same finite theorem scope and public CSV artifacts as v2.1.1,
but removes internal auxiliary files and rebuilds the public repository history
from a clean root commit.
