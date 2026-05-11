from __future__ import annotations

import importlib.util
import shutil
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from prime_reciprocal_projection.covering_prime_prefix_filtration import (
    residue_is_exactly_covered,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import build_public_release  # noqa: E402


EXPERIMENT_DIR = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "critical_radius_birth_dynamics"
)


def _load_tools():
    spec = importlib.util.spec_from_file_location(
        "critical_radius_birth_dynamics_public_tools",
        EXPERIMENT_DIR / "tools.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tools = _load_tools()


def test_public_critical_radius_c4_level_set():
    primes = [2, 3, 5, 7]
    covered_by_radius = {
        residue
        for residue in range(210)
        if tools.critical_radius_certificate(residue, primes)[0] <= Fraction(1, 2)
    }
    assert covered_by_radius == {2, 208}


def test_public_critical_radius_edge_cases():
    single_prime_radius, single_prime_point, single_prime_active = (
        tools.critical_radius_certificate(0, [2])
    )
    assert single_prime_radius == Fraction(1)
    assert single_prime_point == Fraction(1, 2)
    assert single_prime_active == (2,)

    assert tools.critical_radius_certificate(0, [2, 3, 5, 7])[0] == Fraction(1)
    assert tools.critical_radius_certificate(0, [2, 3, 5, 7, 11])[0] == Fraction(1)


def test_public_critical_radius_c5_count_and_zero_residue():
    primes = [2, 3, 5, 7, 11]
    covered_by_radius = {
        residue
        for residue in range(2310)
        if tools.critical_radius_certificate(residue, primes)[0] <= Fraction(1, 2)
    }
    assert len(covered_by_radius) == 36
    assert tools.critical_radius_certificate(0, primes)[0] == Fraction(1)
    assert all(residue_is_exactly_covered(residue, primes) for residue in covered_by_radius)


def test_public_birth_containment_strict_and_endpoint_boundaries():
    strict = tools.classify_birth_containment(
        [(Fraction(1, 4), Fraction(1, 2))],
        [(Fraction(1, 8), Fraction(5, 8))],
    )
    assert strict.margin == Fraction(1, 8)
    assert strict.uses_endpoint_touching is False

    endpoint = tools.classify_birth_containment(
        [(Fraction(1, 4), Fraction(1, 2))],
        [(Fraction(1, 4), Fraction(1, 2))],
    )
    assert endpoint.margin == 0
    assert endpoint.uses_endpoint_touching is True


def test_public_birth_dynamics_b5_b6_b7_counts():
    rows = tools.birth_dynamics_rows(min_k=5, max_k=7)
    summary = {row.k: row for row in tools.birth_dynamics_summary_rows(rows)}

    assert summary[5].birth_count == 14
    assert summary[6].birth_count == 42
    assert summary[7].birth_count == 714
    assert {row.birth_type for row in rows} == {"strict_single_gap_birth"}

    for k in [5, 6, 7]:
        layer_rows = [row for row in rows if row.k == k]
        assert len({row.parent_residue_mod_previous for row in layer_rows}) == len(layer_rows)


def test_public_release_builder_refuses_to_overwrite_source_repo(tmp_path):
    fake_repo = tmp_path / "PrimeClock-2.3.0"
    fake_config_dir = fake_repo / "release" / "public"
    fake_config_dir.mkdir(parents=True)
    shutil.copy2(
        REPO_ROOT / "release" / "public" / "release_config.json",
        fake_config_dir / "release_config.json",
    )

    with pytest.raises(ValueError, match="over the source repository"):
        build_public_release.build_release(fake_repo, tmp_path)


def test_public_release_builder_refuses_output_inside_source_repo():
    with pytest.raises(ValueError, match="inside the source repository"):
        build_public_release.build_release(REPO_ROOT, REPO_ROOT)


def test_public_release_builder_refuses_existing_non_bundle_directory(tmp_path):
    output_parent = tmp_path / "out"
    release_root = output_parent / "PrimeClock-2.3.0"
    release_root.mkdir(parents=True)
    marker = release_root / "keep.txt"
    marker.write_text("do not delete\n", encoding="utf-8")

    with pytest.raises(ValueError, match="existing non-release directory"):
        build_public_release.build_release(REPO_ROOT, output_parent)

    assert marker.read_text(encoding="utf-8") == "do not delete\n"


def test_public_release_builder_replaces_generated_bundle_and_uses_public_workflow(tmp_path):
    output_parent = tmp_path / "out"
    release_root = build_public_release.build_release(REPO_ROOT, output_parent)
    stale_file = release_root / "stale.txt"
    stale_file.write_text("old generated bundle content\n", encoding="utf-8")

    rebuilt_root = build_public_release.build_release(REPO_ROOT, output_parent)

    assert rebuilt_root == release_root
    assert not stale_file.exists()
    workflow = (rebuilt_root / ".github" / "workflows" / "verify.yml").read_text(
        encoding="utf-8"
    )
    assert "verify_candidate_workflow.py" not in workflow
    assert "candidate_workflow_v0_1.yml" not in workflow
    assert "tests/test_critical_radius_birth_dynamics_public.py" in workflow
    assert "tests/test_covering_prime_prefix_filtration.py" in workflow
