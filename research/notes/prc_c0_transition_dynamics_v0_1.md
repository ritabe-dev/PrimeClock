# PRC C0 Transition Dynamics v0.1

Objective: test whether exact complete covering `C0(N)=1` has transition
structure across `N -> N+h` that is interesting outside the current
branch-uniform-null residual-fragmentation line.

## Observable

For a certified contiguous range, define

```text
C0(N) = 1[A(N)=0]
R_h(X) = #{N <= X-h : C0(N)=1 and C0(N+h)=1}.
```

The current v0.1 table compares `R_h` against three baselines:

- independent Bernoulli with observed global `p_c0`;
- residue-conditioned Bernoulli by `N mod 30`;
- residue-conditioned Bernoulli by `N mod 210`.

The residue-conditioned baselines are essential. Without them, the strong wheel
structure of complete values makes `h=30,60,90,120,210` look more mysterious
than it is.

## Command

```bash
python -m prime_reciprocal_projection.cli covering-run-autocorrelation \
  --input data/summaries/prc_combined_runs_2_1000000.csv \
  --start 2 \
  --stop 1000000 \
  --max-lag 210 \
  --out data/summaries/prc_c0_autocorrelation_2_1000000.csv
```

Output:

```text
data/summaries/prc_c0_autocorrelation_2_1000000.csv
```

## Current Result

The raw independent comparison is very strong:

| h | observed pairs | independent expected | observed / independent |
|---:|---:|---:|---:|
| 1 | 10 | 555.59 | 0.018 |
| 2 | 652 | 555.59 | 1.174 |
| 3 | 11 | 555.59 | 0.020 |
| 4 | 5032 | 555.59 | 9.057 |
| 30 | 3084 | 555.58 | 5.551 |
| 60 | 3109 | 555.56 | 5.596 |
| 90 | 3341 | 555.54 | 6.014 |
| 120 | 3527 | 555.53 | 6.349 |
| 210 | 10453 | 555.48 | 18.818 |

But after mod-210 conditioning, most wheel-compatible recurrence weakens:

| h | observed pairs | mod-210 expected | observed / mod-210 |
|---:|---:|---:|---:|
| 1 | 10 | 41.24 | 0.242 |
| 2 | 652 | 674.18 | 0.967 |
| 3 | 11 | 14.70 | 0.748 |
| 4 | 5032 | 5266.11 | 0.956 |
| 30 | 3084 | 3570.91 | 0.864 |
| 60 | 3109 | 3586.12 | 0.867 |
| 90 | 3341 | 3749.90 | 0.891 |
| 120 | 3527 | 3749.84 | 0.941 |
| 210 | 10453 | 11098.98 | 0.942 |

The important surviving signal is therefore not "large positive recurrence at
wheel lags." Much of that is explained by residue concentration. The more
interesting signal is:

```text
after mod-210 conditioning, adjacent persistence h=1 remains strongly
suppressed: observed / expected ~= 0.242.
```

The `h=3` suppression is weaker after mod-210 conditioning, while `h=2` and
`h=4` are close to the mod-210 baseline. This points to a local transition
effect that is sharper than ordinary wheel-class frequency, but narrower than
the raw independent comparison suggests.

## Reading

This remains useful as a forensic side track under the current finite
residue-covering hierarchy frame. The precise side-track theme is:

```text
C0 adjacent anti-persistence after wheel correction.
```

Not:

```text
C0 has unexplained strong recurrence at h=210.
```

The candidate research question becomes:

```text
Given a wheel-compatible complete-covering value, what local endpoint/branch
mechanism makes C0(N+1) much rarer than its mod-210 conditioned rate?
```

This complements the current main line without replacing it:

- main line: finite prime-prefix residue-cell coverings and their residual
  uncovered sets;
- side track: exact full coverage is locally fragile even after small-prime
  residue classes are conditioned out.

## Next Work

1. Add a figure for `observed / expected` over `h=1..210` under the three
   baselines.
2. Add endpoint/branch witness rows around the 10 length-2 pairs and matched
   singleton complete values.
3. Test whether the same mod-210 corrected adjacent suppression holds in the
   `1,000,001 <= N <= 1,100,000` pilot.
4. Only after those checks, decide whether scanner optimization for a larger
   contiguous range is worth it.

## Non-Claims

- This does not claim an asymptotic law for `C0`.
- This does not claim `L(10^7)=2`.
- This does not use independent Bernoulli as the final null.
- This does not claim wheel lags are unexplained; v0.1 shows mod-210 explains
  much of the raw recurrence.

## Work Report

Purpose: turn the strongest alternative theme from
`prc_theme_scout_v0_1.md` into a reproducible first experiment.

Current attainment: **100% for theme discovery**, because an alternative theme
has been selected, corrected against a stronger residue baseline, and tied to a
generated CSV. It is **about 60% for a publishable sub-note**, because figures
and endpoint witnesses are still missing.

Estimated slices to a polished sub-note: **2 slices**.

- Slice 1: plot `h=1..210` observed/expected ratios for independent, mod-30,
  and mod-210 baselines.
- Slice 2: add endpoint/branch witness diagnostics for adjacent survival and
  adjacent failure cases.
