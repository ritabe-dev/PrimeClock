# Critical Radius and Birth Dynamics Sandbox

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
- expose the old-gap geometry that decides whether a near-miss can birth;
- express births as old residual gaps contained in the new prime arc;
- classify `B_5`, `B_6`, and `B_7` births as strict/endpoint and
  single-gap/multi-gap events.

## Read First

Start with:

```text
notes/prc_v2_3_internal_candidate_status.md
promotion_manifest_v0_1.yml
notes/prc_v2_3_theorem_note_draft_v0_1.md
notes/prc_v2_3_theorem_candidate_outline_v0_1.md
notes/prc_weighted_covering_radius_terminology_v0_1.md
notes/prc_weighted_bisector_candidate_lemma_v0_1.md
notes/prc_v2_3_related_work_decision_v0_1.md
notes/prc_v2_3_standalone_checker_contract_v0_1.md
notes/prc_near_miss_birth_predictor_v0_2.md
notes/prc_critical_radius_birth_dynamics_v0_1.md
```

The status note summarizes the current internal milestone. The promotion
manifest fixes the candidate scope: critical-radius layers `k=4,5`, birth
dynamics layers `k=5,6,7`, and no `B_8` or asymptotic claims. The theorem-note
draft is the first compact public-candidate-shaped text, still internal. The
outline records the three selected components: critical radius, level sets, and
birth containment. The terminology note keeps `critical radius` as the primary
project term and treats `weighted covering-radius` as descriptive shorthand.
The bisector note records the finite candidate lemma behind the exact
critical-radius checker. The related-work decision note keeps bibliography
expansion from blocking internal candidate review while preserving the public
release boundary. The standalone checker contract records the standard-library
audit added for the v2.3 candidate CSVs. The v0.2 note explains how near-miss
ranking connects to birth-parent gap geometry.

## Generate

From `research/`:

```bash
.venv/bin/python experiments/critical_radius_birth_dynamics/generate.py
```

Generated CSVs live in `data/` inside this experiment directory. They are not
part of the v2.2.4 public release bundle.

## Check

From `research/`:

```bash
.venv/bin/python experiments/critical_radius_birth_dynamics/check_candidate.py
.venv/bin/python experiments/critical_radius_birth_dynamics/check_candidate_standalone.py
```

Expected result:

```text
check_v2_3_candidate: checks=12, failed=0
check_v2_3_candidate_standalone: checks=7, failed=0
```

The first checker is helper-based and internal. It recomputes the current v2.3
candidate rows from the exact helpers and compares them with the committed
internal CSV artifacts. The standalone checker uses only the Python standard
library, reads the committed CSVs, verifies the candidate CSV SHA256 manifest,
and checks the headline finite claims from those rows.

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
.venv/bin/python experiments/critical_radius_birth_dynamics/candidate_bundle.py \
  --out /private/tmp/primeclock-v2-3-candidate
.venv/bin/python experiments/critical_radius_birth_dynamics/candidate_bundle.py \
  --check /private/tmp/primeclock-v2-3-candidate/PrimeClock-v2.3-candidate-v0.1
```

This bundle has its own `SHA256SUMS` and is for internal promotion testing only.

## Current Status

This is an internal v2.3 candidate, not a public release. It makes finite claims
only for the generated levels and does not assert an asymptotic law or a general
birth theorem beyond the exact containment identity.
