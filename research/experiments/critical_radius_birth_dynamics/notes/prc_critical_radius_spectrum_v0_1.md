# PRC Critical Radius Spectrum v0.1

This note defines the next internal PRC observable after the v2.2.1
`C_4/B_5` finite certificate release.

For the first `k` primes and a residue `r mod M_k`, let

```text
c_p(r) = (r mod p) / p.
```

For `lambda >= 0`, define the scaled closed arc

```text
I_p^(lambda)(r) = [c_p(r)-lambda/p, c_p(r)+lambda/p] in R/Z.
```

The critical radius is

```text
lambda_k(r) = inf { lambda >= 0 :
  union_{i<=k} I_{p_i}^{(lambda)}(r) = R/Z }.
```

The current PRC covering set is the `1/2` level set:

```text
C_k = { r : lambda_k(r) <= 1/2 }.
```

The implementation computes `lambda_k(r)` exactly by evaluating the lower
envelope

```text
max_x min_i p_i d_T(x, c_{p_i}(r)).
```

It enumerates weighted bisector candidates between lifted centers and evaluates
the exact rational bottleneck value. The raw adjacent-center formula is not used
as a theorem-level shortcut, because a smaller prime at a non-adjacent center can
dominate a gap.

Initial artifact:

```text
data/prc_prime_prefix_critical_radius_k4_k5_v0_1.csv
```

The first validation target is exact agreement with the existing finite
filtration:

```text
C_4 = {r : lambda_4(r) <= 1/2} = {2,208} mod 210,
|{r : lambda_5(r) <= 1/2}| = |C_5| = 36.
```
