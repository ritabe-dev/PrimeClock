# Proof Sketch and Known-Result Map

Goal:

```text
mu_N => rho(x) dx
```

where

```text
mu_N = (1 / pi(N)) * sum_{p<=N, p prime} delta_{{N/p}}
rho(x) = sum_{k>=1} 1/(k+x)^2
```

## Meaning of the Limit

The limit is not primarily a new statement about hidden randomness in primes.
It is the first-order shadow of the prime number theorem under the nonlinear
map

```text
p -> {N / p}.
```

The map folds the interval of primes `p <= N` into infinitely many branches.
On each branch, the change of variables `p = N/(k+x)` contributes a Jacobian
factor `(k+x)^(-2)`. Summing the branch contributions gives `rho`.

In other words, the non-uniform density is caused by the reciprocal projection
itself. Prime irregularity appears only in finite-`N` errors around that
deterministic first-order shape.

## Branch Step

Fix `k >= 1`. On branch `k`,

```text
k <= N/p < k+1
```

so

```text
N/(k+1) < p <= N/k
```

and

```text
{N/p} = N/p - k
```

For an interval `[a,b]` in `[0,1)`, the condition `{N/p} in [a,b]` on branch
`k` becomes

```text
N/(k+b) <= p <= N/(k+a)
```

up to endpoint conventions.

## PNT Step

The prime number theorem estimates the number of primes in these intervals.
After normalization by `pi(N)`, the branch contribution approaches

```text
int_a^b 1/(k+x)^2 dx
```

Equivalently, for the CDF on `[0,a)`,

```text
mu_N([0,a) and branch k)
~ (pi(N/k) - pi(N/(k+a))) / pi(N)
-> 1/k - 1/(k+a).
```

Summing over `k` gives

```text
F(a) = sum_{k>=1} (1/k - 1/(k+a)).
```

Then

```text
F'(a) = sum_{k>=1} 1/(k+a)^2 = rho(a).
```

## Tail Step

After summing finitely many branches `k <= K`, the remaining tail corresponds
to primes `p <= N/K`. Its normalized mass is approximately

```text
pi(N/K) / pi(N) ~ 1/K
```

So the tail vanishes as `K -> infinity`.

## Result

Combining finite branches and tail control gives

```text
mu_N => rho(x) dx
```

## Known-Result Map

This convergence should not be presented as original.

Saffari--Vaughan I studies `{x/a}` over subsets `A` whose counting function has
regular variation:

```text
A(x) ~ x^sigma L(x).
```

Their example following Theorem 2 gives the full-range distribution function

```text
sum_{n>=1} (n^(-sigma) - (n+a)^(-sigma)).
```

For primes, `pi(x) ~ x/log x`, so this corresponds to `sigma = 1` with a slowly
varying factor `L(x)=1/log x`. Substituting `sigma = 1` gives

```text
F(a) = sum_{n>=1} (1/n - 1/(n+a)),
```

whose derivative is exactly PRP's

```text
rho(a) = sum_{n>=1} 1/(n+a)^2.
```

Saffari--Vaughan II gives a more direct prime-number treatment for `h(n)=1/n`.
Its prime section proves a weighted prime version and then states that partial
summation gives the unweighted case. For PRP v0, the safest citation path is:

```text
Saffari--Vaughan I for the CDF shape,
Saffari--Vaughan II for the prime-restricted formulation.
```
