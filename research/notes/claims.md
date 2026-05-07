# Claims

Every statement in this research track should be assigned one of these statuses.

| Type | Meaning | Example |
|---|---|---|
| Definition | Notation or object being fixed | `Phi_N`, `mu_N`, `B_{N,k}` |
| Exact identity | True for every finite `N` | `floor(N/p)=k` iff `N/(k+1)<p<=N/k` |
| Proven theorem | Proved in the note | `mu_N => rho(x) dx`, once proof is written |
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
| `mu_N => rho(x) dx` | Proven theorem target |
| `rho_N^PNT` gives a better finite-N comparison than `rho` | Model / Experiment |
| Fourier coefficients converge to the Fourier coefficients of `rho` | Theorem target from weak convergence |

## Non-Claims

- This project does not claim a new theorem about prime distribution in v0.
- This project does not claim primes are uniformly random around the circle.
- This project does not claim the limiting density is new.
- This project does not use the visual clock as proof.

