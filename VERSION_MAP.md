# Version Map

This repository keeps release, package, note, table, and verifier versions
separate. The current public release target is:

| Item | Version / file |
| --- | --- |
| Public release | `v2.2.4` |
| Public release config | `release/public/release_config.json` |
| Public bundle name | `PrimeClock-2.2.4` |
| Version DOI | pending Zenodo publication for the GitHub `v2.2.4` release |
| Concept DOI | `10.5281/zenodo.20091722` |
| Python package | `prime-reciprocal-projection` `0.1.0` |
| Finite theorem note | `research/notes/prc_finite_certificate_note_v2_0.md` |
| Narrow claims | `research/notes/claims_finite_c4_b5.md` |
| C4 witness table | `prc_prime_prefix_c4_exclusion_witness_v1_6.csv` |
| C4 summary table | `prc_prime_prefix_c4_exclusion_summary_v1_5.csv` |
| C5 full table | `prc_prime_prefix_ck_full_v1_1.csv` |
| B5 witness table | `prc_prime_prefix_birth_witness_v1_5.csv` |
| B5 classification table | `prc_prime_prefix_b5_birth_classification_v1_5.csv` |
| B5 pair summary | `prc_prime_prefix_b5_birth_pair_summary_v1_5.csv` |
| Package verifier output | `prc_prime_prefix_certificate_verification_v1_7.csv` |
| Standalone checker output | `prc_prime_prefix_certificate_standalone_verification_v1_8.csv` |

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

The public release bundle remains scoped to the finite `C_k/C_4/B_5`
certificate artifact. Broader proof-core refactors, certificate JSON schemas,
`B_6` exports, and bibliography expansion are future work.

The Python package retains the historical name `prime-reciprocal-projection`.
The release-facing finite theorem bundle is framed as Prime Reciprocal
Covering.
