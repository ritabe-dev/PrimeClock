# PRC v2.3 Standalone Checker Contract v0.1

Status: implemented internal standalone audit, not a public release checker.

The v2.3 candidate now has two verification lanes:

- `check_candidate.py`, an internal helper-based checker that regenerates the
  candidate rows through the experiment helper code and compares them with the
  committed CSV artifacts.
- `check_candidate_standalone.py`, a standard-library-only checker that reads
  the committed CSV artifacts, verifies the candidate CSV SHA256 manifest,
  recomputes the k=4,5 critical-radius values from the definition, and checks
  the headline finite claims without importing `prime_reciprocal_projection` or
  `experiments/critical_radius_birth_dynamics/tools.py`.

The standalone checker is a CSV/hash/headline finite-claim audit. It is not a
full independent regeneration of every `B_5/B_6/B_7` birth layer; that full
helper-based regeneration remains the responsibility of `check_candidate.py`.

The standalone checker verifies:

- the `C_4` and `C_5` critical-radius level-set claims;
- SHA256 coverage for the committed v2.3 candidate CSV set;
- the degenerate zero-residue cusp values `lambda_4(0)=lambda_5(0)=1`;
- all committed k=4,5 critical-radius values by standard-library recomputation;
- the `C_4` critical-radius level set is exactly `{2, 208}`;
- the `C_5` critical-radius level set has 36 rows and matches the committed
  coverage status fields;
- critical-radius summary counts match the row-level critical-radius CSV;
- `B_5`, `B_6`, and `B_7` summary rows are strict single-gap births;
- row-level birth-dynamics rows for `B_5`, `B_6`, and `B_7` are all strict
  single-gap births;
- each `B_5/B_6/B_7` birth parent has exactly one strict admissible
  next-prime remainder, matching the committed row;
- threshold-crossing rows match the birth-dynamics rows and cross from
  `lambda > 1/2` at the parent level to `lambda <= 1/2` at the birth level.

Expected result:

```text
check_v2_3_candidate_standalone: checks=10, failed=0
```

This does not make v2.3 a public release. Public promotion still requires a
v2.3 public release config with GitHub/Zenodo metadata. The related-work
terminology decision is recorded separately in
`notes/prc_v2_3_related_work_decision_v0_1.md`.
