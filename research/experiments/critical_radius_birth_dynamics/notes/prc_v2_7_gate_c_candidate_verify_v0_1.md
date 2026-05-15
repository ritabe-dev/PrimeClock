# Verify PrimeClock v2.7 Gate C Candidate

Run these commands from a clean extracted bundle root.

PyYAML is required by `scripts/verify_candidate_workflow.py`. If the import is
missing, install the research development dependencies in the full repository
environment before rebuilding the bundle.

Generated cache directories such as `__pycache__/` are treated as artifact drift
and may cause integrity checks to fail. Verify from a clean extraction when
checking a ZIP artifact.

```bash
python3 scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_7_v0_1.yml \
  quick
```

```bash
python3 scripts/verify_candidate_workflow.py \
  --config research/experiments/critical_radius_birth_dynamics/candidate_workflow_v2_7_v0_1.yml \
  v2-7-gate-c-candidate
```

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_7_gate_c_candidate.py
```

If the ZIP is next to the extracted bundle directory, verify only the ZIP with:

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_7_gate_c_candidate.py \
  --zip-only \
  --zip ../PrimeClock-v2.7-gate-c-candidate-v0.1.zip
```

```bash
shasum -a 256 -c SHA256SUMS
```
