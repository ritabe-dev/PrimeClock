from pathlib import Path

from prime_reciprocal_projection.cli import main
from prime_reciprocal_projection.cluster_scan import (
    ClusterScanRow,
    ClusterSensitivityRow,
    cluster_sensitivity_table,
    discover_seed_rows,
    discover_seed_values,
    read_cluster_scan_csv,
    scan_cluster_window,
    unique_certified_values,
    write_cluster_scan_csv,
    write_cluster_sensitivity_csv,
)
from prime_reciprocal_projection.covering import exact_is_completely_covered, uncovered_measure


def test_discover_seed_values_uses_log_grid_and_threshold():
    seeds = discover_seed_values(start=1000, stop=2000, count=3, ratio_threshold=float("inf"))
    assert seeds[0] == 1000
    assert seeds[-1] == 2000
    assert len(seeds) == 3


def test_discover_seed_rows_includes_seed_metrics():
    rows = discover_seed_rows(start=1000, stop=2000, count=3, ratio_threshold=float("inf"))
    assert rows[0].n == 1000
    assert rows[0].uncovered_measure >= 0
    assert rows[0].baseline_ratio >= 0


def test_scan_cluster_window_reports_density():
    row = scan_cluster_window(1000, radius=2)
    assert row.center == 1000
    assert row.window_start == 998
    assert row.window_stop == 1002
    assert row.window_size == 5
    assert 0 <= row.d_r <= 1
    assert row.float_positive_exact_count >= 0
    assert row.min_uncovered_measure <= row.median_uncovered_measure <= row.max_uncovered_measure


def test_write_cluster_scan_csv_has_stable_header(tmp_path: Path):
    row = ClusterScanRow(
        center=10,
        seed_uncovered_measure=None,
        seed_baseline_ratio=None,
        radius=1,
        window_start=9,
        window_stop=11,
        window_size=3,
        float_zero_count=1,
        exact_complete_count=1,
        float_positive_exact_count=0,
        d_r=1 / 3,
        min_uncovered_measure=0.0,
        median_uncovered_measure=0.1,
        median_baseline_ratio=0.5,
        max_uncovered_measure=0.2,
        certified_values="10",
    )
    output = tmp_path / "cluster.csv"
    write_cluster_scan_csv([row], output)
    lines = output.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith(
        "center,seed_uncovered_measure,seed_baseline_ratio,radius,window_start"
    )
    assert "certified_values" in lines[0]
    assert lines[1].startswith("10,,,1,9,11,3,1,1,0")

    read_rows = read_cluster_scan_csv(output)
    assert read_rows == [row]
    assert unique_certified_values(read_rows) == [10]


def test_covering_cluster_scan_cli_writes_csv(tmp_path: Path):
    output = tmp_path / "cluster-cli.csv"
    assert (
        main(
            [
                "covering-cluster-scan",
                "--start",
                "1000",
                "--stop",
                "2000",
                "--count",
                "3",
                "--ratio-threshold",
                "inf",
                "--radius",
                "1",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    text = output.read_text(encoding="utf-8")
    assert "d_r" in text
    assert "certified_values" in text
    assert "float_positive_exact_count" in text


def test_scan_cluster_window_exact_checks_all_values():
    row = scan_cluster_window(118, radius=1)
    exact_values = {int(value) for value in row.certified_values.split()}
    expected_values = {
        value
        for value in range(row.window_start, row.window_stop + 1)
        if exact_is_completely_covered(value)
    }
    expected_float_positive = {
        value for value in expected_values if uncovered_measure(value) != 0.0
    }
    assert row.window_size == 3
    assert 118 in exact_values
    assert exact_values == expected_values
    assert row.d_r == row.exact_complete_count / row.window_size
    assert row.float_positive_exact_count == len(expected_float_positive)


def test_cluster_sensitivity_table_reports_threshold_radius_rows():
    rows = cluster_sensitivity_table(
        start=1000,
        stop=2000,
        count=3,
        ratio_thresholds=[0.0, float("inf")],
        radii=[1, 2],
    )
    assert len(rows) == 4
    assert {row.radius for row in rows} == {1, 2}
    assert {row.ratio_threshold for row in rows} == {0.0, float("inf")}
    assert all(0 <= row.d_r_min <= row.d_r_max for row in rows)


def test_write_cluster_sensitivity_csv_has_stable_header(tmp_path: Path):
    row = ClusterSensitivityRow(
        ratio_threshold=0.05,
        radius=250,
        seed_count=1,
        exact_complete_memberships=2,
        unique_exact_complete_count=2,
        d_r_min=0.01,
        d_r_median=0.02,
        d_r_mean=0.02,
        d_r_max=0.03,
        top_center=1000,
        top_exact_count=2,
        top_d_r=0.03,
    )
    output = tmp_path / "sensitivity.csv"
    write_cluster_sensitivity_csv([row], output)
    lines = output.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("ratio_threshold,radius,seed_count")
    assert lines[1].startswith("0.05,250,1")


def test_covering_cluster_sensitivity_cli_writes_csv(tmp_path: Path):
    output = tmp_path / "sensitivity-cli.csv"
    assert (
        main(
            [
                "covering-cluster-sensitivity",
                "--start",
                "1000",
                "--stop",
                "2000",
                "--count",
                "3",
                "--ratio-threshold",
                "0",
                "inf",
                "--radius",
                "1",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    text = output.read_text(encoding="utf-8")
    assert "unique_exact_complete_count" in text
    assert "top_center" in text
