# Prime Reciprocal Covering v0 Initial Reading

Status note: this is an early reading note. Later PRC notes supersede its
candidate language by using exact interval certification and selected-window
`D_R` scans.

This note reads the first PRC outputs generated from:

```bash
python -m prime_reciprocal_projection.cli covering-metrics \
  --log-grid 1000 1000000 50 \
  --out data/summaries/prc_v0_covering_log_grid.csv

python -m prime_reciprocal_projection.cli covering-figures \
  --log-grid 1000 1000000 50 \
  --out figures/v0
```

Generated figures:

```text
figures/v0/prc_covering_trend_N1000_1000000.png
figures/v0/prc_gap_fill_N1000_1000000.png
figures/v0/prc_branch1_gap_N1000_1000000.png
```

## 1. A(N) Is the Right Primary Metric

The power-of-10 anchors are:

| N | A(N) | random baseline | G(N) | G/G1 | components |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.114647 | 0.111016 | 0.015878 | 0.257183 | 19 |
| 10,000 | 0.041923 | 0.083487 | 0.002479 | 0.237630 | 49 |
| 100,000 | 0.040222 | 0.066852 | 0.000655 | 0.394965 | 346 |
| 1,000,000 | 0.050069 | 0.055725 | 0.000117 | 0.396831 | 3308 |

`A(N)` does not decrease monotonically on the v0 grid. This is useful rather
than disappointing: PRC is not just a smooth convergence table. It has visible
finite-`N` structure.

The random arc baseline has the right rough scale, but the measured `A(N)` can
be substantially below or above it. This makes `A(N)` a better research object
than a simple complete-covering event.

## 2. Complete Coverage Appears, but Should Not Be Overclaimed

On the current log grid, two values have floating-point `A(N)=0`:

```text
N = 39069
N = 372759
```

Both also satisfy the scale events `A(N)<1/N` and `A(N)<1/pi(N)`.

This is an interesting signal, but v0 must not call it a proof of exact
complete covering. The implementation is floating-point interval arithmetic.
The correct phrasing is:

```text
These N are numerically completely covered in the v0 float model.
```

The next step is to inspect these two cases with certified or rational interval
arithmetic if exact `C0(N)` becomes important.

## 3. Branch 1 Really Is a Prime-Gap Layer

The branch-1 exposed-gap estimate matches `G1(N)` very closely in the current
CSV. This is expected because branch 1 is ordered by primes in `(N/2,N]`, and
the estimated gap subtracts the two arc radii:

```text
max(0, N*(p_j-p_i)/(p_i*p_j) - 1/(2p_i) - 1/(2p_j)).
```

This supports the refined hypothesis:

```text
G1(N) is a transformed prime-gap statistic.
G(N) is the part of that statistic that survives fill-in by lower branches.
```

The original informal phrase "G(N) is prime gaps visualized" is too strong.
The better statement is:

```text
Branch 1 creates prime-gap shadows; full PRC measures how much of those
shadows remain after all reciprocal branches are added.
```

## 4. Lower Branches Fill Most of the Largest Branch-1 Gap

At the anchor values, `G/G1` is roughly `0.24` to `0.40`, except for local
outliers in the dense grid. This means lower branches often erase more than
half of the largest branch-1 gap.

The drop `G1(N)-G(N)` is therefore more stable to read than `G/G1` alone:

```text
N=1,000,000: G1-G = 0.000178
N=100,000:  G1-G = 0.001003
N=10,000:   G1-G = 0.007953
N=1,000:    G1-G = 0.045859
```

As `N` grows, absolute gaps shrink, while the number of uncovered components
can grow. This suggests PRC has two separate regimes:

- total uncovered mass `A(N)`;
- fragmentation of the remaining uncovered set.

## 5. Next Reading Questions

The most useful next questions are:

1. Are the numerical complete-coverage cases `39069` and `372759` exact under
   rational/certified interval arithmetic?
2. Does `A(N)` have stable behavior after normalizing by the random baseline?
3. Are unusually small `A(N)` values explained by branch fill-in, or by special
   arithmetic of `N`?
4. Is `component_count` a better signal than `G(N)` for the transition from a
   few large gaps to many tiny gaps?

The v0 conclusion is conservative: PRC has stronger experimental potential than
the center-distribution limit alone, but its first serious object is finite-`N`
coverage behavior, not a new limiting law.

## 6. More Concrete Interpretation

The most concrete way to read the first PRC table is not as one trend, but as
three different phenomena that can separate from each other.

### 6.1 A(N) Is Not Just "More Primes Means Less Blank"

The largest uncovered values in the current 52-row grid are:

| N | A(N) | baseline | A/baseline | G(N) | components |
|---:|---:|---:|---:|---:|---:|
| 3,089 | 0.160856 | 0.095561 | 1.68 | 0.009703 | 95 |
| 22,230 | 0.131572 | 0.076863 | 1.71 | 0.002065 | 322 |
| 1,151 | 0.125564 | 0.108755 | 1.15 | 0.027613 | 17 |
| 5,429 | 0.118018 | 0.089438 | 1.32 | 0.005104 | 101 |

These are not simply the smallest `N`. For example, `N=22230` has much more
uncovered area than the random-arc baseline predicts, even though its largest
gap is already small. This suggests that high `A(N)` can mean many medium gaps,
not only one large gap.

The smallest uncovered values are:

| N | A(N) | baseline | A/baseline | G(N) | components |
|---:|---:|---:|---:|---:|---:|
| 39,069 | 0 | 0.072789 | 0 | 0 | 0 |
| 372,759 | 0 | 0.060008 | 0 | 0 | 0 |
| 868,511 | 0.005064 | 0.056297 | 0.09 | 0.000103 | 411 |
| 51,795 | 0.005614 | 0.070900 | 0.079 | 0.000685 | 40 |
| 44,984 | 0.006237 | 0.071820 | 0.087 | 0.000496 | 33 |

These are the first strong candidates for "unusually efficient covering".
They are more important than the power-of-10 anchors because they deviate from
the random baseline by an order of magnitude.

### 6.2 Complete-Coverage Candidates Need Exact Certification

The current grid has two numerical complete-covering cases:

```text
N = 39069
N = 372759
```

The important point is not just that `A(N)=0`. It is that the random baseline at
those scales is still around `0.07` and `0.06`. In a naive independent-arc
picture, one would still expect visible uncovered mass. PRC instead finds a
configuration where lower branches fill all branch-1 gaps in the float model.

This made these two `N` values the first certification targets:

```text
For N=39069 and N=372759, verify whether every uncovered interval is truly
covered using exact rational interval endpoints.
```

Both values later survived exact checking. The current research wording should
still distinguish certified selected-window evidence from any unbiased global
frequency claim.

### 6.3 Branch 1 Is Almost Exactly the Prime-Gap Layer

The correlation between

```text
branch1_max_uncovered_gap
branch1_exposed_gap_estimate
```

is `0.9993` on the current grid.

That is strong evidence that the branch-1 formula is the right one:

```text
max(0, N*(p_j-p_i)/(p_i*p_j) - 1/(2p_i) - 1/(2p_j)).
```

So the prime-gap statement should be precise:

```text
G1(N) is essentially the largest exposed transformed prime gap in (N/2,N].
```

The full `G(N)` is different. The correlation between `G(N)` and `G1(N)` is
only about `0.83`, because lower branches erase part of the branch-1 structure.
This is the mathematical content of the covering problem.

### 6.4 Fill-In Has Two Different Meanings

There are two ways a branch-1 gap can disappear:

1. The largest gap gets directly covered, reducing `G(N)`.
2. The uncovered set fragments into many tiny components, reducing `G(N)` even
   if the total uncovered mass `A(N)` remains visible.

This is why `A(N)` and `G(N)` should not be collapsed into one "blankness"
metric.

For example:

```text
N=754312:
A(N)=0.071662
G(N)=0.000115
components=3953
```

This is not close to fully covered in total mass, but no single gap is large.
The blank area is shredded into many tiny pieces.

In contrast:

```text
N=1151:
A(N)=0.125564
G(N)=0.027613
components=17
G/G1=0.818
```

Here the branch-1 largest gap mostly survives. This is closer to the original
visual intuition of a large visible blank sector.

### 6.5 The Best Near-Term Hypotheses

The current data suggests three concrete hypotheses worth testing next.

**Hypothesis A: Efficient-covering N.**

Some `N` values make PRC cover far more efficiently than the random arc
baseline:

```text
A(N) / exp(-sum_{p<=N} 1/p) << 1.
```

Current examples:

```text
39069, 372759, 51795, 44984, 33932, 868511
```

This may be more promising than searching for monotone convergence.

**Hypothesis B: Branch-1 is solved; fill-in is the real problem.**

`G1(N)` is already well explained by transformed prime gaps. The unsolved part
is the survival ratio:

```text
G(N)/G1(N)
```

or more robustly:

```text
G1(N)-G(N).
```

This asks how lower reciprocal branches erase prime-gap shadows.

**Hypothesis C: PRC has a fragmentation transition.**

As `N` grows, the largest gap shrinks, but the number of components can become
large. This means coverage may transition from:

```text
few large gaps -> many tiny gaps -> complete coverage candidates
```

The component count and gap quantiles may be as important as `A(N)` itself.

## 7. Follow-Up Path

The next completed experiment was a focused local study:

1. Exact/certified re-check of `N=39069` and `N=372759`.
2. Neighbor scan around those values, for example `N±500`.
3. Compare `A(N)/baseline`, `component_count`, and `G/G1` in those windows.

This was then generalized into selected-window `D_R` scans. The remaining open
step is to compare those selected-window densities against an explicit null or
held-out sampling design.
