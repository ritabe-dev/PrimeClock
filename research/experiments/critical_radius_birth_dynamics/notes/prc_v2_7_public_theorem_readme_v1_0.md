# PRC v2.7.1: General q-Prime Single-Gap Aperture Classification Theorem

Status: Gate P preflight README text for `v2.7.1-prc-general-q-prime-theorem`.
This is not a GitHub Release, not a DOI artifact, and not a Zenodo archive.

## What Is Proved

PRC v2.7 states a structural theorem inside the PRC circular-arc model.
For every `k >= 3`, every old residue `r in Z/M_kZ`, and every later odd prime
modulus `q>p_k`, a nonempty q-birth lift is exactly a single residual gap plus
q-grid aperture alignment.

The theorem concerns the direct one-prime q-lift over the old prefix. For
`q != p_{k+1}`, it does not claim that intermediate sequential PRC transitions
are skipped or unchanged.

## How To Verify

From the repository root or from the extracted preflight bundle root:

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_7_public_theorem_preflight.py
```

Expected result:

```text
check_v2_7_public_theorem_preflight: checks=7, failed=0
```

The exact audit is a recorded birth rows consistency audit for the committed
recorded birth rows in the finite next-prime support CSV. It is not a full
finite-universe completeness audit and is not the proof of the theorem.

For bundle-local integrity, also run this from the extracted preflight bundle
root:

```bash
python3 research/experiments/critical_radius_birth_dynamics/candidate_bundle.py \
  --profile v2_7_public_theorem_preflight \
  --check .
```

The bundle also includes a bundle-local workflow that intentionally omits the
repo-only DOI/registry integrity gate:

```bash
python3 scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/public_theorem_preflight_bundle_workflow_v2_7_v1_0.yml \
  public-theorem-review
```

DOI and registry integrity checks are full-repository preflight checks only.
They depend on `scripts/check_release_doi_integrity.py` and
`release/public/release_registry.json`, which are not required for bundle-local
verification and are not included in this preflight ZIP.

## What Is Not Proved

- no B8 theorem;
- no full transition-graph theorem;
- no general predictor;
- no asymptotic law;
- no prime-gap theorem outside PRC model;
- not a full finite-universe completeness audit.

## Citation

This Gate P preflight has no assigned DOI and no GitHub Release URL. The
included `DRAFT_CITATION.cff` is draft metadata only; root `CITATION.cff` is
created during final public release execution.
