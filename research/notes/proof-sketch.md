# Proof Sketch

Goal:

```text
mu_N => rho(x) dx
```

where

```text
mu_N = (1 / pi(N)) * sum_{p<=N, p prime} delta_{{N/p}}
rho(x) = sum_{k>=1} 1/(k+x)^2
```

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

This sketch must still be checked against known results before it is presented
as original.

