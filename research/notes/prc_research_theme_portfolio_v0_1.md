# PRC Research Theme Portfolio v0.1

Objective: consolidate the research themes found so far and rank which ones can
develop into stronger research programs.

Status: this is a scouting portfolio, not the current main roadmap. The current
main frame is:

```text
Prime Reciprocal Covering as a finite-N hierarchy of prime residue-cell coverings.
```

The themes below are kept because they describe useful layers of that hierarchy,
but the ordering is about research potential inside the scouting set. It should
not be read as replacing `notes/prc_main_roadmap.md`.

The earlier main direction was:

```text
PRC residual sets are more fragmented than branch-uniform random placements
with the same branch sizes and arc widths.
```

That remains useful as a geometric null-comparison layer. Later scouting found
several finite residue-covering themes, especially around small-prime strata and
complete-covering certificates. Those `C0` themes are now treated as boundary
or forensic side tracks, not as the main external claim.

## Scouting Ranking

1. **Small-prime wheel covering strata and residual hierarchy**
2. **Certificate depth of complete covering**
3. **Complete-covering cliff dynamics**
4. **Adjacent volatility / saltation of `A(N)`**
5. **`C0` adjacent anti-persistence after wheel correction**
6. **Residual fragmentation against branch-uniform null**

This ranking is about research potential, not claim strength. Themes 1 and 2
are strongest because they can become finite, verifiable structural statements.
Themes 3 and 4 are strongest as geometric/dynamical explanations. Themes 5 and
6 remain useful controls and comparisons.

## Current Main-Axis Mapping

- **Main object:** prime-prefix residue-cell hierarchy.
- **Main diagnostics:** `A_P(N)`, residual components, gap shape, and
  residual fragmentation.
- **Geometric null layer:** branch-uniform and future stricter residue-aware
  nulls.
- **Boundary/certificate layer:** `C0`, wheel strata, certificate depth, and
  complete-covering cliffs.
- **Forensic transition layer:** adjacent anti-persistence and other
  `C0` transition dynamics.

Thus, Theme 6 is not discarded even though it is last in the scouting ranking:
it remains the main null-comparison layer. Themes 1, 2, 3, and 5 are `C0`
side-track material unless they are phrased as finite-prefix residue-covering
structure.

## Theme 1: Small-Prime Wheel Covering Strata

Main observation:

```text
N == 208 mod 210  -> C0(N)=1 for every tested N in 2 <= N <= 10^6
N == 2 mod 210    -> C0(N)=1 for every tested N except N=2
```

Evidence:

```text
residue 208 mod 210: 4761 / 4761 complete
residue   2 mod 210: 4761 / 4762 complete
```

This is deterministic at the small-prime level:

```text
the arcs from p = 2,3,5,7 already cover the circle for residues 2 and 208 mod 210.
```

Data:

```text
data/summaries/prc_c0_wheel_residue_rates_2_1000000.csv
```

Why it matters:

`C0` is not one homogeneous phenomenon. Up to `10^6`, `9522` of `23571`
complete values are in the two small-prime deterministic classes. Those should
be separated before analyzing transition, density, or clustering.

Research path:

1. Prove the `{2,208} mod 210` statement directly from the four arcs.
2. Generalize to primorial layers: `2*3*5*7*11`, then `2*3*5*7*11*13`.
3. Define a nontrivial `C0` subset by removing deterministic small-prime strata.
4. Redo `C0` density and transition summaries on that nontrivial subset.

Estimated slices:

```text
2 slices to a short rigorous note.
```

## Theme 2: Certificate Depth of Complete Covering

Main observation:

For a complete value `N`, define the certificate depth:

```text
P_cert(N) = smallest prime P such that arcs from primes p <= P cover the circle.
```

In the selected complete values from the broad windows plus the two original
candidate windows:

```text
unique complete values checked: 208
all certificate prime median: 11
all certificate prime max: 331
nontrivial certificate prime median: 17
nontrivial certificate prime max: 331
trivial small-prime stratum median/max: 7 / 7
```

Data:

```text
data/summaries/prc_selected_window_c0_certificate_depth_v0_1.csv
```

Why it matters:

This reframes complete covering as a finite certificate problem. Even for
large `N` near `10^6`, selected complete values can often be certified by very
small primes. The largest certificate prime in this selected set is `331`,
with `P_cert(N)/N` still tiny.

This is potentially stronger than a raw scan of `C0` values because it gives a
compact explanatory object:

```text
complete covering certificate = a small finite arc-covering proof.
```

Research path:

1. Compute certificate-depth distributions for all certified `C0` values up to
   `10^6`, not only selected windows.
2. Compare trivial, nontrivial-high-rate, and low-rate mod-210 classes.
3. Search for upper envelopes of `P_cert(N)` as `N` grows.
4. Turn each complete value into a minimal or near-minimal covering certificate.

Estimated slices:

```text
3 slices to a credible empirical note; more if minimal set certificates are
required rather than prime-prefix certificates.
```

## Theme 3: Complete-Covering Cliff Dynamics

Main observation:

Selected windows show that exact complete values are often adjacent to ordinary
uncovered mass. Even after removing the two trivial small-prime residues, the
neighbors of complete values are not merely tiny perturbations of zero.

Evidence:

```text
all C0-neighbor cliff rows:
count = 416
median neighbor A(N) ~= 0.0510
max neighbor A(N) ~= 0.1486

nontrivial C0-neighbor cliff rows:
count = 258
median neighbor A(N) ~= 0.0510
max neighbor A(N) ~= 0.1486
```

Data:

```text
data/summaries/prc_selected_window_c0_cliffs_v0_1.csv
```

Why it matters:

This says complete coverage is often a one-step cliff:

```text
A(N-1) visibly positive -> A(N)=0 -> A(N+1) visibly positive
```

That is a geometric mechanism question, not only a classification question.

Research path:

1. Add endpoint witnesses for nontrivial cliffs.
2. Identify which prime arcs close the last visible gaps.
3. Compare cliff sizes against matched non-complete local minima.
4. Build local-window figures showing repeated falls to zero and reopenings.

Estimated slices:

```text
3 slices to a convincing geometric note.
```

## Theme 4: Adjacent Volatility / Saltation of `A(N)`

Main observation:

`A(N)` is locally rough in selected windows, even away from exact zero events.
Across adjacent pairs in the selected windows:

```text
broad selected windows:
  adjacent pairs = 6000
  median |Delta A| ~= 0.0303
  p90 |Delta A|    ~= 0.0731
  p99 |Delta A|    ~= 0.1146
  max |Delta A|    ~= 0.1766
  median component-count jump = 116
  p99 component-count jump    = 4612
  max component-count jump    = 8691

original candidate windows:
  adjacent pairs = 2000
  median |Delta A| ~= 0.0282
  p90 |Delta A|    ~= 0.0683
  p99 |Delta A|    ~= 0.1064
  max |Delta A|    ~= 0.1450
  median component-count jump = 266.5
  p99 component-count jump    = 2790
  max component-count jump    = 4035
```

Data:

```text
data/summaries/prc_selected_window_adjacent_volatility_v0_1.csv
```

Why it matters:

The current PRC note treats `A(N)` as the main metric, but this theme asks about
the time series itself:

```text
how rough is A(N) under N -> N+1, and what causes large jumps?
```

This is broader than complete-covering cliffs. It could explain why local
windows can contain both exact zeros and very inefficient values.

Research path:

1. Compute adjacent volatility on unbiased contiguous ranges, not only selected
   windows.
2. Compare volatility by residue class and by small-prime residual measure.
3. Track which branches or prime intervals cause the largest component-count
   jumps.
4. Build a null model for local volatility, not only static residual shape.

Estimated slices:

```text
3 slices to a solid empirical note.
```

## Theme 5: `C0` Adjacent Anti-Persistence After Wheel Correction

Main observation:

The raw adjacent suppression is very strong:

```text
observed C0(N) and C0(N+1): 10
independent expected: about 555.59
observed / expected ~= 0.018
```

But after mod-210 conditioning, most wheel-compatible recurrence is explained.
The surviving signal is narrower:

```text
h=1 observed / mod-210 expected ~= 0.242
h=2 observed / mod-210 expected ~= 0.967
h=4 observed / mod-210 expected ~= 0.956
h=210 observed / mod-210 expected ~= 0.942
```

Data:

```text
data/summaries/prc_c0_autocorrelation_2_1000000.csv
notes/prc_c0_transition_dynamics_v0_1.md
```

Why it matters:

This is still a useful transition statistic, but it should now be downstream of
Theme 1. First remove deterministic small-prime strata; then re-evaluate
adjacent persistence on the nontrivial set.

Estimated slices:

```text
2 slices after Theme 1 cleanup.
```

## Theme 6: Residual Fragmentation Against Branch-Uniform Null

Main observation:

The current main-line v0.9 result:

```text
median observed residual-gap-count percentile vs branch_uniform null
complete              0.929
local_mod6_control    0.949
band_mod6_control     0.957
band_ordinary_control 0.962
```

Why it matters:

This remains the best theme for PRC as a random-covering-like geometric object:

```text
why does reciprocal phase structure fragment the residual uncovered set more
than branch-uniform random placement?
```

But it is now less central for exact `C0`, because small-prime strata and
certificate depth show that many complete events are decided by shallow finite
structure.

Estimated slices:

```text
2 slices for a stricter local branch-bucket null.
```

## Recommended Development Order

The old strongest path for the `C0` side track was:

1. **Write Theme 1 as a rigorous finite note.**
2. **Extend Theme 2 to all `C0` values up to `10^6`.**
3. **Use Theme 2 certificates to pick cases for Theme 3 endpoint witnesses.**
4. **Use Theme 4 to place cliffs inside a broader local-volatility theory.**
5. Return to Theme 5 only after the deterministic small-prime stratum is
   removed.
6. Continue Theme 6 as the geometric-null comparison line, separate from exact
   `C0` claims.

The current main-line order is instead:

1. Define the prime-prefix residue-cell hierarchy clearly.
2. Recast residual fragmentation as a diagnostic of that hierarchy.
3. Use Theme 1 only as the first finite wheel/certificate example.
4. Build stricter residue-aware null models before making stronger claims.
5. Return to `C0` transition dynamics only as a downstream forensic track.

## Non-Claims

- Do not claim all complete values are explained by `2,3,5,7`.
- Do not claim selected-window certificate depths are representative of all
  `C0` values.
- Do not claim selected-window volatility is globally representative.
- Do not treat branch-uniform null as the final random-covering null.
- Do not claim any asymptotic law from the current finite scans.

## Work Report

Purpose: find two more research-developable themes and consolidate all themes
found so far into one note.

Current attainment: **100% for the scouting and consolidation request**. Two
additional themes were found:

```text
certificate depth of complete covering
adjacent volatility / saltation of A(N)
```

and all six themes are summarized in this portfolio note.

Estimated slices from here:

- **2 slices**: rigorous Theme 1 note.
- **3 slices**: full `N<=10^6` certificate-depth scan and note.
- **3 slices**: endpoint-witness cliff note.
- **3 slices**: adjacent-volatility note on unbiased contiguous ranges.
