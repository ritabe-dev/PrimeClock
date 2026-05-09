# Verify the Finite C4/B5 Certificate Bundle

From `research/`, install the package in editable mode and run the focused
finite theorem checks:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
python -m pytest tests/test_covering_prime_prefix_filtration.py -q
python -m prime_reciprocal_projection.cli covering-prime-prefix-verify-certificates \
  --out data/summaries/prc_prime_prefix_certificate_verification_v1_7.csv
python certificates/check_prime_prefix_c4_b5.py \
  --out data/summaries/prc_prime_prefix_certificate_standalone_verification_v1_8.csv
```

Expected focused results:

```text
focused pytest: 41 passed
package verifier: checks=14, failed=0
standalone checker: checks=9, failed=0
```

The same verifier contract is documented in
`research/VERIFY_FINITE_C4_B5.md`.

From the repository root, check the release allowlist hashes and public-bundle
hygiene:

```bash
python3 scripts/update_public_hashes.py --check
python3 scripts/build_public_release.py --version 2.2.2 --out /private/tmp/primeclock-public-release --zip
python3 scripts/check_public_release.py /private/tmp/primeclock-public-release/PrimeClock-2.2.2
```
