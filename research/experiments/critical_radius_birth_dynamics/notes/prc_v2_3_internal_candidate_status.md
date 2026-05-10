# PRC v2.3 Internal Candidate Status

Status: internal-candidate.
Release eligibility: included in v2.3 candidate bundle, excluded from public release until promoted.

## Objective

The v2.2.4 public release remains the stable finite certificate artifact for:

```text
C_4 = {2,208} mod 210
|C_5| = 36
|B_5| = 14
```

This v2.3 internal line asks a narrower follow-up question:

```text
Can exact critical-radius spectra and gap-aperture windows explain early birth
dynamics through the next prime q-grid?
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
B_5: 14 unique strict single-gap births
B_6: 42 unique strict single-gap births
B_7: 714 unique strict single-gap births
```

Here `unique` means that each birth parent has exactly one admissible
next-prime remainder in the dual containment window, and it matches the
committed birth row.

Near-miss predictor:

```text
k=4 top-20 near-misses: 13 are B_5 birth parents
k=5 top-20 near-misses: 19 are B_6 birth parents
```

The useful finite predictor is not `lambda` rank alone. It is:

```text
near-miss candidate + q-grid phase in the dual containment window
```

The non-birth near-misses are phase misses: the old gaps are close to the
threshold, but no next-prime grid point lies in the needed window.

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
notes/prc_v2_3_related_work_v0_2.md
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
check_candidate.py: checks=13, failed=0
check_candidate_standalone.py: checks=10, failed=0
```

The helper-based checker regenerates the candidate rows from experiment code.
The standalone checker uses only the Python standard library, reads the
committed CSV artifacts, recomputes the k=4,5 critical-radius values from the
definition, and verifies the candidate CSV SHA256 manifest and headline finite
claims.

Quick verification is the standalone checker plus the lightweight non-bundle
pytest path:

```text
check_candidate_standalone.py: checks=10, failed=0
pytest -m "not slow and not bundle": 27 passed, 29 deselected
```

Bundle verification is separate because it builds temporary candidate packages
and exercises package hygiene guards:

```text
candidate_bundle.py --check <printed-candidate-package-directory>
candidate_bundle.py --zip
unzip -t <printed-candidate-zip-path>
pytest -m "bundle and not slow"  # CI/internal hygiene path
```

Current bundle pytest result:

```text
pytest -m "bundle and not slow": 18 passed, 38 deselected
```

Full internal verification remains helper-based and intentionally slower:

```text
check_candidate.py --progress: checks=13, failed=0
pytest -m slow: 11 passed, 45 deselected
```

Internal candidate bundle:

```text
candidate_bundle_manifest_v0_1.json
candidate_bundle.py -> PrimeClock-v2.3-candidate-v0.1
```

The v2.4 future-work notes are tracked internally but excluded from this
candidate bundle:

```text
notes/prc_no_multigap_birth_note_v0_1.md
notes/prc_v2_4_residual_gap_transition_graph_idea_v0_1.md
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
   unique single-gap birth theorem.

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
- that the v2.2.4 public release has changed.
