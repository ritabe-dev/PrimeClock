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
| `C_{p,r}=[(2r-1)/(2p),(2r+1)/(2p)] mod 1` and `I_p(N)=C_{p,N mod p}` define the finite prime residue-cell covering view of PRC | Definition |
| `U_P(N)=union_{p<=P} I_p(N)`, `A_P(N)=|T\\U_P(N)|`, and `R_P(N)=T\\U_P(N)` define the prime-prefix hierarchy | Definition |
| `M_k=prod_{i<=k}p_i` and `C_k={r in Z/M_kZ : union_{i<=k}I_{p_i}(r)=T}` define the exact prime-prefix residue-covering filtration | Definition |
| Prefix coverage by the first `k` primes depends only on `N mod M_k` | Exact identity |
| If `r in C_k`, then every lift of `r` modulo `M_{k+1}` belongs to `C_{k+1}` | Exact identity |
| The scouting exact table finds `C_1=C_2=C_3=empty`, `C_4={2,208} mod 210`, and `|C_7|=9384` with `714` new births at `p=17` | Experiment / theorem target |
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
| The v0.2 NumPy prefilter benchmark is about 5.3x faster than the pure Python prefilter on `1,000,001 <= N <= 1,001,000` in the recorded local run | Experiment |
| The v0.2 pilot over `1,000,001 <= N <= 1,100,000` found 2,380 exact-certified complete-covering values, 2,378 runs, longest run length `2`, and no length-3 starts | Experiment |
| Branch-1 `G1(N)` is compared to transformed adjacent prime gaps | Experiment |
| The v0.3 branch fill-in summary shows `K50=27` for `N=1000`, `K50=126..885` for four tested anchors, and censored `K50` for `N=1000000`; `K90/K99` are censored at `K=1000` for all tested anchors except `N=1000` | Experiment |
| The v0.4 matched cohort selected 36 complete seeds from `1000<=N<=1000000`, excluded 0 seeds, and generated 144 branch fill-in summary rows | Experiment |
| In the v0.4 matched cohort, complete rows have median `K50=234` and median residual at `K=1000` of `0.371519`; the three control groups have median `K50` of `211`, `160`, and `195`, and median residuals around `0.332` to `0.340` | Experiment |
| The v0.5.1 residual-gap table generated 144 raw rows after the common prefix `K=1000`; 3 prefix-exhausted seeds (`1258`, `1262`, `1329`) are marked ineligible, leaving 33 eligible seeds and 132 eligible rows for the main reading | Experiment |
| In the v0.5.1 eligible rows, complete rows have median residual max gap `0.001555` and median top-gap share `0.004218`; the three control groups have median max gaps `0.001531..0.001805` and median top-gap shares `0.004384..0.005354` | Experiment |
| In the v0.6 paired residual-gap summary, complete rows have fewer residual components than matched controls in `22/33`, `19/33`, and `26/33` pairs for the three control roles; top-gap-share direction is mixed across controls | Experiment |
| In the exploratory v0.7 residual-gap-count test, the weaker `band_ordinary_control` comparison has sign-test `p=0.00132` and BH `q=0.00396`, while the harder `local_mod6_control` and `band_mod6_control` comparisons have BH `q=0.1202` and `0.2810`; this is discovery evidence only | Experiment |
| In the exploratory v0.8 cluster audit, the 33 eligible seeds collapse to 11 clusters; complete rows have fewer residual components in `9/11`, `6/11`, and `10/11` clusters for the three control roles, with the hard `local_mod6_control` result remaining suggestive but not confirmatory | Experiment |
| In the v0.9 branch-uniform null model with 1000 iterations per row, all four cohorts have high median observed residual-gap-count percentiles (`0.929`, `0.949`, `0.957`, `0.962`), suggesting broad PRC residual fragmentation relative to this first coarse null rather than a complete-specific low-component effect | Experiment |
| In the v0.2 prime-prefix certificate-depth table, `18,377 / 23,571` exact-certified complete-covering values for `2<=N<=10^6` have a prefix certificate with `k<=7`; the remaining `5,194` are not certified within the checked `C_k` range | Experiment / exact finite filtration |
| In the v0.3 guarded `k=8` extension, `|C_8|=185,048` modulo `9,699,690`, and `699` additional exact-certified complete-covering values get a prefix certificate at `p=19`, leaving `4,495` uncertified within `max_k=8` | Experiment / exact finite filtration |
| In the v0.4 uncertified-residue profile, the `4,495` values left uncertified after `C_8` occupy `98` modulo-210 classes; nearest distance to `C_8` has median `25`, p90 `56`, p99 `90`, and max `97` in residue units modulo `M_8` | Experiment / diagnostic |
| In the v0.5 uncertified control profile, local non-complete controls have almost the same nearest-`C_8` distance distribution as the uncertified complete rows; the hard `local_mod210_control` comparison has median paired delta `0` | Experiment / diagnostic |
| In the v0.6 uncertified control audit, the v0.5 matched profile splits into `196` modulo-210 audit rows and `15` source-depth rows; source-depth composition is similar across complete rows and local controls | Experiment / diagnostic |
| In the v0.7 modulo-210 class review, `16` large classes have mixed control direction, so the sign of the nearest-`C_8` distance comparison often depends on whether the control preserves modulo `210` | Experiment / diagnostic |
| The v0.8 modulo-210 class detail table expands the top `8` v0.7 classes into `4,227` seed/control rows for inspection | Experiment / diagnostic |
| The v0.9 modulo-210 source summary shows that selected classes split into shallow `C_4`-adjacent classes (`4`, `206`, `201`) and mostly `C_5`-adjacent classes (`111`, `99`, with `118`, `88`, `62` more mixed) | Experiment / diagnostic |

## Non-Claims

- This project does not claim a new theorem about prime distribution in v0.
- This project does not claim primes are uniformly random around the circle.
- This project does not claim the limiting density is new.
- This project does not claim the weak convergence `mu_N => rho(x) dx` is new; it appears to fall under Saffari--Vaughan style results on fractional parts of `x/n` and related sequences, including prime-restricted variants.
- This project does not use the visual clock as proof.
- This project does not assign number-theoretic meaning to individual Fourier residual peaks in v0.
- This project does not claim complete covering from floating-point `C0` checks alone; exact or certified interval checking is required.
- This project does not claim the finite residue-covering hierarchy is a new
  prime distribution theorem; it is a framework for finite-`N` PRC covering
  experiments.
- This project does not claim an asymptotic law for `|C_k|/M_k`; the current
  prime-prefix residue filtration table is a finite exact generated artifact.
- This project does not claim `k<=7` certificate coverage explains all
  complete-covering values; rows without a prefix certificate are only
  uncertified within the checked filtration range.
- This project does not claim `k<=8` is exhaustive for complete-covering
  certificates; the remaining rows may need deeper prefixes or a different
  description.
- This project does not claim nearest-residue distance to `C_8` explains
  complete covering; v0.4 is only a diagnostic profile of rows left
  uncertified after `max_k=8`.
- This project does not claim the v0.5 local-control comparison is a final null
  model; it only shows that nearest-`C_8` distance alone is not currently a
  complete-specific explanation.
- This project does not claim the v0.6 modulo-210 audit explains the remaining
  uncertified complete-covering values; it is only a class-level diagnostic of
  the existing v0.5 control profile.
- This project does not claim the v0.7 class review explains complete covering;
  it is a ranking table for choosing modulo-210 classes to inspect next.
- This project does not claim the v0.8 class detail table is a null model; it
  is only an expanded inspection table for the highest-priority classes.
- This project does not claim the v0.9 source-depth split explains complete
  covering; it only identifies which shallow `C_k` layers the selected classes
  sit near.
- This project does not claim the v0.10 boundary-anchor split explains
  complete covering; it only identifies which shallow modulo-210 covered
  anchors the selected classes sit near.
- This project does not treat complete covering or anti-clustering as the main
  PRC axis in v1.0; they remain exploratory forensic subproblems.
- This project does not claim the selected `D_R` windows are an unbiased sample
  of all `N`; current cluster results are conditional on the seed rule.
- The prefilter guarantee is only an implementation-level binary64 guardrail
  for the documented v0.2 range `N <= 10^7`; it is not a theorem about PRC and
  does not extend to larger scans without renewed justification.
- This project does not claim `L(10^7)=2`; the full `N <= 10^7` scan has not
  been run.
- This project does not claim `G1(N)` is exactly the largest raw prime gap divided by `N`; the transformed gap and arc radii must be used.
- This project does not claim from v0.4 that complete-covering values are
  generally faster or slower branch fill-in cases; the matched cohort result is
  only an experiment-level comparison.
- This project does not claim from v0.5 that complete-covering values generally
  have smaller residual gaps; the result is only a matched-cohort observation.
- This project does not claim from v0.6 that residual component count explains
  exact complete covering; it is only a paired observation on 33 eligible seeds.
- This project does not claim from v0.7 that the tested residual-gap-count
  signal is stable outside the 33 eligible-seed matched cohort.
- This project does not claim v0.7 p-values are confirmatory; the metric was
  chosen after v0.6 exploration and the cohort has possible clustering/control
  reuse.
- This project does not claim v0.8 cluster-level p-values are confirmatory; the
  cluster rule is an audit guardrail after earlier exploration, not a
  preregistered design.
- This project does not claim the `band_ordinary_control` signal is robust,
  because that control role is a band-center non-complete control and has heavy
  reuse.
- This project does not claim the v0.9 branch-uniform null is the final or
  uniquely correct null model; it deliberately destroys within-branch arithmetic
  phase structure and does not preserve within-branch density/order.
- This project does not claim from v0.9 that high residual fragmentation is
  asymptotic or universal.

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
