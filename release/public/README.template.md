# PrimeClock / PRC Finite Certificate Bundle

This public release bundle contains the finite `C_k/C_4/B_5` Prime Reciprocal
Covering (PRC) research package: theorem notes, exact rational CSV certificates,
package verification tools, and a standard-library standalone checker.

The React/Vite PrimeClock visualization app is not included in this bundle.
This bundle is intentionally narrower than the development repository.

The Python package keeps the historical name `prime-reciprocal-projection`.
The finite theorem bundle is now framed as Prime Reciprocal Covering.

## Read First

1. `research/notes/prc_finite_certificate_note_v2_0.md`
2. `research/notes/claims_finite_c4_b5.md`
3. `VERIFY.md`
4. `research/VERIFY_FINITE_C4_B5.md`
5. `DATA_FILES.md`
6. `VERSION_MAP.md`

## Finite Claims

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

## Scope

This public release bundle is scoped to finite prime-prefix residue-covering
certificates, specifically `C_4` and `B_5`. It does not include the React/Vite
PrimeClock visualization app, broad research archive, certificate-depth diagnostics,
modulo-210 diagnostics, branch-uniform diagnostics, `B_6` exports, or broader
asymptotic, distributional, or complete PRC claims.

## Citation and License

Use `CITATION.cff` for citation metadata. The v2.2.4 version DOI is
`10.5281/zenodo.20096689`; the Zenodo concept DOI for the release series is
`10.5281/zenodo.20091722`.

The project is released under the MIT License; see `LICENSE`.
