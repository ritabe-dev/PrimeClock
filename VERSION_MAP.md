# Version Map

This repository keeps release, package, note, table, verifier, and DOI metadata
versions separate. Multi-version release metadata is tracked in
`release/public/release_registry.json`.

<!-- BEGIN GENERATED PUBLIC SURFACE -->
## Current Public Releases

| Item | Version / file |
| --- | --- |
| Current public theorem release | `v2.7.1-prc-general-q-prime-theorem` |
| Current theorem release title | `PRC v2.7.1: General q-Prime Single-Gap Aperture Classification Theorem` |
| Current theorem release asset | `PrimeClock-v2.7.1-general-q-prime-theorem-v1.0.zip` |
| Current theorem DOI state | `10.5281/zenodo.20209528` |
| Current theorem GitHub Release | `https://github.com/ritabe-dev/PrimeClock/releases/tag/v2.7.1-prc-general-q-prime-theorem` |
| Current theorem README | `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_7_public_theorem_release_readme_v1_0.md` |
| Current theorem release notes | `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_7_public_theorem_release_notes_final_v1_0.md` |
| Current theorem citation | `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_7_public_theorem_release_citation_v1_0.cff` |
| Latest DOI-backed theorem release | `v2.7.1-prc-general-q-prime-theorem` |
| Latest DOI-backed theorem title | `PRC v2.7.1: General q-Prime Single-Gap Aperture Classification Theorem` |
| Latest DOI-backed theorem asset | `PrimeClock-v2.7.1-general-q-prime-theorem-v1.0.zip` |
| Latest DOI-backed theorem Version DOI | `10.5281/zenodo.20209528` |
| Latest DOI-backed theorem GitHub Release | `https://github.com/ritabe-dev/PrimeClock/releases/tag/v2.7.1-prc-general-q-prime-theorem` |
| Release registry | `release/public/release_registry.json` |
| Python package | `prime-reciprocal-projection` `0.1.0` |
<!-- END GENERATED PUBLIC SURFACE -->

## Foundational v2.3 Release

| Item | Version / file |
| --- | --- |
| Public release | `v2.3.0` |
| Foundational public release | `v2.3.0` |
| Public release config | `release/public/release_config.json` |
| Public bundle name | `PrimeClock-2.3.0` |
| Version DOI | `10.5281/zenodo.20119473` |
| Concept DOI | `10.5281/zenodo.20091722` |
| Finite theorem note | `research/notes/prc_finite_certificate_note_v2_0.md` |
| v2.3 theorem note | `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_theorem_note_draft_v0_1.md` |
| Related work note | `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_related_work_v0_2.md` |
| C4 witness table | `prc_prime_prefix_c4_exclusion_witness_v1_6.csv` |
| C5 full table | `prc_prime_prefix_ck_full_v1_1.csv` |
| B5 classification table | `prc_prime_prefix_b5_birth_classification_v1_5.csv` |
| Critical-radius table | `prc_prime_prefix_critical_radius_k4_k5_v0_1.csv` |
| Birth-dynamics table | `prc_prime_prefix_birth_dynamics_k5_k7_v0_1.csv` |
| v2.3 helper verifier output | `prc_v2_3_candidate_verification_v0_1.csv` |
| v2.3 standalone audit output | `prc_v2_3_candidate_standalone_verification_v0_1.csv` |

## Release Lines

| Line | Status | Maintenance handling |
| --- | --- | --- |
| `v2.2.4` | historical stable finite certificate | Do not retag; use `ERRATA.md` for clarifications or a maintenance patch release. |
| `maintenance/v2.2.5` | reserved historical maintenance patch line | Use only for errata or docs clarification rooted at `v2.2.4`. |
| `v2.3.0` | immutable foundational public DOI release for critical-radius and gap-aperture finite claims | Do not rewrite after publication; use `ERRATA.md` or a maintenance patch release if corrections are needed. |
| `maintenance/v2.3.1` | reserved maintenance patch line | Use only for errata or docs clarification rooted at `v2.3.0`. |
| `v2.4.x` | source-only bridge from v2.3.0 to the v2.5 theorem line | No public release, DOI, or candidate ZIP. Preserve useful diagnostics as internal evidence only. |
| `v2.7.1-prc-general-q-prime-theorem` | current and latest DOI-backed public theorem release | General q-prime single-gap aperture classification theorem for the PRC circular-arc model. |

Historical release corrections are governed by
`release/public/MAINTENANCE_POLICY.md`. The short rule is: published tags and
Zenodo archives are immutable snapshots, so past releases are corrected through
`ERRATA.md` or a new maintenance patch release, not by rewriting old tags.

## DOI and Release Registry

`release/public/release_registry.json` is the source of truth for public release
metadata across versions: release id, tag, title, GitHub Release URL, DOI state,
Zenodo DOI, asset name, manifest path, release notes, README paths, and citation
policy.

Check registry consistency with:

```bash
python3 scripts/render_public_surface.py --check
python3 scripts/check_release_doi_integrity.py --all
python3 scripts/verify_public_release_execution_preflight.py --all
```

New public release lines must be added to the registry before DOI finalization.
Registry-managed DOI finalization uses:

```bash
python3 scripts/finalize_version_doi.py \
  --release-id <registered-release-id> \
  --version-doi 10.5281/zenodo.<version-record>
```

The legacy `scripts/finalize_release_doi.py` path is retained for the v2.3 public
bundle line.

`SHA256SUMS` records the file hashes for the public release allowlist. Update it
with:

```bash
python3 scripts/update_public_hashes.py
```

Check it with:

```bash
python3 scripts/render_public_surface.py --check
python3 scripts/check_release_doi_integrity.py --all
python3 scripts/update_public_hashes.py --check
```

The Python package retains the historical name `prime-reciprocal-projection`.
The package version `0.1.0` is internal tooling metadata for the Python verifier
package; it is intentionally separate from the PrimeClock public release lines.

The top-level `CITATION.cff` uses the v2.3 Zenodo concept DOI as its top-level
DOI. The current theorem release uses release-specific citation metadata and is
waiting for a Zenodo version DOI. Until that DOI exists, the latest DOI-backed
theorem release uses release-specific citation metadata and version DOI
`10.5281/zenodo.20209528`.
