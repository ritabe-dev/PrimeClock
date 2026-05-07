# Fourier Diagnostics

The empirical Fourier coefficient is

```text
hat_mu_N(m)
= (1 / pi(N)) * sum_{p<=N} exp(-2*pi*i*m*{N/p})
```

The limiting coefficient is

```text
hat_rho(m)
= int_0^1 rho(x) exp(-2*pi*i*m*x) dx
```

For `m=0`, both values are `1`. This is a required sanity check in code.

Fourier diagnostics are useful because they compare the whole distribution
through frequency components instead of relying only on histogram shape.

