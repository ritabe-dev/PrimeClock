# PrimeClock Development Repository

This development repository is the working tree for PrimeClock and Prime
Reciprocal Covering (PRC). It can contain broader source history and local
research work, including:

- a small React/Vite PrimeClock visualization app in `src/`;
- the PRC research package under `research/`;
- release scripts used to build a narrow public certificate bundle.

Public release bundles are generated from an allowlist and have their own root
README template at `release/public/README.template.md`. The v2.3.0 public bundle
contains the finite `C_k/C_4/B_5` certificate artifact plus the v2.3
critical-radius and gap-aperture birth-dynamics finite artifact; the React/Vite
visualization app is not included in that bundle. The release version is centralized in
`release/public/release_config.json`.

The Python package keeps the historical name `prime-reciprocal-projection`.
The finite theorem bundle is now framed as Prime Reciprocal Covering.

## Current Release Target

Read these files first:

1. `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_theorem_note_draft_v0_1.md`
2. `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_related_work_v0_2.md`
3. `research/RELEASE_NOTES_v2_3_0.md`
4. `research/notes/prc_finite_certificate_note_v2_0.md`
5. `research/notes/claims_finite_c4_b5.md`
6. `VERSION_MAP.md`

The finite claims are:

- `C_4={2,208} mod 210`;
- `C_5` has `36` covered residues;
- `Lift_5(C_4)` has `22` inherited residues;
- `B_5` has `14` births in `7` reflection pairs;
- every `B_5` birth is a strict single-gap closure by the new `p=11` arc.

The v2.3.0 release also promotes these finite claims:

- `C_k` is the `1/2` level set of the exact critical-radius spectrum for the
  checked `k=4,5` layers;
- `B_5`, `B_6`, and `B_7` are unique strict single-gap births in the checked
  finite data;
- near-miss rank is a diagnostic candidate generator, while birth is decided by
  next-prime `q`-grid phase alignment through the gap-aperture window.

These are finite certificate claims supported by exact rational CSVs, package
verification, standard-library standalone audits, and focused pytest coverage.

## Research Position

Prime Reciprocal Covering is a project-defined finite prime-prefix
circle-covering model. For each residue class and each prime in a prefix, it
places a rational closed arc on `R/Z` centered at `(r mod p)/p`; the public
claims are about exactly checked finite residue layers.

The vocabulary is adjacent to classical covering systems of congruences because
it uses residues, moduli, and covering language, but this release does not claim
a result about classical covering systems. The v2.3.0 research value is that it
makes the early PRC layers auditable as finite certificates and adds a
critical-radius spectrum plus a gap-aperture / `q`-grid phase mechanism for the
checked birth layers. The related-work boundary note
`research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_related_work_v0_2.md`
records nearby terminology and literature context.

Zenodo DOIs identify citable archived snapshots of this finite artifact. They
do not imply peer review.

## Review Workflow

For current public citation, use the `v2.3.0` release and `CITATION.cff`.
The v2.2.4 release remains historical and is not retagged.

Normal cleanup and review-driven edits are pushed to GitHub `main` through
`maintenance_sync`. GitHub Release and Zenodo are used only when
`release/public/release_config.json` is explicitly switched to `doi_release`.
If `v2.2` or `v2.3` corrections appear during `v2.4` work, classify them with
`release/public/MAINTENANCE_POLICY.md` before editing: lightweight findings go
to `ERRATA.md` or docs clarification, while reproducibility or finite-claim
corrections use an isolated patch branch such as `maintenance/v2.3.1`.

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
focused pytest: 55 passed
package verifier: checks=14, failed=0
standalone checker: checks=9, failed=0
```

## Non-Claims

This release is scoped to finite prime-prefix residue-covering certificates and
the checked v2.3 critical-radius / gap-aperture birth-dynamics artifact. Broader
asymptotic, distributional, and complete PRC questions are outside this release.

Historical PRC diagnostics, certificate-depth work, `B_8` or larger experiments,
residual-gap transition graph ideas, and null-model work remain in the full
repository as context. They are not part of the v2.3.0 public release bundle.

## Public Release Bundle

Public releases are built from an explicit allowlist. The source repository can
contain broader research history, but the release bundle contains only the
finite `C_k/C_4/B_5` certificate artifact, the v2.3.0 critical-radius and
gap-aperture birth-dynamics artifact, and their verification paths.
The bundled Python package source includes broader implementation modules needed
by the verifier and tests; the public claims, notes, and CSVs remain limited to
the finite certificate artifact.

Build and inspect a local release bundle with:

```bash
python3 scripts/check_release_versions.py
python3 scripts/verify_public_release.py --out "${TMPDIR:-/tmp}/primeclock-public-release" --zip
```

The release manifest is `research/PUBLIC_RELEASE_MANIFEST.md`; file hashes are
recorded in `SHA256SUMS`, and version correspondence is recorded in
`VERSION_MAP.md`. Historical-release corrections are tracked in `ERRATA.md`
and governed by `release/public/MAINTENANCE_POLICY.md`.

## Citation and License

Use `CITATION.cff` for citation metadata. Its top-level DOI is the Zenodo
concept DOI for the release series: `10.5281/zenodo.20091722`. The current version DOI is `10.5281/zenodo.20119473`.

The project is released under the MIT License; see `LICENSE`.
