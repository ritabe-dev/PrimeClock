# Public Release Checklist

Use this checklist for the PRC public release line.
GitHub main is the public working surface. GitHub Release and Zenodo are only
for important fixed versions.

## Preflight

```bash
python3 scripts/check_release_versions.py
python3 scripts/update_public_hashes.py --check
python3 scripts/verify_public_release.py --out "${TMPDIR:-/tmp}/primeclock-public-release-test" --zip
cd research && .venv/bin/python -m pytest tests/test_covering_prime_prefix_filtration.py -q
cd research && .venv/bin/python -m pytest tests/test_critical_radius_birth_dynamics_public.py -q
```

## GitHub-only Improvement Loop

Use this for ordinary cleanup, CI, README, verifier, or review-driven changes.
It updates public `main` only and does not create a tag, GitHub Release, or
Zenodo archive.

If the change concerns an older release while a newer research line is active,
classify it with `release/public/MAINTENANCE_POLICY.md` first. Lightweight
historical clarifications go to `ERRATA.md`; reproducibility, metadata, or
finite-claim corrections require an isolated maintenance patch branch.

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

## Registry-First DOI Release Loop

Use this only for important fixed versions that should be archived by Zenodo.
Public releases are tracked in `release/public/release_registry.json`. Add or
update the registry entry before creating a GitHub Release or finalizing a DOI.
The registry is the multi-version source of truth for tag, GitHub Release URL,
version DOI, citation policy, and release asset metadata. This prevents a later
release such as v2.5 or v2.6 from accidentally rewriting v2.3-only metadata.

For a new public release line:

1. Add a registry entry.
2. Register release README, release notes, citation, manifest, workflow, and
   asset name in the registry.
3. Run `python3 scripts/check_release_doi_integrity.py --all`.
4. Build and verify the release archive from the registered manifest/workflow.
5. Create the GitHub Release and attach the registered release asset.
6. Wait for Zenodo to mint the version DOI.
7. Run `scripts/finalize_version_doi.py --release-id ... --version-doi ...`.
8. Rebuild the archive and refresh the GitHub Release body/asset.
9. Check Zenodo UI/API metadata for title, version, DOI, description, and files.

Check all registered release metadata before and after DOI work:

```bash
python3 scripts/check_release_doi_integrity.py --all
```

Use the release-id based finalizer for registry-managed releases:

```bash
python3 scripts/finalize_version_doi.py \
  --release-id <registered-release-id> \
  --version-doi 10.5281/zenodo.<version-record>
python3 scripts/finalize_version_doi.py \
  --release-id <registered-release-id> \
  --version-doi 10.5281/zenodo.<version-record> \
  --execute
```

The legacy v2.3 public bundle path still supports `release/public/release_config.json`
and `scripts/finalize_release_doi.py`, but future release lines should use the
registry and `scripts/finalize_version_doi.py`.

For the legacy v2.3 public line only, the config must say:

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

Do not force-update public tags. The tag archive may contain the concept DOI;
the main branch, release body, and release asset carry the final version DOI.
For new release lines, do not run DOI finalization until the release has a
registry entry.  Zenodo record metadata itself is still checked separately in
Zenodo UI/API after the repo-side metadata is consistent.
