# PrimeClock / Prime Reciprocal Covering

This source repository contains the historical PrimeClock React/Vite
visualization and the current Prime Reciprocal Covering (PRC) research package.
The v2.2.1 public release bundle is narrower: it contains the finite
`C_k/C_4/B_5` research package, certificate CSVs, and verification tools. The
visualization remains origin context and is not included in that release bundle.

## Current Release Target

Read these files first:

1. `research/notes/prc_finite_certificate_note_v2_0.md`
2. `research/notes/claims_finite_c4_b5.md`
3. `research/VERIFY_FINITE_C4_B5.md`
4. `research/RELEASE_NOTES_v2_2_1.md`
5. `research/notes/known-results.md`
6. `VERSION_MAP.md`

The finite claims are:

- `C_4={2,208} mod 210`;
- `C_5` has `36` covered residues;
- `Lift_5(C_4)` has `22` inherited residues;
- `B_5` has `14` births in `7` reflection pairs;
- every `B_5` birth is a strict single-gap closure by the new `p=11` arc.

These are finite certificate claims supported by exact rational CSVs, a package
verifier, and a standard-library standalone checker.

## Verify

From `research/`:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
python -m pytest tests/test_covering_prime_prefix_filtration.py -q
python -m prime_reciprocal_projection.cli covering-prime-prefix-verify-certificates \
  --out data/summaries/prc_prime_prefix_certificate_verification_v1_7.csv
python certificates/check_prime_prefix_c4_b5.py \
  --out data/summaries/prc_prime_prefix_certificate_standalone_verification_v1_8.csv
```

Expected focused results:

```text
focused pytest: 41 passed
package verifier: checks=14, failed=0
standalone checker: checks=9, failed=0
```

## Non-Claims

This release is scoped to finite prime-prefix residue-covering certificates,
specifically `C_4` and `B_5`. Broader asymptotic, distributional, and complete
PRC questions are outside this release.

Historical PRC diagnostics, certificate-depth work, `k=8` experiments, and
residual-fragmentation studies remain in the full repository as context. They
are not part of the narrow finite-theorem release bundle.

## Public Release Bundle

Public releases are built from an explicit allowlist. The source repository can
contain broader research history, but the release bundle contains only the
finite `C_k/C_4/B_5` certificate artifact and its verification path.
The bundled Python package source includes broader implementation modules needed
by the verifier and tests; the public claims, notes, and CSVs remain limited to
the finite certificate artifact.

Build and inspect a local release bundle with:

```bash
python3 scripts/update_public_hashes.py --check
python3 scripts/build_public_release.py --version 2.2.1 --out /private/tmp/primeclock-public-release --zip
python3 scripts/check_public_release.py /private/tmp/primeclock-public-release/PrimeClock-2.2.1
```

The release manifest is `research/PUBLIC_RELEASE_MANIFEST.md`; file hashes are
recorded in `SHA256SUMS`, and version correspondence is recorded in
`VERSION_MAP.md`.

## Citation and License

Use `CITATION.cff` for citation metadata. The current public DOI is
`pending Zenodo publication`.

The project is released under the MIT License; see `LICENSE`.
