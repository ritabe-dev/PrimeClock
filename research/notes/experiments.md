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
uncovered measure. In the current framing, these metrics are diagnostics of a
finite residue-covering hierarchy: each prime `p` selects the residue cell
`N mod p` on the `p`-partitioned circle, and the prime-prefix process leaves a
residual set whose measure, components, and gap shape are measured.

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
- `random_arc_baseline`: legacy column equal to `poisson_arc_baseline`.
- `poisson_arc_baseline`: `exp(-sum_{p<=N} 1/p)`, a Poissonized rough scale.
- `product_arc_baseline`: `prod_{p<=N}(1 - 1/p)`, the fixed-point baseline for
  independent uniformly centered arcs.
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

- `A(N)` and prime-prefix residual structure are the primary metrics.
- Residual fragmentation is a diagnostic of the finite hierarchy, not a
  standalone theorem.
- `C0(N)` is not a v0 numerical claim unless exact or certified arithmetic is
  added later.
- Exact `C0`, certificate depth, and anti-clustering are boundary/forensic
  side tracks.
- Branch-1 gap comparisons must use transformed gaps, not raw prime gaps.
- `G/G1` should be read with `G1-G` and gap quantiles because the ratio can be
  unstable when `G1` is small.

## PRC Prime-Prefix Profile v0.1

Generate the prime-prefix residual profile with:

```bash
python -m prime_reciprocal_projection.cli covering-prime-prefix-profile \
  --n 1000 10000 100000 1000000 39069 372759 \
  --out data/summaries/prc_prime_prefix_profile_v0_1.csv
```

This is the first artifact for the finite residue-covering hierarchy:

```text
U_P(N) = union_{p<=P} I_p(N)
A_P(N) = |T \ U_P(N)|
R_P(N) = T \ U_P(N)
```

Current output:

- 125 data rows across 6 `N` values.
- Checkpoints with `P > N` are omitted.
- `A_P(N)` is tracked together with product/Poisson prefix baselines,
  component count, gap quantiles, and top-gap share.
- `numeric_complete_prefix` is a descriptive floating-point flag, not an exact
  certificate.

## PRC Prime-Prefix Residue Filtration v0.1

The exact finite counterpart of the prime-prefix profile is:

```text
M_k = product_{i<=k} p_i
C_k = {r in Z/M_kZ : union_{i<=k} I_{p_i}(r)=T}
```

Generate the exact filtration tables with:

```bash
python -m prime_reciprocal_projection.cli covering-prime-prefix-filtration \
  --max-k 7 \
  --birth-sample-limit 200 \
  --summary-out data/summaries/prc_prime_prefix_residue_covering_filtration_v0_1.csv \
  --birth-samples-out data/summaries/prc_prime_prefix_residue_covering_birth_samples_v0_1.csv
```

Current generated artifacts:

```text
notes/prc_mathematical_theme_prime_prefix_filtration_v0_1.md
data/summaries/prc_prime_prefix_residue_covering_filtration_v0_1.csv
data/summaries/prc_prime_prefix_residue_covering_birth_samples_v0_1.csv
```

Current table:

| k | new prime | M_k | covered residues | density | inherited | births |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 2 | 0 | 0.000000 | 0 | 0 |
| 2 | 3 | 6 | 0 | 0.000000 | 0 | 0 |
| 3 | 5 | 30 | 0 | 0.000000 | 0 | 0 |
| 4 | 7 | 210 | 2 | 0.009524 | 0 | 2 |
| 5 | 11 | 2,310 | 36 | 0.015584 | 22 | 14 |
| 6 | 13 | 30,030 | 510 | 0.016983 | 468 | 42 |
| 7 | 17 | 510,510 | 9,384 | 0.018382 | 8,670 | 714 |

This is stronger than a numeric prefix-complete flag: it is a finite exact
classification problem over primorial residue rings. The CLI uses lift
monotonicity to avoid exact-rechecking inherited covered classes.

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

## PRC Main v0.3 Branch Fill-In

The main PRC direction now tracks how lower reciprocal branches fill the
uncovered circle. Generate the v0.3 branch fill-in long table, summary table,
and figures with:

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill \
  --n 1000 10000 100000 1000000 39069 372759 \
  --max-branch 1000 \
  --out data/summaries/prc_branch_fill_v0_3.csv

python -m prime_reciprocal_projection.cli covering-branch-fill-summary \
  --input data/summaries/prc_branch_fill_v0_3.csv \
  --out data/summaries/prc_branch_fill_summary_v0_3.csv

python -m prime_reciprocal_projection.cli covering-branch-fill-figures \
  --input data/summaries/prc_branch_fill_v0_3.csv \
  --out figures/v0
```

Outputs:

```text
data/summaries/prc_branch_fill_v0_3.csv
data/summaries/prc_branch_fill_summary_v0_3.csv
figures/v0/prc_branch_fill_residual_v0_3.png
figures/v0/prc_branch_fill_fraction_v0_3.png
figures/v0/prc_branch_fill_manifest.json
```

Initial reading:

- Branch 1 is the prime-gap shadow layer, but it leaves about `0.90` to `0.95`
  of the circle uncovered on the tested values.
- `N=1000` reaches `K50=27`, `K90=333`, and `K99=500`.
- `N=10000`, `39069`, `100000`, and `372759` reach `K50` between `126` and
  `885`, but `K90/K99` are censored at `K=1000`.
- `N=1000000` is censored even for `K50` at `K=1000`.
- The exact-complete values `39069` and `372759` are not early-fill examples;
  both still have large normalized residuals at `K=1000`.

See `notes/prc_main_v0_3.md`.

## PRC Main v0.4 Matched Branch Fill-In Cohorts

Generate deterministic complete/control cohorts from the certified
`N<=10^6` run table:

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill-cohorts \
  --complete-source data/summaries/prc_combined_runs_2_1000000.csv \
  --start 1000 \
  --stop 1000000 \
  --bin-count 12 \
  --max-per-bin 3 \
  --local-radius 250 \
  --out data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv

python -m prime_reciprocal_projection.cli covering-branch-fill-cohort-summary \
  --manifest data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv \
  --max-branch 1000 \
  --summary-out data/summaries/prc_branch_fill_cohort_summary_v0_4.csv \
  --checkpoint-out data/summaries/prc_branch_fill_cohort_checkpoints_v0_4.csv

python -m prime_reciprocal_projection.cli covering-branch-fill-cohort-figures \
  --summary data/summaries/prc_branch_fill_cohort_summary_v0_4.csv \
  --checkpoints data/summaries/prc_branch_fill_cohort_checkpoints_v0_4.csv \
  --out figures/v0
```

Outputs:

```text
data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv
data/summaries/prc_branch_fill_cohort_summary_v0_4.csv
data/summaries/prc_branch_fill_cohort_checkpoints_v0_4.csv
figures/v0/prc_branch_fill_cohort_k_depth_v0_4.png
figures/v0/prc_branch_fill_cohort_residual_v0_4.png
figures/v0/prc_branch_fill_cohort_checkpoint_fill_v0_4.png
```

Initial result:

- 36 complete seeds, 0 exclusions, 144 summary rows.
- Complete median `K50=234`; controls have median `K50` of `211`, `160`, and
  `195`.
- Complete median residual at `K=1000` is `0.371519`; controls are about
  `0.332` to `0.340`.
- The v0.4 sample does not support the simple explanation that complete values
  are early low-branch fill-in cases.

See `notes/prc_main_v0_4.md`.

## PRC Main v0.5 Residual Gap Structure

Generate residual gap metrics after the common branch prefix `K=1000`:

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill-residual-gaps \
  --manifest data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv \
  --summary data/summaries/prc_branch_fill_cohort_summary_v0_4.csv \
  --max-branch 1000 \
  --near-zero-threshold 1e-6 \
  --out data/summaries/prc_branch_fill_residual_gaps_v0_5.csv \
  --figures-out figures/v0
```

Outputs:

```text
data/summaries/prc_branch_fill_residual_gaps_v0_5.csv
figures/v0/prc_branch_fill_residual_gap_count_v0_5.png
figures/v0/prc_branch_fill_residual_gap_shape_v0_5.png
figures/v0/prc_branch_fill_residual_gaps_manifest.json
```

Initial result:

- 144 raw rows were generated in about `3.53s`.
- Prefix censoring marks `1258`, `1262`, and `1329` ineligible because
  `K=1000` exhausts all branches for at least one role in each seed.
- The main v0.5.1 reading uses 33 eligible seeds and 132 eligible rows.
- Complete rows have median residual max gap `0.001555`; controls range from
  `0.001531` to `0.001805`.
- Complete rows have median top-gap share `0.004218`; controls range from
  `0.004384` to `0.005354`.
- Residual entropy is similar across all groups.

See `notes/prc_main_v0_5.md`.

Generate v0.6 paired complete-minus-control residual gap deltas:

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill-residual-gap-pairs \
  --input data/summaries/prc_branch_fill_residual_gaps_v0_5.csv \
  --delta-out data/summaries/prc_residual_gap_pair_deltas_v0_6.csv \
  --summary-out data/summaries/prc_residual_gap_effect_summary_v0_6.csv \
  --figures-out figures/v0
```

Outputs:

```text
data/summaries/prc_residual_gap_pair_deltas_v0_6.csv
data/summaries/prc_residual_gap_effect_summary_v0_6.csv
figures/v0/prc_residual_gap_pair_delta_v0_6.png
figures/v0/prc_residual_gap_effect_summary_v0_6.png
figures/v0/prc_residual_gap_pairs_manifest.json
```

Initial v0.6 result:

- 594 paired delta rows and 18 summary rows were generated in about `0.50s`.
- For `residual_gap_count`, complete rows are smaller in `22/33`,
  `19/33`, and `26/33` pairs across the three control roles.
- For `residual_top_gap_share`, the direction is mixed: `19/33`, `15/33`,
  and `16/33` complete-smaller pairs.

See `notes/prc_main_v0_6.md`.

Generate v0.7 residual gap count tests:

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill-residual-gap-count-test \
  --input data/summaries/prc_residual_gap_pair_deltas_v0_6.csv \
  --out data/summaries/prc_residual_gap_count_tests_v0_7.csv \
  --secondary-out data/summaries/prc_residual_gap_secondary_direction_v0_7.csv \
  --figures-out figures/v0
```

Outputs:

```text
data/summaries/prc_residual_gap_count_tests_v0_7.csv
data/summaries/prc_residual_gap_secondary_direction_v0_7.csv
data/summaries/prc_residual_gap_control_reuse_audit_v0_7_1.csv
figures/v0/prc_residual_gap_count_test_v0_7.png
figures/v0/prc_residual_gap_count_ci_v0_7.png
figures/v0/prc_residual_gap_count_tests_manifest.json
```

Initial v0.7.1 result:

- 3 primary test rows and 18 secondary direction rows were generated in about
  `0.79s`.
- For `local_mod6_control`, complete rows are smaller in `22/33` pairs,
  with exploratory sign-test `p=0.0801` and BH `q=0.1202`.
- For `band_mod6_control`, complete rows are smaller in `19/31` non-tie pairs,
  with exploratory `p=q=0.2810`.
- For `band_ordinary_control`, complete rows are smaller in `26/33` pairs,
  with exploratory `p=0.00132` and BH `q=0.00396`.
- `band_ordinary_control` is a band-center non-complete control, not a random
  control. It is the weakest control and has more reuse than the mod-6 controls.
- The hard-control reading is not confirmed; v0.8 should use cluster/block
  checks and better null models before strengthening the claim.

See `notes/prc_main_v0_7.md`.

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
- `median_baseline_ratio`: legacy median `A(N) / random_arc_baseline(N)`, where
  `random_arc_baseline` is the Poisson approximation.
- `certified_values`: exact complete-covering values in the window.

## PRC Consecutive Runs and Prefilter Guardrail

The contiguous run scan to `10^6` uses:

```text
numeric prefilter -> exact rational certification of every numeric candidate
```

The prefilter is guarded for the documented v0.2 range by:

```text
PREFILTER_GUARANTEE_MAX_N = 10,000,000
DEFAULT_PREFILTER_TOLERANCE = 1e-12
required_prefilter_tolerance = 4096 * eps ~= 9.09e-13
```

This is an implementation-level binary64 guardrail, not a PRC theorem. It says
the default numeric merge tolerance is larger than the documented endpoint
rounding budget, so exact complete-covering values should not be rejected by
the prefilter within `N <= 10^7`. All reported values are still exact-certified.
The completed contiguous scan currently reaches `N <= 10^6`; the `N <= 10^7`
full scan has not been run.

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

This is a forensic subproblem, not the main PRC axis. It asks whether exact
complete covering can persist at consecutive integers:

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

## PRC Fast Scan v0.2 Pilot

The v0.2 scanner adds a NumPy numeric prefilter and a block/resume command.
The proof step remains exact rational certification of numeric candidates.

Benchmark output:

```text
data/summaries/prc_fastscan_benchmark.csv
```

Pilot outputs:

```text
data/summaries/prc_fastscan_pilot_runs_1000001_1100000.csv
data/summaries/prc_fastscan_pilot_summary_1000001_1100000.csv
data/summaries/prc_fastscan_pilot_blocks_1000001_1100000/
```

Pilot command:

```bash
python -m prime_reciprocal_projection.cli covering-run-block-scan \
  --start 1000001 \
  --stop 1100000 \
  --block-size 10000 \
  --workers 4 \
  --chunk-size 1000 \
  --engine numpy \
  --out-dir data/summaries/prc_fastscan_pilot_blocks_1000001_1100000 \
  --combined-out data/summaries/prc_fastscan_pilot_runs_1000001_1100000.csv \
  --summary-out data/summaries/prc_fastscan_pilot_summary_1000001_1100000.csv
```

Current pilot result:

```text
1,000,001 <= N <= 1,100,000:
2,380 exact-certified complete-covering values
2,378 consecutive runs
longest run length = 2
length-2 runs = 2
length-3 starts = 0
```

The full `N <= 10^7` scan has not been run.

## PRC Main v0.8 Cluster Audit

The v0.8 audit checks whether the v0.7 `residual_gap_count` direction survives
seed clustering and control reuse scrutiny.

Command:

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill-cluster-audit \
  --manifest data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv \
  --deltas data/summaries/prc_residual_gap_pair_deltas_v0_6.csv \
  --metric residual_gap_count \
  --cluster-radius 250 \
  --cluster-out data/summaries/prc_seed_cluster_audit_v0_8.csv \
  --direction-out data/summaries/prc_cluster_level_gap_count_direction_v0_8.csv \
  --reuse-out data/summaries/prc_control_reuse_detail_v0_8.csv \
  --figures-out figures/v0
```

Outputs:

```text
data/summaries/prc_seed_cluster_audit_v0_8.csv
data/summaries/prc_cluster_level_gap_count_direction_v0_8.csv
data/summaries/prc_control_reuse_detail_v0_8.csv
figures/v0/prc_cluster_level_gap_count_direction_v0_8.png
figures/v0/prc_control_reuse_v0_8.png
figures/v0/prc_cluster_audit_manifest.json
```

Recorded local run:

```text
33 seed rows
11 seed clusters
3 cluster-direction rows
74 control-reuse rows
2 figures
runtime about 0.50s
```

Cluster-level direction for `residual_gap_count`:

| control | clusters | complete smaller clusters | median cluster delta | sign p |
|---|---:|---:|---:|---:|
| local_mod6_control | 11 | 9 | -24.0 | 0.0654 |
| band_mod6_control | 11 | 6 | -27.0 | 0.5078 |
| band_ordinary_control | 11 | 10 | -37.0 | 0.0117 |

Control reuse:

| control | pairs | unique controls | reused controls | reused pairs |
|---|---:|---:|---:|---:|
| local_mod6_control | 33 | 33 | 0 | 0 |
| band_mod6_control | 33 | 25 | 8 | 16 |
| band_ordinary_control | 33 | 16 | 11 | 28 |

Reading: the local mod-6 result remains suggestive after clustering, but the
hard controls do not confirm the signal. The strongest numeric result is still
in `band_ordinary_control`, which is the weakest and most reused control role.

## PRC Main v0.9 Branch-Uniform Null Model

The v0.9 null model checks whether the observed `K=1000`
`residual_gap_count` is unusual after preserving branch sizes and prime arc
widths but replacing centers by independent uniform random centers.

Command:

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill-null-model \
  --manifest data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv \
  --observed data/summaries/prc_branch_fill_residual_gaps_v0_5.csv \
  --model branch_uniform \
  --max-branch 1000 \
  --iterations 1000 \
  --seed 1729 \
  --out data/summaries/prc_branch_uniform_null_v0_9.csv \
  --summary-out data/summaries/prc_branch_uniform_null_summary_v0_9.csv \
  --figures-out figures/v0
```

Outputs:

```text
data/summaries/prc_branch_uniform_null_v0_9.csv
data/summaries/prc_branch_uniform_null_summary_v0_9.csv
figures/v0/prc_branch_uniform_null_percentile_v0_9.png
figures/v0/prc_branch_uniform_null_deviation_v0_9.png
figures/v0/prc_branch_uniform_null_manifest.json
```

Recorded local run:

```text
132 per-row null summaries
4 cohort summaries
1000 iterations per row
runtime about 1162s
```

Summary:

| cohort | rows | median observed percentile | median observed < null rate | below null p05 | above null p95 |
|---|---:|---:|---:|---:|---:|
| complete | 33 | 0.929 | 0.071 | 0 | 12 |
| local_mod6_control | 33 | 0.949 | 0.051 | 1 | 16 |
| band_mod6_control | 33 | 0.957 | 0.043 | 0 | 17 |
| band_ordinary_control | 33 | 0.962 | 0.038 | 0 | 18 |

Reading: the branch-uniform null is a first coarse null. It preserves branch
sizes and arc widths but deliberately destroys within-branch arithmetic order
and does not preserve the smooth branch density. Under that loose comparison,
the data do not support the idea that complete rows have unusually low residual
component count in an absolute random-covering sense. Instead, all cohorts have
high observed percentiles. The conservative v0.9 observation is that PRC
residual sets look more fragmented than branch-uniform random placements with
the same widths.
