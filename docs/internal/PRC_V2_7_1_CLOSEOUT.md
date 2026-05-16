# PRC v2.7.1 Closeout

Status: closed public theorem release. Future mathematical changes, claim
extensions, or new release metadata belong to v2.8 or later.

## Release Record

| Field | Value |
| --- | --- |
| Release id | `v2.7.1-prc-general-q-prime-theorem` |
| Tag | `v2.7.1-prc-general-q-prime-theorem` |
| Title | `PRC v2.7.1: General q-Prime Single-Gap Aperture Classification Theorem` |
| Zenodo version DOI | `10.5281/zenodo.20209528` |
| GitHub Release | `https://github.com/ritabe-dev/PrimeClock/releases/tag/v2.7.1-prc-general-q-prime-theorem` |
| Release asset | `PrimeClock-v2.7.1-general-q-prime-theorem-v1.0.zip` |
| Release asset SHA256 | `6ba8e6b3ee8ab84eecdc8568613e6d06e0ab9cecfe4788ac647ab65dce2c974d` |
| Registry source | `release/public/release_registry.json` |
| Public theorem workflow | `research/experiments/critical_radius_birth_dynamics/public_theorem_release_workflow_v2_7_v1_0.yml` |
| Bundle profile | `v2_7_public_theorem_release` |

## Public Surface State

`README.md` and `VERSION_MAP.md` are rendered from the registry and identify
v2.7.1 as the current public theorem release and the latest DOI-backed public
theorem release. The top-level `CITATION.cff` remains the legacy v2.3 citation
metadata; v2.7.1 citation metadata lives in the release bundle and release
notes.

The v2.7.1 theorem remains scoped to the PRC circular-arc model. It does not
claim a B8 theorem, a full transition-graph theorem, a general predictor, an
asymptotic law, a prime-gap theorem outside the PRC model, or a full
finite-universe completeness audit.

## Paper Review Package

The v2.7.1 paper/reviewer materials are tracked under `paper/` and can be
bundled with profile `v2_7_1_paper_review`. They are reviewer-facing reading
materials only; they do not replace the DOI-backed public theorem release ZIP.

The checked pre-upload package SHA256 after SVG clipping fixes was:

```text
116d30ea00984e43f2013c62fd022101023f80f3bd7f2e76d028a11f30662c7a
```

## Branch State

Keep:

- `main`: repository source of truth and public README surface.
- `public/v2.7.1-prc-general-q-prime-theorem`: clean artifact branch for the
  v2.7.1 public source archive.

Delete after verification:

- `release/v2.7-public-surface`: completed work branch that has been merged into
  `main` and is no longer the source of truth.

Do not use worker- or tool-branded branch names for public release work. Use
human-readable branch families such as `release/`, `public/`, `maintenance/`,
or `research/`.

## Closeout Verification

Run before starting v2.8 work:

```bash
python3 scripts/render_public_surface.py --check
python3 scripts/check_release_doi_integrity.py --all
python3 scripts/verify_public_release_execution_preflight.py --all
python3 scripts/update_public_hashes.py --check
python3 research/experiments/critical_radius_birth_dynamics/check_v2_7_public_theorem_release.py
python3 research/experiments/critical_radius_birth_dynamics/check_v2_7_1_paper_review_package.py
```

