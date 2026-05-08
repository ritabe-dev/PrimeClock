# Public Artifact Manifest

Use this manifest when preparing a review zip for Prime Reciprocal Projection /
Prime Reciprocal Covering.

## Minimal External Review Package

Use this smaller package for first-pass external review. It emphasizes the
finite theorem note and keeps modulo-210 diagnostics out of the main path.

- `README.md`
- `pyproject.toml`
- `uv.lock`
- `src/prime_reciprocal_projection/`
- `tests/`
- `VERIFY_FINITE_C4_B5.md`
- `RELEASE_NOTES_v2_0.md`
- `notes/prc_finite_certificate_note_v2_0.md`
- `notes/prc_prime_prefix_finite_note_v1_1.md`
- `notes/claims_finite_c4_b5.md`
- `notes/known-results.md`
- `notes/prc_mathematical_theme_prime_prefix_filtration_v0_1.md`
- `data/summaries/prc_prime_prefix_residue_covering_filtration_v0_1.csv`
- `data/summaries/prc_prime_prefix_residue_covering_birth_samples_v0_1.csv`
- `data/summaries/prc_prime_prefix_ck_full_v1_1.csv`
- `data/summaries/prc_prime_prefix_c4_exclusion_witness_v1_6.csv`
- `data/summaries/prc_prime_prefix_c4_exclusion_summary_v1_5.csv`
- `data/summaries/prc_prime_prefix_birth_witness_v1_5.csv`
- `data/summaries/prc_prime_prefix_b5_birth_classification_v1_5.csv`
- `data/summaries/prc_prime_prefix_b5_birth_pair_summary_v1_5.csv`
- `data/summaries/prc_prime_prefix_certificate_verification_v1_7.csv`
- `data/summaries/prc_prime_prefix_certificate_standalone_verification_v1_8.csv`
- `certificates/check_prime_prefix_c4_b5.py`

The certificate-depth note and CSVs are context artifacts for the full archive,
not part of the minimal `C_k/C_4/B_5` theorem package. This prevents a minimal
reviewer from hitting references to complete-covering source tables that are
not included in the small zip.

The broad `notes/claims.md` file is also a full-archive context artifact. The
minimal package should include `notes/claims_finite_c4_b5.md` instead, so every
claim in the small zip is audited by the included C4/B5 artifacts.

The existing `review_packages/` directory contains stale archived snapshots.
Do not send those as the current review package; regenerate a new package from
this minimal manifest instead.

Scouting notes are excluded unless explicitly promoted into the main review
path.

## Full Reproducibility Archive

Use this broader archive when the reviewer wants all historical diagnostics and
figures, including modulo-210 and branch-uniform experiments.

- `README.md`
- `pyproject.toml`
- `uv.lock`
- `src/prime_reciprocal_projection/`
- `tests/`
- `notes/`
- `data/summaries/`
- `figures/v0/`

## v2.0 Release-Ready Bundle

Use this package when the reviewer should see the polished finite theorem note
and citation metadata, but not the full historical archive.

- `CITATION.cff`
- `README.md`
- `research/README.md`
- `research/RELEASE_NOTES_v2_0.md`
- `research/VERIFY_FINITE_C4_B5.md`
- `research/notes/prc_finite_certificate_note_v2_0.md`
- `research/notes/claims_finite_c4_b5.md`
- `research/notes/known-results.md`
- `research/data/summaries/prc_prime_prefix_*`
- `research/src/prime_reciprocal_projection/`
- `research/tests/test_covering_prime_prefix_filtration.py`
- `research/certificates/check_prime_prefix_c4_b5.py`

From the repository root, also include the small PrimeClock visualization only
when the reviewer wants the origin artifact:

- `package.json`
- `package-lock.json`
- `index.html`
- `src/`

## Exclude

- `.git/`
- `.venv/`
- `node_modules/`
- `.uv-cache/`
- `.pytest_cache/`
- `.ruff_cache/`
- `.matplotlib-cache/`
- `dist/`
- `review_packages/`
- `__pycache__/`
- `.DS_Store`
- generated local zip/tar archives

## Review Entry Point

For a minimal research review, start with:

```text
research/README.md
research/notes/prc_finite_certificate_note_v2_0.md
research/notes/claims_finite_c4_b5.md
research/VERIFY_FINITE_C4_B5.md
research/notes/known-results.md
research/notes/prc_mathematical_theme_prime_prefix_filtration_v0_1.md
```

For a full reproducibility review, continue with appendix/internal diagnostics:

```text
research/notes/prc_research_note_v1_0_ja.md
research/notes/prc_prime_prefix_profile_v0_1.md
research/notes/prc_prime_prefix_k8_extension_v0_3.md
research/notes/prc_prime_prefix_uncertified_residue_profile_v0_4.md
research/notes/prc_prime_prefix_uncertified_control_profile_v0_5.md
research/notes/prc_prime_prefix_uncertified_control_audit_v0_6.md
research/notes/prc_prime_prefix_uncertified_mod210_class_review_v0_7.md
research/notes/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.md
research/notes/prc_prime_prefix_uncertified_mod210_source_summary_v0_9.md
research/notes/prc_prime_prefix_uncertified_mod210_boundary_summary_v0_10.md
research/notes/prc_prime_prefix_uncertified_mod210_lift_boundary_v0_11.md
research/notes/prc_prime_prefix_mod210_anchor_neighborhood_v0_12.md
research/notes/prc_main_v0_9.md
```

The current project should be read as a finite-`N` experimental mathematics
artifact. It does not claim a new theorem about prime distribution or a law for
complete covering.

Current prime-prefix artifacts to include in the summaries directory:

```text
research/data/summaries/prc_prime_prefix_profile_v0_1.csv
research/data/summaries/prc_prime_prefix_residue_covering_filtration_v0_1.csv
research/data/summaries/prc_prime_prefix_residue_covering_birth_samples_v0_1.csv
research/data/summaries/prc_prime_prefix_ck_full_v1_1.csv
research/data/summaries/prc_prime_prefix_c4_exclusion_witness_v1_6.csv
research/data/summaries/prc_prime_prefix_c4_exclusion_summary_v1_5.csv
research/data/summaries/prc_prime_prefix_birth_witness_v1_5.csv
research/data/summaries/prc_prime_prefix_b5_birth_classification_v1_5.csv
research/data/summaries/prc_prime_prefix_b5_birth_pair_summary_v1_5.csv
research/data/summaries/prc_prime_prefix_certificate_verification_v1_7.csv
research/data/summaries/prc_prime_prefix_certificate_standalone_verification_v1_8.csv
research/data/summaries/prc_prime_prefix_certificate_depth_v0_2.csv
research/data/summaries/prc_prime_prefix_certificate_depth_summary_v0_2.csv
research/data/summaries/prc_prime_prefix_residue_covering_filtration_k8_v0_3.csv
research/data/summaries/prc_prime_prefix_residue_covering_birth_samples_k8_v0_3.csv
research/data/summaries/prc_prime_prefix_certificate_depth_k8_v0_3.csv
research/data/summaries/prc_prime_prefix_certificate_depth_summary_k8_v0_3.csv
research/data/summaries/prc_prime_prefix_uncertified_residue_profile_v0_4.csv
research/data/summaries/prc_prime_prefix_uncertified_residue_summary_v0_4.csv
research/data/summaries/prc_prime_prefix_uncertified_mod210_summary_v0_4.csv
research/data/summaries/prc_prime_prefix_uncertified_control_profile_v0_5.csv
research/data/summaries/prc_prime_prefix_uncertified_control_summary_v0_5.csv
research/data/summaries/prc_prime_prefix_uncertified_control_pair_deltas_v0_5.csv
research/data/summaries/prc_prime_prefix_uncertified_control_mod210_audit_v0_6.csv
research/data/summaries/prc_prime_prefix_uncertified_source_depth_summary_v0_6.csv
research/data/summaries/prc_prime_prefix_uncertified_mod210_class_review_v0_7.csv
research/data/summaries/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.csv
research/data/summaries/prc_prime_prefix_uncertified_mod210_class_source_summary_v0_9.csv
research/data/summaries/prc_prime_prefix_uncertified_mod210_class_boundary_summary_v0_10.csv
research/data/summaries/prc_prime_prefix_uncertified_mod210_lift_boundary_v0_11.csv
research/data/summaries/prc_prime_prefix_mod210_anchor_neighborhood_v0_12.csv
```
