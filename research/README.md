# Prime Reciprocal Covering Research Package

This directory contains the reproducible research package for Prime Reciprocal
Covering (PRC). The current citable public theorem release is the scoped v2.5
finite aperture-orbit separator theorem. The v2.3.0 DOI release remains an
immutable foundational critical-radius and gap-aperture birth-dynamics artifact.
The active next research line is v2.6 source-only Gate R work on special point
obstruction.

The PrimeClock visualization is origin/discovery context for the research.
Public release bundles contain finite residue-covering research artifacts and
exact certificate verifiers, not the React/Vite visualization app.

The Python package keeps the historical name `prime-reciprocal-projection`.
The finite theorem bundle is framed as Prime Reciprocal Covering.

## Current Release Entry Point

For the current v2.5 public theorem release, read these files first:

1. `experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_readme_v1_0.md`
2. `experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_release_notes_v1_0.md`
3. `experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_draft_v0_1.md`
4. `experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_citation_v1_0.cff`
5. `../release/public/release_registry.json`
6. `../VERSION_MAP.md`

The v2.5 theorem is limited to the recorded complete `B4->B5`, `B5->B6`, and
`B6->B7` transition scopes. It proves a finite exact terminal containment
certificate on committed checked rows, not a general predictor.

## Active Source-Only Research Line

v2.6 is not a public release, DOI artifact, B8 theorem, general predictor, or
asymptotic law. Its current Gate R direction is special point obstruction:
forbidden special remainders, central endpoint obstruction, and mod 6 ancestry
diagnostics.

Start here:

1. `experiments/critical_radius_birth_dynamics/notes/prc_v2_6_research_seed_note_v0_1.md`
2. `experiments/critical_radius_birth_dynamics/notes/prc_v2_6_special_point_obstruction_gate_r_v0_1.md`
3. `experiments/critical_radius_birth_dynamics/candidate_workflow_v2_6_v0_1.yml`

Run the source-only v2.6 Gate R checks from the repository root:

```bash
python3 scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_6_v0_1.yml \
  quick
```

## Foundational v2.3 Entry Point

Read these files in order:

1. `experiments/critical_radius_birth_dynamics/notes/prc_v2_3_theorem_note_draft_v0_1.md`
2. `experiments/critical_radius_birth_dynamics/notes/prc_v2_3_related_work_v0_2.md`
3. `RELEASE_NOTES_v2_3_0.md`
4. `notes/prc_finite_certificate_note_v2_0.md`
5. `notes/claims_finite_c4_b5.md`
6. `../VERSION_MAP.md`

The public package supports:

- `C_4={2,208} mod 210`;
- `C_5` has `36` covered residues;
- `C_k` is the `1/2` level set of the exact critical-radius spectrum for the
  checked `k=4,5` layers;
- `B_5`, `B_6`, and `B_7` are unique strict single-gap births in the checked
  finite data;
- near-miss rank is a diagnostic candidate generator, while birth is decided by
  next-prime `q`-grid phase alignment through the gap-aperture window.

These are finite certificate claims only. Broader asymptotic, distributional,
and complete PRC questions are outside the v2.3.0 release scope.

## Verify The v2.3.0 Package

Use a local editable install for the package verifier and tests:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
```

Run the v2.3.0 checks:

```bash
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

The original finite `C_4/B_5` verifier path is preserved in
`VERIFY_FINITE_C4_B5.md`.

## Included v2.3.0 Data

The release-facing v2.3.0 CSVs are under:

```text
experiments/critical_radius_birth_dynamics/data/
```

The key tables are the `k=4,5` critical-radius spectrum, the
`B_5/B_6/B_7` birth-dynamics table, the threshold-crossing table, near-miss
diagnostics, and the helper/standalone verification CSVs.

## Full Repository Context

The full repository also contains earlier PRC diagnostics, certificate-depth
experiments, `B_8` or larger exploratory directions, branch-fill experiments,
branch-uniform null comparisons, and residual-fragmentation studies. Those
remain useful context, but they are not part of the v2.3.0 public release
bundle.

Use `PUBLIC_RELEASE_MANIFEST.md` before preparing a public release bundle.

## Non-Claims

This package is finite. It does not claim an asymptotic law, a
prime-distribution theorem, a theorem that all future births are single-gap
births, or a complete solution of PRC.
