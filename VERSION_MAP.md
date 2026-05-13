# Version Map

This repository keeps release, package, note, table, verifier, and DOI metadata
versions separate. Multi-version release metadata is tracked in
`release/public/release_registry.json`.

## Current Public Releases

| Item | Version / file |
| --- | --- |
| Current scoped public theorem release | `v2.5.0-prc-public-theorem` |
| Current theorem release title | `PRC v2.5: finite aperture-orbit separator theorem` |
| Current theorem release asset | `PrimeClock-v2.5-public-theorem-v1.0.zip` |
| Current theorem Version DOI | `10.5281/zenodo.20154561` |
| Current theorem README | `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_readme_v1_0.md` |
| Current theorem release notes | `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_release_notes_v1_0.md` |
| Current theorem citation | `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_citation_v1_0.cff` |
| Release registry | `release/public/release_registry.json` |
| Python package | `prime-reciprocal-projection` `0.1.0` |

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
| `v2.2.4` | historical stable finite certificate | Do not retag; use `ERRATA.md` for clarifications or `maintenance/v2.2.5` for citable patch releases. |
| `v2.3.0` | immutable foundational public DOI release for critical-radius and gap-aperture finite claims | Do not rewrite after publication; use `ERRATA.md` or `maintenance/v2.3.1` if corrections are needed. |
| `v2.4.x` | source-only bridge from v2.3.0 to the v2.5 theorem line | No public release, DOI, or candidate ZIP. Preserve useful diagnostics as internal Gate R evidence only. |
| `v2.5.0-prc-public-theorem` | current scoped public theorem DOI release | Finite exact aperture-orbit separator theorem for recorded `B4->B5`, `B5->B6`, and `B6->B7` scopes. |
| `v2.6.x` | next research line | Must be registered in `release/public/release_registry.json` before DOI or GitHub Release work starts. |

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
python3 scripts/check_release_doi_integrity.py --all
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

`SHA256SUMS` records the file hashes for the v2.3 public release allowlist.
Update it with:

```bash
python3 scripts/update_public_hashes.py
```

Check it with:

```bash
python3 scripts/check_release_versions.py
python3 scripts/update_public_hashes.py --check
```

The Python package retains the historical name `prime-reciprocal-projection`.
The package version `0.1.0` is internal tooling metadata for the Python verifier
package; it is intentionally separate from the PrimeClock public release lines.

The top-level `CITATION.cff` uses the v2.3 Zenodo concept DOI as its top-level
DOI. The v2.5 theorem release uses a release-specific `CITATION.cff` and version
DOI `10.5281/zenodo.20154561`.
