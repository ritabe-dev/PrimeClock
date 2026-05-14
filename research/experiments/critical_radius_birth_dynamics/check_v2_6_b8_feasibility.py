#!/usr/bin/env python3
"""Audit v2.6 Gate R starter boundaries before any B8 full graph work."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


EXPERIMENT_REL = Path("research/experiments/critical_radius_birth_dynamics")
SUMMARY_REL = EXPERIMENT_REL / "data/prc_v2_6_b8_feasibility_summary_v0_1.csv"
DECISION_REL = EXPERIMENT_REL / "data/prc_v2_6_gate_r_decision_table_v0_1.csv"
SEED_NOTE_REL = EXPERIMENT_REL / "notes/prc_v2_6_research_seed_note_v0_1.md"
WORKFLOW_REL = EXPERIMENT_REL / "candidate_workflow_v2_6_v0_1.yml"
V2_5_PUBLIC_MANIFEST_REL = (
    EXPERIMENT_REL / "public_theorem_release_manifest_v2_5_v1_0.json"
)

PUBLIC_PATH_FORBIDDEN_MARKERS = (
    "b8",
    "targeted_probe",
    "control_calibration",
    "stress_control",
    "predictor",
    "breakthrough",
)
B8_SOURCE_PATTERNS = (
    "*b8*",
    "*B8*",
)
POSITIVE_B8_CLAIM_PHRASES = (
    "B8 coverage",
    "B8 recall",
    "B8 holdout",
    "public B8 claim",
    "validated on B8",
)
REQUIRED_NON_CLAIMS = (
    "no public claim",
    "no DOI",
    "no B8 theorem",
    "no B8 full graph",
    "no general predictor",
    "no asymptotic law",
)
REQUIRED_DECISION_ROUTES = (
    "B8 finite extension",
    "prefix-only predictor",
    "obstruction theorem",
    "negative diagnostic",
)
ESTIMATE_KEYS = (
    "b8_family_count_estimate",
    "b8_lift_row_estimate",
    "b8_runtime_estimate",
    "b8_disk_size_estimate",
)


def repo_root_from_script() -> Path:
    path = Path(__file__).resolve()
    for parent in path.parents:
        if (parent / "release/public/release_registry.json").is_file():
            return parent
    raise RuntimeError("could not locate PrimeClock repository root")


def read_text(repo_root: Path, relative_path: Path) -> str:
    path = repo_root / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"missing required v2.6 Gate R file: {relative_path}")
    return path.read_text(encoding="utf-8")


def load_json(repo_root: Path, relative_path: Path) -> dict[str, Any]:
    return json.loads(read_text(repo_root, relative_path))


def manifest_source_paths(manifest: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for entry in manifest.get("root_file_map", []):
        paths.append(entry["source"])
    for key in ("root_files", "research_files", "research_dirs"):
        paths.extend(manifest.get(key, []))
    return paths


def count_forbidden_public_manifest_hits(paths: list[str]) -> tuple[int, list[str]]:
    hits: list[str] = []
    for path in paths:
        lowered = path.lower()
        if any(marker in lowered for marker in PUBLIC_PATH_FORBIDDEN_MARKERS):
            hits.append(path)
    return len(hits), hits


def find_b8_source_artifacts(repo_root: Path) -> list[str]:
    experiment_root = repo_root / EXPERIMENT_REL
    found: set[str] = set()
    for pattern in B8_SOURCE_PATTERNS:
        for path in experiment_root.rglob(pattern):
            if path.is_file():
                relative = path.relative_to(repo_root).as_posix()
                if "v2_6" not in relative:
                    found.add(relative)
    return sorted(found)


def count_positive_b8_claims(texts: dict[str, str]) -> tuple[int, list[str]]:
    hits: list[str] = []
    for relative_path, text in texts.items():
        for phrase in POSITIVE_B8_CLAIM_PHRASES:
            if phrase in text:
                hits.append(f"{relative_path}: {phrase}")
    return len(hits), hits


def read_summary_rows(repo_root: Path) -> list[dict[str, str]]:
    path = repo_root / SUMMARY_REL
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_summary(repo_root: Path, rows: list[dict[str, str]], out_path: Path) -> Path:
    path = out_path if out_path.is_absolute() else repo_root / out_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["key", "value", "status", "notes"])
        writer.writeheader()
        writer.writerows(rows)
    return path


def require_summary_estimate_rows(rows: list[dict[str, str]], failures: list[str]) -> None:
    by_key = {row["key"]: row for row in rows}
    for key in ESTIMATE_KEYS:
        row = by_key.get(key)
        if not row:
            failures.append(f"missing feasibility estimate row: {key}")
            continue
        if not row.get("value") or not row.get("status") or not row.get("notes"):
            failures.append(f"incomplete feasibility estimate row: {key}")


def require_seed_note(text: str, failures: list[str]) -> None:
    for section in (
        "## Goal",
        "## Non-claims",
        "## Candidate Routes",
        "## B8 Feasibility Questions",
        "## Stop Conditions",
        "## Gate R Decision Table",
    ):
        if section not in text:
            failures.append(f"seed note missing section {section}")
    lowered = text.lower()
    for phrase in REQUIRED_NON_CLAIMS:
        if phrase.lower() not in lowered:
            failures.append(f"seed note missing non-claim phrase {phrase!r}")


def require_decision_table(repo_root: Path, failures: list[str]) -> None:
    path = repo_root / DECISION_REL
    if not path.is_file():
        failures.append(f"missing decision table: {DECISION_REL}")
        return
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    routes = {row.get("route", "") for row in rows}
    for route in REQUIRED_DECISION_ROUTES:
        if route not in routes:
            failures.append(f"decision table missing route {route!r}")


def build_summary_rows(repo_root: Path) -> tuple[list[dict[str, str]], list[str]]:
    manifest = load_json(repo_root, V2_5_PUBLIC_MANIFEST_REL)
    manifest_paths = manifest_source_paths(manifest)
    public_hits, public_hit_paths = count_forbidden_public_manifest_hits(manifest_paths)
    b8_artifacts = find_b8_source_artifacts(repo_root)
    seed_text = read_text(repo_root, SEED_NOTE_REL)
    workflow_text = read_text(repo_root, WORKFLOW_REL)
    positive_claim_count, positive_claim_hits = count_positive_b8_claims(
        {
            SEED_NOTE_REL.as_posix(): seed_text,
            WORKFLOW_REL.as_posix(): workflow_text,
        }
    )

    rows = [
        {
            "key": "v2_5_public_manifest_b8_path_hits",
            "value": str(sum(1 for path in manifest_paths if "b8" in path.lower())),
            "status": "pass",
            "notes": "public theorem release manifest paths contain no B8 material artifacts",
        },
        {
            "key": "v2_5_public_manifest_forbidden_artifact_hits",
            "value": str(public_hits),
            "status": "pass" if public_hits == 0 else "fail",
            "notes": "; ".join(public_hit_paths) if public_hit_paths else (
                "public theorem release manifest excludes B8 stress-control probe and predictor artifacts"
            ),
        },
        {
            "key": "existing_b8_source_artifact_count",
            "value": str(len(b8_artifacts)),
            "status": "info",
            "notes": "; ".join(b8_artifacts) if b8_artifacts else (
                "no B8 source-only stress-control artifacts are present on the default public branch"
            ),
        },
        {
            "key": "b8_family_count_estimate",
            "value": "pending",
            "status": "blocked_before_full_graph",
            "notes": "required before B8 finite extension can continue",
        },
        {
            "key": "b8_lift_row_estimate",
            "value": "pending",
            "status": "blocked_before_full_graph",
            "notes": "required before B8 finite extension can continue",
        },
        {
            "key": "b8_runtime_estimate",
            "value": "pending",
            "status": "blocked_before_full_graph",
            "notes": "required before B8 finite extension can continue",
        },
        {
            "key": "b8_disk_size_estimate",
            "value": "pending",
            "status": "blocked_before_full_graph",
            "notes": "required before B8 finite extension can continue",
        },
        {
            "key": "forbidden_positive_b8_claims",
            "value": str(positive_claim_count),
            "status": "pass" if positive_claim_count == 0 else "fail",
            "notes": "; ".join(positive_claim_hits) if positive_claim_hits else (
                "v2.6 seed and workflow do not call B8 coverage recall holdout theorem or public claim"
            ),
        },
    ]
    failures: list[str] = []
    if public_hits:
        failures.append("v2.5 public theorem manifest contains forbidden B8-related artifact paths")
    if positive_claim_count:
        failures.append("v2.6 seed/workflow contains forbidden positive B8 claim wording")
    return rows, failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Optional output CSV path")
    parser.add_argument(
        "--update",
        action="store_true",
        help="Regenerate the committed summary CSV, or --out if provided",
    )
    parser.add_argument("--boundary-only", action="store_true", help="Run only boundary checks")
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    failures: list[str] = []
    seed_text = read_text(repo_root, SEED_NOTE_REL)
    require_seed_note(seed_text, failures)
    require_decision_table(repo_root, failures)

    rows, row_failures = build_summary_rows(repo_root)
    failures.extend(row_failures)
    require_summary_estimate_rows(rows, failures)
    if not args.boundary_only and not args.update:
        committed_rows = read_summary_rows(repo_root)
        if not committed_rows:
            failures.append(f"missing committed summary for read-only audit: {SUMMARY_REL}")
        elif committed_rows != rows:
            failures.append(f"committed summary differs from regenerated summary: {SUMMARY_REL}")
    output_path = repo_root / SUMMARY_REL
    if args.update or args.out:
        output_path = write_summary(repo_root, rows, args.out or SUMMARY_REL)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    check_count = 6 if args.boundary_only else 8
    mode = "updated" if args.update or args.out else "read_only"
    print(
        f"check_v2_6_b8_feasibility: checks={check_count}, failed=0, "
        f"mode={mode}, artifact={output_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
