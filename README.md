# PrimeClock / PRC v2.3.0 Public Release Bundle

This public release bundle contains the finite Prime Reciprocal Covering (PRC)
research package for the v2.3.0 critical-radius and gap-aperture
birth-dynamics artifact. It includes exact rational CSV certificates, package
verification tools, a standard-library standalone audit, and focused pytest
coverage.

The React/Vite PrimeClock visualization app is not included in this bundle.
This bundle is intentionally narrower than the development repository.

The Python package keeps the historical name `prime-reciprocal-projection`.
The finite theorem bundle is framed as Prime Reciprocal Covering.

## Read First

1. `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_theorem_note_draft_v0_1.md`
2. `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_related_work_v0_2.md`
3. `VERIFY.md`
4. `DATA_FILES.md`
5. `VERSION_MAP.md`
6. `research/notes/prc_finite_certificate_note_v2_0.md`

## Finite Claims

- `C_4={2,208} mod 210`;
- `C_5` has `36` covered residues;
- `C_k` is the `1/2` level set of the exact critical-radius spectrum for the
  checked `k=4,5` layers;
- `B_5`, `B_6`, and `B_7` are unique strict single-gap births in the checked
  finite data;
- near-miss rank is a diagnostic candidate generator, while birth is decided by
  next-prime `q`-grid phase alignment through the gap-aperture window.

These are finite certificate claims supported by exact rational CSVs, helper
verification, a standard-library standalone audit, and focused pytest coverage.

## Research Position

Prime Reciprocal Covering is a project-defined finite prime-prefix
circle-covering model. For each residue class and each prime in a prefix, it
places a rational closed arc on `R/Z` centered at `(r mod p)/p`; the public
claims are about exactly checked finite residue layers.

The vocabulary is adjacent to classical covering systems of congruences because
it uses residues, moduli, and covering language, but this release does not claim
a result about classical covering systems. The v2.3.0 contribution is the
auditable finite certificate package together with the critical-radius spectrum
and gap-aperture / `q`-grid phase mechanism for the checked birth layers.
Terminology and nearby literature context are recorded in
`research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_related_work_v0_2.md`.

Zenodo DOIs identify citable archived snapshots of this finite artifact. They
do not imply peer review.

## Verify

From `research/`:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
python experiments/critical_radius_birth_dynamics/check_candidate.py \
  --out /tmp/prc-v2.3-helper-check.csv
python experiments/critical_radius_birth_dynamics/check_candidate_standalone.py \
  --out /tmp/prc-v2.3-standalone-check.csv
python -m pytest tests/test_critical_radius_birth_dynamics_public.py -q
```

Expected v2.3.0 results:

```text
check_v2_3_candidate: checks=13, failed=0
check_v2_3_candidate_standalone: checks=10, failed=0
public critical-radius/birth-dynamics pytest: 9 passed
```

The original finite `C_4/B_5` verifier path remains documented in `VERIFY.md`.

## Scope

This public release bundle is scoped to finite checked PRC claims. It does not
include the React/Vite PrimeClock visualization app, `B_8` or larger layers,
residual-gap transition graphs, null models, broad research archives, or
asymptotic, distributional, or complete PRC claims.

## Citation and License

Use `CITATION.cff` for citation metadata. The v2.3.0 version DOI is pending
Zenodo publication for the GitHub `v2.3.0` release. The Zenodo concept DOI for
the release series is `10.5281/zenodo.20091722`.

The project is released under the MIT License; see `LICENSE`.
