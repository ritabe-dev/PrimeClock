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

## v0 Convergence Table

Generate the table with:

```bash
python -m prime_reciprocal_projection.cli metrics --out data/summaries/prp_v0_summary.csv
```

Columns:

- `hist_l1`: L1 distance between empirical and limiting bin masses.
- `ks_distance`: one-sample KS distance against the limiting CDF.
- `branch_l1_k1_20`: L1 branch mass error for `k=1..20`.
- `branch_max_k1_20`: largest branch mass error for `k=1..20`.
- `fourier_mean_m1_20`: mean Fourier residual for modes `1..20`.
- `fourier_max_m1_20`: largest Fourier residual for modes `1..20`.

Current v0 output:

| N | pi(N) | histogram L1 | KS distance | branch L1 k<=20 | branch max k<=20 | Fourier mean m<=20 | Fourier max |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 168 | 0.5417 | 0.0384 | 0.1438 | 0.0655 | 0.0445 | 0.1086 |
| 10,000 | 1,229 | 0.1915 | 0.0241 | 0.0759 | 0.0443 | 0.0180 | 0.0427 |
| 100,000 | 9,592 | 0.0548 | 0.0131 | 0.0583 | 0.0351 | 0.0062 | 0.0140 |
| 1,000,000 | 78,498 | 0.0219 | 0.0087 | 0.0488 | 0.0292 | 0.0027 | 0.0105 |

Initial reading:

- Histogram L1 decreases sharply as `N` grows. This supports the use of
  `rho(x)` as the visible limit shape.
- KS distance also decreases monotonically on this grid, so the convergence is
  not only a binning artifact.
- Fourier mean residual decreases clearly, which supports the claim that low
  frequency components converge to the Fourier coefficients of `rho`.
- Branch errors decrease more slowly. This is expected because the first few
  branches are sensitive to finite-N prime counts in intervals
  `(N/(k+1), N/k]`.

## Main Rule

For `N=1000`, do not use a 100-bin histogram as a main visual. There are only
168 primes up to 1000, so CDF/KS/Fourier diagnostics are more reliable.

For `N >= 100000`, 100-bin histogram figures are acceptable as visual evidence.

## PRC Covering Metrics

Prime Reciprocal Covering (PRC) adds arc widths to the PRP centers and studies
uncovered measure.

Generate the v0 covering table with:

```bash
python -m prime_reciprocal_projection.cli covering-metrics --out data/summaries/prc_v0_covering.csv
```

Generate a denser log-spaced analysis grid with:

```bash
python -m prime_reciprocal_projection.cli covering-metrics \
  --log-grid 1000 1000000 50 \
  --out data/summaries/prc_v0_covering_log_grid.csv
```

Generate the PRC v0 figures with:

```bash
python -m prime_reciprocal_projection.cli covering-figures \
  --log-grid 1000 1000000 50 \
  --out figures/v0
```

Main columns:

- `uncovered_measure`: `A(N)`, the total uncovered measure.
- `uncovered_measure_times_log_n`: a normalized view motivated by the random
  arc baseline.
- `random_arc_baseline`: `exp(-sum_{p<=N} 1/p)`, a rough null-control scale.
- `max_uncovered_gap`: `G(N)`, the largest uncovered component.
- `complete_scale_1_over_n`: `A(N) < 1/N`, the main v0 scale event.
- `complete_scale_1_over_pi_n`: `A(N) < 1/pi(N)`.
- `complete_numeric_1e_9`: numerical threshold only, not an exact proof of
  complete covering.
- `branch1_uncovered_measure`: `A1(N)` using primes with `N/2 < p <= N`.
- `branch1_max_uncovered_gap`: `G1(N)` using primes with `N/2 < p <= N`.
- `branch1_exposed_gap_estimate`: largest transformed adjacent-prime gap after
  subtracting arc radii.
- `gap_fill_ratio`: `G(N)/G1(N)` when `G1(N)>0`.
- `gap_fill_drop`: `G1(N)-G(N)`.
- `gap_p50`, `gap_p90`, `gap_p99`: uncovered-gap quantiles.

Initial PRC reading should be conservative:

- `A(N)` is the primary metric.
- `C0(N)` is not a v0 numerical claim unless exact or certified arithmetic is
  added later.
- Branch-1 gap comparisons must use transformed gaps, not raw prime gaps.
- `G/G1` should be read with `G1-G` and gap quantiles because the ratio can be
  unstable when `G1` is small.

## PRC Candidate Windows

The first exact-complete candidates from the v0 log grid are:

```text
N = 39069
N = 372759
```

Check exact rational coverage with:

```bash
python -m prime_reciprocal_projection.cli covering-certify --n 39069 372759
```

Scan local windows with:

```bash
python -m prime_reciprocal_projection.cli covering-metrics \
  --window 39069 500 \
  --window 372759 500 \
  --out data/summaries/prc_v0_covering_candidate_windows.csv
```

Generate local window figures with:

```bash
python -m prime_reciprocal_projection.cli covering-window-figure \
  --center 39069 --radius 500 --out figures/v0

python -m prime_reciprocal_projection.cli covering-window-figure \
  --center 372759 --radius 500 --out figures/v0
```

Initial result:

- `39069 +/- 500` contains 21 exact complete-covering values.
- `372759 +/- 500` contains 26 exact complete-covering values.

See `notes/prc_candidate_windows.md` for the first reading.

## PRC Broad Cluster Scan

A broader first scan used 500 log-spaced sample points from `10^3` to `10^6`,
then expanded the 12 exact-complete seeds into `+/-250` windows.

Outputs:

```text
data/summaries/prc_broad_log_grid_500.csv
data/summaries/prc_broad_candidate_windows_r250.csv
data/summaries/prc_broad_candidate_exact_certification.txt
```

Initial result:

```text
161 exact complete-covering values in 12 windows
161 / 6012 ~= 0.0268
```

See `notes/prc_broad_cluster_scan.md`.

## PRC Two-Stage Cluster Scan

The dedicated scanner implements the current main workflow:

```text
coarse float scan -> selected local windows -> exact certification for every M in each window -> D_R table
```

Run:

```bash
python -m prime_reciprocal_projection.cli covering-cluster-scan \
  --start 1000 \
  --stop 1000000 \
  --count 500 \
  --ratio-threshold 0.05 \
  --radius 250 \
  --out data/summaries/prc_cluster_scan_v0.csv
```

Output:

```text
data/summaries/prc_cluster_scan_v0.csv
```

Main columns:

- `center`: local cluster center from the coarse float scan.
- `radius`: `R` in `D_R`.
- `float_zero_count`: values in the window with floating-point `A(N)==0`.
- `exact_complete_count`: values in the full window certified as exact complete
  covering by exact interval arithmetic.
- `float_positive_exact_count`: exact complete-covering values whose floating
  `A(N)` was positive; this diagnoses float prefilter misses.
- `d_r`: `D_R(center) = exact_complete_count / window_size`.
- `median_uncovered_measure`: median `A(N)` in the local window.
- `median_baseline_ratio`: median `A(N) / random_arc_baseline(N)`.
- `certified_values`: exact complete-covering values in the window.

## PRC Consecutive Runs and Prefilter Guardrail

The contiguous run scan to `10^6` uses:

```text
numeric prefilter -> exact rational certification of every numeric candidate
```

The prefilter is guarded for the v0 range by:

```text
PREFILTER_GUARANTEE_MAX_N = 1,000,000
DEFAULT_PREFILTER_TOLERANCE = 1e-12
required_prefilter_tolerance = 4096 * eps ~= 9.09e-13
```

This is an implementation-level binary64 guardrail, not a PRC theorem. It says
the default numeric merge tolerance is larger than the documented endpoint
rounding budget, so exact complete-covering values should not be rejected by
the prefilter within `N <= 10^6`. All reported values are still exact-certified.

See:

```text
notes/prc_prefilter_guarantee.md
notes/prc_consecutive_runs.md
```

Current v0 command found:

```text
21 centers
262 exact complete-covering window memberships
260 unique exact complete-covering values
0 float-positive exact-complete memberships
D_250 range: 0.0180 to 0.0339
```

Generate cluster-density figures with:

```bash
python -m prime_reciprocal_projection.cli covering-cluster-figures \
  --input data/summaries/prc_cluster_scan_v0.csv \
  --out figures/v0
```

Outputs:

```text
figures/v0/prc_cluster_density_N1839_986252.png
figures/v0/prc_cluster_efficiency_N1839_986252.png
figures/v0/prc_cluster_manifest.json
```

Generate sensitivity table with:

```bash
python -m prime_reciprocal_projection.cli covering-cluster-sensitivity \
  --start 1000 \
  --stop 1000000 \
  --count 500 \
  --ratio-threshold 0 0.02 0.05 \
  --radius 100 250 500 \
  --out data/summaries/prc_cluster_sensitivity_v0.csv
```

Output:

```text
data/summaries/prc_cluster_sensitivity_v0.csv
```

## PRC Consecutive Complete-Covering Runs

This subproblem asks whether exact complete covering can persist at consecutive
integers:

```text
C0(N)=C0(N+1)=1.
```

Exact contiguous scan:

```bash
python -m prime_reciprocal_projection.cli covering-run-scan \
  --start 2 \
  --stop 100000 \
  --out data/summaries/prc_exact_runs_2_100000.csv
```

Current exact result:

```text
2 <= N <= 100000:
2369 exact complete-covering values
2368 consecutive runs
longest run length = 2
longest run = [92229, 92230]
```

Selected-window cluster run decomposition:

```bash
python -m prime_reciprocal_projection.cli covering-runs \
  --input data/summaries/prc_cluster_scan_v0.csv \
  --out data/summaries/prc_complete_runs_v0.csv
```

Current selected-window result:

```text
260 exact complete-covering values
260 consecutive runs
longest run length = 1
```

See `notes/prc_consecutive_runs.md`.

Prefiltered extension:

```bash
python -m prime_reciprocal_projection.cli covering-run-prefilter-scan \
  --start 100001 \
  --stop 200000 \
  --workers 10 \
  --chunk-size 10000 \
  --out data/summaries/prc_prefilter_exact_runs_100001_200000.csv
```

The same `100000`-wide block command was repeated up to `1000000`. The
reported values are exact-certified after the numeric prefilter. The prefilter
matched the all-exact run scan on `2 <= N <= 100000`.

Combined result:

```text
2 <= N <= 1000000:
23571 exact-certified complete-covering values
23561 consecutive runs
longest run length = 2
length-2 runs = 10
length-3 starts = 0
```

Forensic tables:

```bash
python -m prime_reciprocal_projection.cli covering-run-forensics \
  --input data/summaries/prc_combined_runs_2_1000000.csv \
  --start 2 \
  --stop 1000000 \
  --transition-out data/summaries/prc_run_transition_stats_2_1000000.csv \
  --pair-out data/summaries/prc_length2_pair_forensics_2_1000000.csv \
  --neighborhood-out data/summaries/prc_length2_neighborhoods_2_1000000.csv \
  --validation-out data/summaries/prc_prefilter_validation_windows.csv
```

Forensic result:

```text
transition stats rows: 1
length-2 pair rows: 10
length-2 neighborhood rows: 40
prefilter validation windows: 20
validation mismatches: 0
```
