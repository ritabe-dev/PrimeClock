# PRC v2.3 Internal Candidate Bundle

This internal candidate bundle contains the v2.3 critical-radius and
birth-dynamics research artifacts. It is not a public release.

The stable public release remains v2.2.3, focused on the `C_4/B_5` finite
certificate package. This candidate extends that line internally with:

- exact critical-radius spectra for `k=4,5`;
- `C_k = { r : lambda_k(r) <= 1/2 }` level-set checks;
- birth dynamics for `B_5`, `B_6`, and `B_7`;
- near-miss gap-geometry diagnostics for `k=4,5`;
- an internal candidate checker.

## Verify

From the bundle root:

```bash
cd research
python -m pip install -e ".[dev]"
python experiments/critical_radius_birth_dynamics/check_candidate.py
python -m pytest tests/test_critical_radius_birth_dynamics.py -q
```

Expected result:

```text
check_v2_3_candidate: checks=11, failed=0
```

## Scope

This candidate is finite and intentionally narrow:

```text
critical radius: k=4,5
birth dynamics: k=5,6,7
near-miss discussion: k=4,5
no B_8 or larger layers
no asymptotic or prime-distribution claims
```

## Status

This bundle is for internal promotion testing only. It should not be cited as a
public release or uploaded to Zenodo.
