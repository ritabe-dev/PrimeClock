from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from fractions import Fraction
from pathlib import Path

import pytest

from prime_reciprocal_projection.covering_prime_prefix_filtration import (
    residue_is_exactly_covered,
)


EXPERIMENT_DIR = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "critical_radius_birth_dynamics"
)
REPO_ROOT = EXPERIMENT_DIR.parents[2]
WORKFLOW_CONFIG = EXPERIMENT_DIR / "candidate_workflow_v0_1.yml"
WORKFLOW_ENGINE = REPO_ROOT / "scripts" / "verify_candidate_workflow.py"


def _load_tools():
    spec = importlib.util.spec_from_file_location(
        "critical_radius_birth_dynamics_tools",
        EXPERIMENT_DIR / "tools.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tools = _load_tools()


def _rewrite_candidate_sha256sums(bundle_root: Path) -> None:
    lines = []
    for path in sorted(bundle_root.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS":
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(bundle_root).as_posix()}")
    (bundle_root / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_standalone_checker():
    spec = importlib.util.spec_from_file_location(
        "critical_radius_birth_dynamics_standalone",
        EXPERIMENT_DIR / "check_candidate_standalone.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


standalone_checker = _load_standalone_checker()


def _load_candidate_workflow_engine():
    spec = importlib.util.spec_from_file_location(
        "primeclock_candidate_workflow_engine",
        WORKFLOW_ENGINE,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


candidate_workflow_engine = _load_candidate_workflow_engine()

BUNDLE_SUBPROCESS_TIMEOUT_SECONDS = 120
SLOW_SUBPROCESS_TIMEOUT_SECONDS = 900


def _run_candidate_subprocess(
    args: list[str],
    *,
    timeout: int = BUNDLE_SUBPROCESS_TIMEOUT_SECONDS,
    **kwargs,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(args, timeout=timeout, **kwargs)
    except subprocess.TimeoutExpired as error:
        stdout = (
            error.stdout.decode("utf-8", errors="replace")
            if isinstance(error.stdout, bytes)
            else error.stdout
        )
        stderr = (
            error.stderr.decode("utf-8", errors="replace")
            if isinstance(error.stderr, bytes)
            else error.stderr
        )
        pytest.fail(
            "candidate subprocess timed out after "
            f"{timeout}s: {args!r}\nstdout:\n{stdout or ''}\nstderr:\n{stderr or ''}"
        )


def _copy_hash_manifest_fixture(tmp_path: Path) -> Path:
    manifest_root = tmp_path / "candidate"
    for relative_path in standalone_checker.EXPECTED_HASH_PATHS:
        source = EXPERIMENT_DIR / relative_path
        target = manifest_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    manifest = manifest_root / "data/prc_v2_3_candidate_sha256sums_v0_1.txt"
    shutil.copy2(
        EXPERIMENT_DIR / "data/prc_v2_3_candidate_sha256sums_v0_1.txt",
        manifest,
    )
    return manifest


def test_critical_radius_c4_endpoint_residues():
    primes = [2, 3, 5, 7]
    assert tools.critical_radius_certificate(2, primes)[0] == Fraction(1, 2)
    assert tools.critical_radius_certificate(208, primes)[0] == Fraction(1, 2)


def test_critical_radius_zero_residue_cusp_is_one():
    assert tools.critical_radius_certificate(0, [2, 3, 5, 7])[0] == Fraction(1)
    assert tools.critical_radius_certificate(0, [2, 3, 5, 7, 11])[0] == Fraction(1)


def test_critical_radius_level_set_matches_c4():
    primes = [2, 3, 5, 7]
    covered_by_radius = {
        residue
        for residue in range(210)
        if tools.critical_radius_certificate(residue, primes)[0] <= Fraction(1, 2)
    }
    assert covered_by_radius == {2, 208}


@pytest.mark.slow
def test_critical_radius_level_set_matches_c5_count():
    primes = [2, 3, 5, 7, 11]
    covered_by_radius = {
        residue
        for residue in range(2310)
        if tools.critical_radius_certificate(residue, primes)[0] <= Fraction(1, 2)
    }
    assert len(covered_by_radius) == 36
    assert all(residue_is_exactly_covered(residue, primes) for residue in covered_by_radius)


def test_critical_radius_reflection_invariance_for_k5():
    primes = [2, 3, 5, 7, 11]
    modulus = 2310
    for residue in [0, 2, 118, 849, 1202, 2309]:
        radius = tools.critical_radius_certificate(residue, primes)[0]
        reflected = tools.critical_radius_certificate((-residue) % modulus, primes)[0]
        assert radius == reflected


def test_critical_radius_rows_have_stable_statuses():
    rows = tools.critical_radius_rows(min_k=4, max_k=4)
    assert [row.__dataclass_fields__.keys() for row in rows[:1]]
    assert sum(row.status == "endpoint_covered" for row in rows) == 2
    assert sum(row.current_covering_residue for row in rows) == 2


@pytest.mark.slow
def test_critical_radius_summary_counts_match_level_sets():
    rows = tools.critical_radius_rows(min_k=4, max_k=5)
    summary = {row.k: row for row in tools.critical_radius_summary_rows(rows)}

    assert summary[4].residue_count == 210
    assert summary[4].covered_count == 2
    assert summary[4].endpoint_covered_count == 2
    assert summary[4].robust_covered_count == 0
    assert summary[4].nearest_uncovered_lambda_fraction

    assert summary[5].residue_count == 2310
    assert summary[5].covered_count == 36
    assert summary[5].covered_count == (
        summary[5].robust_covered_count + summary[5].endpoint_covered_count
    )


@pytest.mark.slow
def test_critical_radius_near_misses_are_sorted_uncovered_rows():
    rows = tools.critical_radius_rows(min_k=4, max_k=5)
    near_misses = tools.critical_radius_near_miss_rows(rows, limit_per_k=5)
    grouped = {
        k: [row for row in near_misses if row.k == k]
        for k in [4, 5]
    }

    assert {k: len(group) for k, group in grouped.items()} == {4: 5, 5: 5}
    assert grouped[4][0].lambda_fraction == "5/9"
    assert grouped[5][0].lambda_fraction == "7/13"

    for group in grouped.values():
        margins = [Fraction(row.lambda_minus_half_fraction) for row in group]
        assert margins == sorted(margins)
        assert all(margin > 0 for margin in margins)
        assert [row.near_miss_rank for row in group] == list(range(1, len(group) + 1))


@pytest.mark.slow
def test_near_miss_birth_parent_overlap_links_next_birth_layer():
    radius_rows = tools.critical_radius_rows(min_k=4, max_k=5)
    near_misses = tools.critical_radius_near_miss_rows(radius_rows, limit_per_k=20)
    parent_rows = tools.near_miss_birth_parent_rows(near_misses)
    grouped = {
        k: [row for row in parent_rows if row.k == k]
        for k in [4, 5]
    }

    assert {k: len(group) for k, group in grouped.items()} == {4: 20, 5: 20}
    assert sum(row.birth_lift_count > 0 for row in grouped[4]) == 13
    assert sum(row.birth_lift_count > 0 for row in grouped[5]) == 19

    for row in parent_rows:
        assert row.next_k == row.k + 1
        if row.birth_lift_count:
            residues = row.birth_lift_residues.split()
            remainders = row.birth_lift_remainders.split()
            assert len(residues) == row.birth_lift_count
            assert len(remainders) == row.birth_lift_count
            assert set(row.birth_types.split()) == {"strict_single_gap_birth"}


@pytest.mark.slow
def test_near_miss_gap_geometry_matches_birth_parent_overlap():
    radius_rows = tools.critical_radius_rows(min_k=4, max_k=5)
    near_misses = tools.critical_radius_near_miss_rows(radius_rows, limit_per_k=20)
    parent_rows = tools.near_miss_birth_parent_rows(near_misses)
    gap_rows = tools.near_miss_gap_geometry_rows(near_misses)

    parent_by_key = {(row.k, row.residue): row for row in parent_rows}
    assert len(gap_rows) == 40
    for row in gap_rows:
        parent = parent_by_key[(row.k, row.residue)]
        assert row.containing_remainder_count == parent.birth_lift_count
        assert row.containing_remainders == parent.birth_lift_remainders
        assert row.previous_open_gap_count >= 1
        assert Fraction(row.previous_uncovered_measure_fraction) > 0
        assert Fraction(row.max_previous_open_gap_length_fraction) > 0
        if row.containing_remainder_count:
            assert row.best_containment_margin_fraction
            assert Fraction(row.best_containment_margin_fraction) > 0


@pytest.mark.slow
def test_b5_threshold_crossing_rows_connect_parent_and_child_radius():
    rows = tools.birth_threshold_crossing_rows(min_k=5)

    assert len(rows) == 14
    assert {row.birth_type for row in rows} == {"strict_single_gap_birth"}
    for row in rows:
        assert Fraction(row.parent_lambda_fraction) > Fraction(1, 2)
        assert Fraction(row.current_lambda_fraction) <= Fraction(1, 2)
        assert row.parent_status == "uncovered"
        assert row.current_status in {"robust_covered", "endpoint_covered"}


@pytest.mark.slow
def test_threshold_crossing_rows_cover_b5_b6_b7_births():
    rows = tools.birth_threshold_crossing_rows(min_k=5, max_k=7)
    counts = {k: sum(row.k == k for row in rows) for k in [5, 6, 7]}

    assert counts == {5: 14, 6: 42, 7: 714}
    assert {row.birth_type for row in rows} == {"strict_single_gap_birth"}
    for row in rows:
        assert Fraction(row.parent_lambda_fraction) > Fraction(1, 2)
        assert Fraction(row.current_lambda_fraction) <= Fraction(1, 2)
        assert row.parent_status == "uncovered"
        assert row.current_status in {"robust_covered", "endpoint_covered"}


@pytest.mark.slow
def test_birth_dynamics_counts_and_summary_through_k7():
    rows = tools.birth_dynamics_rows(min_k=5, max_k=7)
    summary = {row.k: row for row in tools.birth_dynamics_summary_rows(rows)}

    assert summary[5].birth_count == 14
    assert summary[6].birth_count == 42
    assert summary[7].birth_count == 714

    for row in summary.values():
        classified = (
            row.strict_single_gap_birth
            + row.endpoint_single_gap_birth
            + row.strict_multi_gap_birth
            + row.endpoint_multi_gap_birth
        )
        assert classified == row.birth_count


@pytest.mark.slow
def test_b5_births_are_strict_single_gap_births():
    rows = [row for row in tools.birth_dynamics_rows(min_k=5, max_k=5) if row.k == 5]
    assert len(rows) == 14
    assert {row.birth_type for row in rows} == {"strict_single_gap_birth"}
    assert all(row.previous_open_gap_count == 1 for row in rows)
    assert all(not row.uses_endpoint_touching for row in rows)


def test_integrated_experiment_note_keeps_scope_narrow():
    note = EXPERIMENT_DIR / "notes" / "prc_critical_radius_birth_dynamics_v0_1.md"
    text = note.read_text(encoding="utf-8")

    assert "C_k = { r : lambda_k(r) <= 1/2 }" in text
    assert "B_7: 714 unique strict single-gap births" in text
    assert "unique single-gap theorem for all levels" in text
    assert "does not claim" in text


def test_near_miss_predictor_note_keeps_gap_geometry_boundary():
    note = EXPERIMENT_DIR / "notes" / "prc_near_miss_birth_predictor_v0_2.md"
    text = note.read_text(encoding="utf-8")

    assert "k=4 near-misses: 13/20 are B_5 birth parents" in text
    assert "k=5 near-misses: 19/20 are B_6 birth parents" in text
    assert "near-miss rank is useful but not sufficient" in text
    assert "q-grid phase in the dual containment window" in text
    assert "phase misses" in text
    assert "residues `99` and `111`" in text
    assert "does not claim" in text


def test_v2_3_internal_status_note_keeps_release_boundary():
    note = EXPERIMENT_DIR / "notes" / "prc_v2_3_internal_candidate_status.md"
    text = note.read_text(encoding="utf-8")

    assert "Status: internal-candidate." in text
    assert "Release eligibility: included in v2.3 candidate bundle" in text
    assert "promotion_manifest_v0_1.yml" in text
    assert "notes/prc_v2_3_theorem_note_draft_v0_1.md" in text
    assert "notes/prc_v2_3_theorem_candidate_outline_v0_1.md" in text
    assert "notes/prc_weighted_covering_radius_terminology_v0_1.md" in text
    assert "notes/prc_weighted_bisector_candidate_lemma_v0_1.md" in text
    assert "notes/prc_v2_3_related_work_decision_v0_1.md" in text
    assert "notes/prc_v2_3_standalone_checker_contract_v0_1.md" in text
    assert "v2.2.4 public release remains the stable finite certificate artifact" in text
    assert "gap-aperture windows" in text
    assert "unique strict single-gap births" in text
    assert "q-grid phase in the dual containment window" in text
    assert "v2.4 future-work notes are tracked internally but excluded" in text
    assert "Before promotion to a public v2.3 release bundle" in text
    assert "check_candidate_standalone.py: checks=10, failed=0" in text
    assert "the v2.2.4 public release has changed" in text


def test_v2_3_theorem_candidate_outline_keeps_scope_and_claims():
    note = EXPERIMENT_DIR / "notes" / "prc_v2_3_theorem_candidate_outline_v0_1.md"
    text = note.read_text(encoding="utf-8")

    assert "Status: internal theorem-candidate outline, not a public release." in text
    assert "C_k = { r : lambda_k(r) <= 1/2 }" in text
    assert "B_7: 714 unique strict single-gap births" in text
    assert "gap-aperture formula" in text
    assert "q-grid phase" in text
    assert "naive adjacent-center formula" in text
    assert "birth containment identity" in text
    assert "This outline does not claim" in text


def test_v2_3_theorem_note_draft_keeps_public_candidate_boundary():
    note = EXPERIMENT_DIR / "notes" / "prc_v2_3_theorem_note_draft_v0_1.md"
    text = note.read_text(encoding="utf-8")

    assert "Status: internal-candidate." in text
    assert "Release eligibility: included in v2.3 candidate bundle" in text
    assert "C_k = { r : lambda_k(r) <= 1/2 }" in text
    assert "B_7: 714 unique strict single-gap births" in text
    assert "weighted covering-radius" in text
    assert "formula" in text
    assert "naive adjacent-center formula" in text
    assert "Terminology boundary" in text
    assert "notes/prc_weighted_covering_radius_terminology_v0_1.md" in text
    assert "notes/prc_weighted_bisector_candidate_lemma_v0_1.md" in text
    assert "Gap-Aperture Birth Formula" in text
    assert "dual containment window" in text
    assert "q-grid phase" in text
    assert "|C_6| = 13*36 + 42 = 510" in text
    assert "|C_7| = 17*510 + 714 = 9384" in text
    assert "check_candidate.py: checks=13, failed=0" in text
    assert "check_candidate_standalone.py: checks=10, failed=0" in text
    assert "no B_8 or larger layers" in text
    assert "candidate_bundle_manifest_v0_1.json" in text
    assert "standalone checker uses only the Python standard library" in text
    assert "Future Work" in text
    assert "v2.4 residual-gap transition graph" in text
    assert "any change to the v2.2.4 public release" in text


@pytest.mark.slow
def test_v2_3_candidate_checker_passes(tmp_path):
    output = tmp_path / "v2_3_candidate_verification.csv"
    result = _run_candidate_subprocess(
        [
            sys.executable,
            str(EXPERIMENT_DIR / "check_candidate.py"),
            "--progress",
            "--out",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=SLOW_SUBPROCESS_TIMEOUT_SECONDS,
    )

    assert "check_v2_3_candidate: checks=13, failed=0" in result.stdout
    assert "[check_candidate] computing prime-prefix full rows through k=7" in result.stderr
    with output.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 13
    assert {row["status"] for row in rows} == {"pass"}
    check_names = {row["check_name"] for row in rows}
    assert "critical_radius_c4_level_set_exact" in check_names
    assert "critical_radius_c5_level_set_matches_exact_coverage" in check_names
    assert "birth_dynamics_b5_b6_b7_strict_single_gap_exact" in check_names
    assert "birth_dynamics_b5_b6_b7_unique_strict_single_gap_remainders" in check_names


def test_v2_3_candidate_standalone_checker_passes(tmp_path):
    output = tmp_path / "v2_3_candidate_standalone_verification.csv"
    result = _run_candidate_subprocess(
        [
            sys.executable,
            str(EXPERIMENT_DIR / "check_candidate_standalone.py"),
            "--out",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "check_v2_3_candidate_standalone: checks=10, failed=0" in result.stdout
    with output.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 10
    assert {row["status"] for row in rows} == {"pass"}
    check_names = {row["check_name"] for row in rows}
    assert "candidate_csv_hashes_exact" in check_names
    hash_row = next(row for row in rows if row["check_name"] == "candidate_csv_hashes_exact")
    assert hash_row["total"] == "60"
    assert hash_row["passed"] == "60"
    assert hash_row["failed"] == "0"
    assert "critical_radius_zero_residue_cusp_exact" in check_names
    assert "critical_radius_values_recomputed_from_definition" in check_names
    assert "critical_radius_c5_level_set_from_csv" in check_names
    assert "birth_dynamics_b5_b6_b7_unique_strict_single_gap_remainders" in check_names
    assert "birth_threshold_crossing_rows_match_births" in check_names


def test_v2_3_standalone_hash_manifest_rejects_missing_expected_path(tmp_path):
    manifest = _copy_hash_manifest_fixture(tmp_path)
    lines = manifest.read_text(encoding="utf-8").splitlines()
    manifest.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")

    result = standalone_checker.check_hash_manifest(manifest)

    assert result.status == "fail"
    assert result.failed > 0


def test_v2_3_standalone_hash_manifest_rejects_unknown_path(tmp_path):
    manifest = _copy_hash_manifest_fixture(tmp_path)
    text = manifest.read_text(encoding="utf-8")
    manifest.write_text(
        text
        + "0" * 64
        + "  data/unknown.csv\n",
        encoding="utf-8",
    )

    result = standalone_checker.check_hash_manifest(manifest)

    assert result.status == "fail"
    assert result.failed > 0


def test_v2_3_standalone_hash_manifest_rejects_duplicate_path(tmp_path):
    manifest = _copy_hash_manifest_fixture(tmp_path)
    first_line = manifest.read_text(encoding="utf-8").splitlines()[0]
    with manifest.open("a", encoding="utf-8") as handle:
        handle.write(first_line + "\n")

    result = standalone_checker.check_hash_manifest(manifest)

    assert result.status == "fail"
    assert result.failed > 0


def test_v2_3_standalone_hash_manifest_rejects_invalid_hash(tmp_path):
    manifest = _copy_hash_manifest_fixture(tmp_path)
    first_line, *rest = manifest.read_text(encoding="utf-8").splitlines()
    _, relative_path = first_line.split("  ", 1)
    manifest.write_text(
        "\n".join(["not-a-sha256  " + relative_path, *rest]) + "\n",
        encoding="utf-8",
    )

    result = standalone_checker.check_hash_manifest(manifest)

    assert result.status == "fail"
    assert result.failed > 0
    assert result.passed >= 0


def test_v2_3_standalone_hash_manifest_counts_never_go_negative(tmp_path):
    manifest = _copy_hash_manifest_fixture(tmp_path)
    manifest.write_text(
        "\n".join(
            [
                "not-a-sha256  data/unknown.csv",
                "malformed line without separator",
                f"{'0' * 64}  data/unknown.csv",
                f"{'0' * 64}  data/unknown.csv",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = standalone_checker.check_hash_manifest(manifest)

    assert result.status == "fail"
    assert result.failed > 0
    assert result.passed >= 0
    assert result.total >= result.failed


def test_v2_3_promotion_manifest_fixes_candidate_scope():
    manifest = EXPERIMENT_DIR / "promotion_manifest_v0_1.yml"
    text = manifest.read_text(encoding="utf-8")

    assert "status: internal_promotion_manifest" in text
    assert "base_public_release: v2.2.4" in text
    assert "critical_radius_layers: [4, 5]" in text
    assert "birth_dynamics_layers: [5, 6, 7]" in text
    assert "include_b8_or_larger: false" in text
    assert "include_asymptotic_claims: false" in text
    assert "helper_expected: checks=13, failed=0" in text
    assert "standalone_expected: checks=10, failed=0" in text
    assert "builder: candidate_bundle.py" in text
    assert "manifest: candidate_bundle_manifest_v0_1.json" in text
    assert "helper_scope: internal_helper_based" in text
    assert "standalone_scope: standard_library_definition_and_csv_audit" in text
    assert "terminology_status:" in text
    assert "primary_term: critical radius" in text
    assert "decision_note: notes/prc_v2_3_related_work_decision_v0_1.md" in text
    assert "future_work_excluded:" in text
    assert "v2.4 future-work notes are tracked internally but excluded" in text


def test_v2_3_candidate_bundle_manifest_fixes_allowlist():
    manifest = EXPERIMENT_DIR / "candidate_bundle_manifest_v0_1.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))

    assert data["status"] == "internal_candidate_manifest"
    assert data["public_release"] is False
    assert data["base_public_release"] == "v2.2.4"
    assert data["default_name"] == "PrimeClock-v2.3-candidate-v0.1"
    assert {
        "source": (
            "research/experiments/critical_radius_birth_dynamics/"
            "candidate_research_README_v0_1.md"
        ),
        "target": "research/README.md",
    } in data["root_file_map"]
    assert "research/README.md" not in data["research_files"]
    assert (
        "research/experiments/critical_radius_birth_dynamics/"
        "candidate_research_README_v0_1.md"
    ) in data["research_files"]
    assert "research/experiments/critical_radius_birth_dynamics/check_candidate_standalone.py" in data["research_files"]
    assert "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_related_work_decision_v0_1.md" in data["research_files"]
    assert "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_3_related_work_v0_2.md" in data["research_files"]
    assert "convert this manifest into a release/public config only after promotion" in data["promotion_boundary"]
    assert "do not include v2.4 or no-multigap future-work notes in this candidate bundle" in data["promotion_boundary"]


def test_v2_3_weighted_covering_radius_terminology_note_keeps_scope():
    note = (
        EXPERIMENT_DIR
        / "notes"
        / "prc_weighted_covering_radius_terminology_v0_1.md"
    )
    text = note.read_text(encoding="utf-8")

    assert "Status: internal terminology note, not a related-work survey." in text
    assert "critical radius" in text
    assert "finite max-min expression" in text
    assert "descriptive shorthand" in text
    assert "naive adjacent-center formula" in text
    assert "does not claim novelty" in text


def test_v2_3_related_work_decision_keeps_internal_boundary():
    note = EXPERIMENT_DIR / "notes" / "prc_v2_3_related_work_decision_v0_1.md"
    text = note.read_text(encoding="utf-8")

    assert "Status: internal terminology decision" in text
    assert "use `critical radius` as the primary" in text
    assert "Do not delay internal v2.3 candidate review" in text
    assert "formal related-work citations" in text


def test_v2_3_related_work_note_keeps_claim_boundary():
    note = EXPERIMENT_DIR / "notes" / "prc_v2_3_related_work_v0_2.md"
    text = note.read_text(encoding="utf-8")

    assert "Status: internal related-work note" in text
    assert "critical radius" in text
    assert "does not claim novelty" in text
    assert "weighted one-center" in text
    assert "10.1287/opre.30.4.777" in text
    assert "10.1287/moor.8.4.498" in text
    assert "It is not a claim" in text
    assert "classical covering systems" in text
    assert "does not claim that all future births are single-gap births" in text


def test_v2_3_weighted_bisector_candidate_lemma_keeps_scope():
    note = (
        EXPERIMENT_DIR
        / "notes"
        / "prc_weighted_bisector_candidate_lemma_v0_1.md"
    )
    text = note.read_text(encoding="utf-8")

    assert "Status: internal certificate lemma note, not a public release." in text
    assert "weighted bisector" in text
    assert "lower envelope" in text
    assert "naive adjacent-center formula" in text
    assert "certificate lemma" in text


def test_v2_3_standalone_checker_contract_marks_audit_scope():
    note = (
        EXPERIMENT_DIR
        / "notes"
        / "prc_v2_3_standalone_checker_contract_v0_1.md"
    )
    text = note.read_text(encoding="utf-8")

    assert "Status: implemented internal standalone audit" in text
    assert "check_candidate_standalone.py" in text
    assert "standard-library-only checker" in text
    assert "CSV/hash/headline finite-claim audit" in text
    assert "full independent regeneration" in text
    assert "`C_4` and `C_5` critical-radius level-set claims" in text
    assert "check_v2_3_candidate_standalone: checks=10, failed=0" in text


@pytest.mark.bundle
def test_v2_3_candidate_bundle_builds_and_checks(tmp_path):
    builder = EXPERIMENT_DIR / "candidate_bundle.py"
    bundle_name = "PrimeClock-v2.3-candidate-test"
    build = _run_candidate_subprocess(
        [
            sys.executable,
            str(builder),
            "--out",
            str(tmp_path),
            "--name",
            bundle_name,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    bundle_root = tmp_path / bundle_name

    assert f"candidate package directory: {bundle_root}" in build.stdout
    assert "candidate ZIP: not generated" in build.stdout
    assert f"latest path note: {tmp_path / 'LATEST_CANDIDATE_PATHS.txt'}" in build.stdout
    assert f"codex links note: {tmp_path / 'LATEST_CANDIDATE_LINKS.md'}" in build.stdout
    assert (bundle_root / "SHA256SUMS").is_file()
    latest_note = tmp_path / "LATEST_CANDIDATE_PATHS.txt"
    latest_links = tmp_path / "LATEST_CANDIDATE_LINKS.md"
    assert latest_note.is_file()
    assert latest_links.is_file()
    latest_note_text = latest_note.read_text(encoding="utf-8")
    latest_links_text = latest_links.read_text(encoding="utf-8")
    assert f"candidate package directory: {bundle_root}" in latest_note_text
    assert "candidate ZIP: not generated" in latest_note_text
    assert f"[Candidate package directory]({bundle_root})" in latest_links_text
    assert "Candidate ZIP: not generated" in latest_links_text
    assert (bundle_root / "README.md").is_file()
    assert (bundle_root / "research/src/prime_reciprocal_projection").is_dir()
    assert (
        bundle_root
        / "research/experiments/critical_radius_birth_dynamics/check_candidate.py"
    ).is_file()
    assert (
        bundle_root
        / "research/experiments/critical_radius_birth_dynamics/check_candidate_standalone.py"
    ).is_file()
    assert (
        bundle_root
        / "research/experiments/critical_radius_birth_dynamics/candidate_bundle.py"
    ).is_file()
    assert (
        bundle_root
        / "research/experiments/critical_radius_birth_dynamics/candidate_README_v0_1.md"
    ).is_file()
    assert (
        bundle_root
        / "research/experiments/critical_radius_birth_dynamics/"
        "candidate_research_README_v0_1.md"
    ).is_file()
    assert (
        bundle_root
        / "research/experiments/critical_radius_birth_dynamics/candidate_bundle_manifest_v0_1.json"
    ).is_file()
    assert (bundle_root / "research/README.md").is_file()
    research_readme = (bundle_root / "research/README.md").read_text(encoding="utf-8")
    assert "PRC v2.3 Candidate Research Package" in research_readme
    assert "experiments/critical_radius_birth_dynamics/README.md" in research_readme
    assert "The v2.2.4 public release files are not" in research_readme
    assert "VERIFY_FINITE_C4_B5.md" not in research_readme
    assert "test_covering_prime_prefix_filtration.py" not in research_readme
    bundle_file_manifest = bundle_root / "BUNDLE_FILE_MANIFEST.txt"
    assert bundle_file_manifest.is_file()
    manifest_paths = set(bundle_file_manifest.read_text(encoding="utf-8").splitlines())
    assert "README.md" in manifest_paths
    assert "BUNDLE_FILE_MANIFEST.txt" not in manifest_paths
    assert "SHA256SUMS" not in manifest_paths

    check = _run_candidate_subprocess(
        [sys.executable, str(builder), "--check", str(bundle_root)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert f"OK: {bundle_root}" in check.stdout


@pytest.mark.bundle
@pytest.mark.parametrize("unsafe_name", ["", "../bad", "/tmp/bad", "bad/name", "bad\\name", "bad"])
def test_v2_3_candidate_bundle_rejects_unsafe_names(tmp_path, unsafe_name):
    builder = EXPERIMENT_DIR / "candidate_bundle.py"

    result = _run_candidate_subprocess(
        [
            sys.executable,
            str(builder),
            "--out",
            str(tmp_path),
            "--name",
            unsafe_name,
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "FAIL:" in result.stdout


@pytest.mark.bundle
def test_v2_3_candidate_bundle_refuses_to_replace_non_candidate_dir(tmp_path):
    builder = EXPERIMENT_DIR / "candidate_bundle.py"
    bundle_name = "PrimeClock-v2.3-candidate-test"
    target = tmp_path / bundle_name
    target.mkdir()
    (target / "unrelated.txt").write_text("do not delete\n", encoding="utf-8")

    result = _run_candidate_subprocess(
        [
            sys.executable,
            str(builder),
            "--out",
            str(tmp_path),
            "--name",
            bundle_name,
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "refusing to replace existing non-candidate directory" in result.stdout
    assert (target / "unrelated.txt").is_file()


@pytest.mark.bundle
def test_v2_3_candidate_bundle_check_rejects_forbidden_paths(tmp_path):
    builder = EXPERIMENT_DIR / "candidate_bundle.py"
    bundle_name = "PrimeClock-v2.3-candidate-test"
    _run_candidate_subprocess(
        [
            sys.executable,
            str(builder),
            "--out",
            str(tmp_path),
            "--name",
            bundle_name,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    bundle_root = tmp_path / bundle_name
    forbidden_file = bundle_root / ".venv" / "secret.txt"
    forbidden_file.parent.mkdir()
    forbidden_file.write_text("must fail\n", encoding="utf-8")

    result = _run_candidate_subprocess(
        [sys.executable, str(builder), "--check", str(bundle_root)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "forbidden path component .venv" in result.stdout


@pytest.mark.bundle
def test_v2_3_candidate_bundle_check_ignores_local_python_caches(tmp_path):
    builder = EXPERIMENT_DIR / "candidate_bundle.py"
    bundle_name = "PrimeClock-v2.3-candidate-test"
    _run_candidate_subprocess(
        [
            sys.executable,
            str(builder),
            "--out",
            str(tmp_path),
            "--name",
            bundle_name,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    bundle_root = tmp_path / bundle_name
    cache_file = (
        bundle_root
        / "research/experiments/critical_radius_birth_dynamics/__pycache__/local.pyc"
    )
    cache_file.parent.mkdir()
    cache_file.write_bytes(b"local cache")
    pytest_cache = bundle_root / "research/.pytest_cache/CACHEDIR.TAG"
    pytest_cache.parent.mkdir()
    pytest_cache.write_text("local cache\n", encoding="utf-8")

    result = _run_candidate_subprocess(
        [sys.executable, str(builder), "--check", str(bundle_root)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert f"OK: {bundle_root}" in result.stdout


@pytest.mark.bundle
def test_v2_3_candidate_bundle_check_ignores_editable_install_metadata(tmp_path):
    builder = EXPERIMENT_DIR / "candidate_bundle.py"
    bundle_name = "PrimeClock-v2.3-candidate-test"
    _run_candidate_subprocess(
        [
            sys.executable,
            str(builder),
            "--out",
            str(tmp_path),
            "--name",
            bundle_name,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    bundle_root = tmp_path / bundle_name
    egg_info = bundle_root / "research/src/prime_reciprocal_projection.egg-info/PKG-INFO"
    egg_info.parent.mkdir()
    egg_info.write_text("local editable metadata\n", encoding="utf-8")
    dist_info = bundle_root / "research/src/prime_reciprocal_projection-0.0.0.dist-info/METADATA"
    dist_info.parent.mkdir()
    dist_info.write_text("local install metadata\n", encoding="utf-8")

    result = _run_candidate_subprocess(
        [sys.executable, str(builder), "--check", str(bundle_root)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert f"OK: {bundle_root}" in result.stdout


@pytest.mark.bundle
def test_v2_3_candidate_bundle_check_rejects_unexpected_manifest_file(tmp_path):
    builder = EXPERIMENT_DIR / "candidate_bundle.py"
    bundle_name = "PrimeClock-v2.3-candidate-test"
    _run_candidate_subprocess(
        [
            sys.executable,
            str(builder),
            "--out",
            str(tmp_path),
            "--name",
            bundle_name,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    bundle_root = tmp_path / bundle_name
    extra_file = bundle_root / "research" / "EXTRA.md"
    extra_file.write_text("extra file must fail\n", encoding="utf-8")
    _rewrite_candidate_sha256sums(bundle_root)

    result = _run_candidate_subprocess(
        [sys.executable, str(builder), "--check", str(bundle_root)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "unexpected bundle file: research/EXTRA.md" in result.stdout


@pytest.mark.bundle
def test_v2_3_candidate_bundle_check_rejects_missing_manifest_file(tmp_path):
    builder = EXPERIMENT_DIR / "candidate_bundle.py"
    bundle_name = "PrimeClock-v2.3-candidate-test"
    _run_candidate_subprocess(
        [
            sys.executable,
            str(builder),
            "--out",
            str(tmp_path),
            "--name",
            bundle_name,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    bundle_root = tmp_path / bundle_name
    required_file = (
        bundle_root
        / "research/experiments/critical_radius_birth_dynamics/data/"
        "prc_prime_prefix_critical_radius_k4_k5_v0_1.csv"
    )
    required_file.unlink()
    _rewrite_candidate_sha256sums(bundle_root)

    result = _run_candidate_subprocess(
        [sys.executable, str(builder), "--check", str(bundle_root)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert (
        "missing bundle file: research/experiments/critical_radius_birth_dynamics/"
        "data/prc_prime_prefix_critical_radius_k4_k5_v0_1.csv"
    ) in result.stdout


@pytest.mark.bundle
def test_v2_3_candidate_bundle_check_rejects_missing_file_manifest(tmp_path):
    builder = EXPERIMENT_DIR / "candidate_bundle.py"
    bundle_name = "PrimeClock-v2.3-candidate-test"
    _run_candidate_subprocess(
        [
            sys.executable,
            str(builder),
            "--out",
            str(tmp_path),
            "--name",
            bundle_name,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    bundle_root = tmp_path / bundle_name
    (bundle_root / "BUNDLE_FILE_MANIFEST.txt").unlink()

    result = _run_candidate_subprocess(
        [sys.executable, str(builder), "--check", str(bundle_root)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "missing BUNDLE_FILE_MANIFEST.txt" in result.stdout


@pytest.mark.bundle
def test_v2_3_candidate_bundle_check_rejects_file_manifest_traversal(tmp_path):
    builder = EXPERIMENT_DIR / "candidate_bundle.py"
    bundle_name = "PrimeClock-v2.3-candidate-test"
    _run_candidate_subprocess(
        [
            sys.executable,
            str(builder),
            "--out",
            str(tmp_path),
            "--name",
            bundle_name,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    bundle_root = tmp_path / bundle_name
    file_manifest = bundle_root / "BUNDLE_FILE_MANIFEST.txt"
    with file_manifest.open("a", encoding="utf-8") as handle:
        handle.write("../outside.txt\n")

    result = _run_candidate_subprocess(
        [sys.executable, str(builder), "--check", str(bundle_root)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "unsafe BUNDLE_FILE_MANIFEST.txt path" in result.stdout


@pytest.mark.bundle
def test_v2_3_candidate_bundle_check_rejects_sha256sum_traversal(tmp_path):
    builder = EXPERIMENT_DIR / "candidate_bundle.py"
    bundle_name = "PrimeClock-v2.3-candidate-test"
    _run_candidate_subprocess(
        [
            sys.executable,
            str(builder),
            "--out",
            str(tmp_path),
            "--name",
            bundle_name,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    bundle_root = tmp_path / bundle_name
    with (bundle_root / "SHA256SUMS").open("a", encoding="utf-8") as handle:
        handle.write(f"{'0' * 64}  ../outside.txt\n")

    result = _run_candidate_subprocess(
        [sys.executable, str(builder), "--check", str(bundle_root)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "unsafe SHA256SUMS path" in result.stdout


@pytest.mark.bundle
def test_v2_3_candidate_bundle_check_rejects_future_work_notes(tmp_path):
    builder = EXPERIMENT_DIR / "candidate_bundle.py"
    bundle_name = "PrimeClock-v2.3-candidate-test"
    _run_candidate_subprocess(
        [
            sys.executable,
            str(builder),
            "--out",
            str(tmp_path),
            "--name",
            bundle_name,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    bundle_root = tmp_path / bundle_name
    future_note = (
        bundle_root
        / "research/experiments/critical_radius_birth_dynamics/notes/prc_v2_4_example.md"
    )
    future_note.write_text("must fail\n", encoding="utf-8")

    result = _run_candidate_subprocess(
        [sys.executable, str(builder), "--check", str(bundle_root)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "forbidden candidate path marker prc_v2_4" in result.stdout


@pytest.mark.bundle
def test_v2_3_candidate_bundle_check_rejects_future_work_status(tmp_path):
    builder = EXPERIMENT_DIR / "candidate_bundle.py"
    bundle_name = "PrimeClock-v2.3-candidate-test"
    _run_candidate_subprocess(
        [
            sys.executable,
            str(builder),
            "--out",
            str(tmp_path),
            "--name",
            bundle_name,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    bundle_root = tmp_path / bundle_name
    note = bundle_root / "research/experiments/critical_radius_birth_dynamics/notes/future.md"
    future_status = "Status: " + "future-work"
    future_release_line = (
        "Release eligibility: excluded from v2.3 "
        "candidate bundle until promoted."
    )
    note.write_text(
        f"{future_status}.\n"
        f"{future_release_line}\n",
        encoding="utf-8",
    )

    result = _run_candidate_subprocess(
        [sys.executable, str(builder), "--check", str(bundle_root)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert f"forbidden candidate text marker {future_status}" in result.stdout


@pytest.mark.slow
@pytest.mark.bundle
def test_v2_3_candidate_zip_is_self_contained(tmp_path):
    builder = EXPERIMENT_DIR / "candidate_bundle.py"
    bundle_name = "PrimeClock-v2.3-candidate-test"
    build = _run_candidate_subprocess(
        [
            sys.executable,
            str(builder),
            "--out",
            str(tmp_path),
            "--name",
            bundle_name,
            "--zip",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=SLOW_SUBPROCESS_TIMEOUT_SECONDS,
    )
    bundle_root = tmp_path / bundle_name
    zip_path = tmp_path / f"{bundle_name}.zip"

    assert f"candidate package directory: {bundle_root}" in build.stdout
    assert f"candidate ZIP: {zip_path}" in build.stdout
    assert f"latest path note: {tmp_path / 'LATEST_CANDIDATE_PATHS.txt'}" in build.stdout
    assert f"codex links note: {tmp_path / 'LATEST_CANDIDATE_LINKS.md'}" in build.stdout
    assert zip_path.is_file()
    latest_note = tmp_path / "LATEST_CANDIDATE_PATHS.txt"
    latest_links = tmp_path / "LATEST_CANDIDATE_LINKS.md"
    assert latest_note.is_file()
    assert latest_links.is_file()
    latest_note_text = latest_note.read_text(encoding="utf-8")
    latest_links_text = latest_links.read_text(encoding="utf-8")
    assert f"candidate package directory: {bundle_root}" in latest_note_text
    assert f"candidate ZIP: {zip_path}" in latest_note_text
    assert f"[Candidate package directory]({bundle_root})" in latest_links_text
    assert f"[Candidate ZIP]({zip_path})" in latest_links_text

    forbidden_name_markers = [
        "AGENTS",
        "no_multigap",
        "prc_v2_4",
        "private_notes",
        "review_packages",
        "scratch",
    ]
    forbidden_text_patterns = [
        re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
        for term in [
            "Chat" + "GPT",
            "L" + "LM",
            "A" + "I",
            "pro" + "mpt",
            "review " + "package",
        ]
    ]
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        assert f"{bundle_name}/README.md" in names
        assert (
            f"{bundle_name}/research/experiments/critical_radius_birth_dynamics/"
            "candidate_bundle.py"
        ) in names
        assert (
            f"{bundle_name}/research/experiments/critical_radius_birth_dynamics/"
            "candidate_README_v0_1.md"
        ) in names
        assert not any(
            marker in name
            for marker in forbidden_name_markers
            for name in names
        )
        for name in names:
            if not name.endswith((".json", ".md", ".py", ".txt", ".yaml", ".yml")):
                continue
            text = archive.read(name).decode("utf-8")
            assert not any(pattern.search(text) for pattern in forbidden_text_patterns)

    extract_root = tmp_path / "unzipped"
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(extract_root)
    unpacked_root = extract_root / bundle_name
    unpacked_research = unpacked_root / "research"
    unpacked_builder = (
        unpacked_research
        / "experiments/critical_radius_birth_dynamics/candidate_bundle.py"
    )
    unpacked_env = os.environ.copy()
    unpacked_env["PYTHONPATH"] = (
        str(unpacked_research / "src")
        + os.pathsep
        + unpacked_env.get("PYTHONPATH", "")
    )

    _run_candidate_subprocess(
        [sys.executable, str(unpacked_builder), "--check", str(unpacked_root)],
        cwd=unpacked_research,
        env=unpacked_env,
        check=True,
        capture_output=True,
        text=True,
        timeout=SLOW_SUBPROCESS_TIMEOUT_SECONDS,
    )
    _run_candidate_subprocess(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_critical_radius_birth_dynamics.py",
            "-q",
            "-m",
            "not slow and not bundle",
            "-k",
            "not candidate_zip_is_self_contained",
        ],
        cwd=unpacked_research,
        env=unpacked_env,
        check=True,
        capture_output=True,
        text=True,
        timeout=SLOW_SUBPROCESS_TIMEOUT_SECONDS,
    )
    _run_candidate_subprocess(
        [
            sys.executable,
            "experiments/critical_radius_birth_dynamics/check_candidate.py",
        ],
        cwd=unpacked_research,
        env=unpacked_env,
        check=True,
        capture_output=True,
        text=True,
        timeout=SLOW_SUBPROCESS_TIMEOUT_SECONDS,
    )
    _run_candidate_subprocess(
        [
            sys.executable,
            "experiments/critical_radius_birth_dynamics/check_candidate_standalone.py",
        ],
        cwd=unpacked_research,
        env=unpacked_env,
        check=True,
        capture_output=True,
        text=True,
        timeout=SLOW_SUBPROCESS_TIMEOUT_SECONDS,
    )


def test_v2_3_future_work_notes_are_tracked_but_not_bundled():
    manifest = EXPERIMENT_DIR / "manifest.yml"
    candidate_manifest = EXPERIMENT_DIR / "candidate_bundle_manifest_v0_1.json"
    manifest_text = manifest.read_text(encoding="utf-8")
    data = json.loads(candidate_manifest.read_text(encoding="utf-8"))
    candidate_files = "\n".join(data["research_files"])

    assert "tracked_internal_notes_excluded_from_candidate:" in manifest_text
    artifact_section = manifest_text.split("tracked_internal_notes_excluded_from_candidate:", 1)[0]
    assert "notes/prc_no_multigap_birth_note_v0_1.md" not in artifact_section
    assert "notes/prc_v2_4_residual_gap_transition_graph_idea_v0_1.md" not in artifact_section
    assert "notes/prc_no_multigap_birth_note_v0_1.md" in manifest_text
    assert "notes/prc_v2_4_residual_gap_transition_graph_idea_v0_1.md" in manifest_text
    assert "candidate_bundle.py" in candidate_files
    assert "candidate_README_v0_1.md" in candidate_files
    assert "prc_no_multigap_birth_note_v0_1.md" not in candidate_files
    assert "prc_v2_4_residual_gap_transition_graph_idea_v0_1.md" not in candidate_files


def test_v2_3_candidate_readme_uses_dev_install():
    readme = EXPERIMENT_DIR / "candidate_README_v0_1.md"
    text = readme.read_text(encoding="utf-8")

    assert 'python -m pip install -e ".[dev]"' in text


def test_v2_3_candidate_subprocesses_use_timeout_helper():
    source = Path(__file__).read_text(encoding="utf-8")

    assert "BUNDLE_SUBPROCESS_TIMEOUT_SECONDS = 120" in source
    assert "SLOW_SUBPROCESS_TIMEOUT_SECONDS = 900" in source
    assert "return subprocess.run(args, timeout=timeout, **kwargs)" in source
    assert "_run_candidate_subprocess(" in source


def test_v2_3_verification_docs_split_fast_and_slow_paths():
    root = EXPERIMENT_DIR.parents[1]
    pyproject = root / "pyproject.toml"
    readme_text = (EXPERIMENT_DIR / "README.md").read_text(encoding="utf-8")
    candidate_readme_text = (EXPERIMENT_DIR / "candidate_README_v0_1.md").read_text(
        encoding="utf-8"
    )
    pyproject_text = pyproject.read_text(encoding="utf-8")

    assert '"slow: long-running v2.3 candidate verification' in pyproject_text
    assert '"bundle: candidate package build, check, and ZIP verification"' in pyproject_text
    for text in [readme_text, candidate_readme_text]:
        assert "Quick Verification" in text
        assert "Bundle Verification" in text
        assert "Full Internal Verification" in text
        assert '-m "not slow and not bundle"' in text
        assert '-m "bundle and not slow"' in text
        assert "-m slow" in text
        assert "--out /tmp/prc-v2.3-standalone-check.csv" in text
        assert "--progress --out /tmp/prc-v2.3-helper-check.csv" in text
        assert "--out /tmp/prc-v2.3-helper-check.csv" in text
        assert "unzip -t <printed-candidate-zip-path>" in text
        assert "primary package hygiene check" in text
        assert "independently" in text
        assert "regenerated" in text
        assert "internal slow regression" in text
        assert "BUNDLE_FILE_MANIFEST.txt" in text
        assert "accidental" in text
        assert "file-drift guard" in text
        assert "*.egg-info" in text
        assert "*.dist-info" in text
        assert "check_candidate_standalone.py" in text
        assert "check_candidate.py" in text
        assert "process-hygiene" in text
        assert "schedule timezone" in text
        assert "labels" in text
        assert "without adding work" in text
        assert "report metadata" in text


def test_candidate_workflow_process_hygiene_passes_current_config(monkeypatch):
    monkeypatch.delenv("GITHUB_EVENT_NAME", raising=False)
    monkeypatch.delenv("GITHUB_EVENT_PATH", raising=False)
    config = candidate_workflow_engine.load_config(WORKFLOW_CONFIG)

    failures = candidate_workflow_engine.process_hygiene_failures(
        config,
        repo_root=REPO_ROOT,
    )

    assert failures == []


def test_candidate_workflow_status_report_requires_goal_percent_and_slice():
    valid = (
        "## Goal\n"
        "Keep the candidate workflow reusable.\n"
        "Current completion: 98%.\n"
        "Remaining slice estimate: 1-2 slices.\n"
    )
    assert candidate_workflow_engine.status_report_failures(valid, source="fixture") == []

    missing_percent = valid.replace("98%", "nearly complete")
    assert "missing current completion percent" in "\n".join(
        candidate_workflow_engine.status_report_failures(
            missing_percent,
            source="fixture",
        )
    )

    missing_slice = valid.replace("1-2 slices", "a small amount")
    assert "missing remaining slice estimate" in "\n".join(
        candidate_workflow_engine.status_report_failures(
            missing_slice,
            source="fixture",
        )
    )


def test_candidate_workflow_pr_body_hygiene_uses_pull_request_event(
    tmp_path,
    monkeypatch,
):
    config = candidate_workflow_engine.load_config(WORKFLOW_CONFIG)
    event_path = tmp_path / "event.json"
    event_path.write_text(
        json.dumps(
            {
                "pull_request": {
                    "body": (
                        "## Goal\n"
                        "Add reusable candidate workflow checks.\n"
                        "Current completion: 98%.\n"
                        "Remaining slice estimate: 0.5-1 slices.\n"
                    )
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event_path))

    assert (
        candidate_workflow_engine.process_hygiene_failures(
            config,
            repo_root=REPO_ROOT,
            require_pr_body=True,
        )
        == []
    )

    event_path.write_text(
        json.dumps({"pull_request": {"body": "## Goal\nNo percent here.\n1 slice left."}}),
        encoding="utf-8",
    )
    failures = candidate_workflow_engine.process_hygiene_failures(
        config,
        repo_root=REPO_ROOT,
        require_pr_body=True,
    )
    assert any("PR body: missing current completion percent" in failure for failure in failures)


def test_candidate_workflow_schedule_docs_include_utc_and_jst(tmp_path):
    config = candidate_workflow_engine.load_config(WORKFLOW_CONFIG)

    assert candidate_workflow_engine.check_timezone_docs(config, repo_root=REPO_ROOT) == []

    utc_only = tmp_path / "schedule.md"
    utc_only.write_text("Weekly candidate slow gate: Sunday 18:20 UTC.\n", encoding="utf-8")
    bad_config = dict(config)
    bad_config["process_hygiene"] = {
        "timezone_docs": [{"path": str(utc_only), "label": "fixture"}]
    }
    failures = candidate_workflow_engine.check_timezone_docs(bad_config, repo_root=REPO_ROOT)
    assert "UTC and JST" in failures[0]

    bad_config["process_hygiene"] = dict(config["process_hygiene"])
    bad_config["process_hygiene"]["timezone_docs"] = [
        {
            "path": ".github/workflows/verify.yml",
            "required_text": "Sunday 18:20 UTC = Monday 04:20 JST",
        }
    ]
    failures = candidate_workflow_engine.check_timezone_docs(bad_config, repo_root=REPO_ROOT)
    assert "missing timezone text" in failures[0]


def test_candidate_workflow_artifact_wording_detector_is_neutral():
    private_terms = [
        "Ob" + "sidian",
        "my" + "ContextVault",
        "North" + "star",
        "G" + "mail",
        "Google " + "Calendar",
        "Todo" + "ist",
        "No" + "tion",
        "Chat" + "GPT",
        "A" + "I",
        "L" + "LM",
        "pro" + "mpt",
    ]

    text = "This candidate artifact mentions " + private_terms[0] + "."

    assert candidate_workflow_engine.forbidden_term_matches(text, private_terms) == [
        private_terms[0]
    ]
