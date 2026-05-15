#!/usr/bin/env python3
"""Render registry-derived root public release surface files."""

from __future__ import annotations

import argparse
import difflib
from pathlib import Path
from typing import Any

from release_registry import REGISTRY_PATH, load_release_registry, release_entries


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def public_releases(registry: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        entry
        for entry in release_entries(registry)
        if entry["release_kind"] == "doi_release"
    ]


def current_public_release(registry: dict[str, Any]) -> dict[str, Any]:
    releases = public_releases(registry)
    if not releases:
        raise ValueError("release registry has no public releases")
    return releases[-1]


def latest_doi_backed_release(registry: dict[str, Any]) -> dict[str, Any]:
    releases = [
        entry
        for entry in public_releases(registry)
        if entry["doi_state"] == "assigned"
    ]
    if not releases:
        raise ValueError("release registry has no assigned DOI-backed releases")
    return releases[-1]


def entry_doi_text(entry: dict[str, Any]) -> str:
    if entry["doi_state"] == "assigned":
        return entry["zenodo_version_doi"]
    return "pending Zenodo publication"


def doi_backed_readme_note(current: dict[str, Any], doi_backed: dict[str, Any]) -> str:
    if current["release_id"] == doi_backed["release_id"]:
        return "This is the same release as the current public theorem release."
    return (
        "This remains the theorem citation to use when a Zenodo version DOI is required\n"
        "and the current public theorem release is still DOI pending."
    )


def citation_note(current: dict[str, Any], doi_backed: dict[str, Any]) -> str:
    if current["release_id"] == doi_backed["release_id"]:
        return (
            "Use the current release-specific `CITATION.cff` for DOI-backed references."
        )
    return (
        "Use the current release-specific `CITATION.cff` after Zenodo assigns the current\n"
        "version DOI. Until then, the latest DOI-backed theorem release-specific\n"
        "`CITATION.cff` remains the theorem citation for DOI-backed references."
    )


def version_map_citation_note(current: dict[str, Any], doi_backed: dict[str, Any]) -> str:
    if current["release_id"] == doi_backed["release_id"]:
        return (
            "The current theorem release has an assigned Zenodo version DOI and uses\n"
            "release-specific citation metadata. The latest DOI-backed theorem release\n"
            f"is the same release: `{doi_backed['release_id']}` with version DOI\n"
            f"`{doi_backed['zenodo_version_doi']}`."
        )
    return (
        "The current theorem release uses release-specific citation metadata and is\n"
        "waiting for a Zenodo version DOI. Until that DOI exists, the latest DOI-backed\n"
        "theorem release uses release-specific citation metadata and version DOI\n"
        f"`{doi_backed['zenodo_version_doi']}`."
    )


def release_line_rows(current: dict[str, Any], doi_backed: dict[str, Any]) -> str:
    if current["release_id"] == doi_backed["release_id"]:
        return (
            f"| `{current['release_id']}` | current and latest DOI-backed public theorem release | "
            "General q-prime single-gap aperture classification theorem for the PRC circular-arc model. |"
        )
    return (
        f"| `{doi_backed['release_id']}` | latest DOI-backed scoped public theorem release | "
        "Finite exact aperture-orbit separator theorem for recorded `B4->B5`, `B5->B6`, and `B6->B7` scopes. |\n"
        f"| `{current['release_id']}` | current public theorem release, DOI pending | "
        "General q-prime single-gap aperture classification theorem for the PRC circular-arc model. |"
    )


def render_readme(registry: dict[str, Any]) -> str:
    current = current_public_release(registry)
    doi_backed = latest_doi_backed_release(registry)
    v23 = next(entry for entry in release_entries(registry) if entry["release_id"] == "v2.3.0")

    return f"""# PrimeClock Public Releases

<!-- BEGIN GENERATED PUBLIC SURFACE -->
This repository publishes finite Prime Reciprocal Covering (PRC) artifacts and
their verification tooling. The current public theorem release is
`{current["release_id"]}`. Its Zenodo DOI state is `{entry_doi_text(current)}`.
The latest DOI-backed public theorem release is `{doi_backed["release_id"]}`.
<!-- END GENERATED PUBLIC SURFACE -->

## Current Public Theorem Release

```text
{current["release_id"]}
{current["title"]}
Version DOI: {entry_doi_text(current)}
GitHub Release: {current["github_release_url"]}
Release asset: {current["asset_name"]}
```

The current theorem is a structural theorem inside the PRC circular-arc model.
For every `k >= 3`, every old residue `r in Z/M_kZ`, and every later odd prime
modulus `q>p_k`, a nonempty q-birth lift is exactly a single residual gap plus
q-grid aperture alignment.

The result is a direct one-prime q-lift theorem over the old prefix. For
`q != p_{{k+1}}`, it does not claim that intermediate sequential PRC transitions
are skipped or unchanged. The exact audit is a recorded birth rows consistency
audit, not a full finite-universe completeness audit and not the proof of the
general q-prime theorem; the theorem proof is the geometric argument in the
theorem note.

Read these current release files first:

1. `{current["readme_paths"][0]}`
2. `{current["release_notes_paths"][0]}`
3. `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_7_general_single_gap_aperture_theorem_note_v0_1.md`
4. `{current["citation_paths"][0]}`

The current release does not claim a B8 theorem, a full transition-graph
theorem, a general predictor, an asymptotic law, a prime-gap theorem outside
the PRC model, or a full finite-universe completeness audit.

## Latest DOI-Backed Public Theorem Release

```text
{doi_backed["release_id"]}
{doi_backed["title"]}
Version DOI: {doi_backed["zenodo_version_doi"]}
GitHub Release: {doi_backed["github_release_url"]}
Release asset: {doi_backed["asset_name"]}
```

{doi_backed_readme_note(current, doi_backed)}

## Foundational Public Release

The older `v2.3.0` release remains an immutable foundational DOI release for the
finite `C_k/C_4/B_5` certificate artifact plus the v2.3 critical-radius and
gap-aperture birth-dynamics finite artifact.

```text
{v23["release_id"]}
Version DOI: {v23["zenodo_version_doi"]}
Concept DOI: {v23["zenodo_concept_doi"]}
GitHub Release: {v23["github_release_url"]}
```

The v2.3 finite claims are:

- `C_4={{2,208}} mod 210`;
- `C_5` has `36` covered residues;
- `Lift_5(C_4)` has `22` inherited residues;
- `B_5` has `14` births in `7` reflection pairs;
- every `B_5` birth is a strict single-gap closure by the new `p=11` arc;
- `C_k` is the `1/2` level set of the exact critical-radius spectrum for the
  checked `k=4,5` layers;
- `B_5`, `B_6`, and `B_7` are unique strict single-gap births in the checked
  finite data.

The v2.3 public bundle README template remains at
`release/public/README.template.md`; it is intentionally v2.3-specific.

## Research Position

Prime Reciprocal Covering is a project-defined finite prime-prefix
circle-covering model. For each residue class and each prime in a prefix, it
places a rational closed arc on `R/Z` centered at `(r mod p)/p`; the public
claims are about exactly stated PRC model artifacts.

The vocabulary is adjacent to classical covering systems of congruences because
it uses residues, moduli, and covering language, but this repository does not
claim a result about classical covering systems. The related-work boundary note
`research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_related_work_v0_2.md`
records nearby terminology and literature context.

Zenodo DOIs identify citable archived snapshots of this finite artifact. They
do not imply peer review.

## Verify

From the repository root, verify release metadata and public release guardrails:

```bash
python3 scripts/render_public_surface.py --check
python3 scripts/check_release_doi_integrity.py --all
python3 scripts/verify_public_release_execution_preflight.py --all
```

Expected focused result:

```text
failed=0
```

For the current theorem release bundle, use:

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_7_public_theorem_release.py
python3 scripts/verify_candidate_workflow.py \\
  --config research/experiments/critical_radius_birth_dynamics/public_theorem_release_bundle_workflow_v2_7_v1_0.yml \\
  public-theorem-review
```

For the v2.3 foundational verifier path, use `research/`:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
python -m pytest tests/test_covering_prime_prefix_filtration.py -q
python -m prime_reciprocal_projection.cli covering-prime-prefix-verify-certificates \\
  --out data/summaries/prc_prime_prefix_certificate_verification_v1_7.csv
python certificates/check_prime_prefix_c4_b5.py \\
  --out data/summaries/prc_prime_prefix_certificate_standalone_verification_v1_8.csv
```

Expected focused results:

```text
focused pytest: 55 passed
package verifier: checks=14, failed=0
standalone checker: checks=9, failed=0
```

## Public Release Bundles

Public releases are built from explicit allowlists. The source repository can
contain broader research history, but each public release bundle contains only
the files listed by its release manifest or registry entry.

Build and inspect the current theorem release bundle with:

```bash
research/.venv/bin/python scripts/verify_candidate_workflow.py \\
  --config {current["workflow_path"]} \\
  public-theorem-review
```

Build and inspect the v2.3 public bundle with:

```bash
python3 scripts/check_release_versions.py
python3 scripts/verify_public_release.py --out "${{TMPDIR:-/tmp}}/primeclock-public-release" --zip
```

## Citation and License

{citation_note(current, doi_backed)}

The top-level `CITATION.cff` remains the v2.3.0 citation metadata. Its
top-level DOI is the Zenodo concept DOI for the v2.3 release series:
`{v23["zenodo_concept_doi"]}`; the v2.3.0 version DOI is
`{v23["zenodo_version_doi"]}`.

The project is released under the MIT License; see `LICENSE`.
"""


def render_version_map(registry: dict[str, Any]) -> str:
    current = current_public_release(registry)
    doi_backed = latest_doi_backed_release(registry)
    v23 = next(entry for entry in release_entries(registry) if entry["release_id"] == "v2.3.0")

    return f"""# Version Map

This repository keeps release, package, note, table, verifier, and DOI metadata
versions separate. Multi-version release metadata is tracked in
`release/public/release_registry.json`.

<!-- BEGIN GENERATED PUBLIC SURFACE -->
## Current Public Releases

| Item | Version / file |
| --- | --- |
| Current public theorem release | `{current["release_id"]}` |
| Current theorem release title | `{current["title"]}` |
| Current theorem release asset | `{current["asset_name"]}` |
| Current theorem DOI state | `{entry_doi_text(current)}` |
| Current theorem GitHub Release | `{current["github_release_url"]}` |
| Current theorem README | `{current["readme_paths"][0]}` |
| Current theorem release notes | `{current["release_notes_paths"][0]}` |
| Current theorem citation | `{current["citation_paths"][0]}` |
| Latest DOI-backed theorem release | `{doi_backed["release_id"]}` |
| Latest DOI-backed theorem title | `{doi_backed["title"]}` |
| Latest DOI-backed theorem asset | `{doi_backed["asset_name"]}` |
| Latest DOI-backed theorem Version DOI | `{doi_backed["zenodo_version_doi"]}` |
| Latest DOI-backed theorem GitHub Release | `{doi_backed["github_release_url"]}` |
| Release registry | `release/public/release_registry.json` |
| Python package | `prime-reciprocal-projection` `0.1.0` |
<!-- END GENERATED PUBLIC SURFACE -->

## Foundational v2.3 Release

| Item | Version / file |
| --- | --- |
| Public release | `{v23["tag"]}` |
| Foundational public release | `{v23["release_id"]}` |
| Public release config | `release/public/release_config.json` |
| Public bundle name | `PrimeClock-2.3.0` |
| Version DOI | `{v23["zenodo_version_doi"]}` |
| Concept DOI | `{v23["zenodo_concept_doi"]}` |
| Finite theorem note | `research/notes/prc_finite_certificate_note_v2_0.md` |
| v2.3 theorem note | `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_theorem_note_draft_v0_1.md` |
| Related work note | `research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_related_work_v0_2.md` |
| C4 witness table | `prc_prime_prefix_c4_exclusion_witness_v1_6.csv` |
| C5 full table | `prc_prime_prefix_ck_full_v1_1.csv` |
| B5 classification table | `prc_prime_prefix_b5_birth_classification_v1_5.csv` |
| Critical-radius table | `prc_prime_prefix_critical_radius_k4_k5_v0_1.csv` |
| Birth-dynamics table | `prc_prime_prefix_birth_dynamics_k5_k7_v0_1.csv` |
| v2.3 helper verifier output | `prc_v2_3_candidate_verification_v0_1.csv` |
| v2.3 standalone audit output | `prc_v2_3_candidate_standalone_verification_v0_1.csv` |

## Release Lines

| Line | Status | Maintenance handling |
| --- | --- | --- |
| `v2.2.4` | historical stable finite certificate | Do not retag; use `ERRATA.md` for clarifications or a maintenance patch release. |
| `maintenance/v2.2.5` | reserved historical maintenance patch line | Use only for errata or docs clarification rooted at `v2.2.4`. |
| `v2.3.0` | immutable foundational public DOI release for critical-radius and gap-aperture finite claims | Do not rewrite after publication; use `ERRATA.md` or a maintenance patch release if corrections are needed. |
| `maintenance/v2.3.1` | reserved maintenance patch line | Use only for errata or docs clarification rooted at `v2.3.0`. |
| `v2.4.x` | source-only bridge from v2.3.0 to the v2.5 theorem line | No public release, DOI, or candidate ZIP. Preserve useful diagnostics as internal evidence only. |
{release_line_rows(current, doi_backed)}

Historical release corrections are governed by
`release/public/MAINTENANCE_POLICY.md`. The short rule is: published tags and
Zenodo archives are immutable snapshots, so past releases are corrected through
`ERRATA.md` or a new maintenance patch release, not by rewriting old tags.

## DOI and Release Registry

`release/public/release_registry.json` is the source of truth for public release
metadata across versions: release id, tag, title, GitHub Release URL, DOI state,
Zenodo DOI, asset name, manifest path, release notes, README paths, and citation
policy.

Check registry consistency with:

```bash
python3 scripts/render_public_surface.py --check
python3 scripts/check_release_doi_integrity.py --all
python3 scripts/verify_public_release_execution_preflight.py --all
```

New public release lines must be added to the registry before DOI finalization.
Registry-managed DOI finalization uses:

```bash
python3 scripts/finalize_version_doi.py \\
  --release-id <registered-release-id> \\
  --version-doi 10.5281/zenodo.<version-record>
```

The legacy `scripts/finalize_release_doi.py` path is retained for the v2.3 public
bundle line.

`SHA256SUMS` records the file hashes for the public release allowlist. Update it
with:

```bash
python3 scripts/update_public_hashes.py
```

Check it with:

```bash
python3 scripts/render_public_surface.py --check
python3 scripts/check_release_doi_integrity.py --all
python3 scripts/update_public_hashes.py --check
```

The Python package retains the historical name `prime-reciprocal-projection`.
The package version `0.1.0` is internal tooling metadata for the Python verifier
package; it is intentionally separate from the PrimeClock public release lines.

The top-level `CITATION.cff` uses the v2.3 Zenodo concept DOI as its top-level
DOI. The current theorem release uses release-specific citation metadata and is
{version_map_citation_note(current, doi_backed)}
"""


def write_or_check(repo_root: Path, relative_path: str, expected: str, *, write: bool) -> list[str]:
    path = repo_root / relative_path
    if write:
        path.write_text(expected, encoding="utf-8")
        return []
    actual = path.read_text(encoding="utf-8") if path.is_file() else ""
    if actual == expected:
        return []
    diff = "\n".join(
        difflib.unified_diff(
            actual.splitlines(),
            expected.splitlines(),
            fromfile=relative_path,
            tofile=f"{relative_path} (generated)",
            lineterm="",
        )
    )
    return [f"{relative_path} is not registry-rendered:\n{diff}"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Check generated public surface files")
    mode.add_argument("--write", action="store_true", help="Rewrite generated public surface files")
    parser.add_argument("--repo-root", type=Path, help="Repository root")
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH, help="Release registry path")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve() if args.repo_root else repo_root_from_script()
    registry = load_release_registry(repo_root, args.registry)
    failures: list[str] = []
    failures.extend(write_or_check(repo_root, "README.md", render_readme(registry), write=args.write))
    failures.extend(write_or_check(repo_root, "VERSION_MAP.md", render_version_map(registry), write=args.write))
    if failures:
        print("render_public_surface: failed")
        for failure in failures:
            print(failure)
        return 1
    action = "wrote" if args.write else "checked"
    print(f"render_public_surface: {action}=2, failed=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
