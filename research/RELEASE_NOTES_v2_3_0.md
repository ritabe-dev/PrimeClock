# PRC v2.3.0 Research Release Notes

Version DOI: `10.5281/zenodo.20119473`
Concept DOI: `10.5281/zenodo.20091722`.

This research release promotes the v2.3 critical-radius and gap-aperture
birth-dynamics finite artifact to public release status.

## Included Finite Results

- Critical-radius spectra for `k=4,5`.
- `C_4 = {2, 208}` modulo `210`.
- `C_5` has `36` covered residues.
- Birth-dynamics tables for `B_5/B_6/B_7`.
- `B_5/B_6/B_7` are unique strict single-gap births in the checked data.
- Near-miss and gap-geometry diagnostics for `k=4,5`.

## Verification

Run the v2.3 helper checker and standalone audit from `research/`:

```bash
python experiments/critical_radius_birth_dynamics/check_candidate.py \
  --out /tmp/prc-v2.3-helper-check.csv
python experiments/critical_radius_birth_dynamics/check_candidate_standalone.py \
  --out /tmp/prc-v2.3-standalone-check.csv
```

Expected summaries:

```text
check_v2_3_candidate: checks=13, failed=0
check_v2_3_candidate_standalone: checks=10, failed=0
```

## Non-Claims

This release is finite. It does not claim an asymptotic law, a prime-distribution
theorem, or a theorem that all future births are single-gap births. It does not
include `B_8`, null models, or residual-gap transition graph work.

Future work includes larger-layer spectra, static spectrum and gap-aperture
visual summaries, residual-gap transition graphs, null models, and broader
paper-preparation notes. These are not part of v2.3.0.
