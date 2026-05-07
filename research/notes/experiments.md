# Experiments

## v0 Grid

```text
N = 10^3, 10^4, 10^5, 10^6
bins = 100
modes = 0..20
```

## Outputs

- histogram bin masses versus limiting `rho` bin masses
- KS distance against the limiting CDF
- branch masses for `k=1..20`
- Fourier residuals `|hat_mu_N(m)-hat_rho(m)|`

## Main Rule

For `N=1000`, do not use a 100-bin histogram as a main visual. There are only
168 primes up to 1000, so CDF/KS/Fourier diagnostics are more reliable.

For `N >= 100000`, 100-bin histogram figures are acceptable as visual evidence.

