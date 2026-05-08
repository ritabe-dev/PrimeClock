import csv

from prime_reciprocal_projection.cli import main
from prime_reciprocal_projection.covering_branch_fill_cohorts import (
    DEFAULT_CHECKPOINTS,
    build_cohort_manifest,
    cohort_branch_fill_tables,
    read_cohort_manifest_csv,
)
from prime_reciprocal_projection.covering_runs import CompleteCoveringRun


def test_cohort_manifest_is_deterministic_and_nonoverlapping():
    runs = [
        CompleteCoveringRun(start=118, stop=118, length=1),
        CompleteCoveringRun(start=178, stop=178, length=1),
        CompleteCoveringRun(start=201, stop=201, length=1),
        CompleteCoveringRun(start=208, stop=208, length=1),
    ]
    rows = build_cohort_manifest(
        runs,
        start=100,
        stop=1000,
        bin_count=2,
        max_per_bin=2,
        local_radius=50,
    )
    assert rows == build_cohort_manifest(
        runs,
        start=100,
        stop=1000,
        bin_count=2,
        max_per_bin=2,
        local_radius=50,
    )
    complete_values = {row.n for row in rows if row.cohort_role == "complete"}
    control_values = {row.n for row in rows if row.cohort_role != "complete" and row.n is not None}
    assert complete_values.isdisjoint(control_values)


def test_local_mod6_control_matches_radius_and_residue():
    rows = build_cohort_manifest(
        [CompleteCoveringRun(start=118, stop=118, length=1)],
        start=100,
        stop=300,
        bin_count=1,
        max_per_bin=1,
        local_radius=20,
    )
    seed = next(row for row in rows if row.cohort_role == "complete")
    local = next(row for row in rows if row.cohort_role == "local_mod6_control")
    assert local.n is not None
    assert seed.n is not None
    assert local.n % 6 == seed.n % 6
    assert abs(local.n - seed.n) <= 20


def test_cohort_branch_fill_tables_have_expected_shape():
    manifest = build_cohort_manifest(
        [CompleteCoveringRun(start=118, stop=118, length=1)],
        start=100,
        stop=300,
        bin_count=1,
        max_per_bin=1,
        local_radius=20,
    )
    summary_rows, checkpoint_rows = cohort_branch_fill_tables(manifest, max_branch=5)
    eligible_seed_count = len({row.seed_n for row in manifest if row.eligible})
    assert len(summary_rows) == eligible_seed_count * 4
    assert len(checkpoint_rows) == eligible_seed_count * 4 * len(
        [branch for branch in DEFAULT_CHECKPOINTS if branch <= 5]
    )
    assert all(row.k50 is None or row.k50 <= 5 for row in summary_rows)


def test_cohort_cli_writes_manifest_and_summary(tmp_path):
    runs_csv = tmp_path / "runs.csv"
    runs_csv.write_text("start,stop,length\n118,118,1\n178,178,1\n", encoding="utf-8")
    manifest_csv = tmp_path / "manifest.csv"
    assert (
        main(
            [
                "covering-branch-fill-cohorts",
                "--complete-source",
                str(runs_csv),
                "--start",
                "100",
                "--stop",
                "300",
                "--bin-count",
                "1",
                "--max-per-bin",
                "1",
                "--local-radius",
                "20",
                "--out",
                str(manifest_csv),
            ]
        )
        == 0
    )
    manifest_rows = read_cohort_manifest_csv(manifest_csv)
    assert len(manifest_rows) == 4

    summary_csv = tmp_path / "summary.csv"
    checkpoint_csv = tmp_path / "checkpoints.csv"
    assert (
        main(
            [
                "covering-branch-fill-cohort-summary",
                "--manifest",
                str(manifest_csv),
                "--max-branch",
                "5",
                "--summary-out",
                str(summary_csv),
                "--checkpoint-out",
                str(checkpoint_csv),
            ]
        )
        == 0
    )
    with summary_csv.open(encoding="utf-8", newline="") as handle:
        summary_rows = list(csv.DictReader(handle))
    assert len(summary_rows) == 4
    assert summary_rows[0]["cohort_role"] == "complete"
