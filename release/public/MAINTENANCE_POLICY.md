# PrimeClock Release-Line Maintenance Policy

Purpose: keep active research work, historical release corrections, and
GitHub/Zenodo publication decisions separate.

Published GitHub tags and Zenodo archives are treated as immutable snapshots.
Do not rewrite a historical tag or replace an old archive to correct a past
release. Record the correction as errata, or create a new patch release when
the correction changes the public artifact in a way that should be cited.

## Decision Classes

| Class | Use when | DOI action |
| --- | --- | --- |
| `errata` | A past release needs a known-issue note or interpretation warning. | No new DOI. Record in `ERRATA.md`. |
| `docs clarification` | Main branch docs can explain an old release more clearly without changing the old artifact. | No new DOI. Record in `ERRATA.md` when it concerns a published release. |
| `maintenance patch release` | A past release has reproducibility, metadata, or finite-claim-impacting corrections. | New version DOI only if published through GitHub Release / Zenodo. |
| `superseding research release` | A later line such as `v2.4.x` gives a better or broader research result. | Cite the later version DOI; do not rewrite the old tag. |

## Branching Rule

When a patch release is needed while later research is in progress, branch from
the affected tag, not from the active research branch:

```text
maintenance/v2.3.1  starts from v2.3.0
maintenance/v2.2.5  starts from v2.2.4
```

The patch branch must contain only the correction for that release line. Do not
mix `v2.4` data, notes, or claims into a `v2.2.x` or `v2.3.x` patch. After the
patch is complete, forward-port only the relevant correction to `main` or the
active research line.

## Release Config Rule

`release/public/release_config.json` is switched to a patch version only while
preparing that patch release. Routine notes, cleanup, and review-driven changes
stay on `main` and use `maintenance_sync`.

Use `doi_release` only when the patch is important enough to become a citable
GitHub Release / Zenodo archive. Otherwise keep the correction as `ERRATA.md`
or a docs clarification on `main`.

## v2.4 Interaction Rule

While working on `v2.4.x`, classify any `v2.2` or `v2.3` concern before editing:

```text
typo or explanation       -> docs clarification
known issue or warning    -> errata
broken verification path  -> maintenance patch release
finite claim correction   -> errata plus maintenance patch release
better new explanation    -> superseding research release
```

The `v2.4.x` release notes should say whether relevant `v2.3.0` claims are
retained, corrected, or superseded. They should not silently modify the meaning
of an older version DOI.
