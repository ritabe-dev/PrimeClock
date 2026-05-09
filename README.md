# PrimeClock / Prime Reciprocal Covering

This repository contains two related artifacts:

- a small React/Vite PrimeClock visualization in `src/`;
- a research package in `research/` for Prime Reciprocal Covering (PRC).

The current release-ready research artifact is intentionally narrow. It focuses
on a finite prime-prefix residue-covering problem and the checked `C_4/B_5`
certificate package, not on a broad theorem about prime distribution.

## Current Release Target

Read these files first:

1. `research/notes/prc_finite_certificate_note_v2_0.md`
2. `research/notes/claims_finite_c4_b5.md`
3. `research/VERIFY_FINITE_C4_B5.md`
4. `research/RELEASE_NOTES_v2_2.md`
5. `research/notes/known-results.md`

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
python -m pip install -e ".[dev]"
python -m pytest tests/test_covering_prime_prefix_filtration.py -q
python -m prime_reciprocal_projection.cli covering-prime-prefix-verify-certificates \
  --out data/summaries/prc_prime_prefix_certificate_verification_v1_7.csv
python certificates/check_prime_prefix_c4_b5.py \
  --out data/summaries/prc_prime_prefix_certificate_standalone_verification_v1_8.csv
```

Expected focused results:

```text
focused pytest: 39 passed
package verifier: checks=14, failed=0
standalone checker: checks=9, failed=0
```

## Non-Claims

This repository does not claim:

- a new theorem about prime distribution;
- a new limiting law for `{N/p}`;
- an asymptotic law for `|C_k|/M_k`;
- that `C_4` or `C_5` explains all complete PRC events.

Historical PRC diagnostics, certificate-depth work, `k=8` experiments, and
residual-fragmentation studies remain in the full repository as context. They
are not part of the narrow finite-theorem release bundle.

## Citation and License

Use `CITATION.cff` for citation metadata. The archived v2.2.0 DOI is:

```text
10.5281/zenodo.20091829
```

The project is released under the MIT License; see `LICENSE`.
