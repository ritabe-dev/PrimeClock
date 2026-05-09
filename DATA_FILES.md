# Data Files

All paths below are relative to `research/data/summaries/`.

## Finite Certificate CSVs

- `prc_prime_prefix_residue_covering_filtration_v0_1.csv`
  - One row per prefix level `k<=7`.
  - Counts are exact finite enumeration results.
  - Density columns are decimal summaries.
- `prc_prime_prefix_residue_covering_birth_samples_v0_1.csv`
  - Sampled birth residues through `k=7`.
- `prc_prime_prefix_ck_full_v1_1.csv`
  - All covered residues through `k=5`, marked `inherited` or `birth`.
- `prc_prime_prefix_c4_exclusion_witness_v1_6.csv`
  - One rational open-gap witness and `witness_point` for each residue outside
    `C_4={2,208}`.
- `prc_prime_prefix_c4_exclusion_summary_v1_5.csv`
  - `36` compressed C4 exclusion classes with complete residue lists.
- `prc_prime_prefix_birth_witness_v1_5.csv`
  - One row per `B_5` birth, including exact old-gap and new-arc boundaries.
- `prc_prime_prefix_b5_birth_classification_v1_5.csv`
  - One row per `B_5` birth with reflection-pair and parent-residue fields.
- `prc_prime_prefix_b5_birth_pair_summary_v1_5.csv`
  - One row per B5 reflection pair for the displayed theorem table.
- `prc_prime_prefix_certificate_verification_v1_7.csv`
  - Package-level rational CSV verification summary.
- `prc_prime_prefix_certificate_standalone_verification_v1_8.csv`
  - Standard-library standalone verification summary.

## Expected Checker Results

```text
package verifier: checks=14, failed=0
standalone checker: checks=9, failed=0
```
