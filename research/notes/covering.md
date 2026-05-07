# Prime Reciprocal Covering

Prime Reciprocal Covering (PRC) is the covering version of Prime Reciprocal
Projection (PRP). PRP studies the center points

```text
{N/p},  p prime, p <= N.
```

PRC gives each point the same angular width as the corresponding prime hand in
the clock.

## Definition

Work on the circle

```text
T = R/Z.
```

For an integer `N >= 2` and a prime `p <= N`, define

```text
c_p(N) = {N/p}
r_p = 1/(2p)
I_p(N) = [c_p(N)-r_p, c_p(N)+r_p] on T
```

The covered set is

```text
U_N = union_{p<=N, p prime} I_p(N).
```

The primary metric is the uncovered measure

```text
A(N) = |T \ U_N|.
```

The largest uncovered gap is

```text
G(N) = max connected gap length in T \ U_N.
```

The exact complete-covering event is

```text
C0(N) = 1[A(N)=0].
```

The broad covering tables use floating-point intervals, so exact complete
covering is not inferred from those rows alone. They report scale events:

```text
C_scale(N) = 1[A(N) < 1/N]
C_prime(N) = 1[A(N) < 1/pi(N)]
C_numeric(N) = 1[A(N) < 1e-9]
```

`C_scale` is the main mathematical scale event. `C_numeric` is only a numerical
threshold.

For candidate windows and cluster-density scans, `C0(N)` is counted only after
exact interval certification. The current `D_R` scanner exact-checks every
integer in each selected local window, so `D_R` is a certified local density for
that selected window rather than a float-zero lower bound.

## Branch 1 and Prime Gaps

Branch 1 is

```text
floor(N/p)=1, equivalently N/2 < p <= N.
```

Let

```text
A1(N) = uncovered measure using only branch-1 arcs
G1(N) = largest uncovered gap using only branch-1 arcs.
```

For adjacent branch-1 primes `p_i < p_j`, the center spacing is

```text
N*(p_j-p_i)/(p_i*p_j).
```

After subtracting arc radii, the exposed-gap estimate is

```text
max(0, N*(p_j-p_i)/(p_i*p_j) - 1/(2p_i) - 1/(2p_j)).
```

Thus `G1(N)` is not simply the largest prime gap divided by `N`; it is the
largest transformed prime gap after local scaling and width subtraction.

The full `G(N)` then measures how much of this branch-1 gap structure survives
after lower branches are added.

## Derived Fill-In Metrics

The v0 CSV reports:

```text
gap_fill_ratio = G(N)/G1(N), if G1(N)>0
gap_fill_drop = G1(N)-G(N)
component_count = number of uncovered components
gap_p50, gap_p90, gap_p99 = uncovered-gap quantiles
```

`gap_fill_ratio` can be unstable when `G1(N)` is small, so `gap_fill_drop` and
gap quantiles should be read alongside it.

## Baseline

A first null model is independent random arcs with the same widths. Since

```text
sum_{p<=N} 1/p ~ log log N,
```

the rough uncovered-measure baseline is

```text
random_arc_baseline_A(N) = exp(-sum_{p<=N} 1/p).
```

This is not a theorem for PRC. It is a control scale for asking whether
`A(N)` is showing more than generic dense covering behavior.
