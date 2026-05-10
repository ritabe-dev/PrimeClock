# PRC v2.3 Internal Candidate Bundle

Status: internal-candidate.
Release eligibility: candidate package only; not a public release.

This internal candidate bundle contains the v2.3 critical-radius and
gap-aperture birth-dynamics research artifacts. It is not a public release.

For external reviewers, use the generated candidate ZIP:

```text
PrimeClock-v2.3-candidate-v0.1.zip
```

When generated from the source repo, the generator prints the exact local
candidate package, ZIP, path note, and local-link note paths. Use `--out` when a
stable output directory is needed.

The stable public release remains v2.2.4, focused on the `C_4/B_5` finite
certificate package. This candidate extends that line internally with:

- exact critical-radius spectra for `k=4,5`;
- `C_k = { r : lambda_k(r) <= 1/2 }` level-set checks;
- gap-aperture birth dynamics for `B_5`, `B_6`, and `B_7`;
- unique strict single-gap remainder checks for `B_5/B_6/B_7`;
- near-miss gap-geometry diagnostics for `k=4,5`;
- an internal helper-based candidate checker;
- a standard-library standalone CSV checker for the candidate artifacts.

## Quick Verification

From the bundle root:

```bash
cd research
python -m pip install -e ".[dev]"
python experiments/critical_radius_birth_dynamics/check_candidate_standalone.py \
  --out /tmp/prc-v2.3-standalone-check.csv
python -m pytest tests/test_critical_radius_birth_dynamics.py -q -m "not slow and not bundle"
```

Expected result:

```text
check_v2_3_candidate_standalone: checks=10, failed=0
quick pytest: 27 passed, 29 deselected
```

This quick path uses the standard-library standalone checker and lightweight
pytest checks. It avoids helper regeneration, candidate package build/check
tests, and nested ZIP verification.

The standalone checker is a CSV/hash/headline finite-claim audit. It is not a
full independent regeneration of every `B_5/B_6/B_7` birth layer; that remains
the role of the internal slow regression checker. Do not read
`checks=10, failed=0` as a claim that every birth layer was independently
regenerated.

## Bundle Verification

Run this only when checking package hygiene or a generated candidate package:

```bash
cd research
python experiments/critical_radius_birth_dynamics/candidate_bundle.py \
  --check <printed-candidate-package-directory>
python experiments/critical_radius_birth_dynamics/candidate_bundle.py --zip
unzip -t <printed-candidate-zip-path>
```

The direct `--check` command is the primary package hygiene check for reviewers.
The `--zip` command prints the ZIP path; use that printed path with `unzip -t`.

For CI or internal hygiene testing, also run:

```bash
python -m pytest tests/test_critical_radius_birth_dynamics.py -q -m "bundle and not slow"
```

Expected bundle pytest result:

```text
bundle pytest: 18 passed, 38 deselected
```

The nested self-contained ZIP test is slower and belongs to the full internal
verification path below.

## Full Internal Verification

From the bundle root:

```bash
cd research
python experiments/critical_radius_birth_dynamics/check_candidate.py \
  --progress --out /tmp/prc-v2.3-helper-check.csv
python -m pytest tests/test_critical_radius_birth_dynamics.py -q -m slow
```

Expected result:

```text
check_v2_3_candidate: checks=13, failed=0
slow pytest: 11 passed, 45 deselected
```

This is the full internal slow regression path. It is intended for promotion
checks, not for the default quick verification path.

The generated package includes `BUNDLE_FILE_MANIFEST.txt`. It is an accidental
file-drift guard used by `candidate_bundle.py --check`, not an external
signature. Local Python cache directories produced by verification commands are
ignored by `--check`. A clean candidate package is preferred, but local Python
cache and install metadata directories produced by verification commands, such
as `__pycache__`, `.pytest_cache`, `*.egg-info`, and `*.dist-info`, are ignored
by `--check`.

The candidate package is verified through `python -m pip install -e ".[dev]"`.
The repository-level `uv.lock` is not included or required.

## Reusable Candidate Workflow

Source checkouts include a reusable, non-publishing candidate workflow engine:

```bash
python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v0_1.yml \
  quick
python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v0_1.yml \
  artifact-freshness
python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v0_1.yml \
  manifest-consistency
```

This workflow may build temporary candidate packages and readiness reports, but
it must not create tags, GitHub Releases, or Zenodo archives. Future candidates
should add their own workflow config instead of changing the engine.

## Scope

This candidate is finite and intentionally narrow:

```text
critical radius: k=4,5
birth dynamics: k=5,6,7
near-miss discussion: k=4,5
no B_8 or larger layers
no asymptotic or prime-distribution claims
```

## Status

This bundle is for internal promotion testing only. It should not be cited as a
public release or uploaded to Zenodo.
