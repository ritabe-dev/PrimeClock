# PrimeClock v2.7 Gate C Candidate

This bundle is an internal Gate C candidate for the PRC v2.7 General q-Prime
Single-Gap Aperture Classification Theorem.

It is not a public theorem release, not a DOI artifact, not a GitHub Release,
and not a public release registry entry.

## Contents

- `THEOREM_NOTE.md` states the geometric theorem note.
- `VERIFY.md` lists the reproducibility commands.
- `research/experiments/critical_radius_birth_dynamics/check_v2_7_general_single_gap_aperture_theorem_note.py`
  checks theorem-note structure and claim boundaries.
- `research/experiments/critical_radius_birth_dynamics/check_v2_7_strict_single_gap_aperture_exact_audit.py`
  checks implementation consistency for the committed recorded birth rows in
  the finite next-prime support CSV.
- `research/experiments/critical_radius_birth_dynamics/check_v2_7_gate_c_candidate.py`
  checks this Gate C candidate bundle and ZIP integrity.

The theorem proof is geometric and general over later odd prime moduli `q>p_k`
inside the PRC circular-arc model. For later primes beyond the next-prime case,
it concerns the direct one-prime q-lift over the old prefix, not the full
sequential insertion of all intermediate primes. The exact audit checks
implementation consistency for the committed recorded birth rows in the
B4-to-B5, B5-to-B6, and B6-to-B7 finite next-prime support CSV; it is not a full
finite-universe completeness audit and is not the proof of the theorem.

## Boundary

This candidate makes no B8 theorem, predictor, or asymptotic-law claim. It does
not update DOI material, GitHub Release material, the public release registry,
or the root public README.
