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
promotion_manifest_v0_1.yml
notes/prc_v2_3_theorem_note_draft_v0_1.md
notes/prc_v2_3_theorem_candidate_outline_v0_1.md
notes/prc_weighted_covering_radius_terminology_v0_1.md
notes/prc_weighted_bisector_candidate_lemma_v0_1.md
notes/prc_v2_3_related_work_decision_v0_1.md
notes/prc_v2_3_standalone_checker_contract_v0_1.md
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
data/prc_v2_3_candidate_verification_v0_1.csv
data/prc_v2_3_candidate_sha256sums_v0_1.txt
data/prc_v2_3_candidate_standalone_verification_v0_1.csv
```

Internal checkers:

```text
check_candidate.py: checks=12, failed=0
check_candidate_standalone.py: checks=7, failed=0
```

The helper-based checker regenerates the candidate rows from experiment code.
The standalone checker uses only the Python standard library, reads the
committed CSV artifacts, and verifies the candidate CSV SHA256 manifest and
headline finite claims.

Internal candidate bundle:

```text
candidate_bundle_manifest_v0_1.json
candidate_bundle.py -> PrimeClock-v2.3-candidate-v0.1
```

## Promotion Boundary

This is ready as an internal research milestone, but not yet a public release.

The internal promotion manifest fixes the candidate scope:

```text
critical radius: k=4,5
birth dynamics: k=5,6,7
near-miss discussion: k=4,5
no B_8 or larger layers
```

Before promotion to a public v2.3 release bundle:

1. Convert `candidate_bundle_manifest_v0_1.json` into a `release/public`
   config with GitHub/Zenodo metadata.
2. Keep the related-work decision fixed: use `critical radius` as the project
   term, and add formal covering-radius citations only if the public note leans
   on that external terminology.
3. Keep all statements finite; do not claim an asymptotic law or a general
   single-gap birth theorem.

## Next Slice

The design slice now has a first internal theorem-note draft:

```text
notes/prc_v2_3_theorem_note_draft_v0_1.md
notes/prc_v2_3_theorem_candidate_outline_v0_1.md
```

The next useful slice is still not brute force. The checker path, promotion
manifest, internal candidate bundle path, and terminology boundary note now
exist, so the next step should decide whether to run an external review on the
candidate or prepare the public v2.3 release manifest. Only after that should
new data be added.

## Non-Claims

This internal candidate does not claim:

- that all births are single-gap births;
- that near-miss rank alone predicts births;
- that the checked finite layers imply an asymptotic law;
- that the v2.2.3 public release has changed.
