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

## Prime Reciprocal Covering

Prime Reciprocal Covering (PRC) keeps the PRP center points and adds the prime
hand width.

On the circle `T = R/Z`, define

```text
c_p(N) = Phi_N(p) = {N/p}
r_p = 1/(2p)
I_p(N) = [c_p(N)-r_p, c_p(N)+r_p]
```

The covered set is

```text
U_N = union_{p<=N, p prime} I_p(N)
```

The primary uncovered-measure metric is

```text
A(N) = |T \ U_N|
```

The largest uncovered gap is

```text
G(N) = max connected gap length in T \ U_N
```

The exact complete-covering event is

```text
C0(N) = 1[A(N)=0]
```

In floating-point v0 experiments, use scale events such as `A(N)<1/N` rather
than treating `C0(N)` as a certified exact statement.
