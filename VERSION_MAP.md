# Version Map

This repository keeps release, package, note, table, and verifier versions
separate. The current public release target is:

| Item | Version / file |
| --- | --- |
| Public release | `v2.3.0` |
| Public release config | `release/public/release_config.json` |
| Public bundle name | `PrimeClock-2.3.0` |
| Version DOI | `10.5281/zenodo.20119473` |
| Concept DOI | `10.5281/zenodo.20091722` |
| Python package | `prime-reciprocal-projection` `0.1.0` |
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
| `v2.3.0` | current public DOI release candidate for critical-radius and gap-aperture finite claims | Do not rewrite after publication; use `ERRATA.md` or `maintenance/v2.3.1` if corrections are needed. |
| `v2.4.x` | next research line | Keep new claims in the active research line; release notes should state whether relevant `v2.3.0` claims are retained, corrected, or superseded. |

Historical release corrections are governed by
`release/public/MAINTENANCE_POLICY.md`. The short rule is: published tags and
Zenodo archives are immutable snapshots, so past releases are corrected through
`ERRATA.md` or a new maintenance patch release, not by rewriting old tags.

`SHA256SUMS` records the file hashes for the public release allowlist. Update it
with:

```bash
python3 scripts/update_public_hashes.py
```

Check it with:

```bash
python3 scripts/check_release_versions.py
python3 scripts/update_public_hashes.py --check
```

The public release bundle is scoped to finite checked PRC claims: the original
`C_k/C_4/B_5` certificate artifact, the `k=4,5` critical-radius spectra, and the
`B_5/B_6/B_7` gap-aperture birth-dynamics classification. `B_8` or larger
layers, residual-gap transition graphs, null models, and asymptotic or
prime-distribution claims are future work.

The Python package retains the historical name `prime-reciprocal-projection`.
The release-facing finite theorem bundle is framed as Prime Reciprocal
Covering. The package version `0.1.0` is internal tooling metadata for the
Python verifier package; it is intentionally separate from the PrimeClock public
release line `v2.3.0`.

`CITATION.cff` uses the Zenodo concept DOI as its top-level DOI. Version DOIs
are recorded here and in release notes for DOI releases after Zenodo publishes
the GitHub release archive. The release config fixes this as
`concept_doi_in_citation_version_doi_in_release_notes`.
