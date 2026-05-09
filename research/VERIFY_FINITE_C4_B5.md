# Verify Finite C4/B5 Package

This file is the verifier contract for the narrow `C_k/C_4/B_5` public
release bundle. It documents what the included checkers read, what they check,
and what their passing result supports.

## Setup

From `research/`:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
```

The `ruff` command requires this dev install step. If you only want the
standard-library standalone checker, no package install is needed.

## Input CSVs

The finite certificate checks use:

- `data/summaries/prc_prime_prefix_ck_full_v1_1.csv`
- `data/summaries/prc_prime_prefix_c4_exclusion_witness_v1_6.csv`
- `data/summaries/prc_prime_prefix_c4_exclusion_summary_v1_5.csv`
- `data/summaries/prc_prime_prefix_birth_witness_v1_5.csv`
- `data/summaries/prc_prime_prefix_b5_birth_classification_v1_5.csv`
- `data/summaries/prc_prime_prefix_b5_birth_pair_summary_v1_5.csv`

## Package Verifier

Run:

```bash
python -m prime_reciprocal_projection.cli covering-prime-prefix-verify-certificates \
  --out data/summaries/prc_prime_prefix_certificate_verification_v1_7.csv
```

Expected result:

```text
checks=14, failed=0
```

This verifier checks row counts, residue-set completeness, closed-arc coverage,
open-gap witnesses, rational witness points, exact interval/fraction fields,
the `C_4` summary partition, the `B_5` classification table, the reflection
pair quotient, and strict containment of each old open gap inside the new
`p=11` closed arc.
It exits with a nonzero status if any verification check fails.

## Standalone Checker

Run:

```bash
python certificates/check_prime_prefix_c4_b5.py \
  --out data/summaries/prc_prime_prefix_certificate_standalone_verification_v1_8.csv
```

Expected result:

```text
checks=9, failed=0
```

This checker uses only the Python standard library and does not import the
`prime_reciprocal_projection` package. It is the compact external audit path
for the public CSVs.

## Focused Test Suite

Run:

```bash
python -m pytest tests/test_covering_prime_prefix_filtration.py -q
```

Expected focused result:

```text
40 passed
```

## Logical Consequence of Passing Checks

When the public CSVs and both checkers pass, the narrow package supports:

- `C_4={2,208} mod 210`.
- Every other residue modulo `210` has a rational open-gap witness.
- `C_5` has `36` covered residues: `22` inherited lifts and `14` births.
- `B_5` is exactly the listed `14` residues modulo `2310`.
- The `14` B5 births form `7` reflection pairs.
- Each B5 birth is a strict single-gap closure by the new `p=11` closed arc.

These are finite certificate claims only. They are not claims about asymptotic
prime distribution or about all complete PRC events.
