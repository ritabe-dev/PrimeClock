from pathlib import Path

import pytest

from prime_reciprocal_projection.cli import main
from prime_reciprocal_projection.cluster_scan import ClusterScanRow, write_cluster_scan_csv
from prime_reciprocal_projection.covering_runs import (
    CompleteCoveringRun,
    DEFAULT_PREFILTER_TOLERANCE,
    PREFILTER_GUARANTEE_MAX_N,
    block_scan_prefilter_runs,
    complete_covering_runs_from_cluster_csv,
    consecutive_runs,
    default_prefilter_validation_windows,
    exact_complete_runs_in_range,
    exact_complete_values_in_range,
    factorization,
    length2_neighborhood_rows,
    length2_pair_forensics,
    prefilter_validation_windows,
    prefiltered_exact_complete_values_in_range,
    required_prefilter_tolerance,
    transition_stats_from_runs,
    summarize_runs,
    validate_prefilter_tolerance,
    write_complete_covering_runs_csv,
)


def test_consecutive_runs_dedupes_and_splits():
    runs = consecutive_runs([5, 2, 3, 3, 8, 9, 10])
    assert runs == [
        CompleteCoveringRun(start=2, stop=3, length=2),
        CompleteCoveringRun(start=5, stop=5, length=1),
        CompleteCoveringRun(start=8, stop=10, length=3),
    ]


def test_summarize_runs_reports_longest_and_multi_runs():
    summary = summarize_runs(
        [
            CompleteCoveringRun(start=2, stop=3, length=2),
            CompleteCoveringRun(start=5, stop=5, length=1),
            CompleteCoveringRun(start=8, stop=10, length=3),
        ]
    )
    assert summary.value_count == 6
    assert summary.run_count == 3
    assert summary.longest_run_length == 3
    assert summary.longest_run_start == 8
    assert summary.longest_run_stop == 10
    assert summary.multi_run_count == 2
    assert summary.values_in_multi_runs == 5


def test_complete_covering_runs_from_cluster_csv_uses_unique_certified_values(tmp_path: Path):
    csv_path = tmp_path / "cluster.csv"
    rows = [
        _cluster_row(center=10, certified_values="10 11 12"),
        _cluster_row(center=11, certified_values="11 12 14"),
    ]
    write_cluster_scan_csv(rows, csv_path)

    assert complete_covering_runs_from_cluster_csv(csv_path) == [
        CompleteCoveringRun(start=10, stop=12, length=3),
        CompleteCoveringRun(start=14, stop=14, length=1),
    ]


def test_write_complete_covering_runs_csv_has_stable_header(tmp_path: Path):
    output = tmp_path / "runs.csv"
    write_complete_covering_runs_csv(
        [CompleteCoveringRun(start=10, stop=12, length=3)],
        output,
    )
    assert output.read_text(encoding="utf-8").splitlines() == [
        "start,stop,length",
        "10,12,3",
    ]


def test_exact_complete_values_in_range_checks_every_integer():
    values = exact_complete_values_in_range(116, 120)
    assert values == [118]
    assert exact_complete_runs_in_range(116, 120) == [
        CompleteCoveringRun(start=118, stop=118, length=1)
    ]


def test_prefiltered_exact_complete_values_in_range_exact_checks_candidates():
    result = prefiltered_exact_complete_values_in_range(116, 120)
    assert result.checked_count == 5
    assert result.numeric_candidate_count >= result.exact_complete_count
    assert result.values == (118,)


def test_prefiltered_exact_complete_values_in_range_supports_chunks():
    result = prefiltered_exact_complete_values_in_range(116, 124, chunk_size=3)
    assert result.checked_count == 9
    assert result.values == (118,)


def test_numpy_prefilter_matches_python_prefilter_on_small_ranges():
    for start, stop in [(116, 124), (92204, 92255), (999000, 999020)]:
        python_result = prefiltered_exact_complete_values_in_range(
            start,
            stop,
            engine="python",
            chunk_size=max(1, stop - start + 1),
        )
        numpy_result = prefiltered_exact_complete_values_in_range(
            start,
            stop,
            engine="numpy",
            chunk_size=max(1, stop - start + 1),
        )
        assert numpy_result.values == python_result.values
        assert numpy_result.numeric_candidate_count == python_result.numeric_candidate_count


def test_prefilter_tolerance_guardrails_cover_v0_range():
    assert required_prefilter_tolerance(PREFILTER_GUARANTEE_MAX_N) < DEFAULT_PREFILTER_TOLERANCE
    assert PREFILTER_GUARANTEE_MAX_N == 10_000_000
    validate_prefilter_tolerance(PREFILTER_GUARANTEE_MAX_N)

    with pytest.raises(ValueError, match="below the conservative required"):
        validate_prefilter_tolerance(PREFILTER_GUARANTEE_MAX_N, tolerance=1e-16)

    with pytest.raises(ValueError, match="documented only"):
        validate_prefilter_tolerance(PREFILTER_GUARANTEE_MAX_N + 1)

    validate_prefilter_tolerance(PREFILTER_GUARANTEE_MAX_N + 1, require_guarantee=False)


def test_prefilter_scan_can_opt_into_unguaranteed_range():
    result = prefiltered_exact_complete_values_in_range(
        PREFILTER_GUARANTEE_MAX_N + 1,
        PREFILTER_GUARANTEE_MAX_N + 1,
        require_guarantee=False,
        engine="numpy",
    )
    assert result.checked_count == 1


def test_factorization_formats_stably():
    assert factorization(92230) == "2*5*23*401"
    assert factorization(257672) == "2^3*31*1039"


def test_transition_stats_counts_runs_and_residues():
    stats = transition_stats_from_runs(
        [
            CompleteCoveringRun(start=10, stop=12, length=3),
            CompleteCoveringRun(start=20, stop=21, length=2),
        ],
        start=10,
        stop=30,
    )
    assert stats.complete_count == 5
    assert stats.run_count == 2
    assert stats.longest_run_length == 3
    assert stats.length2_run_count == 3
    assert stats.length3_start_count == 1
    assert stats.c0_mod_6_counts == "0:1 1:0 2:1 3:1 4:1 5:1"
    assert stats.length2_start_mod_6_counts == "0:0 1:0 2:1 3:0 4:1 5:1"


def test_length2_forensics_and_neighborhood_cover_expected_offsets():
    runs = [CompleteCoveringRun(start=118, stop=119, length=2)]
    pair_rows = length2_pair_forensics(runs)
    assert len(pair_rows) == 1
    assert pair_rows[0].run_start == 118
    assert pair_rows[0].start_mod_6 == 4
    assert pair_rows[0].factorization_start == "2*59"

    neighborhood_rows = length2_neighborhood_rows(runs)
    assert [row.offset for row in neighborhood_rows] == [-1, 0, 1, 2]
    assert [row.n for row in neighborhood_rows] == [117, 118, 119, 120]


def test_prefilter_validation_windows_reports_match():
    rows = prefilter_validation_windows([(116, 120, "tiny")])
    assert len(rows) == 1
    assert rows[0].matches
    assert rows[0].all_exact_values == "118"
    assert rows[0].prefilter_exact_values == "118"


def test_default_prefilter_validation_windows_uses_length2_and_large_blocks():
    windows = default_prefilter_validation_windows(
        [CompleteCoveringRun(start=118, stop=119, length=2)],
        start=2,
        stop=100000,
    )
    assert windows[0] == (93, 144, "length2:118-119")
    assert windows[1] == (49952, 50452, "block-mid:2-100000")


def test_covering_runs_cli_writes_csv(tmp_path: Path):
    cluster_csv = tmp_path / "cluster.csv"
    output = tmp_path / "runs.csv"
    write_cluster_scan_csv([_cluster_row(center=10, certified_values="10 11 13")], cluster_csv)

    assert (
        main(
            [
                "covering-runs",
                "--input",
                str(cluster_csv),
                "--out",
                str(output),
            ]
        )
        == 0
    )
    assert output.read_text(encoding="utf-8").splitlines() == [
        "start,stop,length",
        "10,11,2",
        "13,13,1",
    ]


def test_covering_run_scan_cli_writes_csv(tmp_path: Path):
    output = tmp_path / "exact-runs.csv"
    assert (
        main(
            [
                "covering-run-scan",
                "--start",
                "116",
                "--stop",
                "120",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    assert output.read_text(encoding="utf-8").splitlines() == [
        "start,stop,length",
        "118,118,1",
    ]


def test_covering_run_forensics_cli_writes_outputs(tmp_path: Path):
    input_csv = tmp_path / "runs.csv"
    transition_out = tmp_path / "transition.csv"
    pair_out = tmp_path / "pairs.csv"
    neighborhood_out = tmp_path / "neighborhood.csv"
    validation_out = tmp_path / "validation.csv"
    write_complete_covering_runs_csv(
        [CompleteCoveringRun(start=118, stop=119, length=2)],
        input_csv,
    )

    assert (
        main(
            [
                "covering-run-forensics",
                "--input",
                str(input_csv),
                "--start",
                "116",
                "--stop",
                "124",
                "--transition-out",
                str(transition_out),
                "--pair-out",
                str(pair_out),
                "--neighborhood-out",
                str(neighborhood_out),
                "--validation-out",
                str(validation_out),
            ]
        )
        == 0
    )
    assert "length2_run_count" in transition_out.read_text(encoding="utf-8")
    assert "factorization_start" in pair_out.read_text(encoding="utf-8")
    assert "offset" in neighborhood_out.read_text(encoding="utf-8")
    assert "matches" in validation_out.read_text(encoding="utf-8")


def test_covering_run_prefilter_scan_cli_writes_csv(tmp_path: Path):
    output = tmp_path / "prefilter-runs.csv"
    assert (
        main(
            [
                "covering-run-prefilter-scan",
                "--start",
                "116",
                "--stop",
                "120",
                "--chunk-size",
                "2",
                "--engine",
                "numpy",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    assert output.read_text(encoding="utf-8").splitlines() == [
        "start,stop,length",
        "118,118,1",
    ]


def test_block_scan_prefilter_runs_writes_and_resumes(tmp_path: Path):
    out_dir = tmp_path / "blocks"
    combined_out = tmp_path / "combined.csv"
    summary_out = tmp_path / "summary.csv"

    result = block_scan_prefilter_runs(
        116,
        124,
        block_size=3,
        out_dir=out_dir,
        combined_out=combined_out,
        summary_out=summary_out,
        engine="numpy",
        chunk_size=3,
    )
    assert result.block_count == 3
    assert result.computed_block_count == 3
    assert result.resumed_block_count == 0
    assert combined_out.read_text(encoding="utf-8").splitlines() == [
        "start,stop,length",
        "118,118,1",
    ]
    assert "block_start" in summary_out.read_text(encoding="utf-8")

    resumed = block_scan_prefilter_runs(
        116,
        124,
        block_size=3,
        out_dir=out_dir,
        combined_out=combined_out,
        summary_out=summary_out,
        engine="numpy",
        chunk_size=3,
        resume=True,
    )
    assert resumed.computed_block_count == 0
    assert resumed.resumed_block_count == 3
    summary_lines = summary_out.read_text(encoding="utf-8").splitlines()
    assert summary_lines[1].endswith(",True")
    assert summary_lines[2].endswith(",True")
    assert summary_lines[3].endswith(",True")


def test_block_scan_resume_rejects_mismatched_engine(tmp_path: Path):
    out_dir = tmp_path / "blocks"
    combined_out = tmp_path / "combined.csv"
    summary_out = tmp_path / "summary.csv"

    block_scan_prefilter_runs(
        116,
        124,
        block_size=3,
        out_dir=out_dir,
        combined_out=combined_out,
        summary_out=summary_out,
        engine="numpy",
        chunk_size=3,
    )

    with pytest.raises(ValueError, match="engine=numpy, expected python"):
        block_scan_prefilter_runs(
            116,
            124,
            block_size=3,
            out_dir=out_dir,
            combined_out=combined_out,
            summary_out=summary_out,
            engine="python",
            chunk_size=3,
            resume=True,
        )


def test_block_scan_resume_rejects_mismatched_checked_count(tmp_path: Path):
    out_dir = tmp_path / "blocks"
    combined_out = tmp_path / "combined.csv"
    summary_out = tmp_path / "summary.csv"

    block_scan_prefilter_runs(
        116,
        124,
        block_size=3,
        out_dir=out_dir,
        combined_out=combined_out,
        summary_out=summary_out,
        engine="numpy",
        chunk_size=3,
    )
    first_summary = out_dir / "prc_summary_116_118.csv"
    first_summary.write_text(
        first_summary.read_text(encoding="utf-8").replace(",3,", ",99,", 1),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="checked_count=99, expected 3"):
        block_scan_prefilter_runs(
            116,
            124,
            block_size=3,
            out_dir=out_dir,
            combined_out=combined_out,
            summary_out=summary_out,
            engine="numpy",
            chunk_size=3,
            resume=True,
        )


def test_covering_run_block_scan_cli_writes_outputs(tmp_path: Path):
    out_dir = tmp_path / "blocks"
    combined_out = tmp_path / "combined.csv"
    summary_out = tmp_path / "summary.csv"
    assert (
        main(
            [
                "covering-run-block-scan",
                "--start",
                "116",
                "--stop",
                "124",
                "--block-size",
                "3",
                "--chunk-size",
                "3",
                "--engine",
                "numpy",
                "--out-dir",
                str(out_dir),
                "--combined-out",
                str(combined_out),
                "--summary-out",
                str(summary_out),
            ]
        )
        == 0
    )
    assert combined_out.exists()
    assert summary_out.exists()


def test_covering_run_benchmark_cli_writes_csv(tmp_path: Path):
    output = tmp_path / "benchmark.csv"
    assert (
        main(
            [
                "covering-run-benchmark",
                "--window",
                "116",
                "124",
                "tiny",
                "--engine",
                "python",
                "numpy",
                "--chunk-size",
                "9",
                "--out",
                str(output),
            ]
        )
        == 0
    )
    lines = output.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("label,start,stop,engine")
    assert len(lines) == 3

    assert (
        main(
            [
                "covering-run-benchmark",
                "--window",
                "125",
                "127",
                "tiny2",
                "--engine",
                "numpy",
                "--chunk-size",
                "3",
                "--out",
                str(output),
                "--append",
            ]
        )
        == 0
    )
    appended_lines = output.read_text(encoding="utf-8").splitlines()
    assert appended_lines.count(lines[0]) == 1
    assert len(appended_lines) == 4


def _cluster_row(center: int, certified_values: str) -> ClusterScanRow:
    return ClusterScanRow(
        center=center,
        seed_uncovered_measure=None,
        seed_baseline_ratio=None,
        radius=1,
        window_start=center - 1,
        window_stop=center + 1,
        window_size=3,
        float_zero_count=0,
        exact_complete_count=len(certified_values.split()),
        float_positive_exact_count=0,
        d_r=1 / 3,
        min_uncovered_measure=0.0,
        median_uncovered_measure=0.1,
        median_baseline_ratio=0.5,
        max_uncovered_measure=0.2,
        certified_values=certified_values,
    )
