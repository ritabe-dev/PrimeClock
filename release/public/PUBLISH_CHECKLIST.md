# Public Release Checklist

Use this checklist for the finite `C_k/C_4/B_5` public release line.
GitHub main is the public working surface. GitHub Release and Zenodo are only
for important fixed versions.

## Preflight

```bash
python3 scripts/check_release_versions.py
python3 scripts/update_public_hashes.py --check
python3 scripts/verify_public_release.py --out /private/tmp/primeclock-public-release-test --zip
cd research && .venv/bin/python -m pytest tests/test_covering_prime_prefix_filtration.py -q
```

## GitHub-only Improvement Loop

Use this for ordinary cleanup, CI, README, verifier, or review-driven changes.
It updates public `main` only and does not create a tag, GitHub Release, or
Zenodo archive.

```bash
python3 scripts/publish_public_release.py
python3 scripts/publish_public_release.py --execute
```

The config must say:

```json
"release_kind": "maintenance_sync",
"zenodo_expected": false,
"allow_github_release": false
```

For external review snapshots, send a commit or tree URL, not a
GitHub Release URL.

## DOI Release Loop

Use this only for important fixed versions that should be archived by Zenodo.
The config must say:

```json
"release_kind": "doi_release",
"zenodo_expected": true,
"allow_github_release": true
```

Dry-run first:

```bash
python3 scripts/publish_public_release.py
```

Publish only after the dry-run output is correct:

```bash
python3 scripts/publish_public_release.py --execute
```

This script fetches the public repository, reapplies the generated bundle on top
of `origin/main`, verifies the public worktree, pushes `main`, creates the tag,
and creates the GitHub Release with the generated zip asset only for
`doi_release`.

## Stage B: Zenodo DOI Metadata

After Zenodo publishes the GitHub release archive, finalize the version DOI:

```bash
python3 scripts/finalize_release_doi.py
python3 scripts/finalize_release_doi.py --execute
```

Then update source metadata, rebuild the public bundle, push the public
worktree metadata commit, and refresh the GitHub release body/asset:

```bash
python3 scripts/finalize_release_doi.py --execute
```

Do not force-update public tags. The tag archive may contain the concept DOI;
the main branch, release body, and release asset carry the final version DOI.
