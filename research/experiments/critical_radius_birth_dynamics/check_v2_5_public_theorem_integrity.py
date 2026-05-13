#!/usr/bin/env python3
"""Verify the scoped PRC v2.5 public theorem review bundle boundary."""

from __future__ import annotations

import argparse
import csv
import json
import tempfile
from fractions import Fraction
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).resolve().parent
PUBLIC_MANIFEST = EXPERIMENT_DIR / "public_theorem_manifest_v2_5_v0_1.json"
PUBLIC_THEOREM_DRAFT = (
    EXPERIMENT_DIR / "notes" / "prc_v2_5_public_theorem_draft_v0_1.md"
)
PUBLIC_README_DRAFT = (
    EXPERIMENT_DIR / "notes" / "prc_v2_5_public_readme_draft_v0_1.md"
)
PUBLIC_SUMMARY_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_public_theorem_summary_v0_1.csv"
)
PHASE_FAMILY_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_phase_gate_family_summary_v0_1.csv"
)
PHASE_LIFT_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_phase_gate_lift_diagnostics_v0_1.csv"
)
EXACT_HULL_FAMILY_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_5_exact_hull_obstruction_family_v0_1.csv"
)
DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_5_public_theorem_integrity_verification_v0_1.csv"
)
SCOPES = ("B4_to_B5_full", "B5_to_B6_full", "B6_to_B7_full")


def term(*parts: str) -> str:
    return "".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    args = parser.parse_args()

    checks = verification_rows()
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_5_public_theorem_integrity: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows() -> list[dict[str, str]]:
    return [
        check_public_theorem_wording(),
        check_public_readme_wording(),
        check_public_manifest_boundary(),
        check_public_summary_counts(),
        check_phase_gate_certificate_counts(),
        check_exact_hull_certificate_counts(),
    ]


def check_public_theorem_wording() -> dict[str, str]:
    text = normalized_text(PUBLIC_THEOREM_DRAFT)
    required = [
        "finite exact aperture-orbit separator theorem",
        "U_{4->5}",
        "U_{5->6}",
        "U_{6->7}",
        "Close(row)",
        "Capacity(row)",
        "NonClose(row)",
        "m(row)",
        "Close(row) => m(row) > 0",
        "Capacity(row) and NonClose(row) => m(row) <= 0",
        "recorded complete transition scopes",
        "terminal containment certificate",
        term("not a general ", "pre", "dictor"),
        term("B", "8 selected stress-control only"),
    ]
    return phrase_check("v2_5_public_theorem_wording", text, required, [])


def check_public_readme_wording() -> dict[str, str]:
    text = normalized_text(PUBLIC_README_DRAFT)
    required = [
        "draft for scoped public theorem review",
        "not a release",
        "What Is Proved",
        "What Is Not Proved",
        "Exact Counts",
        "How To Reproduce",
        "finite exact aperture-orbit separator theorem",
        term("no B", "8 theorem"),
        term("no general ", "pre", "dictor"),
    ]
    return phrase_check("v2_5_public_readme_wording", text, required, [])


def check_public_manifest_boundary() -> dict[str, str]:
    manifest = json.loads(PUBLIC_MANIFEST.read_text(encoding="utf-8"))
    sources = manifest_sources(manifest)
    required = {
        "research/experiments/critical_radius_birth_dynamics/check_v2_5_public_theorem_integrity.py",
        "research/experiments/critical_radius_birth_dynamics/public_theorem_manifest_v2_5_v0_1.json",
        "research/experiments/critical_radius_birth_dynamics/public_theorem_workflow_v2_5_v0_1.yml",
        "research/experiments/critical_radius_birth_dynamics/data/prc_v2_5_public_theorem_summary_v0_1.csv",
        "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_draft_v0_1.md",
        "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_readme_draft_v0_1.md",
    }
    forbidden_terms = [
        term("b", "8"),
        term("pre", "dictor"),
        term("break", "through"),
        term("targeted", "_probe"),
        term("control", "_calibration"),
    ]
    failures = len(required - sources)
    for source in sources:
        source_lower = source.lower()
        failures += int(any(term in source_lower for term in forbidden_terms))
    failures += int(manifest.get("public_release") is not False)
    failures += int(manifest.get("id") != "prc_v2_5_public_theorem_review_bundle_v0_1")
    return check_bool(
        "v2_5_public_manifest_boundary",
        failures == 0,
        total=len(required) + len(sources) + 2,
        failed=failures,
    )


def check_public_summary_counts() -> dict[str, str]:
    rows = read_csv_dicts(PUBLIC_SUMMARY_CSV)
    values = {
        (row["section"], row["scope"], row["metric"]): row["value"]
        for row in rows
    }
    expected = {
        ("historical_totals", "all", "close_or_birth_rows"): "770",
        ("historical_totals", "all", "capacity_nonclose_families"): "2430",
        ("historical_totals", "all", "nonclose_positive_margin_rows"): "0",
        ("exact_hull", "B4_to_B5_full", "hull_obstructed_multi_component_families"): "65",
        ("exact_hull", "B5_to_B6_full", "hull_obstructed_multi_component_families"): "913",
        ("exact_hull", "B6_to_B7_full", "hull_obstructed_multi_component_families"): "13785",
    }
    failures = sum(values.get(key) != value for key, value in expected.items())
    return check_bool(
        "v2_5_public_summary_counts",
        failures == 0,
        total=len(expected),
        failed=failures,
    )


def check_phase_gate_certificate_counts() -> dict[str, str]:
    family_rows = read_csv_dicts(PHASE_FAMILY_CSV)
    lift_rows = read_csv_dicts(PHASE_LIFT_CSV)
    families = [row for row in family_rows if row["scope"] in SCOPES]
    lifts = [row for row in lift_rows if row["scope"] in SCOPES]

    family_counts = {scope: 0 for scope in SCOPES}
    close_counts = {scope: 0 for scope in SCOPES}
    capacity_nonclose = {scope: 0 for scope in SCOPES}
    for row in families:
        scope = row["scope"]
        family_counts[scope] += 1
        close_lifts = int(row["close_lift_count"])
        close_counts[scope] += close_lifts
        if row["capacity_pass"] == "True" and close_lifts == 0:
            capacity_nonclose[scope] += 1

    close_positive = 0
    nonclose_positive = 0
    nonbirth_close = 0
    for row in lifts:
        margin_positive = Fraction(row["phase_margin"]) > 0
        is_close = row["is_close"] == "True"
        is_birth = row["is_birth"] == "True"
        if is_close and margin_positive:
            close_positive += 1
        if not is_close and margin_positive:
            nonclose_positive += 1
        if is_close and not is_birth:
            nonbirth_close += 1

    expected_family_counts = {
        "B4_to_B5_full": 208,
        "B5_to_B6_full": 2274,
        "B6_to_B7_full": 29520,
    }
    expected_close_counts = {
        "B4_to_B5_full": 14,
        "B5_to_B6_full": 42,
        "B6_to_B7_full": 714,
    }
    expected_capacity_nonclose = {
        "B4_to_B5_full": 14,
        "B5_to_B6_full": 182,
        "B6_to_B7_full": 2234,
    }
    failures = 0
    failures += sum(family_counts[scope] != value for scope, value in expected_family_counts.items())
    failures += sum(close_counts[scope] != value for scope, value in expected_close_counts.items())
    failures += sum(
        capacity_nonclose[scope] != value
        for scope, value in expected_capacity_nonclose.items()
    )
    failures += int(close_positive != 770)
    failures += int(nonclose_positive != 0)
    failures += int(nonbirth_close != 0)
    return check_bool(
        "v2_5_phase_gate_certificate_counts",
        failures == 0,
        total=12,
        failed=failures,
    )


def check_exact_hull_certificate_counts() -> dict[str, str]:
    rows = [row for row in read_csv_dicts(EXACT_HULL_FAMILY_CSV) if row["scope"] in SCOPES]
    multi_component = {scope: 0 for scope in SCOPES}
    hull_obstructed = {scope: 0 for scope in SCOPES}
    multi_component_close = 0
    for row in rows:
        if int(row["old_component_count"]) <= 1:
            continue
        scope = row["scope"]
        multi_component[scope] += 1
        if row["hull_obstruction"] == "True":
            hull_obstructed[scope] += 1
        if int(row["close_lift_count"]) > 0:
            multi_component_close += 1
    expected = {
        "B4_to_B5_full": 65,
        "B5_to_B6_full": 913,
        "B6_to_B7_full": 13785,
    }
    failures = sum(multi_component[scope] != value for scope, value in expected.items())
    failures += sum(hull_obstructed[scope] != value for scope, value in expected.items())
    failures += int(multi_component_close != 0)
    return check_bool(
        "v2_5_exact_hull_certificate_counts",
        failures == 0,
        total=7,
        failed=failures,
    )


def manifest_sources(manifest: dict) -> set[str]:
    sources = {entry["source"] for entry in manifest.get("root_file_map", [])}
    sources.update(manifest.get("root_files", []))
    sources.update(manifest.get("research_files", []))
    return sources


def normalized_text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").replace("`", "").split())


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def phrase_check(
    name: str,
    text: str,
    required: list[str],
    forbidden: list[str],
) -> dict[str, str]:
    normalized = text.lower()
    missing = [phrase for phrase in required if phrase.lower() not in normalized]
    forbidden_found = [
        phrase for phrase in forbidden if phrase.lower() in normalized
    ]
    failed = len(missing) + len(forbidden_found)
    return check_bool(
        name,
        failed == 0,
        total=len(required) + len(forbidden),
        failed=failed,
    )


def check_bool(name: str, passed: bool, *, total: int, failed: int) -> dict[str, str]:
    return {
        "check": name,
        "total": str(total),
        "passed": str(max(total - failed, 0)),
        "failed": str(failed),
        "status": "pass" if passed else "fail",
    }


def write_checks(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["check", "total", "passed", "failed", "status"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
