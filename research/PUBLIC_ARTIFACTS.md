# Public Artifact Manifest

Use this manifest when preparing a review zip for Prime Reciprocal Projection /
Prime Reciprocal Covering.

## Include

- `README.md`
- `pyproject.toml`
- `uv.lock`
- `src/prime_reciprocal_projection/`
- `tests/`
- `notes/`
- `data/summaries/`
- `figures/v0/`

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

For research review, start with:

```text
research/README.md
research/notes/prc_research_note_v1_0_ja.md
research/notes/prc_prime_prefix_profile_v0_1.md
research/notes/prc_mathematical_theme_prime_prefix_filtration_v0_1.md
research/notes/prc_prime_prefix_finite_note_v1_1.md
research/notes/prc_prime_prefix_certificate_depth_v0_2.md
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
research/notes/claims.md
research/notes/known-results.md
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
research/data/summaries/prc_prime_prefix_birth_witness_v1_1.csv
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
