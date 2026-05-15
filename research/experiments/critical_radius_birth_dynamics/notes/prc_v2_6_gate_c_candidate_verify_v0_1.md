# Verify PrimeClock v2.6 Gate C Candidate

These checks require Python 3 with PyYAML available for `scripts/verify_candidate_workflow.py`.
To confirm the dependency:

```bash
python3 -c "import yaml; print(yaml.__version__)"
```

Run them from a clean extraction of the bundle. Generated files such as
`__pycache__/` are treated as artifact drift and should not be present in the
candidate directory.

Run the full Gate C candidate check:

```bash
python3 scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_6_v0_1.yml \
  v2-6-gate-c-candidate
```

Run the quick local check from an extracted bundle:

```bash
python3 scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_6_v0_1.yml \
  quick
```

Run the direct bundle self-check:

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_6_gate_c_candidate.py
```

Run the ZIP artifact check:

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_6_gate_c_candidate.py \
  --zip-only \
  --zip ../PrimeClock-v2.6-gate-c-candidate-v0.1.zip
```

Direct bundle build:

```bash
python3 research/experiments/critical_radius_birth_dynamics/candidate_bundle.py \
  --profile v2_6_gate_c_candidate \
  --out /private/tmp/primeclock-v26-gate-c-candidate \
  --zip
```

Direct bundle self-check:

```bash
python3 research/experiments/critical_radius_birth_dynamics/candidate_bundle.py \
  --profile v2_6_gate_c_candidate \
  --check /private/tmp/primeclock-v26-gate-c-candidate/PrimeClock-v2.6-gate-c-candidate-v0.1
```

Zip integrity check:

```bash
unzip -t /private/tmp/primeclock-v26-gate-c-candidate/PrimeClock-v2.6-gate-c-candidate-v0.1.zip
```
