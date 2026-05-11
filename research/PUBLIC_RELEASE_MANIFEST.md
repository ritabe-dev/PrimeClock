# Public Release Manifest

Use this manifest when preparing the public release bundle for the v2.3.0
finite PRC critical-radius and gap-aperture birth-dynamics artifact.

## Stable Public Claim

The stable public claim for the current release line is limited to finite,
checked PRC statements. In particular:

- `C_4 = {2, 208} mod 210`;
- `C_5` has 36 covered residues;
- `C_k` is the `1/2` level set of the exact critical-radius spectrum for the
  checked `k=4,5` layers;
- `B_5`, `B_6`, and `B_7` are unique strict single-gap births in the checked
  finite data;
- near-miss rank is a diagnostic candidate generator, while birth depends on
  next-prime `q`-grid phase alignment through the gap-aperture window.

The package contains exact CSV certificates plus helper, standalone, and focused
pytest verification paths.

## Included

The public bundle should contain only the files needed to read, verify, and cite
the finite v2.3.0 artifact.

Root files include:

- `README.md` generated from `release/public/README.template.md`
- `LICENSE`
- `CITATION.cff`
- `DATA_FILES.md`
- `ERRATA.md`
- `SHA256SUMS`
- `VERSION_MAP.md`
- `VERIFY.md`
- `RELEASE_NOTES_v2_3_0.md`
- `.github/workflows/verify.yml`
- `release/public/MAINTENANCE_POLICY.md`
- public release scripts under `scripts/`
- `release/public/release_config.json`

Research files include:

- `research/README.md`
- `research/PUBLIC_RELEASE_MANIFEST.md`
- `research/RELEASE_NOTES_v2_3_0.md`
- `research/VERIFY_FINITE_C4_B5.md`
- `research/tests/test_covering_prime_prefix_filtration.py`
- `research/tests/test_critical_radius_birth_dynamics_public.py`
- `research/certificates/check_prime_prefix_c4_b5.py`
- `research/notes/prc_finite_certificate_note_v2_0.md`
- `research/notes/claims_finite_c4_b5.md`
- `research/notes/known-results.md`
- selected `research/experiments/critical_radius_birth_dynamics/` checker,
  data, and public-facing theorem/related-work notes

The Python source package is included as verifier/test support.

## Excluded

Keep these in the full source repository, but do not include them in the public
v2.3.0 release bundle:

- candidate bundle builders and candidate bundle manifests;
- candidate workflow configs and promotion-readiness reports;
- v2.4 residual-gap transition graph notes;
- no-multi-gap future-work notes;
- null-model, active-prime taxonomy expansion, and `B_8` or larger exploratory
  work;
- PrimeClock React/Vite visualization files;
- historical local release bundles and archives.

The source repository root `README.md` is not copied into the public bundle.
The bundle root `README.md` is generated from
`release/public/README.template.md` to keep source-repository wording separate
from public release wording.

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
Use `release/public/PUBLISH_CHECKLIST.md` for the two-stage GitHub release and
Zenodo DOI metadata workflow.
Use `release/public/MAINTENANCE_POLICY.md` and `ERRATA.md` when a past release
line needs clarification or correction while later research is active.
Zenodo uploads are allowed only when
`release/public/release_config.json` sets `release_kind` to `doi_release`.
The release config DOI policy is
`concept_doi_in_citation_version_doi_in_release_notes`: `CITATION.cff` keeps the
Zenodo concept DOI as the top-level DOI, while version DOIs are recorded in
release notes, `VERSION_MAP.md`, and GitHub Release text for DOI releases.

## Entry Point

For the v2.3.0 finite artifact, start with:

```text
README.md
research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_theorem_note_draft_v0_1.md
research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_related_work_v0_2.md
VERIFY.md
DATA_FILES.md
VERSION_MAP.md
```

The package should be read as a finite experimental-mathematics certificate
artifact. Broader asymptotic, distributional, and complete PRC questions are
outside the v2.3.0 release scope.
