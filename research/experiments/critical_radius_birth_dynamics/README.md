# Critical Radius and Birth Dynamics Sandbox

Status: internal-candidate.
Release eligibility: excluded from public release until promoted.

This experiment starts the post-v2.2.4 PRC research line. The public v2.2.4
release remains the stable `C_4/B_5` finite certificate artifact; files here are
internal research artifacts until explicitly promoted to a claim release.

## Purpose

- define the exact critical radius `lambda_k(r)` for prime-prefix residue
  coverings;
- verify `C_k = {r : lambda_k(r) <= 1/2}` for `k=4,5`;
- summarize the `k=4,5` spectrum and the `B_5/B_6/B_7` threshold crossings;
- list the nearest uncovered `k=4,5` residues just above `lambda=1/2`;
- compare those near-miss residues with the next birth layer's parent residues;
- expose the q-grid phase that decides whether a near-miss can birth;
- express births through old residual gap-aperture windows;
- classify `B_5`, `B_6`, and `B_7` births as strict/endpoint and
  single-gap/multi-gap events, with unique strict single-gap remainders in the
  checked layers.

## Read First

Start with:

```text
notes/prc_v2_3_internal_candidate_status.md
notes/prc_v2_3_research_review_note_v0_1.md
promotion_manifest_v0_1.yml
candidate_workflow_v0_1.yml
notes/prc_v2_3_theorem_note_draft_v0_1.md
notes/prc_v2_3_theorem_candidate_outline_v0_1.md
notes/prc_weighted_covering_radius_terminology_v0_1.md
notes/prc_weighted_bisector_candidate_lemma_v0_1.md
notes/prc_v2_3_related_work_decision_v0_1.md
notes/prc_v2_3_related_work_v0_2.md
notes/prc_v2_3_standalone_checker_contract_v0_1.md
notes/prc_near_miss_birth_predictor_v0_2.md
notes/prc_critical_radius_birth_dynamics_v0_1.md
```

The status note summarizes the current internal milestone. The research review
note records Gate R: whether the research story is worth packaging before
artifact integrity checks start. The promotion
manifest fixes the candidate scope: critical-radius layers `k=4,5`, birth
dynamics layers `k=5,6,7`, and no `B_8` or asymptotic claims. The candidate
workflow config drives the reusable non-publishing quick, bundle, slow,
research-review, artifact-freshness, manifest-consistency, and
promotion-readiness gates. The
theorem-note draft is the first compact public-candidate-shaped text, still internal. The
outline records the three selected components: critical radius, level sets, and
birth containment. The terminology note keeps `critical radius` as the primary
project term and treats `weighted covering-radius` as descriptive shorthand.
The bisector note records the finite candidate lemma behind the exact
critical-radius checker. The related-work decision note keeps bibliography
expansion from blocking internal candidate review while preserving the public
release boundary. The related-work note records the minimal formal references
for public-candidate review. The standalone checker contract records the
standard-library audit added for the v2.3 candidate CSVs. The v0.2 note
explains how near-miss ranking connects to birth-parent gap geometry.

## Generate

From `research/`:

```bash
.venv/bin/python experiments/critical_radius_birth_dynamics/generate.py
```

Generated CSVs live in `data/` inside this experiment directory. They are not
part of the v2.2.4 public release bundle.

## Quick Verification

From `research/`:

```bash
.venv/bin/python experiments/critical_radius_birth_dynamics/check_candidate_standalone.py \
  --out /tmp/prc-v2.3-standalone-check.csv
.venv/bin/python -m pytest tests/test_critical_radius_birth_dynamics.py -q -m "not slow and not bundle"
```

Expected result:

```text
check_v2_3_candidate_standalone: checks=10, failed=0
quick pytest: 36 passed, 29 deselected
```

This is the path intended for external reviewers who want a short check. The
standalone checker uses only the Python standard library, reads the committed
CSVs, verifies the candidate CSV SHA256 manifest including its expected file
set, recomputes the k=4,5 critical-radius values from the definition, and
checks the headline finite claims from those rows. The quick pytest path avoids
helper regeneration, candidate package build/check tests, and nested ZIP
verification.

The standalone checker is a CSV/hash/headline finite-claim audit. It is not a
full independent regeneration of every `B_5/B_6/B_7` birth layer; that remains
the role of the internal slow regression checker. Do not read
`checks=10, failed=0` as a claim that every birth layer was independently
regenerated.

## Bundle Verification

Run this only when checking package hygiene or a generated candidate package:

```bash
.venv/bin/python experiments/critical_radius_birth_dynamics/candidate_bundle.py \
  --check <printed-candidate-package-directory>
.venv/bin/python experiments/critical_radius_birth_dynamics/candidate_bundle.py --zip
unzip -t <printed-candidate-zip-path>
```

The direct `--check` command is the primary package hygiene check for reviewers.
The `--zip` command prints the ZIP path; use that printed path with `unzip -t`.

For CI or internal hygiene testing, also run:

```bash
.venv/bin/python -m pytest tests/test_critical_radius_birth_dynamics.py -q -m "bundle and not slow"
```

Expected bundle pytest result:

```text
bundle pytest: 18 passed, 47 deselected
```

The nested self-contained ZIP test is slower and belongs to the full internal
verification path below.

## Full Internal Verification

From `research/`:

```bash
.venv/bin/python experiments/critical_radius_birth_dynamics/check_candidate.py \
  --progress --out /tmp/prc-v2.3-helper-check.csv
.venv/bin/python -m pytest tests/test_critical_radius_birth_dynamics.py -q -m slow
```

Expected result:

```text
check_v2_3_candidate: checks=13, failed=0
slow pytest: 11 passed, 54 deselected
```

The helper checker is an internal slow regression checker. It recomputes the
current v2.3 candidate rows from the exact helpers and compares them with the
committed internal CSV artifacts. The slow pytest path includes heavier
recomputation and the nested candidate ZIP self-contained check; run it before
promotion, not as the default quick review path.

## Reusable Candidate Workflow

From the repository root, the shared candidate workflow engine can run the same
gates from `candidate_workflow_v0_1.yml`:

```bash
research/.venv/bin/python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v0_1.yml \
  research-review
research/.venv/bin/python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v0_1.yml \
  quick
research/.venv/bin/python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v0_1.yml \
  artifact-freshness
research/.venv/bin/python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v0_1.yml \
  manifest-consistency
research/.venv/bin/python scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v0_1.yml \
  process-hygiene
```

The gates answer separate questions:

```text
Gate R: Is this research story worth packaging?
Gate C: Is this package reproducible and clean?
Gate P: Is this stable enough to cite?
```

The workflow engine is non-publishing. It may build temporary candidate
packages and readiness reports, but it must not create tags, GitHub Releases,
or Zenodo archives. The research-review gate is intentionally upstream of ZIP,
hash, manifest, and reproducibility checks; it records the research decision
without treating package validity as research value. The process-hygiene gate
checks PR/report status metadata, schedule timezone labels, and candidate-facing
wording without adding work report metadata to the candidate README. Future
candidates should add a new workflow config and research review note instead of
hard-coding their scope into the engine.

## Dependency Note

The candidate package is verified through `python -m pip install -e ".[dev]"`.
The repository-level `uv.lock` is not part of this candidate package and is not
required for the quick or full verification paths.

## Candidate Bundle Check

`candidate_bundle.py` writes `BUNDLE_FILE_MANIFEST.txt` into each generated
candidate package. That file is an accidental file-drift guard: `--check`
compares the current package payload against the recorded payload list and then
verifies `SHA256SUMS`. It is not an external signature. A clean candidate
package is preferred, but local Python cache and install metadata directories
produced by verification commands, such as `__pycache__`, `.pytest_cache`,
`*.egg-info`, and `*.dist-info`, are ignored by `--check`.

## Candidate Scope

The current internal promotion manifest fixes the first v2.3 candidate scope:

```text
critical radius: k=4,5
birth dynamics: k=5,6,7
near-miss discussion: k=4,5
no B_8 or larger layers
no asymptotic or prime-distribution claims
```

## Candidate Bundle

An internal candidate bundle can be generated without touching the v2.2.4 public
release line:

```bash
.venv/bin/python experiments/critical_radius_birth_dynamics/candidate_bundle.py --zip
.venv/bin/python experiments/critical_radius_birth_dynamics/candidate_bundle.py \
  --check <printed-candidate-package-directory>
```

This bundle has its own `SHA256SUMS` and is for internal promotion testing only.
The default output parent is `tempfile.gettempdir() / "prc-v2.3-candidate-latest"`.
The command prints the exact candidate package, ZIP, path note, and local-link
note paths after generation. Use `--out` to choose a stable output directory.

## Current Status

This is an internal v2.3 candidate, not a public release. It makes finite claims
only for the generated levels and does not assert an asymptotic law or a general
birth theorem beyond the exact containment identity.
