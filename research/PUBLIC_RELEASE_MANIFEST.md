# Public Release Manifest

Use this manifest when preparing the public release bundle for the finite
`C_k/C_4/B_5` certificate artifact.

## Stable Public Claim

The stable public claim for the current release line is limited to the finite
`C_k/C_4/B_5` certificate artifact. In particular:

- `C_4 = {2, 208} mod 210`;
- `C_5` has 36 covered residues;
- `B_5` has 14 births in 7 reflection pairs;
- the public package contains exact CSV certificates plus package and
  standalone verification paths.

Any newer research line remains experimental until it has its own release
manifest, verification path, non-claims section, hash manifest, and release
approval.

## Included

The public bundle should contain only the files needed to read, verify, and
cite the finite certificate artifact.

Root files:

- `README.md` (generated from `release/public/README.template.md`)
- `LICENSE`
- `CITATION.cff`
- `DATA_FILES.md`
- `SHA256SUMS`
- `VERSION_MAP.md`
- `VERIFY.md`
- `RELEASE_NOTES_v2_2_3.md`
- `.github/workflows/verify.yml`
- `release/public/README.template.md`
- `release/public/release_config.json`
- `scripts/build_public_release.py`
- `scripts/check_public_release.py`
- `scripts/check_release_versions.py`
- `scripts/release_config.py`
- `scripts/update_public_hashes.py`
- `scripts/verify_public_release.py`

Research files:

- `research/README.md`
- `research/PUBLIC_RELEASE_MANIFEST.md`
- `research/RELEASE_NOTES_v2_2_3.md`
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

## Excluded

Keep these in the full source repository, but do not include them in the public
finite certificate bundle:

- broad `research/notes/claims.md`;
- older finite-note drafts and theme notes;
- certificate-depth notes and CSVs;
- `k=8`, modulo-210, C0, branch-fill, branch-uniform, and residual-fragmentation diagnostics;
- PrimeClock React/Vite visualization files;
- historical local release bundles and archives.
- `research/experiments/critical_radius_birth_dynamics/`, including its
  critical-radius and birth-dynamics candidate artifacts, until explicitly
  promoted through a future public release manifest.

The Python source package is included as verifier/test support and may contain
broader implementation modules. The public release-facing notes, CSVs, and
claims remain restricted to the finite `C_k/C_4/B_5` certificate artifact.
`release/public/release_config.json` is the release-version source of truth.
`SHA256SUMS` records hashes for the public release allowlist, and
`VERSION_MAP.md` records the release, package, note, table, and verifier
version correspondence.

The source repository root `README.md` is not copied into the public bundle.
The bundle root `README.md` is generated from
`release/public/README.template.md` to keep source-repository wording separate
from public release wording.

## Experimental/Internal

Experimental or internal-candidate work can live in the source repository, but
must not enter the stable public release bundle until promoted. This includes:

- critical-radius spectrum drafts;
- birth-dynamics candidate artifacts beyond the stable `C_4/B_5` certificate;
- fragmentation, p-adic, branch-fill, residual, and null-model diagnostics;
- candidate bundles and candidate bundle manifests;
- informal research selection notes or pasted review material.

Research notes under `research/notes/` or `research/experiments/` should carry a
clear status line such as `Status: stable`, `Status: experimental`,
`Status: internal-candidate`, or `Status: historical`.

## Never Include

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
- `review_packages/`
- `scratch/`
- `private_notes/`
- `local_notes/`
- candidate bundle directories or archives
- generated local zip/tar archives

GitHub Release and Zenodo uploads should use only a bundle that passes
`scripts/verify_public_release.py`.

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
outside the v2.2.3 release scope.
