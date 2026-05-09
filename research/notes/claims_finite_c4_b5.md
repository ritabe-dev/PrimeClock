# Finite C4/B5 Claims

This is the narrow claim registry for the public `C_k/C_4/B_5` finite
certificate bundle. It only covers the finite certificate artifacts included in
this release.

The release-ready v2.0 theorem note is
`prc_finite_certificate_note_v2_0.md`.

## Status Labels

| Type | Meaning |
|---|---|
| Definition | Notation or object being fixed |
| Exact identity | Finite statement true by the definitions |
| Exact generated artifact | Reproducible finite CSV/checker artifact |
| Non-claim | Statement that should not be inferred from this package |

## Audited Claims

| Statement | Status |
|---|---|
| `M_k=prod_{i<=k}p_i` and `C_k={r in Z/M_kZ : union_{i<=k}I_{p_i}(r)=T}` define the exact prime-prefix residue-covering filtration | Definition |
| The theorem-level arcs are closed subsets of `R/Z`; open-gap strings in CSVs are boundary endpoints for uncovered open gaps | Definition |
| Prefix coverage by the first `k` primes depends only on `N mod M_k` | Exact identity |
| If `r in C_k`, then every lift of `r` modulo `M_{k+1}` belongs to `C_{k+1}` | Exact identity |
| With `B_k=C_k \\ Lift_k(C_{k-1})` and `alpha_k=|C_k|/M_k`, `alpha_k=alpha_{k-1}+|B_k|/M_k`; therefore `alpha_k` is nondecreasing | Exact identity |
| If `r in C_k`, then `-r mod M_k in C_k` by circle reflection symmetry | Exact identity |
| The finite note states `C_1=C_2=C_3=empty` and `C_4={2,208} mod 210` | Exact generated artifact |
| The v1.6 `C_4` exclusion-witness table gives one rational open-gap witness and one rational `witness_point` for each of the `208` residues outside `{2,208} mod 210` | Exact generated artifact |
| The v1.5 `C_4` exclusion-summary table compresses the `208` excluded residues into `36` exact uncovered-measure/component classes with complete residue lists | Exact generated artifact |
| The v1.1 full export gives all covered rows through `k=5`: `C_5` has `36` rows, split into `22` inherited lifts and `14` births | Exact generated artifact |
| The finite `B_5` proposition states the exact birth set `{118,448,542,778,849,872,1108,1202,1438,1461,1532,1768,1862,2192} mod 2310` | Exact generated artifact |
| In `B_5`, every birth is a strict single-gap closure by the new `p=11` arc; six reflection pairs close a gap of length `1/20`, one pair closes a gap of length `1/21`, and no pair uses endpoint touching | Exact generated artifact |
| The v1.5 `B_5` witness/classification/pair-summary CSVs support the `14` births and `7` reflection pairs | Exact generated artifact |
| The v1.7 package verifier reports `14` checks and `0` failures on the public finite theorem CSVs | Exact generated artifact |
| The v1.8 standard-library standalone checker reports `9` checks and `0` failures without importing `prime_reciprocal_projection` | Exact generated artifact |

## Non-Claims

- This package does not claim a new theorem about prime distribution.
- This package does not claim a new limiting law for `{N/p}`.
- This package does not claim an asymptotic law for `|C_k|/M_k`.
- This package does not claim `C_4` or `C_5` explains all complete PRC events.
- This package does not claim selected modulo-210 diagnostics are representative.
- This package does not use floating-point coverage checks for theorem-level claims.
- This package does not include the full historical PRC archive; claims about
  certificate depth, `k=8`, residual fragmentation, or C0 anti-clustering are
  context claims in the full repository, not audited by the minimal bundle.
