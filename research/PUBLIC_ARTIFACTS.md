# Public Artifact Manifest

Use this manifest when preparing the narrow external package for the finite
`C_k/C_4/B_5` theorem track.

## Release-Ready Finite Bundle

The current sendable package should contain only the files needed to read,
verify, and cite the `C_4/B_5` finite certificate artifact.

Root files:

- `README.md`
- `LICENSE`
- `CITATION.cff`
- `CSV_SUMMARY.md`
- `PROMPT.md`
- `RELEASE_NOTES_v2_1.md`
- `VERIFY.md`

Research files:

- `research/README.md`
- `research/PUBLIC_ARTIFACTS.md`
- `research/RELEASE_NOTES_v2_1.md`
- `research/VERIFY_FINITE_C4_B5.md`
- `research/pyproject.toml`
- `research/uv.lock`
- `research/src/prime_reciprocal_projection/`
- `research/tests/test_covering_prime_prefix_filtration.py`
- `research/certificates/check_prime_prefix_c4_b5.py`
- `research/notes/prc_finite_certificate_note_v2_0.md`
- `research/notes/claims_finite_c4_b5.md`
- `research/notes/known-results.md`

Finite certificate CSVs:

- `research/data/summaries/prc_prime_prefix_residue_covering_filtration_v0_1.csv`
- `research/data/summaries/prc_prime_prefix_residue_covering_birth_samples_v0_1.csv`
- `research/data/summaries/prc_prime_prefix_ck_full_v1_1.csv`
- `research/data/summaries/prc_prime_prefix_c4_exclusion_witness_v1_6.csv`
- `research/data/summaries/prc_prime_prefix_c4_exclusion_summary_v1_5.csv`
- `research/data/summaries/prc_prime_prefix_birth_witness_v1_5.csv`
- `research/data/summaries/prc_prime_prefix_b5_birth_classification_v1_5.csv`
- `research/data/summaries/prc_prime_prefix_b5_birth_pair_summary_v1_5.csv`
- `research/data/summaries/prc_prime_prefix_certificate_verification_v1_7.csv`
- `research/data/summaries/prc_prime_prefix_certificate_standalone_verification_v1_8.csv`

## Excluded From The Narrow Bundle

Keep these in the full repository, but do not include them in the finite
theorem review/release zip unless a reviewer explicitly asks for broader
context:

- broad `research/notes/claims.md`;
- older `research/notes/prc_prime_prefix_finite_note_v1_1.md`;
- historical `research/notes/prc_mathematical_theme_prime_prefix_filtration_v0_1.md`;
- certificate-depth notes and CSVs;
- `k=8`, modulo-210, C0, branch-fill, branch-uniform, and residual-fragmentation diagnostics;
- PrimeClock React/Vite visualization files;
- `review_packages/` snapshots.

## Excluded Local Files

Never include:

- `.git/`
- `.venv/`
- `node_modules/`
- `.uv-cache/`
- `.pytest_cache/`
- `.ruff_cache/`
- `.matplotlib-cache/`
- `dist/`
- `__pycache__/`
- `.DS_Store`
- generated local zip/tar archives from older review packages

## Review Entry Point

For a finite-theorem review, start with:

```text
README.md
research/notes/prc_finite_certificate_note_v2_0.md
research/notes/claims_finite_c4_b5.md
research/VERIFY_FINITE_C4_B5.md
research/notes/known-results.md
```

The package should be read as a finite experimental-mathematics certificate
artifact. It does not claim a new theorem about prime distribution, a law for
complete covering, or an asymptotic law for `|C_k|/M_k`.
