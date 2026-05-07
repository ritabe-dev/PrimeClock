# Claims

Every statement in this research track should be assigned one of these statuses.

| Type | Meaning | Example |
|---|---|---|
| Definition | Notation or object being fixed | `Phi_N`, `mu_N`, `B_{N,k}` |
| Exact identity | True for every finite `N` | `floor(N/p)=k` iff `N/(k+1)<p<=N/k` |
| Proven theorem | Proved in the note | a finite identity or a self-contained lemma |
| Known theorem / citation | Covered by existing literature, or a direct corollary | `mu_N => rho(x) dx` via fractional-parts results for `x/n` |
| Model | Approximation, not a theorem | `rho_N^PNT` |
| Experiment | Numerically checked | histogram, KS distance, Fourier error |
| Conjecture | Observed but unproved | a specific finite-N error rate |
| Non-claim | Must not be stated as a finding | “new law of prime distribution” |
| Rejected | Disproved by a counterexample | any failed visual hypothesis |

## Current Claims

| Statement | Status |
|---|---|
| `Phi_N(p)={N/p}` for primes `p<=N` | Definition |
| `mu_N` is a probability measure on `[0,1)` | Exact identity |
| `rho(x)=sum_{k>=1}1/(k+x)^2` integrates to `1` | Exact identity |
| `mu_N => rho(x) dx` | Known theorem / citation target |
| `rho_N^PNT` gives a better finite-N comparison than `rho` | Model / Experiment |
| Fourier coefficients converge to the Fourier coefficients of `rho` | Theorem target from weak convergence |
| Histogram L1 decreases from `N=10^3` to `N=10^6` in v0 data | Experiment |
| KS distance decreases from `N=10^3` to `N=10^6` in v0 data | Experiment |
| Mean Fourier residual for modes `1..20` decreases from `N=10^3` to `N=10^6` in v0 data | Experiment |
| Branch errors decrease more slowly than histogram/Fourier metrics in v0 data | Experiment |
| `A(N)` is the total uncovered measure in Prime Reciprocal Covering | Definition |
| `G(N)` is the largest uncovered gap in Prime Reciprocal Covering | Definition |
| `C0(N)=1[A(N)=0]` is exact complete covering | Definition |
| `C_scale(N)=1[A(N)<1/N]` is the v0 scale event | Experiment |
| `C0(N)=1` for selected candidate-window values after exact interval checking | Exact identity / Experiment |
| `D_R(N)=#{M in [N-R,N+R]: C0(M)=1}/(2R+1)` is local complete-covering density | Definition |
| The v0 two-stage scan exact-checked every integer in the selected local windows and found 262 exact complete-covering window memberships, representing 260 unique `N` values, in 21 `R=250` windows from `10^3` to `10^6` | Experiment |
| The v0 two-stage scan found `float_positive_exact_count=0` on the regenerated `R=250`, threshold `0.05` data | Experiment |
| The v0 sensitivity table shows center-weighted mean `D_R` remains near `0.024` to `0.027` for `R=100,250,500` on the tested seed-conditioned window sets | Experiment |
| The all-exact contiguous scan found `L(100000)=2`, with the only length-2 run `[92229,92230]` | Experiment |
| The guarded prefiltered-and-exact-certified scan to `10^6` found longest run length `2` and no length-3 starts under the documented binary64 prefilter tolerance guarantee | Experiment / implementation-certified |
| In the v0 forensic validation set, all 20 all-exact windows matched the numeric-prefilter exact-certified values | Experiment |
| In the `10^6` forensic table, all length-2 runs start in residue `2` or `3` modulo `6` | Experiment |
| Branch-1 `G1(N)` is compared to transformed adjacent prime gaps | Experiment |

## Non-Claims

- This project does not claim a new theorem about prime distribution in v0.
- This project does not claim primes are uniformly random around the circle.
- This project does not claim the limiting density is new.
- This project does not claim the weak convergence `mu_N => rho(x) dx` is new; it appears to fall under Saffari--Vaughan style results on fractional parts of `x/n` and related sequences, including prime-restricted variants.
- This project does not use the visual clock as proof.
- This project does not assign number-theoretic meaning to individual Fourier residual peaks in v0.
- This project does not claim complete covering from floating-point `C0` checks alone; exact or certified interval checking is required.
- This project does not claim the selected `D_R` windows are an unbiased sample
  of all `N`; current cluster results are conditional on the seed rule.
- The prefilter guarantee is only an implementation-level binary64 guardrail
  for the documented v0 range `N <= 10^6`; it is not a theorem about PRC and
  does not extend to larger scans without renewed justification.
- This project does not claim `G1(N)` is exactly the largest raw prime gap divided by `N`; the transformed gap and arc radii must be used.

## Known-Result Check

The basic limiting density should be treated as known or standard unless a
reviewer says otherwise.

- Saffari--Vaughan I gives a general framework for fractional parts of `x/a`
  over subsets `A` whose counting function has regular variation. Since primes
  satisfy `pi(x) ~ x/log x`, the prime case has the right shape for this
  framework. The corresponding CDF is
  `F(a)=sum_{k>=1}(1/k - 1/(k+a))`, whose derivative is PRP's `rho(a)`.
- Saffari--Vaughan II explicitly studies `h(n)=1/n` and includes a prime-number
  section. Its Theorem 10 gives a weighted prime version, and the paper notes
  that partial summation gives the unweighted prime-counting version.
- For PRP, the safe v0 position is: cite this literature for the weak limit,
  then study finite-`N` correction, branch diagnostics, and Fourier diagnostics
  as the project's experimental contribution.
