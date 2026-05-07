# Known Results Check

This note records how Prime Reciprocal Projection (PRP) relates to existing
work. It is intentionally conservative: the basic limiting density is treated
as known unless a specialist reviewer identifies a gap.

## PRP Object

PRP studies

```text
Phi_N(p) = {N / p},  p prime, p <= N
```

and the empirical measure

```text
mu_N = (1 / pi(N)) * sum_{p<=N, p prime} delta_{Phi_N(p)}.
```

The observed limiting density is

```text
rho(x) = sum_{k>=1} 1/(k+x)^2.
```

## Main Match

Saffari--Vaughan I gives a general framework for fractional parts `{x/a}` where
`a` ranges over a subset `A` of the positive integers. In the example following
their Theorem 2, if the counting function has the regular-variation form

```text
A(x) ~ x^sigma L(x),
```

then the full-range distribution has CDF

```text
F_sigma(a) = sum_{n>=1} (n^(-sigma) - (n+a)^(-sigma)).
```

For primes,

```text
pi(x) ~ x/log x,
```

so this is the case `sigma = 1` with a slowly varying factor. Therefore

```text
F(a) = sum_{n>=1} (1/n - 1/(n+a)).
```

Differentiating gives

```text
F'(a) = sum_{n>=1} 1/(n+a)^2 = rho(a).
```

This is the same density used in PRP.

## Prime-Specific Match

Saffari--Vaughan II has a section on prime numbers for the standard case
`h(n)=1/n`. Their Theorem 10 gives a weighted prime estimate, and the following
paragraph says that partial summation gives the unweighted prime version. This
is closer to the PRP normalization, because PRP gives each prime equal mass.

The exact notation differs:

| PRP | Saffari--Vaughan style |
|---|---|
| `N` | large parameter `x` |
| prime `p <= N` | prime order in the range up to `y`, with `y=x` for full range |
| `{N/p}` | fractional part of `x/p` |
| `mu_N([0,a))` | prime-counting distribution function at `a` |
| `rho(a)` | derivative of the limiting CDF |

## What This Means

The limit density is not the new mathematical content of PRP. It is a known or
standard consequence of the fractional-parts literature and the prime number
theorem.

The useful interpretation is:

1. The reciprocal projection `p -> {N/p}` folds primes into branches
   `floor(N/p)=k`.
2. Each branch contributes a deterministic density `1/(k+x)^2`.
3. The total first-order shape is `rho(x)`.
4. The remaining research object is the finite-`N` error around this shape.

This shifts PRP's research focus from "discovering a new prime distribution" to
the following more defensible questions:

- How quickly do PRP's histogram, KS, and Fourier diagnostics approach the
  known limiting density?
- Does the PNT correction model explain finite-`N` behavior better than the
  limit density alone?
- Can branch-level errors be related to prime counts in the intervals
  `(N/(k+1), N/k]`?
- Are Fourier residuals merely generic finite-size errors, or do they expose a
  useful diagnostic of short-interval prime fluctuations?

## Safe External Wording

Use wording like:

```text
PRP is an experimental notation and visualization for a known fractional-parts
phenomenon: the distribution of {N/p} over primes p <= N. The limiting density
matches the Saffari--Vaughan framework for fractional parts of x/n and related
sequences. The current project focuses on finite-N diagnostics, branch
decomposition, and Fourier error structure rather than claiming a new limiting
law.
```

