# Prime Reciprocal Projection / Covering

Prime Reciprocal Projection (PRP) is the research track that grew out of the
former PrimeClock visualization. The clock artwork stays in the React/Vite app;
this directory is for reproducible mathematical experiments, notes, figures,
and tests.

The core object is

```text
Phi_N(p) = {N / p},  p prime, p <= N
mu_N = (1 / pi(N)) * sum_{p<=N, p prime} delta_{Phi_N(p)}
```

where `N >= 2` is an integer and `{x}` is the fractional part in `[0, 1)`.

The current external-review focus is Prime Reciprocal Covering (PRC), not the
clock artwork and not a novelty claim for the PRP limiting density. PRC is now
framed as a finite-`N` hierarchy of prime residue-cell coverings: each prime
`p <= N` selects the cell indexed by `N mod p` on the `p`-partitioned circle and
places an arc of width `1/p` there.

The main object is the residual uncovered set left by this finite hierarchy:
the uncovered measure `A(N)`, residual components, and gap shape. Complete
covering is a boundary/certificate case of this process, not the external
claim by itself.

## External Review Entry Point

Read in this order:

1. `notes/prc_research_note_v1_0_ja.md` for the current integrated PRC note.
2. `notes/claims.md` for claim categories and non-claims.
3. `notes/known-results.md` for the PRP relationship to Saffari--Vaughan style
   fractional-parts results.
4. `notes/prc_main_v0_9.md` for the first branch-uniform null comparison.
5. `PUBLIC_ARTIFACTS.md` before creating or reviewing a public zip.

Canonical PRC v1 artifacts:

- `data/summaries/prc_branch_fill_v0_3.csv`
- `data/summaries/prc_branch_fill_summary_v0_3.csv`
- `data/summaries/prc_branch_fill_residual_gaps_v0_5.csv`
- `data/summaries/prc_branch_uniform_null_summary_v0_9.csv`
- `figures/v0/prc_branch_fill_residual_v0_3.png`
- `figures/v0/prc_branch_fill_residual_gap_count_v0_5.png`
- `figures/v0/prc_branch_uniform_null_percentile_v0_9.png`
- `figures/v0/prc_branch_uniform_null_deviation_v0_9.png`

Conservative summary: PRC is best read as a finite residue-covering hierarchy.
The current finite cohort suggests that its residual sets look more fragmented
than the first coarse branch-uniform null. This is not a theorem about primes,
not a complete-covering law, and not a final null model. Complete covering and
anti-clustering remain useful forensic subproblems, not the main PRC axis.

## Scope

v0 is intentionally conservative:

- no MATLAB
- no Mathematica
- no GPU or numba
- no browser dashboard
- no React integration
- no claim of a new theorem about prime distribution

The v0 goal is a small, testable Python package plus notes that separate
definitions, exact identities, models, experiments, conjectures, rejected
claims, and non-claims.

## Current Research Frame

The hierarchy language separates three related layers:

- **Prime-prefix hierarchy**: add arcs from primes `p <= P`. This is the main
  finite residue-covering object.
- **Branch hierarchy**: group arcs by `floor(N/p)=k`. This is an existing
  diagnostic layer for fill-in behavior.
- **Primorial / wheel hierarchy**: study residues modulo `Q_P = prod_{p<=P} p`.
  This explains deterministic small-prime strata and certificate side cases.

Residual fragmentation belongs to the main object as a diagnostic of the
uncovered set. `C0`, certificate depth, and anti-clustering stay downstream as
boundary/certificate or forensic analyses.

## Setup

`uv` is the preferred environment manager when available:

```bash
cd research
uv sync --extra dev
uv run pytest
uv run python -m prime_reciprocal_projection.cli figures --out figures/v0
```

If `uv` is not installed, use standard Python:

```bash
cd research
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
python -m prime_reciprocal_projection.cli figures --out figures/v0
```

Expected smoke-test result for the current suite is `116 passed`.

## First Experiments

The default v0 grid is:

```text
N = 10^3, 10^4, 10^5, 10^6
bins = 100
Fourier modes = 0..20
```

For `N=1000`, the histogram is too sparse for a main visual. Use CDF/KS and
Fourier diagnostics first, and reserve 100-bin histogram figures for
`N >= 100000`.

## PRC Covering Metrics

Main baseline columns:

- `random_arc_baseline`: legacy column equal to `poisson_arc_baseline`.
- `poisson_arc_baseline`: `exp(-sum_{p<=N} 1/p)`, a Poissonized rough scale.
- `product_arc_baseline`: `prod_{p<=N}(1 - 1/p)`, the fixed-point baseline for
  independent uniformly centered arcs.

Regenerate core PRC covering metrics:

```bash
python -m prime_reciprocal_projection.cli covering-metrics \
  --out data/summaries/prc_v0_covering.csv
python -m prime_reciprocal_projection.cli covering-metrics \
  --log-grid 1000 1000000 50 \
  --out data/summaries/prc_v0_covering_log_grid.csv
```

Regenerate the v0.9 branch-uniform null only when a long run is acceptable:

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill-null-model \
  --manifest data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv \
  --observed data/summaries/prc_branch_fill_residual_gaps_v0_5.csv \
  --model branch_uniform \
  --max-branch 1000 \
  --iterations 1000 \
  --seed 1729 \
  --out data/summaries/prc_branch_uniform_null_v0_9.csv \
  --summary-out data/summaries/prc_branch_uniform_null_summary_v0_9.csv \
  --figures-out figures/v0
```
