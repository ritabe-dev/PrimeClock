# Verify the PRC v2.3.0 Public Bundle

From `research/`, install the package in editable mode:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
```

Run the original finite `C_4/B_5` checks:

```bash
python -m pytest tests/test_covering_prime_prefix_filtration.py -q
python -m prime_reciprocal_projection.cli covering-prime-prefix-verify-certificates \
  --out data/summaries/prc_prime_prefix_certificate_verification_v1_7.csv
python certificates/check_prime_prefix_c4_b5.py \
  --out data/summaries/prc_prime_prefix_certificate_standalone_verification_v1_8.csv
```

Expected focused results:

```text
focused pytest: 55 passed
package verifier: checks=14, failed=0
standalone checker: checks=9, failed=0
```

Run the v2.3.0 critical-radius and birth-dynamics checks:

```bash
python experiments/critical_radius_birth_dynamics/check_candidate.py \
  --out /tmp/prc-v2.3-helper-check.csv
python experiments/critical_radius_birth_dynamics/check_candidate_standalone.py \
  --out /tmp/prc-v2.3-standalone-check.csv
python -m pytest tests/test_critical_radius_birth_dynamics_public.py -q
```

Expected v2.3.0 results:

```text
check_v2_3_candidate: checks=13, failed=0
check_v2_3_candidate_standalone: checks=10, failed=0
public critical-radius/birth-dynamics pytest: 9 passed
```

From the repository root, check the release allowlist hashes and public-bundle
hygiene:

```bash
python3 scripts/check_release_versions.py
python3 scripts/verify_public_release.py --out "${TMPDIR:-/tmp}/primeclock-public-release" --zip
```
