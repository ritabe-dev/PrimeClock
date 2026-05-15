# PrimeClock Public Releases

<!-- BEGIN GENERATED PUBLIC SURFACE -->
This repository publishes finite Prime Reciprocal Covering (PRC) artifacts and
their verification tooling. The current public theorem release is
`v2.7.1-prc-general-q-prime-theorem`. Its Zenodo DOI state is `10.5281/zenodo.20209528`.
The latest DOI-backed public theorem release is `v2.7.1-prc-general-q-prime-theorem`.
<!-- END GENERATED PUBLIC SURFACE -->

## Current Public Theorem Release

```text
v2.7.1-prc-general-q-prime-theorem
PRC v2.7.1: General q-Prime Single-Gap Aperture Classification Theorem
Version DOI: 10.5281/zenodo.20209528
GitHub Release: https://github.com/ritabe-dev/PrimeClock/releases/tag/v2.7.1-prc-general-q-prime-theorem
Release asset: PrimeClock-v2.7.1-general-q-prime-theorem-v1.0.zip
```

The current theorem is a structural theorem inside the PRC circular-arc model.
For every `k >= 3`, every old residue `r in Z/M_kZ`, and every later odd prime
modulus `q>p_k`, a nonempty q-birth lift is exactly a single residual gap plus
q-grid aperture alignment.

The result is a direct one-prime q-lift theorem over the old prefix. For
`q != p_{k+1}`, it does not claim that intermediate sequential PRC transitions
are skipped or unchanged. The exact audit is a recorded birth rows consistency
audit, not a full finite-universe completeness audit and not the proof of the
general q-prime theorem.

Read these current release files first:

1. `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_7_public_theorem_release_readme_v1_0.md`
2. `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_7_public_theorem_release_notes_final_v1_0.md`
3. `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_7_general_single_gap_aperture_theorem_note_v0_1.md`
4. `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_7_public_theorem_release_citation_v1_0.cff`

The current release does not claim a B8 theorem, a full transition-graph
theorem, a general predictor, an asymptotic law, a prime-gap theorem outside
the PRC model, or a full finite-universe completeness audit.

## Latest DOI-Backed Public Theorem Release

```text
v2.7.1-prc-general-q-prime-theorem
PRC v2.7.1: General q-Prime Single-Gap Aperture Classification Theorem
Version DOI: 10.5281/zenodo.20209528
GitHub Release: https://github.com/ritabe-dev/PrimeClock/releases/tag/v2.7.1-prc-general-q-prime-theorem
Release asset: PrimeClock-v2.7.1-general-q-prime-theorem-v1.0.zip
```

This is the same release as the current public theorem release.

## Foundational Public Release

The older `v2.3.0` release remains an immutable foundational DOI release for the
finite `C_k/C_4/B_5` certificate artifact plus the v2.3 critical-radius and
gap-aperture birth-dynamics finite artifact.

```text
v2.3.0
Version DOI: 10.5281/zenodo.20119473
Concept DOI: 10.5281/zenodo.20091722
GitHub Release: https://github.com/ritabe-dev/PrimeClock/releases/tag/v2.3.0
```

The v2.3 finite claims are:

- `C_4={2,208} mod 210`;
- `C_5` has `36` covered residues;
- `Lift_5(C_4)` has `22` inherited residues;
- `B_5` has `14` births in `7` reflection pairs;
- every `B_5` birth is a strict single-gap closure by the new `p=11` arc;
- `C_k` is the `1/2` level set of the exact critical-radius spectrum for the
  checked `k=4,5` layers;
- `B_5`, `B_6`, and `B_7` are unique strict single-gap births in the checked
  finite data.

The v2.3 public bundle README template remains at
`release/public/README.template.md`; it is intentionally v2.3-specific.

## Research Position

Prime Reciprocal Covering is a project-defined finite prime-prefix
circle-covering model. For each residue class and each prime in a prefix, it
places a rational closed arc on `R/Z` centered at `(r mod p)/p`; the public
claims are about exactly stated PRC model artifacts.

The vocabulary is adjacent to classical covering systems of congruences because
it uses residues, moduli, and covering language, but this repository does not
claim a result about classical covering systems. The related-work boundary note
`research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_related_work_v0_2.md`
records nearby terminology and literature context.

Zenodo DOIs identify citable archived snapshots of this finite artifact. They
do not imply peer review.

## Verify

From the repository root, verify release metadata and public release guardrails:

```bash
python3 scripts/render_public_surface.py --check
python3 scripts/check_release_doi_integrity.py --all
python3 scripts/verify_public_release_execution_preflight.py --all
```

Expected focused result:

```text
failed=0
```

For the current theorem release bundle, use:

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_7_public_theorem_release.py
python3 scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/public_theorem_release_bundle_workflow_v2_7_v1_0.yml \
  public-theorem-review
```

For the v2.3 foundational verifier path, use `research/`:

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

## Public Release Bundles

Public releases are built from explicit allowlists. The source repository can
contain broader research history, but each public release bundle contains only
the files listed by its release manifest or registry entry.

Build and inspect the current theorem release bundle with:

```bash
research/.venv/bin/python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/public_theorem_release_workflow_v2_7_v1_0.yml \
  public-theorem-review
```

Build and inspect the v2.3 public bundle with:

```bash
python3 scripts/check_release_versions.py
python3 scripts/verify_public_release.py --out "${TMPDIR:-/tmp}/primeclock-public-release" --zip
```

## Citation and License

Use the current release-specific `CITATION.cff` for DOI-backed references.

The top-level `CITATION.cff` remains the v2.3.0 citation metadata. Its
top-level DOI is the Zenodo concept DOI for the v2.3 release series:
`10.5281/zenodo.20091722`; the v2.3.0 version DOI is
`10.5281/zenodo.20119473`.

The project is released under the MIT License; see `LICENSE`.
