# Public Release Manifest

Use this manifest when preparing the public release bundle for the finite
`C_k/C_4/B_5` certificate artifact.

## Release Bundle

The public bundle should contain only the files needed to read, verify, and
cite the finite certificate artifact.

Root files:

- `README.md`
- `LICENSE`
- `CITATION.cff`
- `DATA_FILES.md`
- `SHA256SUMS`
- `VERSION_MAP.md`
- `VERIFY.md`
- `RELEASE_NOTES_v2_2.md`
- `.github/workflows/verify.yml`
- `scripts/build_public_release.py`
- `scripts/check_public_release.py`
- `scripts/update_public_hashes.py`

Research files:

- `research/README.md`
- `research/PUBLIC_RELEASE_MANIFEST.md`
- `research/RELEASE_NOTES_v2_2.md`
- `research/VERIFY_FINITE_C4_B5.md`
- `research/pyproject.toml`
- `research/setup.py`
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

## Excluded From The Public Bundle

Keep these in the full source repository, but do not include them in the public
finite certificate bundle:

- broad `research/notes/claims.md`;
- older finite-note drafts and theme notes;
- certificate-depth notes and CSVs;
- `k=8`, modulo-210, C0, branch-fill, branch-uniform, and residual-fragmentation diagnostics;
- PrimeClock React/Vite visualization files;
- historical local release bundles and archives.

The Python source package is included as verifier/test support and may contain
broader implementation modules. The public release-facing notes, CSVs, and
claims remain restricted to the finite `C_k/C_4/B_5` certificate artifact.
`SHA256SUMS` records hashes for the public release allowlist, and
`VERSION_MAP.md` records the release, package, note, table, and verifier
version correspondence.

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
- generated local zip/tar archives

## Entry Point

For the finite theorem artifact, start with:

```text
README.md
research/notes/prc_finite_certificate_note_v2_0.md
research/notes/claims_finite_c4_b5.md
research/VERIFY_FINITE_C4_B5.md
research/notes/known-results.md
```

The package should be read as a finite experimental-mathematics certificate
artifact. Broader asymptotic, distributional, and complete PRC questions are
outside the v2.2.0 release scope.
