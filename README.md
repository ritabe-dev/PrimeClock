# PrimeClock Development Repository

This development repository is the working tree for PrimeClock and Prime
Reciprocal Covering (PRC). It can contain broader source history and local
research work, including:

- a small React/Vite PrimeClock visualization app in `src/`;
- the PRC research package under `research/`;
- release scripts used to build a narrow public certificate bundle.

Public release bundles are generated from an allowlist and have their own root
README template at `release/public/README.template.md`. The v2.2.4 public bundle
contains only the finite `C_k/C_4/B_5` certificate artifact, exact rational CSVs,
and verification tools; the React/Vite visualization app is not included in that
bundle. The release version is centralized in
`release/public/release_config.json`.

The Python package keeps the historical name `prime-reciprocal-projection`.
The finite theorem bundle is now framed as Prime Reciprocal Covering.

## Current Release Target

Read these files first:

1. `research/notes/prc_finite_certificate_note_v2_0.md`
2. `research/notes/claims_finite_c4_b5.md`
3. `research/VERIFY_FINITE_C4_B5.md`
4. `research/RELEASE_NOTES_v2_2_4.md`
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
focused pytest: 50 passed
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
python3 scripts/check_release_versions.py
python3 scripts/verify_public_release.py --out /private/tmp/primeclock-public-release --zip
```

The release manifest is `research/PUBLIC_RELEASE_MANIFEST.md`; file hashes are
recorded in `SHA256SUMS`, and version correspondence is recorded in
`VERSION_MAP.md`.

## Citation and License

Use `CITATION.cff` for citation metadata. The v2.2.4 version DOI is
`10.5281/zenodo.20096689`; the Zenodo concept DOI for the release series is
`10.5281/zenodo.20091722`.

The project is released under the MIT License; see `LICENSE`.
