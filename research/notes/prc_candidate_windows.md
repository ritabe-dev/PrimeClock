# PRC Candidate Window Study

This note studies the two complete-coverage candidates from the v0 log grid:

```text
N = 39069
N = 372759
```

The local window scan was generated with:

```bash
python -m prime_reciprocal_projection.cli covering-metrics \
  --window 39069 500 \
  --window 372759 500 \
  --out data/summaries/prc_v0_covering_candidate_windows.csv

python -m prime_reciprocal_projection.cli covering-window-figure \
  --center 39069 --radius 500 --out figures/v0

python -m prime_reciprocal_projection.cli covering-window-figure \
  --center 372759 --radius 500 --out figures/v0
```

Generated figures:

```text
figures/v0/prc_window_N38569_39569.png
figures/v0/prc_window_N372259_373259.png
```

## Exact Certification

The two original candidates are exactly covered under rational interval
arithmetic:

```text
N=39069, exact_complete=True, exact_uncovered_measure=0
N=372759, exact_complete=True, exact_uncovered_measure=0
```

More importantly, the nearby complete-covering candidates also survived exact
checking. This note predates the dedicated `D_R` scanner, so the lists below
should be read as certified values in two selected windows, not as an unbiased
global rate.

In the window `39069 +/- 500`, exact complete coverage occurs at:

```text
38636, 38638, 38642, 38728, 38768, 38822, 38848, 38852, 38859,
39058, 39062, 39069, 39129, 39152, 39159, 39268, 39272,
39388, 39471, 39478, 39482
```

That is 21 exact complete-covering values in 1001 integers.

In the window `372759 +/- 500`, exact complete coverage occurs at:

```text
372272, 372309, 372328, 372332, 372358, 372381, 372452,
372538, 372542, 372609, 372688, 372746, 372748, 372752,
372759, 372782, 372842, 372958, 372962, 373018, 373042,
373071, 373112, 373168, 373172, 373219
```

That is 26 exact complete-covering values in 1001 integers.

This changes the status of complete coverage: it is no longer only a numerical
artifact in v0. At least in these windows, `C0(N)=1` can be certified exactly.

## Local Window Reading

The complete-covering values are not isolated single accidents. They appear in
clusters inside broader efficient-covering windows.

For `39069 +/- 500`:

```text
median A(N)        = 0.049959
median A/baseline = 0.687214
median components = 213
exact complete count = 21
```

The largest uncovered values in the same window are much worse than random:

| N | A(N) | A/baseline | G(N) | G/G1 | components |
|---:|---:|---:|---:|---:|---:|
| 39270 | 0.171209 | 2.354 | 0.001492 | 0.418 | 677 |
| 39180 | 0.163317 | 2.244 | 0.001397 | 0.267 | 674 |
| 39390 | 0.158177 | 2.175 | 0.001385 | 0.386 | 673 |
| 39324 | 0.155083 | 2.132 | 0.001438 | 0.402 | 677 |

So this window is not uniformly efficient. It contains sharp complete-covering
points next to very inefficient points. That suggests `A(N)` is highly sensitive
to arithmetic changes in `N`.

For `372759 +/- 500`:

```text
median A(N)        = 0.041362
median A/baseline = 0.689330
median components = 1361
exact complete count = 26
```

The largest uncovered values are:

| N | A(N) | A/baseline | G(N) | G/G1 | components |
|---:|---:|---:|---:|---:|---:|
| 373176 | 0.128056 | 2.134 | 0.000252 | 0.309 | 3886 |
| 372876 | 0.117711 | 1.962 | 0.000279 | 0.342 | 3573 |
| 372330 | 0.116863 | 1.947 | 0.000263 | 0.322 | 3578 |
| 372594 | 0.116745 | 1.945 | 0.000327 | 0.401 | 3710 |

Again, the complete-covering values live in a window where nearby `N` can be
strongly inefficient. This makes the local arithmetic of `N` look central.

## Interpretation

The local-window scan supports a stronger PRC direction:

```text
Complete covering is not merely a rare float artifact.
It occurs exactly at multiple nearby integers.
```

But the complete-covering values are not forming a smooth basin. They are
interleaved with high-uncovered values. Therefore, the next mathematical object
should not be only `A(N)` as a smooth function. It should include local
volatility:

```text
V_R(N) = variation of A(M) for |M-N| <= R
```

and the local complete-covering density:

```text
D_R(N) = #{M in [N-R,N+R] : A(M)=0} / (2R+1).
```

In the two tested windows with `R=500`:

```text
D_500(39069)  = 21/1001 ~= 0.0210
D_500(372759) = 26/1001 ~= 0.0260
```

These selected-window densities are high enough to motivate `D_R` as a primary
PRC observable. They should not yet be compared to an expected random count
until a null model for exact complete covering is implemented.

## Next Step

The next experiment should scan for exact-complete values over a larger range.
A practical path is:

1. Use float PRC to find candidates with `A(N)=0` or `A(N)<1/N`.
2. Use those candidates only as seed centers for local windows.
3. Certify every integer in each selected window with exact interval
   arithmetic.
4. Record local density `D_R(N)` around candidate clusters.

This turns complete covering from a fragile event into a searchable, certifiable
phenomenon.
