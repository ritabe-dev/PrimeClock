# PRC Main Roadmap

Objective: keep Prime Reciprocal Covering focused on reproducible covering
metrics, not on selected-number interpretation.

## v0.3 Fixed Axis

Primary object:

```text
I_p(N) = [{N/p}-1/(2p), {N/p}+1/(2p)] on T
U_N    = union_{p<=N, p prime} I_p(N)
A(N)   = |T \ U_N|
```

Branch fill-in notation:

```text
B_k(N)      = {p prime : floor(N/p)=k}
U_{<=K}(N)  = union of arcs from branches 1..K
A_{<=K}(N)  = |T \ U_{<=K}(N)|
A_full(N)  = A(N)
```

Deliverables:

- `data/summaries/prc_branch_fill_v0_3.csv`
- `data/summaries/prc_branch_fill_summary_v0_3.csv`
- `figures/v0/prc_branch_fill_residual_v0_3.png`
- `figures/v0/prc_branch_fill_fraction_v0_3.png`
- `figures/v0/prc_branch_fill_manifest.json`
- `notes/prc_main_v0_3.md`

Commands:

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill \
  --n 1000 10000 100000 1000000 39069 372759 \
  --max-branch 1000 \
  --out data/summaries/prc_branch_fill_v0_3.csv

python -m prime_reciprocal_projection.cli covering-branch-fill-summary \
  --input data/summaries/prc_branch_fill_v0_3.csv \
  --out data/summaries/prc_branch_fill_summary_v0_3.csv

python -m prime_reciprocal_projection.cli covering-branch-fill-figures \
  --input data/summaries/prc_branch_fill_v0_3.csv \
  --out figures/v0
```

Validation:

```bash
python -m ruff check src tests
python -m pytest
```

## v0.4 Comparison Cohorts

Goal: test whether branch fill-in depth differs between complete-covering
values and controls.

Cohorts:

- exact-complete cohort from certified `N<=10^6` results
- local matched controls near each complete-covering value
- controls matched by log-N band and `N mod 6`
- ordinary random controls from the same broad range

Planned outputs:

- `data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv`
- `data/summaries/prc_branch_fill_cohort_summary_v0_4.csv`
- `data/summaries/prc_branch_fill_cohort_checkpoints_v0_4.csv`
- `figures/v0/prc_branch_fill_cohort_k_depth_v0_4.png`
- `figures/v0/prc_branch_fill_cohort_residual_v0_4.png`
- `figures/v0/prc_branch_fill_cohort_checkpoint_fill_v0_4.png`
- `notes/prc_main_v0_4.md`

Current v0.4 reading:

- 36 complete seeds were selected, 3 from each of 12 log-N bins.
- All seeds received all 3 matched controls.
- Complete values do not look like simple early-fill cases in this cohort;
  median residual at `K=1000` is slightly higher than the three control groups.
- This is an experiment-level observation, not a general explanation.

## v0.5 Modeling

Goal: compare the observed fill-in curve against null/control models.

Candidate models:

- independent random arcs with matched total arc width
- branch-wise shuffled centers with fixed branch sizes
- local-window controls that preserve nearby prime-count fluctuations

Non-claims until v0.5:

- no claim that complete events are explained by branch fill-in speed
- no claim that the six v0.3 anchors are representative
- no claim that `K90/K99` has a stable asymptotic law

## Canonical Data Scope

Tracked research data for this stage should stay limited to top-level summary
CSVs under `data/summaries/`. Nested block-scan directories are resume artifacts,
not canonical research outputs, unless a manifest is added later.
