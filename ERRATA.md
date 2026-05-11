# PrimeClock Errata Registry

This registry records corrections or clarifications for published PrimeClock /
PRC release lines without rewriting historical GitHub tags or Zenodo archives.

Use `release/public/MAINTENANCE_POLICY.md` to decide whether a finding belongs
here, on `main` as a docs clarification, or in a maintenance patch release.

## Entry Template

```text
Affected release:
Type: errata | docs clarification | maintenance patch | superseded
Impact: none | docs only | reproducibility | claim
Decision:
Target handling:
```

## Current Entries

### v2.2.4 README Research-Position Clarification

Affected release: v2.2.4
Type: docs clarification
Impact: docs only
Decision: v2.2.4 artifact, tag, GitHub Release, and Zenodo archive remain
unchanged. This is not a finite-claim correction and does not require a
v2.2.5 patch release.
Target handling: clarify in `main` and v2.3.0+ public docs that Prime
Reciprocal Covering is a project-defined finite prime-prefix circle-covering
model; classical covering systems are nearby vocabulary, not the claimed
target; and Zenodo DOI identifies a citable archive, not peer review.
