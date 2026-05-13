# PRC v2.5 Publication Plan

Status: Gate P publication-path plan.  This note does not authorize a GitHub
Release, Zenodo upload, DOI minting, or public B8 claim.

## Purpose

The purpose is to publish PRC v2.5, if Gate P later authorizes publication, as a
scoped finite theorem rather than as a ZIP-centered candidate package.

The public theorem scope remains:

```text
B4->B5, B5->B6, and B6->B7 recorded complete transition scopes.
For every committed checked row in the materialized finite universe U,
Close(row) iff m(row) > 0.
```

This is a finite exact aperture-orbit separator theorem and a committed finite
certificate artifact audit.  It is not a general predictor, not a B8 theorem,
and not an asymptotic law.

## What Gets Published

The main publication path is:

```text
repo tag + release notes + public theorem README + verifier command
```

Recommended GitHub Release fields:

```text
tag: v2.5.0-prc-public-theorem
title: PRC v2.5: finite aperture-orbit separator theorem
```

The release notes should state:

- theorem scope: `B4->B5`, `B5->B6`, `B6->B7` only;
- theorem claim: `Close(row) iff m(row) > 0` in the materialized finite universe
  `U`;
- exact counts: `533690` checked lift rows, `770` close rows, `770` birth rows,
  `0` non-close positive-margin rows, `52566` capacity non-close lift rows;
- verification command:

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_5_public_theorem_integrity.py
```

## Optional Archive Asset

ZIP is optional.  It is a snapshot or release-asset format, not the publication
center.

Review ZIP name:

```text
PrimeClock-v2.5-public-theorem-review-v0.1.zip
```

If a release archive asset is needed, generate it as a separate release asset:

```text
PrimeClock-v2.5-public-theorem-v1.0.zip
```

The release archive must still exclude B8 stress-control artifacts, internal
candidate files, predictor notes, breakthrough diagnostics, and other
candidate-only diagnostics.

## Release Sequence

1. Verify the public theorem review path from the repo.
2. Prepare release notes and public theorem README wording.
3. Build an optional archive asset only if the release needs an attached
   snapshot.
4. Tag the repo with `v2.5.0-prc-public-theorem`.
5. Create the GitHub Release only after the tag, release notes, and verifier
   command are checked together.

This sequence must not modify the v2.3.0 public release line.  The existing
`release/public/release_config.json` remains the v2.3.0 release config unless a
later explicit release-systems slice adds a separate v2.5 public config.

## DOI Sequence

Zenodo DOI work comes after the GitHub Release decision.

The Zenodo metadata must match the GitHub Release:

- title: `PRC v2.5: finite aperture-orbit separator theorem`;
- version: `v2.5.0-prc-public-theorem`;
- description: finite checked-scope theorem, not B8, not a predictor, not an
  asymptotic law;
- related identifiers: v2.3.0 public release DOI if appropriate;
- license: same license as the repository release.

Do not write a DOI into README or release notes until the DOI exists.

## Rollback Boundary

Before publication:

- delete or replace temporary release-candidate artifacts;
- keep the repo tag uncreated;
- keep GitHub Release and Zenodo absent.

After publication:

- do not rewrite v2.3.0 release artifacts;
- do not silently replace a DOI archive;
- corrections should be issued as a new release note, erratum, or later version.

## Non-Claims

The v2.5 publication path does not claim:

- B8 theorem;
- B8 full graph;
- general predictor;
- asymptotic law;
- coverage, recall, or holdout validation for B8;
- automatic extension beyond the recorded complete transition scopes.
