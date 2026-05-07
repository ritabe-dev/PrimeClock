# Prime Reciprocal Projection

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

