import pytest

from prime_reciprocal_projection.cli import main
from prime_reciprocal_projection.covering import max_uncovered_gap, uncovered_measure
from prime_reciprocal_projection.covering_branch_fill import (
    branch_fill_rows,
    branch_fill_summary,
    branch_fill_summary_table,
    branch_fill_summary_rows,
    branch_fill_table,
    read_branch_fill_csv,
    write_branch_fill_csv,
    write_branch_fill_summary_csv,
)


def test_branch_fill_first_row_matches_branch_one():
    row = branch_fill_rows(1000, max_branch=3)[0]
    assert row.branch == 1
    assert row.cumulative_uncovered_measure == pytest.approx(uncovered_measure(1000, branch=1))
    assert row.cumulative_max_gap == pytest.approx(max_uncovered_gap(1000, branch=1))
    assert row.cumulative_component_count > 0


def test_branch_fill_uncovered_measure_is_nonincreasing():
    rows = branch_fill_rows(1000, max_branch=8)
    measures = [row.cumulative_uncovered_measure for row in rows]
    assert measures == sorted(measures, reverse=True)
    assert rows[-1].cumulative_minus_full >= -1e-12
    assert all(row.marginal_uncovered_drop >= 0 for row in rows)


def test_branch_fill_fraction_progress_is_normalized():
    rows = branch_fill_rows(1000, max_branch=8)
    fill = [row.fill_fraction for row in rows]
    residual = [row.residual_fraction for row in rows]
    assert fill[0] == pytest.approx(0.0)
    assert residual[0] == pytest.approx(1.0)
    assert all(value is not None and 0 <= value <= 1 for value in fill)
    assert all(value is not None and 0 <= value <= 1 for value in residual)
    assert fill == sorted(fill)
    assert residual == sorted(residual, reverse=True)


def test_branch_fill_tracks_arc_widths_and_exact_complete():
    rows = branch_fill_rows(118, max_branch=5)
    assert rows[0].branch_arc_width > 0
    assert rows[-1].cumulative_arc_width >= rows[0].branch_arc_width
    assert all(row.exact_complete for row in rows)


def test_branch_fill_table_reuses_prime_pool():
    rows = branch_fill_table([1000, 10000], max_branch=2)
    assert [(row.n, row.branch) for row in rows] == [
        (1000, 1),
        (1000, 2),
        (10000, 1),
        (10000, 2),
    ]


def test_write_branch_fill_csv_header(tmp_path):
    output = tmp_path / "branch-fill.csv"
    write_branch_fill_csv(branch_fill_rows(1000, max_branch=1), output)
    lines = output.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("n,max_branch,branch,branch_prime_count")
    assert len(lines) == 2
    read_rows = read_branch_fill_csv(output)
    assert read_rows[0].n == 1000
    assert read_rows[0].fill_fraction == pytest.approx(0.0)


def test_branch_fill_summary_thresholds_and_censoring():
    rows = branch_fill_rows(1000, max_branch=2)
    summary = branch_fill_summary(rows)
    assert summary.k50 is None
    assert summary.k50_censored is True
    assert summary.residual_last is not None

    fuller_summary = branch_fill_summary_rows([1000], max_branch=200)[0]
    assert fuller_summary.a_branch1 >= fuller_summary.a_last
    assert fuller_summary.cumulative_arc_width_last > 0

    grouped_summary = branch_fill_summary_table(rows)
    assert grouped_summary == [summary]


def test_write_branch_fill_summary_csv_header(tmp_path):
    output = tmp_path / "branch-fill-summary.csv"
    write_branch_fill_summary_csv(branch_fill_summary_rows([1000], max_branch=2), output)
    lines = output.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("n,max_branch,full_uncovered_measure,exact_complete")
    assert len(lines) == 2


def test_branch_fill_rejects_invalid_max_branch():
    with pytest.raises(ValueError, match="max_branch"):
        branch_fill_rows(1000, max_branch=0)


def test_covering_branch_fill_cli_writes_csv(tmp_path):
    output = tmp_path / "branch-fill.csv"
    assert (
        main(
            [
                "covering-branch-fill",
                "--n",
                "1000",
                "10000",
                "--max-branch",
                "2",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 5
    assert lines[0].startswith("n,max_branch,branch")


def test_covering_branch_fill_summary_cli_writes_csv(tmp_path):
    output = tmp_path / "branch-fill-summary.csv"
    assert (
        main(
            [
                "covering-branch-fill-summary",
                "--n",
                "1000",
                "--max-branch",
                "2",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert lines[0].startswith("n,max_branch,full_uncovered_measure")

    long_csv = tmp_path / "branch-fill.csv"
    write_branch_fill_csv(branch_fill_rows(1000, max_branch=2), long_csv)
    from_input = tmp_path / "branch-fill-summary-input.csv"
    assert (
        main(
            [
                "covering-branch-fill-summary",
                "--input",
                str(long_csv),
                "--out",
                str(from_input),
            ]
        )
        == 0
    )
    assert from_input.read_text(encoding="utf-8").splitlines()[0] == lines[0]
