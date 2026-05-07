# PRC Consecutive Complete-Covering Runs

This note separates a subproblem from `D_R`.

`D_R` asks how dense exact complete-covering values are inside a selected
window. Consecutive-run analysis asks a sharper question:

```text
Can C0(N)=1 and C0(N+1)=1 both happen?
If yes, how long can a maximal consecutive run be?
```

For a finite set of certified complete-covering values, define a run as a
maximal integer interval

```text
[a,b] such that C0(a)=C0(a+1)=...=C0(b)=1.
```

Its length is `b-a+1`.

## Commands

Exact scan of a contiguous range:

```bash
python -m prime_reciprocal_projection.cli covering-run-scan \
  --start 2 \
  --stop 100000 \
  --out data/summaries/prc_exact_runs_2_100000.csv
```

Run decomposition from the selected-window cluster scan:

```bash
python -m prime_reciprocal_projection.cli covering-runs \
  --input data/summaries/prc_cluster_scan_v0.csv \
  --out data/summaries/prc_complete_runs_v0.csv
```

## Current Results

The exact contiguous scan over `2 <= N <= 100000` found:

```text
exact complete-covering values: 2369
consecutive runs: 2368
longest run length: 2
longest run: 92229, 92230
multi-run count: 1
values in multi-runs: 2
```

The local check around the only length-2 run is:

```text
N=92228: C0(N)=0
N=92229: C0(N)=1
N=92230: C0(N)=1
N=92231: C0(N)=0
```

So this is exactly a length-2 run in the tested range, not part of a longer
block.

The selected-window `R=250`, threshold `0.05` cluster scan found:

```text
exact complete-covering values: 260
consecutive runs: 260
longest run length: 1
```

The original two `R=500` candidate windows around `39069` and `372759` found:

```text
exact complete-covering values: 47
consecutive runs: 47
longest run length: 1
```

The broad 12 selected `R=250` windows found:

```text
exact complete-covering values: 161
consecutive runs: 161
longest run length: 1
```

## Reading

Complete covering is not only isolated in the sense of having low density.
Most certified values are also immediately isolated from their neighbors.

However, exact adjacency is possible. The pair

```text
92229, 92230
```

shows that there is no simple parity obstruction or automatic rule saying
complete covering must alternate with non-complete covering.

This creates a new observable:

```text
L(X) = max length of a C0-run for 2 <= N <= X.
```

The current exact result is:

```text
L(100000) = 2.
```

This is stronger and cleaner than the selected-window result because it comes
from a contiguous exact scan, not from seed-conditioned windows.

## Prefiltered Extension to 10^6

The all-exact scan to `10^6` is still expensive. The current larger scan uses a
numeric complete-covering prefilter and then exact-checks every numeric
candidate. Therefore every reported `C0(N)=1` value is exact-certified.

The prefilter is now guarded by a narrow implementation guarantee for the v0
range:

```text
2 <= N <= 1,000,000
binary64 endpoint arithmetic
default tolerance = 1e-12
required tolerance = 4096 * eps ~= 9.09e-13
```

Within that implemented model, the default tolerance is large enough to bridge
the documented endpoint-error bound, so the prefilter is intended to be
no-false-negative for exact complete-covering values in this range. See
`notes/prc_prefilter_guarantee.md`.

On `2 <= N <= 100000`, the prefiltered result also exactly matches the
all-exact result.

Checkpoint commands:

```bash
python -m prime_reciprocal_projection.cli covering-run-prefilter-scan \
  --start 100001 --stop 200000 \
  --workers 10 --chunk-size 10000 \
  --out data/summaries/prc_prefilter_exact_runs_100001_200000.csv
```

Repeated in `100000`-wide blocks up to `1000000`, then combined into:

```text
data/summaries/prc_combined_runs_2_1000000.csv
```

Combined result:

```text
2 <= N <= 1000000:
exact-certified complete-covering values: 23571
consecutive runs: 23561
longest run length: 2
length-2 runs: 10
length-3 starts: 0
```

The length-2 runs are:

```text
92229, 92230
119342, 119343
123477, 123478
257672, 257673
392492, 392493
431967, 431968
537027, 537028
700047, 700048
754922, 754923
824462, 824463
```

The transition statistic is strongly anti-clustered:

```text
P(C0(N)=1) ~= 0.02357
P(C0(N+1)=1 | C0(N)=1) ~= 0.000424
observed adjacent starts: 10
independent-rate adjacent expectation: about 556
```

So complete coverage is common enough to appear around `2.36%` of the time in
this scan, but it almost never survives a `+1` shift.

Residues show a useful structural clue:

```text
C0 values mod 6 mostly lie in residues 2, 3, and 4.
Length-2 run starts are only 2 or 3 mod 6.
```

Thus a length-3 run, if it appears, would naturally be expected in a
`2,3,4 mod 6` pattern. The scan to `10^6` found no such triple.

## Length-2 Forensics

The forensic tables are generated with:

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

Outputs:

```text
data/summaries/prc_run_transition_stats_2_1000000.csv
data/summaries/prc_length2_pair_forensics_2_1000000.csv
data/summaries/prc_length2_neighborhoods_2_1000000.csv
data/summaries/prc_prefilter_validation_windows.csv
```

The transition table makes the anti-clustering reusable:

```text
complete_count = 23571
run_count = 23561
length2_run_count = 10
length3_start_count = 0
p_c0 ~= 0.023571
p_next_given_c0 ~= 0.000424
independent_adjacent_expectation ~= 555.59
```

The 20 validation windows all matched:

```text
10 windows around the length-2 runs
10 deterministic block-mid windows
all_exact values == prefilter exact-certified values in every window
```

This local validation is not the main proof of exhaustiveness; it is a
regression check on top of the binary64 tolerance guardrail. It checks the most
important local neighborhoods plus one fixed window per 100k block.

The length-2 pair table shows a repeated local pattern:

```text
A(N-1) > 0
A(N) = 0
A(N+1) = 0
A(N+2) > 0
```

For the 10 length-2 runs:

```text
min A(N-1) ~= 0.00872
median A(N-1) ~= 0.05196
max A(N-1) ~= 0.08130

min A(N+2) ~= 0.01787
median A(N+2) ~= 0.04788
max A(N+2) ~= 0.09249
```

So the pair is not sitting inside a flat almost-covered basin. The immediate
neighbors usually reopen a visible amount of uncovered measure.

The residue pattern is exact in this dataset:

```text
length-2 run starts mod 6:
2 -> 5 runs
3 -> 5 runs
other residues -> 0 runs
```

That means every length-2 pair is either a `(2,3)` or `(3,4)` pair modulo `6`.
A length-3 run would have to bridge the natural `(2,3,4)` corridor, but every
observed length-2 corridor breaks immediately on one side.

## Next Questions

1. Does `L(X)` ever reach `3`?
2. Are length-2 runs explained by shared local covering structure between `N`
   and `N+1`, or are they near coincidences?
3. Does the frequency of adjacent pairs grow, stay bounded, or decay relative
   to the number of complete-covering values?
4. Can we design a faster exact scanner for `X >= 10^6`?

The immediate next target is not another selected-window scan. It is an exact
or certified contiguous scan to a larger `X`, with performance work if needed.
