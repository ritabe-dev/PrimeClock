# Critical Radius and Birth Dynamics Sandbox

This experiment starts the post-v2.2.1 PRC research line. The public v2.2.1
release remains the stable `C_4/B_5` finite certificate artifact; files here are
internal research artifacts until explicitly promoted to a claim release.

## Purpose

- define the exact critical radius `lambda_k(r)` for prime-prefix residue
  coverings;
- verify `C_k = {r : lambda_k(r) <= 1/2}` for `k=4,5`;
- express births as old residual gaps contained in the new prime arc;
- classify `B_5`, `B_6`, and `B_7` births as strict/endpoint and
  single-gap/multi-gap events.

## Generate

From `research/`:

```bash
.venv/bin/python experiments/critical_radius_birth_dynamics/generate.py
```

Generated CSVs live in `data/` inside this experiment directory. They are not
part of the v2.2.1 public release bundle.

## Current Status

This is an internal v0.1 sandbox. It makes finite claims only for the generated
levels and does not assert an asymptotic law or a general birth theorem beyond
the exact containment identity.
