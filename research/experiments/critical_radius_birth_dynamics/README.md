# Critical Radius and Birth Dynamics Sandbox

This experiment starts the post-v2.2.3 PRC research line. The public v2.2.3
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
notes/prc_v2_3_theorem_note_draft_v0_1.md
notes/prc_v2_3_theorem_candidate_outline_v0_1.md
notes/prc_near_miss_birth_predictor_v0_2.md
notes/prc_critical_radius_birth_dynamics_v0_1.md
```

The status note summarizes the current internal milestone and promotion
boundary. The theorem-note draft is the first compact public-candidate-shaped
text, still internal. The outline records the three selected components:
critical radius, level sets, and birth containment. The v0.2 note explains how
near-miss ranking connects to birth-parent gap geometry. The v0.1 integrated
note gives the broader critical-radius and birth-dynamics context. The shorter
companion notes split the v0.1 content into the critical-radius and
birth-dynamics sides.

## Generate

From `research/`:

```bash
.venv/bin/python experiments/critical_radius_birth_dynamics/generate.py
```

Generated CSVs live in `data/` inside this experiment directory. They are not
part of the v2.2.3 public release bundle.

## Check

From `research/`:

```bash
.venv/bin/python experiments/critical_radius_birth_dynamics/check_candidate.py
```

Expected result:

```text
check_v2_3_candidate: checks=11, failed=0
```

The checker recomputes the current v2.3 candidate rows from the exact helpers
and compares them with the committed internal CSV artifacts.

## Current Status

This is an internal v2.3 candidate, not a public release. It makes finite claims
only for the generated levels and does not assert an asymptotic law or a general
birth theorem beyond the exact containment identity.
