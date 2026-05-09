# Prime Reciprocal Covering Research Package

This directory contains the reproducible research package for Prime Reciprocal
Covering (PRC). The current external-release target is the narrow finite
`C_k/C_4/B_5` certificate artifact.

The PrimeClock visualization is origin/discovery context for the research. The
v2.2.3 public release bundle contains the finite residue-covering research
package and exact certificate artifacts, not the React/Vite visualization app.

## Current Release Entry Point

Read these files in order:

1. `notes/prc_finite_certificate_note_v2_0.md`
2. `notes/claims_finite_c4_b5.md`
3. `VERIFY_FINITE_C4_B5.md`
4. `RELEASE_NOTES_v2_2_3.md`
5. `notes/known-results.md`
6. `../VERSION_MAP.md`

The narrow finite package supports:

- `C_4={2,208} mod 210`;
- `C_5` has `36` covered residues;
- `Lift_5(C_4)` has `22` inherited residues;
- `B_5` has `14` births in `7` reflection pairs;
- every `B_5` birth is a strict single-gap closure by the new `p=11` arc.

These are finite certificate claims only. Broader asymptotic, distributional,
and complete PRC questions are outside the v2.2.3 release scope.

## Verify The Finite Package

Use a local editable install for the package verifier and tests:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
python -m pytest tests/test_covering_prime_prefix_filtration.py -q
python -m prime_reciprocal_projection.cli covering-prime-prefix-verify-certificates \
  --out data/summaries/prc_prime_prefix_certificate_verification_v1_7.csv
```

The standalone checker uses only the Python standard library:

```bash
python certificates/check_prime_prefix_c4_b5.py \
  --out data/summaries/prc_prime_prefix_certificate_standalone_verification_v1_8.csv
```

Expected focused results:

```text
focused pytest: 41 passed
package verifier: checks=14, failed=0
standalone checker: checks=9, failed=0
```

## Included Finite Certificate Data

The release-facing finite CSVs are:

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

## Full Repository Context

The full repository also contains earlier PRC diagnostics, certificate-depth
experiments, `k=8` extensions, branch-fill experiments, branch-uniform null
comparisons, and residual-fragmentation studies. Those remain useful context,
but they are not part of the narrow `C_k/C_4/B_5` finite-theorem release
package.

The public bundle may include broader Python implementation modules because the
CLI verifier and focused tests share package code. The release-facing claims,
notes, and CSVs remain limited to the finite `C_k/C_4/B_5` artifact.

Use `PUBLIC_RELEASE_MANIFEST.md` before preparing a public release bundle.

## Non-Claims

This package is scoped to finite prime-prefix residue-covering certificates,
specifically `C_4` and `B_5`. Broader asymptotic, distributional, and complete
PRC questions are outside this release.
