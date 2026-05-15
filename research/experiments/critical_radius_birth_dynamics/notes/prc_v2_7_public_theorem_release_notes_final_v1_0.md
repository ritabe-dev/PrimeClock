# PRC v2.7.1: General q-Prime Single-Gap Aperture Classification Theorem

Version DOI: `10.5281/zenodo.20209528`
GitHub Release:
https://github.com/ritabe-dev/PrimeClock/releases/tag/v2.7.1-prc-general-q-prime-theorem
Release asset: `PrimeClock-v2.7.1-general-q-prime-theorem-v1.0.zip`.

## Summary

This release states a structural theorem inside the PRC circular-arc model.
For every `k >= 3`, every old residue `r in Z/M_kZ`, and every later odd prime
modulus `q>p_k`, a nonempty q-birth lift is exactly a single residual gap plus
q-grid aperture alignment.

The result is general over later odd prime moduli `q>p_k` as a direct
one-prime q-lift over the old prefix. It is not a claim about the full
sequential insertion of all intermediate primes.

## Verification

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_7_public_theorem_release.py

python3 scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/public_theorem_release_bundle_workflow_v2_7_v1_0.yml \
  public-theorem-review
```

Expected result:

```text
check_v2_7_public_theorem_release: checks=8, failed=0
```

The exact audit is a recorded birth rows consistency audit for the committed
recorded birth rows in the finite next-prime support CSV. It is not a full
finite-universe completeness audit and is implementation evidence, not the
proof of the general q-prime theorem.

DOI and registry integrity checks remain full-repository release-execution
checks and are not required for extracted-bundle verification.

## Non-Claims

This release does not claim:

- no B8 theorem;
- no full transition-graph theorem;
- no general predictor;
- no asymptotic law;
- no prime-gap theorem outside PRC model;
- not a full finite-universe completeness audit.

## DOI Finalization

The release is prepared for a Zenodo version DOI. The DOI must be added only
after the GitHub Release exists and Zenodo has minted the version record.
