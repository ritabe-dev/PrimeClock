# PRC v2.5 Public Theorem Release Notes

Status: prepared release notes text, pending explicit release execution.  This
file does not create a tag, GitHub Release, Zenodo upload, DOI, or public B8
claim.

## Release Title

```text
PRC v2.5: finite aperture-orbit separator theorem
```

## Recommended Tag

```text
v2.5.0-prc-public-theorem
```

## Summary

This release fixes a scoped finite theorem for PrimeClock PRC residual-covering
dynamics.  In the recorded complete transition scopes `B4->B5`, `B5->B6`, and
`B6->B7`, positive signed aperture-orbit margin exactly separates checked close
rows from checked non-close rows.

For every committed checked row in the materialized finite universe `U`:

```text
Close(row) iff m(row) > 0
```

The signed aperture-orbit margin is a finite exact terminal containment
certificate.  It is not a general predictor.

## Verification

From the repository root:

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_5_public_theorem_integrity.py
```

Expected result:

```text
check_v2_5_public_theorem_integrity: checks=9, failed=0
```

## Counts

```text
checked lift rows                         533690
close rows                                  770
birth rows                                  770
non-close positive-margin rows                0
capacity non-close lift rows             52566
capacity non-close positive-margin rows       0
endpoint-touch rows                           0
minimum close positive margin             1/221
maximum non-close margin                  -1/221
```

## Non-Claims

This release does not claim:

- B8 theorem;
- B8 full graph;
- general predictor;
- asymptotic law;
- coverage, recall, or holdout validation for B8;
- automatic extension beyond the recorded complete transition scopes.

## Archive Boundary

An archive asset is optional.  If one is attached, it should be a release asset
for this scoped theorem and must not include B8 stress-control artifacts,
internal candidate files, predictor notes, breakthrough diagnostics, or other
candidate-only diagnostics.

Do not add a DOI to this release text until Zenodo has minted the DOI.
