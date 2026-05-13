# PrimeClock Development Repository

This development repository is the working tree for PrimeClock and Prime
Reciprocal Covering (PRC). It can contain broader source history, local research
work, release tooling, and the small React/Vite visualization app in `src/`.

## Current Public Theorem Release

The current citable public theorem release is:

```text
v2.5.0-prc-public-theorem
PRC v2.5: finite aperture-orbit separator theorem
Version DOI: 10.5281/zenodo.20154561
GitHub Release: https://github.com/ritabe-dev/PrimeClock/releases/tag/v2.5.0-prc-public-theorem
Release asset: PrimeClock-v2.5-public-theorem-v1.0.zip
```

The v2.5 theorem is scoped to the recorded complete transition scopes
`B4->B5`, `B5->B6`, and `B6->B7`. Let `U` be the materialized finite universe of
committed checked rows in those scopes. The checked theorem is:

```text
Close(row) iff m(row) > 0
```

Here `m(row)` is the exact signed aperture-orbit containment margin. It is a
finite exact terminal containment certificate, not a general predictor.

Read these v2.5 files first:

1. `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_readme_v1_0.md`
2. `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_release_notes_v1_0.md`
3. `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_draft_v0_1.md`
4. `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_citation_v1_0.cff`
5. `release/public/release_registry.json`
6. `VERSION_MAP.md`

The v2.5 release does not claim a B8 theorem, B8 full graph, general predictor,
asymptotic law, coverage/recall/holdout validation for B8, or automatic
extension beyond the recorded complete transition scopes.

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
claims are about exactly checked finite residue layers.

The vocabulary is adjacent to classical covering systems of congruences because
it uses residues, moduli, and covering language, but this repository does not
claim a result about classical covering systems. The related-work boundary note
`research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_related_work_v0_2.md`
records nearby terminology and literature context.

Zenodo DOIs identify citable archived snapshots of this finite artifact. They
do not imply peer review.

## Version-Line Workflow

Do not duplicate the repository for new research lines. Keep shared source,
release tooling, and workflow engines in one repo, and version only the
research-line materials:

| Line | Status | Management |
| --- | --- | --- |
| `v2.3.0` | immutable foundational public DOI release | tag / GitHub Release / Zenodo snapshot; do not retag |
| `v2.4.x` | source-only bridge | no public release or DOI; preserves diagnostics that connect v2.3.0 to the next release line |
| `v2.5.0-prc-public-theorem` | current scoped public theorem DOI release | finite exact aperture-orbit separator theorem for recorded `B4->B5`, `B5->B6`, and `B6->B7` scopes |
| `v2.6.x` | next research line | must be registered in `release/public/release_registry.json` before DOI or GitHub Release work starts |
| `maintenance/v2.x.y` | rare patch line | branch from the published tag only for reproducibility, metadata, or finite-claim-impacting fixes |

The gates stay separate:

```text
Gate R: research story; source-only notes, pilot data, and research checkers
Gate C: candidate integrity; reproducible package and manifest hygiene
Gate P: public promotion; stable enough to cite and publish through GitHub/Zenodo
```

New public release lines must be added to `release/public/release_registry.json`
before DOI finalization. The registry is the source of truth for DOI, GitHub
Release URL, asset name, citation policy, and release metadata.

## Verify

From the repository root, verify the current v2.5 public theorem:

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_5_public_theorem_integrity.py
python3 scripts/check_release_doi_integrity.py --all
```

Expected v2.5 results:

```text
check_v2_5_public_theorem_integrity: checks=9, failed=0
check_release_doi_integrity: checked=2, failed=0
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

The v2.5 public theorem release bundle contains the scoped separator theorem
artifact and verifier. The v2.3 public release bundle contains the finite
`C_k/C_4/B_5` certificate artifact, the v2.3.0 critical-radius and gap-aperture
birth-dynamics artifact, and their verification paths.

Build and inspect the v2.3 public bundle with:

```bash
python3 scripts/check_release_versions.py
python3 scripts/verify_public_release.py --out "${TMPDIR:-/tmp}/primeclock-public-release" --zip
```

Build and inspect the v2.5 public theorem bundle with:

```bash
research/.venv/bin/python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/public_theorem_release_workflow_v2_5_v1_0.yml \
  public-theorem-review
```

## Citation and License

Use the v2.5 release-specific `CITATION.cff` for the current scoped public
theorem. Its Zenodo version DOI is `10.5281/zenodo.20154561`.

The top-level `CITATION.cff` remains the v2.3.0 citation metadata. Its
top-level DOI is the Zenodo concept DOI for the v2.3 release series:
`10.5281/zenodo.20091722`; the v2.3.0 version DOI is
`10.5281/zenodo.20119473`.

The project is released under the MIT License; see `LICENSE`.
