# Definitions

This note fixes the vocabulary for Prime Reciprocal Projection (PRP).

## Prime Reciprocal Projection

For an integer `N >= 2` and a prime `p <= N`, define

```text
Phi_N(p) = {N / p}
```

where `{x} = x - floor(x)` is the fractional part in `[0, 1)`.

The empirical measure is

```text
mu_N = (1 / pi(N)) * sum_{p<=N, p prime} delta_{Phi_N(p)}
```

This is a probability measure on `[0, 1)`.

## Limit Density

The expected limiting density is

```text
rho(x) = sum_{k>=1} 1 / (k + x)^2,  0 <= x < 1
```

It is normalized because

```text
int_0^1 rho(x) dx
= sum_{k>=1} (1/k - 1/(k+1))
= 1
```

## Branch

Branch `k` is

```text
B_{N,k} = {p prime : N/(k+1) < p <= N/k}
```

Equivalently, it is the set of primes with `floor(N / p) = k`.

The limiting branch mass is

```text
w_k = 1 / (k(k+1))
```

