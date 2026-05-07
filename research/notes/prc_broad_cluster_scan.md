# PRC Broad Cluster Scan

This note records the first broad search for exact complete-covering clusters.

## Commands

Coarse broad scan:

```bash
python -m prime_reciprocal_projection.cli covering-metrics \
  --log-grid 1000 1000000 500 \
  --out data/summaries/prc_broad_log_grid_500.csv
```

Local expansion around the complete-covering seeds found in that broad scan:

```bash
python -m prime_reciprocal_projection.cli covering-metrics \
  --window 3992 250 \
  --window 5882 250 \
  --window 11432 250 \
  --window 12422 250 \
  --window 18051 250 \
  --window 19888 250 \
  --window 51692 250 \
  --window 58551 250 \
  --window 423891 250 \
  --window 566901 250 \
  --window 651069 250 \
  --window 986252 250 \
  --out data/summaries/prc_broad_candidate_windows_r250.csv
```

Exact rational certification output:

```text
data/summaries/prc_broad_candidate_exact_certification.txt
```

## Broad Seeds

The 500-point broad log grid found 12 numerical complete-covering seeds:

```text
3992, 5882, 11432, 12422, 18051, 19888,
51692, 58551, 423891, 566901, 651069, 986252
```

These were not in the first 50-point v0 grid except by luck. This shows that
the candidate set is much richer than the first two examples `39069` and
`372759`.

## Window Results

Each seed was expanded to a `+/-250` window. The current certification pass
checks every integer in each window by exact interval arithmetic. Exact
complete-covering values found per selected window:

| center | window size | exact complete count | D_250 | median A(N) | median A/baseline | max A(N) |
|---:|---:|---:|---:|---:|---:|---:|
| 3,992 | 501 | 15 | 0.0299 | 0.062089 | 0.6723 | 0.203192 |
| 5,882 | 501 | 13 | 0.0259 | 0.059775 | 0.6738 | 0.204554 |
| 11,432 | 501 | 12 | 0.0240 | 0.055861 | 0.6783 | 0.180929 |
| 12,422 | 501 | 13 | 0.0259 | 0.054296 | 0.6648 | 0.164289 |
| 18,051 | 501 | 14 | 0.0279 | 0.053887 | 0.6865 | 0.154474 |
| 19,888 | 501 | 13 | 0.0259 | 0.055232 | 0.7111 | 0.171007 |
| 51,692 | 501 | 17 | 0.0339 | 0.047835 | 0.6747 | 0.142616 |
| 58,551 | 501 | 13 | 0.0259 | 0.049542 | 0.7067 | 0.142454 |
| 423,891 | 501 | 11 | 0.0220 | 0.040063 | 0.6743 | 0.138804 |
| 566,901 | 501 | 15 | 0.0299 | 0.041318 | 0.7110 | 0.120099 |
| 651,069 | 501 | 12 | 0.0240 | 0.040404 | 0.7025 | 0.114617 |
| 986,252 | 501 | 13 | 0.0259 | 0.039362 | 0.7057 | 0.118581 |

Total exact complete-covering values in these 12 windows:

```text
161 / 6012 ~= 0.0268
```

The denominator is `12 * 501`; no default `N` values are mixed into this window
table. The exact pass found `161` exact complete-covering memberships and
`161` unique exact complete-covering values in these non-overlapping windows.

## Interpretation

The broad scan changes the status of PRC complete covering, but only
conditionally on how the windows were selected.

Earlier, `C0(N)=1` looked like a possible numerical artifact at two values.
In these selected windows, exact complete coverage appears repeatedly across
scales:

```text
selected complete-coverage windows occur across scales from N ~ 4e3 to N ~ 1e6.
```

This is not yet an unbiased frequency statement over all `N <= 10^6`. The
windows were selected from a coarse scan using the same covering-efficiency
signals later analyzed. Therefore "cluster" means conditional local density
around selected seeds, not a global repeated-cluster theorem.

The exact complete-covering values are not contiguous runs. They are mostly
single points sprinkled through a local window. This means "cluster" should be
understood as local density, not as consecutive intervals of `N`.

The windows also contain very inefficient values. For example, in the `3992`
window the maximum `A(N)` is about `0.203`, while the same window contains 15
exactly complete values. This suggests high local volatility:

```text
small changes in N can move PRC from exact complete coverage to large uncovered
measure.
```

## Working Hypothesis

The next PRC object should be local complete-covering density:

```text
D_R(N) = #{M in [N-R,N+R] : C0(M)=1} / (2R+1).
```

The selected broad windows have

```text
D_250(N) ~= 0.02 to 0.034
```

This is a useful finite-data summary. It should not be compared to an
"expected" count until a proper null model for `C0(N)` has been implemented.

## Next Step

The dedicated two-stage scanner is now implemented:

```bash
python -m prime_reciprocal_projection.cli covering-cluster-scan \
  --start 1000 \
  --stop 1000000 \
  --count 500 \
  --ratio-threshold 0.05 \
  --radius 250 \
  --out data/summaries/prc_cluster_scan_v0.csv
```

It performs:

1. broad float scan to find low `A(N)/baseline` and `A(N)=0` seed centers;
2. local window expansion around those centers;
3. exact complete-covering certification for every integer in each selected
   local window;
4. diagnostic reporting of `float_zero_count` and
   `float_positive_exact_count`;
5. cluster summary output with `D_R(N)`, median `A(N)`,
   median `A(N)/baseline(N)`, max `A(N)`, and certified value list.

Current output:

```text
data/summaries/prc_cluster_scan_v0.csv
```

The `ratio_threshold=0.05` run found 21 centers. Because neighboring windows can
overlap, two counts are tracked separately:

```text
262 exact complete-covering window memberships
260 unique exact complete-covering N values
0 float-positive exact-complete memberships
```

For `R=250`, the observed local density range is:

```text
D_250 ~= 0.0180 to 0.0339
```

The densest current center is:

```text
N = 51692, D_250 = 17 / 501 ~= 0.0339
```

This strengthens the finite observation that selected efficient windows can
contain many exact complete-covering values. It remains a selected-window
result: `D_R` is the right object for these local windows, but the current data
does not yet claim an unbiased global rate of complete covering.

## Cluster-Density Figures

Generate the overview figures with:

```bash
python -m prime_reciprocal_projection.cli covering-cluster-figures \
  --input data/summaries/prc_cluster_scan_v0.csv \
  --out figures/v0
```

Outputs:

```text
figures/v0/prc_cluster_density_N1839_986252.png
figures/v0/prc_cluster_efficiency_N1839_986252.png
```

The first figure treats each local window as a point:

```text
x = cluster center N
y = D_250(N)
size = exact complete-covering count in the window
color = seed A(N) / random baseline
```

The second figure asks whether dense windows are merely windows with low median
uncovered mass:

```text
x = median A(N) / random baseline in the window
y = D_250(N)
color = maximum A(N) in the window
```

The current answer is mixed. Dense windows do tend to sit in generally efficient
regions, but the median ratios remain around `0.66` to `0.71` even in the best
clusters. This means the cluster is not a whole interval of near-complete
covering. It is a sparse set of exact hits embedded inside ordinary-looking
local volatility.
