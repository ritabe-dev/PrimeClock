# PRC Birth Dynamics v0.1

This note records the finite birth mechanism used by the critical-radius
sandbox. It is an internal experiment, not part of the stable v2.2.1 public
release.

Let `q=p_{k+1}`. A lift from `Z/M_kZ` to `Z/M_{k+1}Z` fixes a parent residue
`s mod M_k` and chooses a new residue `a mod q`. Let

```text
R_k(s) = R/Z \ U_k(s)
```

be the old residual open-gap set. A newly covered lift is exactly a lift whose
new `q`-arc contains the old residual set:

```text
r in B_{k+1}
iff
s notin C_k and R_k(s) subset I_q(a).
```

The v0.1 classification records whether this containment is:

```text
strict_single_gap_birth
endpoint_single_gap_birth
strict_multi_gap_birth
endpoint_multi_gap_birth
```

Initial artifacts:

```text
data/prc_prime_prefix_birth_dynamics_k5_k7_v0_1.csv
data/prc_prime_prefix_birth_dynamics_summary_v0_1.csv
```

The finite checks are deliberately limited:

- `B_5` remains the existing `14` birth residues in `7` reflection pairs.
- `B_6` has `42` births.
- `B_7` has `714` births.
- The summary records how many are strict/endpoint and single/multi-gap.

No general claim is made from these initial levels.
