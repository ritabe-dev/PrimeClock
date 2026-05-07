from pathlib import Path

from prime_reciprocal_projection.covering_metrics import (
    CoveringRow,
    branch1_exposed_gap_estimate,
    covering_row,
    write_covering_csv,
)
from prime_reciprocal_projection.cli import main
from prime_reciprocal_projection.primes import primes_up_to


def test_covering_row_has_expected_fields():
    row = covering_row(1000)
    assert row.n == 1000
    assert row.prime_count == 168
    assert 0 <= row.uncovered_measure <= 1
    assert row.uncovered_measure_times_log_n >= 0
    assert row.random_arc_baseline > 0
    assert row.branch1_exposed_gap_estimate >= 0


def test_branch1_exposed_gap_estimate_is_nonnegative():
    assert branch1_exposed_gap_estimate(1000) >= 0


def test_branch1_exposed_gap_estimate_includes_circular_boundary():
    n = 20
    branch1_primes = [p for p in primes_up_to(n) if n // p == 1]
    arc_data = sorted((n / p - 1.0, 1.0 / (2.0 * p)) for p in branch1_primes)
    expected = 0.0
    for index, (center, radius) in enumerate(arc_data):
        next_center, next_radius = arc_data[(index + 1) % len(arc_data)]
        gap = next_center - center
        if index == len(arc_data) - 1:
            gap += 1.0
        expected = max(expected, max(0.0, gap - radius - next_radius))
    assert branch1_exposed_gap_estimate(n) == expected


def test_write_covering_csv_has_stable_header_and_blank_none(tmp_path: Path):
    row = CoveringRow(
        n=10,
        prime_count=4,
        uncovered_measure=0.1,
        uncovered_measure_times_log_n=0.23,
        random_arc_baseline=0.3,
        max_uncovered_gap=0.05,
        complete_scale_1_over_n=False,
        complete_scale_1_over_pi_n=True,
        complete_numeric_1e_9=False,
        branch1_uncovered_measure=0.2,
        branch1_max_uncovered_gap=0.0,
        branch1_exposed_gap_estimate=0.0,
        gap_fill_ratio=None,
        gap_fill_drop=-0.05,
        uncovered_component_count=2,
        gap_p50=0.02,
        gap_p90=0.04,
        gap_p99=0.049,
    )
    output = tmp_path / "covering.csv"
    write_covering_csv([row], output)
    lines = output.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith(
        "n,prime_count,uncovered_measure,uncovered_measure_times_log_n"
    )
    assert ",," in lines[1]


def test_covering_metrics_cli_writes_csv(tmp_path: Path):
    output = tmp_path / "cli-covering.csv"
    assert main(["covering-metrics", "--n", "1000", "--out", str(output)]) == 0
    text = output.read_text(encoding="utf-8")
    assert "branch1_exposed_gap_estimate" in text
    assert "1000" in text


def test_covering_metrics_cli_supports_log_grid(tmp_path: Path):
    output = tmp_path / "cli-covering-log-grid.csv"
    assert (
        main(
            [
                "covering-metrics",
                "--log-grid",
                "1000",
                "10000",
                "3",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 4
    assert "10000" in output.read_text(encoding="utf-8")


def test_covering_metrics_cli_window_does_not_include_default_n(tmp_path: Path):
    output = tmp_path / "cli-covering-window.csv"
    assert (
        main(
            [
                "covering-metrics",
                "--window",
                "100",
                "1",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 4
    assert [line.split(",", 1)[0] for line in lines[1:]] == ["99", "100", "101"]


def test_covering_metrics_cli_explicit_n_combines_with_window(tmp_path: Path):
    output = tmp_path / "cli-covering-window-plus-n.csv"
    assert (
        main(
            [
                "covering-metrics",
                "--n",
                "1000",
                "--window",
                "100",
                "1",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    lines = output.read_text(encoding="utf-8").splitlines()
    assert [line.split(",", 1)[0] for line in lines[1:]] == ["99", "100", "101", "1000"]


def test_covering_figures_cli_writes_pngs(tmp_path: Path):
    assert (
        main(
            [
                "covering-figures",
                "--n",
                "1000",
                "10000",
                "--out",
                str(tmp_path),
            ]
        )
        == 0
    )
    assert (tmp_path / "prc_manifest.json").exists()
    assert any(path.name.startswith("prc_covering_trend") for path in tmp_path.iterdir())


def test_covering_figures_cli_sorts_custom_n(tmp_path: Path):
    assert (
        main(
            [
                "covering-figures",
                "--n",
                "10000",
                "1000",
                "--out",
                str(tmp_path),
            ]
        )
        == 0
    )
    assert (tmp_path / "prc_covering_trend_N1000_10000.png").exists()
