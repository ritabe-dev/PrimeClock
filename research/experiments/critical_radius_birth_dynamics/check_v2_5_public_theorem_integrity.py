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
PUBLIC_REVIEW_MANIFEST = EXPERIMENT_DIR / "public_theorem_manifest_v2_5_v0_1.json"
PUBLIC_RELEASE_MANIFEST = (
    EXPERIMENT_DIR / "public_theorem_release_manifest_v2_5_v1_0.json"
)
PUBLIC_THEOREM_DRAFT = (
    EXPERIMENT_DIR / "notes" / "prc_v2_5_public_theorem_draft_v0_1.md"
)
PUBLIC_REVIEW_README = (
    EXPERIMENT_DIR / "notes" / "prc_v2_5_public_readme_draft_v0_1.md"
)
PUBLIC_RELEASE_README = (
    EXPERIMENT_DIR / "notes" / "prc_v2_5_public_theorem_readme_v1_0.md"
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
    # Split forbidden markers so this checker does not match its own source text.
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
        check_phase_gate_family_counts(),
        check_row_level_separator_counts(),
        check_capacity_false_positive_row_counts(),
        check_margin_gap_counts(),
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
        "Close(row) iff m(row) > 0",
        "Capacity(row) and NonClose(row) => m(row) <= 0",
        "recorded complete transition scopes",
        "terminal containment certificate",
        "committed finite certificate artifacts",
        "does not independently regenerate the full PRC transition universe from first principles",
        term("not a general ", "pre", "dictor"),
        term("B", "8 selected stress-control only"),
    ]
    return phrase_check("v2_5_public_theorem_wording", text, required, [])


def check_public_readme_wording() -> dict[str, str]:
    text = normalized_text(active_public_readme_path())
    if active_public_readme_path() == PUBLIC_RELEASE_README:
        required = [
            "public theorem README text for v2.5.0-prc-public-theorem",
            "What Is Proved",
            "What Is Not Proved",
            "Exact Counts",
            "How To Verify",
            "finite exact aperture-orbit separator theorem",
            "committed finite certificate artifacts",
            "does not independently regenerate the full PRC transition universe from first principles",
            "python3 research/experiments/critical_radius_birth_dynamics/check_v2_5_public_theorem_integrity.py",
            term("no B", "8 theorem"),
            term("no general ", "pre", "dictor"),
        ]
        return phrase_check("v2_5_public_readme_wording", text, required, [])
    required = [
        "draft for scoped public theorem review",
        "not a release",
        "What Is Proved",
        "What Is Not Proved",
        "Exact Counts",
        "How To Reproduce",
        "finite exact aperture-orbit separator theorem",
        "This bundle is not the full research Python package",
        "committed finite certificate artifacts",
        "does not independently regenerate the full PRC transition universe from first principles",
        "python3 research/experiments/critical_radius_birth_dynamics/check_v2_5_public_theorem_integrity.py",
        term("no B", "8 theorem"),
        term("no general ", "pre", "dictor"),
    ]
    return phrase_check("v2_5_public_readme_wording", text, required, [])


def check_public_manifest_boundary() -> dict[str, str]:
    manifest_path = active_public_manifest_path()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sources = manifest_sources(manifest)
    if manifest_path == PUBLIC_RELEASE_MANIFEST:
        required = {
            "research/experiments/critical_radius_birth_dynamics/check_v2_5_public_theorem_integrity.py",
            "research/experiments/critical_radius_birth_dynamics/public_theorem_release_manifest_v2_5_v1_0.json",
            "research/experiments/critical_radius_birth_dynamics/public_theorem_release_workflow_v2_5_v1_0.yml",
            "research/experiments/critical_radius_birth_dynamics/data/prc_v2_5_public_theorem_summary_v0_1.csv",
            "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_draft_v0_1.md",
            "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_citation_v1_0.cff",
            "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_readme_v1_0.md",
            "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_release_notes_v1_0.md",
        }
        expected_id = "prc_v2_5_public_theorem_release_bundle_v1_0"
        expected_public_release = True
    else:
        required = {
            "research/experiments/critical_radius_birth_dynamics/check_v2_5_public_theorem_integrity.py",
            "research/experiments/critical_radius_birth_dynamics/public_theorem_manifest_v2_5_v0_1.json",
            "research/experiments/critical_radius_birth_dynamics/public_theorem_workflow_v2_5_v0_1.yml",
            "research/experiments/critical_radius_birth_dynamics/data/prc_v2_5_public_theorem_summary_v0_1.csv",
            "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_theorem_draft_v0_1.md",
            "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_5_public_readme_draft_v0_1.md",
        }
        expected_id = "prc_v2_5_public_theorem_review_bundle_v0_1"
        expected_public_release = False
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
    failures += int(manifest.get("public_release") is not expected_public_release)
    failures += int(manifest.get("id") != expected_id)
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
        ("historical_totals", "all", "checked_lift_rows"): "533690",
        ("historical_totals", "all", "close_rows"): "770",
        ("historical_totals", "all", "birth_rows"): "770",
        ("historical_totals", "all", "positive_margin_rows"): "770",
        ("historical_totals", "all", "nonclose_rows"): "532920",
        ("historical_totals", "all", "capacity_nonclose_families"): "2430",
        ("historical_totals", "all", "capacity_nonclose_lift_rows"): "52566",
        (
            "historical_totals",
            "all",
            "capacity_nonclose_positive_margin_lift_rows",
        ): "0",
        ("historical_totals", "all", "nonclose_positive_margin_rows"): "0",
        ("historical_totals", "all", "endpoint_touch_rows"): "0",
        ("historical_totals", "all", "min_close_positive_margin"): "1/221",
        ("historical_totals", "all", "max_nonclose_margin"): "-1/221",
        (
            "historical_separator",
            "B4_to_B5_full",
            "capacity_nonclose_lift_rows",
        ): "294",
        (
            "historical_separator",
            "B5_to_B6_full",
            "capacity_nonclose_lift_rows",
        ): "2870",
        (
            "historical_separator",
            "B6_to_B7_full",
            "capacity_nonclose_lift_rows",
        ): "49402",
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


def check_phase_gate_family_counts() -> dict[str, str]:
    family_rows = read_csv_dicts(PHASE_FAMILY_CSV)
    families = [row for row in family_rows if row["scope"] in SCOPES]

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
    return check_bool(
        "v2_5_phase_gate_family_counts",
        failures == 0,
        total=9,
        failed=failures,
    )


def check_row_level_separator_counts() -> dict[str, str]:
    rows = checked_lift_rows()
    total_rows = len(rows)
    close_rows = 0
    birth_rows = 0
    positive_margin_rows = 0
    nonclose_rows = 0
    nonclose_positive = 0
    close_without_positive = 0
    positive_without_close = 0
    phase_pass_mismatch = 0
    endpoint_touch = 0
    nonbirth_close = 0

    for row in rows:
        margin_positive = Fraction(row["phase_margin"]) > 0
        phase_pass = row["phase_pass"] == "True"
        is_close = row["is_close"] == "True"
        is_birth = row["is_birth"] == "True"

        close_rows += int(is_close)
        birth_rows += int(is_birth)
        positive_margin_rows += int(margin_positive)
        nonclose_rows += int(not is_close)
        nonclose_positive += int((not is_close) and margin_positive)
        close_without_positive += int(is_close and not margin_positive)
        positive_without_close += int(margin_positive and not is_close)
        phase_pass_mismatch += int(phase_pass != margin_positive)
        endpoint_touch += int(row["endpoint_touch"] == "True")
        nonbirth_close += int(is_close and not is_birth)

    expected = {
        "total_rows": (total_rows, 533690),
        "close_rows": (close_rows, 770),
        "birth_rows": (birth_rows, 770),
        "positive_margin_rows": (positive_margin_rows, 770),
        "nonclose_rows": (nonclose_rows, 532920),
        "nonclose_positive": (nonclose_positive, 0),
        "close_without_positive": (close_without_positive, 0),
        "positive_without_close": (positive_without_close, 0),
        "phase_pass_mismatch": (phase_pass_mismatch, 0),
        "endpoint_touch": (endpoint_touch, 0),
        "nonbirth_close": (nonbirth_close, 0),
    }
    failures = sum(actual != expected for actual, expected in expected.values())
    return check_bool(
        "v2_5_row_level_separator_counts",
        failures == 0,
        total=len(expected),
        failed=failures,
    )


def check_capacity_false_positive_row_counts() -> dict[str, str]:
    rows = checked_lift_rows()
    capacity_nonclose_by_scope = {scope: 0 for scope in SCOPES}
    capacity_nonclose_positive = 0

    for row in rows:
        is_capacity = row["capacity_pass"] == "True"
        is_close = row["is_close"] == "True"
        margin_positive = Fraction(row["phase_margin"]) > 0
        if is_capacity and not is_close:
            capacity_nonclose_by_scope[row["scope"]] += 1
            capacity_nonclose_positive += int(margin_positive)

    expected_by_scope = {
        "B4_to_B5_full": 294,
        "B5_to_B6_full": 2870,
        "B6_to_B7_full": 49402,
    }
    failures = sum(
        capacity_nonclose_by_scope[scope] != value
        for scope, value in expected_by_scope.items()
    )
    failures += int(sum(capacity_nonclose_by_scope.values()) != 52566)
    failures += int(capacity_nonclose_positive != 0)
    return check_bool(
        "v2_5_capacity_false_positive_row_counts",
        failures == 0,
        total=5,
        failed=failures,
    )


def check_margin_gap_counts() -> dict[str, str]:
    close_margins: list[Fraction] = []
    nonclose_margins: list[Fraction] = []
    for row in checked_lift_rows():
        margin = Fraction(row["phase_margin"])
        if row["is_close"] == "True":
            close_margins.append(margin)
        else:
            nonclose_margins.append(margin)

    min_close = min(close_margins)
    max_nonclose = max(nonclose_margins)
    failures = 0
    failures += int(min_close != Fraction(1, 221))
    failures += int(max_nonclose != Fraction(-1, 221))
    failures += int((min_close - max_nonclose) != Fraction(2, 221))
    return check_bool(
        "v2_5_margin_gap_counts",
        failures == 0,
        total=3,
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


def checked_lift_rows() -> list[dict[str, str]]:
    return [row for row in read_csv_dicts(PHASE_LIFT_CSV) if row["scope"] in SCOPES]


def manifest_sources(manifest: dict) -> set[str]:
    sources = {entry["source"] for entry in manifest.get("root_file_map", [])}
    sources.update(manifest.get("root_files", []))
    sources.update(manifest.get("research_files", []))
    return sources


def active_public_manifest_path() -> Path:
    return PUBLIC_RELEASE_MANIFEST if PUBLIC_RELEASE_MANIFEST.is_file() else PUBLIC_REVIEW_MANIFEST


def active_public_readme_path() -> Path:
    return PUBLIC_RELEASE_README if PUBLIC_RELEASE_README.is_file() else PUBLIC_REVIEW_README


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
