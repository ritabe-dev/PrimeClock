# PRC v2.3 Internal Candidate Status

Status: internal candidate, not a public release.

## Objective

The v2.2.3 public release remains the stable finite certificate artifact for:

```text
C_4 = {2,208} mod 210
|C_5| = 36
|B_5| = 14
```

This v2.3 internal line asks a narrower follow-up question:

```text
Can exact critical-radius spectra explain early birth dynamics through old-gap
containment?
```

The current answer is yes for the checked finite layers, with explicit limits.

## Current Evidence

Critical-radius level sets:

```text
C_4 = { r : lambda_4(r) <= 1/2 }
|C_5| = |{ r : lambda_5(r) <= 1/2 }| = 36
```

Spectrum summary:

```text
k=4: robust=0, endpoint=2, uncovered=208, nearest uncovered lambda=5/9
k=5: robust=2, endpoint=34, uncovered=2274, nearest uncovered lambda=7/13
```

Birth dynamics:

```text
B_5: 14 strict single-gap births
B_6: 42 strict single-gap births
B_7: 714 strict single-gap births
```

Near-miss predictor:

```text
k=4 top-20 near-misses: 13 are B_5 birth parents
k=5 top-20 near-misses: 19 are B_6 birth parents
```

The useful finite predictor is not `lambda` rank alone. It is:

```text
near-miss candidate + containing next-prime remainder
```

## Artifact Map

Read in this order:

```text
notes/prc_v2_3_internal_candidate_status.md
notes/prc_v2_3_theorem_note_draft_v0_1.md
notes/prc_v2_3_theorem_candidate_outline_v0_1.md
notes/prc_near_miss_birth_predictor_v0_2.md
notes/prc_critical_radius_birth_dynamics_v0_1.md
```

Data artifacts:

```text
data/prc_prime_prefix_critical_radius_k4_k5_v0_1.csv
data/prc_prime_prefix_critical_radius_summary_v0_1.csv
data/prc_prime_prefix_critical_radius_near_misses_k4_k5_v0_1.csv
data/prc_prime_prefix_near_miss_birth_parent_overlap_k4_k6_v0_1.csv
data/prc_prime_prefix_near_miss_gap_geometry_k4_k5_v0_1.csv
data/prc_prime_prefix_birth_threshold_crossing_k5_k7_v0_1.csv
data/prc_prime_prefix_birth_dynamics_k5_k7_v0_1.csv
data/prc_prime_prefix_birth_dynamics_summary_v0_1.csv
```

## Promotion Boundary

This is ready as an internal research milestone, but not yet a public release.

Before promotion to a v2.3 public candidate:

1. Add a compact theorem/proposition note for the critical-radius formula.
2. Add a finite proposition for the birth-containment identity.
3. Decide whether to include only `k<=7` birth dynamics or extend the same
   checker format one level further.
4. Keep all statements finite; do not claim an asymptotic law or a general
   single-gap birth theorem.

## Next Slice

The design slice now has a first internal theorem-note draft:

```text
notes/prc_v2_3_theorem_note_draft_v0_1.md
notes/prc_v2_3_theorem_candidate_outline_v0_1.md
```

The next useful slice is still not brute force. It should turn the outline into
a compact checker path for the finite v2.3 candidate claims, or polish the draft
into a public-candidate note. Only after that should new data be added.

## Non-Claims

This internal candidate does not claim:

- that all births are single-gap births;
- that near-miss rank alone predicts births;
- that the checked finite layers imply an asymptotic law;
- that the v2.2.3 public release has changed.
