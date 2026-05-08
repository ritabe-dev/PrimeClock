# PRC Theme Scout v0.1

Objective: find research directions outside the current branch-uniform-null
main line that are at least as interesting as the null-model direction.

Current main line:

```text
Why does reciprocal phase structure fragment the residual uncovered set more
than a branch-uniform random placement with the same branch sizes and arc
widths?
```

This note asks what else is worth pursuing, using only directions that can be
made precise with the current PRC definitions and data.

## Selection Standard

A candidate must satisfy most of:

- it is not just a rephrasing of `branch_uniform` null refinement;
- it has a clean finite observable;
- there is already one reproducible signal in the repo;
- it has an obvious null or control design;
- it is not immediately swallowed by the known PRP limit literature;
- it can produce a short shareable note without claiming a new prime theorem.

## Baseline: Current Null-Model Direction

The current null-model direction is strong because v0.9 has a clean contrast:

```text
median observed residual-gap-count percentile vs branch_uniform null
complete              0.929
local_mod6_control    0.949
band_mod6_control     0.957
band_ordinary_control 0.962
```

This suggests a broad PRC-vs-null fragmentation effect rather than a
complete-specific low-component effect. It is still limited by the looseness of
the null: within-branch arithmetic order and local branch density are destroyed.

Any alternative theme should match this level of clarity.

## Candidate A: `C0` Anti-Clustering and Residue-Corridor Dynamics

Observable:

```text
C0(N) = 1[A(N)=0]
R_h(X) = #{N <= X-h : C0(N)=1 and C0(N+h)=1}
```

Current evidence from the certified contiguous scan `2 <= N <= 10^6`:

```text
complete_count = 23571
p_c0 ~= 0.023571
observed adjacent starts = 10
independent adjacent expectation ~= 555.59
P(C0(N+1)=1 | C0(N)=1) ~= 0.000424
```

A quick autocorrelation read from the same data gives:

| h | observed pairs | independent expectation | observed / expected |
|---:|---:|---:|---:|
| 1 | 10 | 555.59 | 0.018 |
| 2 | 652 | 555.59 | 1.174 |
| 3 | 11 | 555.59 | 0.020 |
| 4 | 5032 | 555.59 | 9.057 |
| 7 | 1595 | 555.59 | 2.871 |
| 30 | 3084 | 555.58 | 5.551 |
| 60 | 3109 | 555.56 | 5.596 |
| 90 | 3341 | 555.54 | 6.014 |
| 120 | 3527 | 555.53 | 6.349 |
| 210 | 10453 | 555.48 | 18.818 |

Residue concentration is also strong:

```text
mod 6 C0 counts:
2 -> 9331
4 -> 9320
3 -> 4768
1 -> 76
5 -> 67
0 -> 9

length-2 run starts mod 6:
2 -> 5
3 -> 5
other -> 0
```

Interpretation:

`C0` is not behaving like independent rare hits. It has severe local
anti-persistence at `h=1` and `h=3`, but strong positive recurrence at periods
such as `4`, `30`, and especially `210`. The mod-6 corridor says length-2 runs
are possible only in the observed `(2,3)` and `(3,4)` lanes up to `10^6`, while
the mod-210 read suggests the wheel structure is not a cosmetic correction.

Why this is at least as interesting as the null-model line:

- the signal is much larger than the v0.9 percentile effect;
- the observable is simpler to explain than residual component percentiles;
- it creates a mechanistic question about how full coverage is destroyed under
  `N -> N+1`;
- it connects the continuous arc model to the discrete residue-cell view
  `{N/p} = (N mod p)/p`;
- it can be tested with held-out contiguous ranges, not only selected windows.

Main risk:

The raw effect is partly forced by small-prime residues. The real theme is not
"adjacent complete values are rare" by itself; it is the residual
anti-clustering after conditioning on wheel classes such as mod `30` and
mod `210`.

Verdict: **best alternative theme**.

## Candidate B: Local Complete-Covering Density `D_R`

Observable:

```text
D_R(N) = #{M in [N-R,N+R] : C0(M)=1} / (2R+1)
```

Current evidence:

```text
selected R=250 windows:
D_250 ~= 0.0180 to 0.0339
mean D_250 ~= 0.0249
top center N=51692, D_250 = 17 / 501 ~= 0.0339
```

This is interesting because selected efficient windows can contain many exact
complete-covering values even when the median `A(N)` in the same window is not
near zero.

Why it is weaker than Candidate A:

- current windows are seed-conditioned;
- a real result needs a held-out sampling design;
- it still asks for a `C0` null model, so it is less independent from null
  design than the autocorrelation theme.

Verdict: good supporting theme; not the lead.

## Candidate C: Arithmetic-Order-Preserving Nulls

Observable:

```text
residual_gap_count percentile under local branch-bucket shuffles
```

This is the most natural next step inside the existing main line. It should
preserve more of:

- branch sizes;
- arc widths;
- within-branch density;
- possibly local order ranks.

Why it is not the requested "other theme":

It is important, but it is a refinement of the current null-model direction,
not a separate research theme.

Verdict: necessary control work, not the best alternative theme.

## Candidate D: Finite-`N` PRP Correction Theory

Observable:

```text
mu_N({N/p}) - rho_N^PNT
branch mass errors for k <= K
Fourier residuals
```

This is mathematically cleaner than PRC, but less novel in this project because
the limiting distribution of fractional parts of `x/n` over primes belongs near
the known Saffari-Vaughan literature. The useful contribution would be a
finite-size experimental model, not a new limit theorem.

Verdict: useful background/control layer; not as interesting as `C0`
anti-clustering.

## Candidate E: Edge-Dynamics Under `N -> N+1`

Observable:

```text
which arc endpoints open the largest new gaps when N changes to N+1?
which prime branches repair or fail to repair those gaps?
```

This is the mechanistic partner to Candidate A. The length-2 forensic table
already shows the repeated pattern:

```text
A(N-1) > 0
A(N) = 0
A(N+1) = 0
A(N+2) > 0
```

with median neighbor uncovered measures around `0.05`, so adjacent pairs are
not sitting inside a flat almost-covered basin.

Verdict: merge into Candidate A as the explanatory work package.

## Recommended Theme

The best alternative theme is:

```text
Complete-covering transition dynamics:
why exact PRC coverage is strongly anti-persistent under N -> N+1 after
small-prime residue structure is accounted for.
```

Short version:

```text
C0 anti-clustering and residue-corridor dynamics.
```

Core question before residue correction:

```text
Given that C0(N)=1, why is C0(N+1)=1 almost forbidden, while recurrence at
wheel-compatible lags such as 30, 60, 90, 120, and 210 is strongly enhanced?
```

After generating the v0.1 autocorrelation table, this should be sharpened:

```text
Given a wheel-compatible complete-covering value, why is C0(N+1) still strongly
suppressed relative to a mod-210 conditioned baseline?
```

The raw recurrence at `h=30,60,90,120,210` is mostly explained by residue
concentration once the mod-210 baseline is used. The surviving lead is adjacent
anti-persistence after wheel correction.

This is not a replacement for the branch-uniform-null main line. It is a second
pillar:

```text
Pillar 1: residual fragmentation relative to structured random coverings.
Pillar 2: exact coverage transition dynamics across N.
```

## First Work Package

1. Compute `R_h(X)` for `h=1..210` from certified contiguous scans.
2. Compare against three baselines:
   - independent Bernoulli with observed `p_c0`;
   - residue-conditioned Bernoulli mod `30`;
   - residue-conditioned Bernoulli mod `210`.
3. Separate two statistics:
   - autocorrelation of exact `C0`;
   - gap distribution between consecutive complete values.
4. For length-2 pairs, compute endpoint/branch witnesses for:
   - what closes the final gaps at `N`;
   - what remains closed at `N+1`;
   - what reopens at `N-1` and `N+2`.
5. Only after the mod-210 correction survives, consider extending the scanner
   beyond the `1,000,001 <= N <= 1,100,000` pilot.

## Non-Claims

- Do not claim `L(10^7)=2`; the full scan has not been run.
- Do not claim adjacent anti-clustering is universal or asymptotic.
- Do not claim the raw independent expectation is the final null; it is only
  the first sanity baseline.
- Do not claim a new theorem about primes from the finite `C0` transition data.

## Work Report

Purpose: identify an alternative research theme at least as interesting as the
current branch-uniform-null direction.

Current attainment: **100% for theme discovery**. A concrete lead theme has
been identified, corrected against mod-30 and mod-210 baselines, and backed by
the generated `data/summaries/prc_c0_autocorrelation_2_1000000.csv` table plus
`notes/prc_c0_transition_dynamics_v0_1.md`.

Estimated slices to reach a polished sub-note: **2 slices**.

- Slice 1: plot `h=1..210` observed/expected ratios for independent, mod-30,
  and mod-210 baselines.
- Slice 2: add endpoint/branch witness diagnostics for adjacent survival and
  adjacent failure cases.
