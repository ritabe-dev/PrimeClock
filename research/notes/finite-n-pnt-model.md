# Finite-N PNT Model

The limiting density

```text
rho(x) = sum_{k>=1} 1/(k+x)^2
```

is the asymptotic target. For finite `N`, especially `N <= 10^6`, experiments
should also compare against a PNT-corrected model.

The informal model is

```text
rho_N^PNT(x)
= (1 / Z_N) *
  sum_{1 <= k+x <= N/2}
    N / ((k+x)^2 log(N/(k+x)))
```

where `Z_N` normalizes the density on `[0,1)`.

This is a model, not a theorem. It is included to reduce the risk of mistaking
finite-size bias for a new phenomenon.

