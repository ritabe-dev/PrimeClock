# PRC v2.7: General q-Prime Single-Gap Aperture Classification Theorem

Status: public theorem release text for `v2.7.0-prc-general-q-prime-theorem`.
Version DOI: pending Zenodo publication for the GitHub
`v2.7.0-prc-general-q-prime-theorem` release.
GitHub Release: pending creation for tag `v2.7.0-prc-general-q-prime-theorem`.

## What Is Proved

PRC v2.7 states a structural theorem inside the PRC circular-arc model.
For every `k >= 3`, every old residue `r in Z/M_kZ`, and every later odd prime
modulus `q>p_k`, a nonempty q-birth lift is exactly a single residual gap plus
q-grid aperture alignment.

The theorem concerns the direct one-prime q-lift over the old prefix. For
`q != p_{k+1}`, it does not claim that intermediate sequential PRC transitions
are skipped or unchanged.

## How To Verify

From the release bundle root:

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_7_public_theorem_release.py

python3 scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/public_theorem_release_bundle_workflow_v2_7_v1_0.yml \
  public-theorem-review
```

Expected results:

```text
check_v2_7_public_theorem_release: checks=8, failed=0
```

The exact audit is a recorded birth rows consistency audit for the committed
recorded birth rows in the finite next-prime support CSV. It is not a full
finite-universe completeness audit and is not the proof of the theorem.

DOI and registry integrity checks are full-repository release-execution checks only.
They depend on `scripts/check_release_doi_integrity.py` and
`release/public/release_registry.json`, which are not required for bundle-local
verification and are not included in this release ZIP.

## What Is Not Proved

- no B8 theorem;
- no full transition-graph theorem;
- no general predictor;
- no asymptotic law;
- no prime-gap theorem outside PRC model;
- not a full finite-universe completeness audit.

## Citation

Use the release-specific `CITATION.cff` in this bundle. The Zenodo version DOI
is finalized only after the GitHub Release is created and Zenodo mints the
version record.
