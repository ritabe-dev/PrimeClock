# Prime Reciprocal Projection: Two-Page Summary v0.1

## Overview

Prime Reciprocal Projection (PRP) is an experimental mathematical notation that
grew out of the former PrimeClock visualization. In the clock, the center phase
of the prime-indexed hand for a prime `p` at integer time `N` is

```text
{N / p}.
```

PRP isolates this phase and studies the point configuration obtained by
projecting primes `p <= N` into the unit interval `[0,1)`.

At this stage, no new theorem about the distribution of primes is claimed. The
goal is to define the object clearly, reproduce numerical experiments, and find
the correct relationship with existing results. The current known-result check
points first to Saffari--Vaughan's work on fractional parts of `x/n` and related
sequences.

## Definition

Fix an integer `N >= 2`. For each prime `p <= N`, define

```text
Phi_N(p) = {N / p},
```

where `{x}` denotes the fractional part in `[0,1)`.

Define the empirical measure

```text
mu_N = (1 / pi(N)) * sum_{p<=N, p prime} delta_{Phi_N(p)}.
```

This is a probability measure on `[0,1)`.

The expected limiting density is

```text
rho(x) = sum_{k>=1} 1 / (k + x)^2,  0 <= x < 1.
```

It is normalized because

```text
int_0^1 rho(x) dx
= sum_{k>=1} (1/k - 1/(k+1))
= 1.
```

The main limiting statement is the weak convergence

```text
mu_N => rho(x) dx  as N -> infinity.
```

This should not be claimed as a new PRP theorem. Saffari--Vaughan I treats
fractional parts `{x/a}` over sets `A` with regularly varying counting
functions; the primes fit this shape through `pi(x) ~ x/log x`. Saffari--Vaughan
II explicitly studies the standard case `h(n)=1/n` and includes a prime-number
version. The remaining task is to pin down the most precise theorem/corollary
to cite for this exact normalization.

Conceptually, `rho` is not a mysterious new distribution of primes. It is the
first-order shape created by the reciprocal projection and its branch structure.
The remaining mathematical object is the finite-`N` deviation from this known
limit, and whether that deviation is better explained through branch counts,
PNT corrections, or Fourier residuals.

## Branch Decomposition

The structure becomes clearer after decomposing by

```text
k = floor(N / p).
```

Branch `k` is

```text
B_{N,k} = { p prime : N/(k+1) < p <= N/k }.
```

On this branch,

```text
N / p = k + x,
x = {N / p},
p = N / (k + x).
```

The limiting branch mass is

```text
w_k = int_0^1 1/(k+x)^2 dx = 1/(k(k+1)).
```

Summing these branch contributions gives the limiting density `rho(x)`.

This branch view is useful because it explains the density shape rather than
only fitting a histogram.

## v0 Numerical Experiments

The v0 experiment uses

```text
N = 10^3, 10^4, 10^5, 10^6
bins = 100
Fourier modes = 1..20
```

The current convergence table is:

| N | pi(N) | histogram L1 | KS distance | branch L1 k<=20 | Fourier mean m<=20 |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 168 | 0.5417 | 0.0384 | 0.1438 | 0.0445 |
| 10,000 | 1,229 | 0.1915 | 0.0241 | 0.0759 | 0.0180 |
| 100,000 | 9,592 | 0.0548 | 0.0131 | 0.0583 | 0.0062 |
| 1,000,000 | 78,498 | 0.0219 | 0.0087 | 0.0488 | 0.0027 |

On this grid, histogram L1 error, KS distance, and mean low-frequency Fourier
residual all decrease as `N` grows. This supports the view that `mu_N` is
approaching the limit density `rho(x) dx`.

The branch error decreases more slowly. This is expected because branch masses
depend on prime counts in finite intervals `(N/(k+1), N/k]`, which still have
visible finite-N fluctuations.

## Non-Claims

At v0, the project does not claim:

- a new law of prime distribution;
- novelty of the limiting density `rho`;
- novelty of the weak convergence `mu_N => rho(x) dx`;
- visual evidence as proof;
- number-theoretic meaning for individual peaks in the Fourier residual plot.

## Questions for Review

The first review questions are:

1. Which theorem or corollary in Saffari--Vaughan I/II is the cleanest citation
   for the weak convergence `mu_N => rho(x) dx` over primes?
2. Are the finite-N correction, branch-error diagnostics, and Fourier
   diagnostics reasonable objects for an experimental mathematical note?

Depending on the answer, PRP should be framed either as a visualization and
reorganization of known theory, or as a short experimental note focused on
finite-N behavior and Fourier diagnostics.
