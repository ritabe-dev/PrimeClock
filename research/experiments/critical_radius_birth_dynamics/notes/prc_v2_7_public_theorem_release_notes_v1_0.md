# PRC v2.7 Public Theorem Preflight Release Notes

Status: Gate P preflight release notes for `v2.7.1-prc-general-q-prime-theorem`.
Version DOI: not assigned.
GitHub Release: not created.

## Release Title

```text
PRC v2.7.1: General q-Prime Single-Gap Aperture Classification Theorem
```

## Proposed Tag

```text
v2.7.1-prc-general-q-prime-theorem
```

## Proposed Release Asset

```text
PrimeClock-v2.7.1-general-q-prime-theorem-v1.0.zip
```

## Summary

This theorem classifies q-birth lifts in the stated PRC circular-arc model. A
nonempty q-birth lift is possible only for a single residual gap, and in that
case it is equivalent to q-grid aperture alignment.

The theorem is general over later odd prime moduli `q>p_k` as a direct
one-prime q-lift over the old prefix. It is not a claim about the full
sequential insertion of all intermediate primes.

## Verification

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_7_public_theorem_preflight.py
```

Expected result:

```text
check_v2_7_public_theorem_preflight: checks=7, failed=0
```

The exact audit is a recorded birth rows consistency audit for the committed
recorded birth rows in the finite next-prime support CSV. It is not a full
finite-universe completeness audit and is implementation evidence, not the
proof of the general q-prime theorem.

The bundle-local preflight workflow excludes the repo-only DOI/registry
integrity gate. DOI and registry integrity remain full-repository preflight
checks and are not required for extracted-bundle verification.

## Non-Claims

This preflight does not claim:

- no B8 theorem;
- no full transition-graph theorem;
- no general predictor;
- no asymptotic law;
- no prime-gap theorem outside PRC model;
- not a full finite-universe completeness audit.

## Publication Boundary

This preflight does not create a tag, GitHub Release, Zenodo archive, DOI, or
public release registry finalization. Those remain Gate P release execution
steps after a separate explicit decision.
