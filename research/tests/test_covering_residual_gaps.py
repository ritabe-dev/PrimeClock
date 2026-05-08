import csv

import pytest

from prime_reciprocal_projection.cli import main
from prime_reciprocal_projection.covering_branch_fill_cohorts import CohortManifestRow
from prime_reciprocal_projection.covering_residual_gaps import (
    benjamini_hochberg_q_values,
    bootstrap_median_delta_ci,
    exact_two_sided_sign_test_p,
    gap_quantile,
    normalized_gap_entropy,
    residual_gap_count_test_rows,
    residual_gap_effect_summary_rows,
    residual_gap_pair_delta_rows,
    residual_gap_rows,
    residual_gap_secondary_direction_rows,
    top_gap_share,
)


def test_gap_shape_helpers_are_stable():
    lengths = [0.1, 0.2, 0.7]
    assert gap_quantile(lengths, 0.50) == pytest.approx(0.2)
    assert gap_quantile(lengths, 0.90) == pytest.approx(0.7)
    assert top_gap_share(lengths) == pytest.approx(0.7)
    assert 0 < normalized_gap_entropy(lengths) <= 1


def test_gap_shape_helpers_handle_empty_and_single_gap():
    assert gap_quantile([], 0.50) == 0.0
    assert top_gap_share([]) == 0.0
    assert normalized_gap_entropy([]) == 0.0
    assert normalized_gap_entropy([0.5]) == 0.0


def test_residual_gap_rows_full_prefix_coverage_has_zero_gaps():
    rows = residual_gap_rows(
        [
            CohortManifestRow(
                seed_n=118,
                cohort_role="complete",
                n=118,
                bin_index=0,
                bin_start=100,
                bin_stop=200,
                n_mod_6=4,
                eligible=True,
                exclusion_reason="",
            )
        ],
        max_branch=100,
    )
    assert len(rows) == 1
    row = rows[0]
    assert row.exact_complete is True
    assert row.residual_gap_count == 0
    assert row.residual_gap_max == 0.0
    assert row.residual_top_gap_share == 0.0
    assert row.max_possible_branch == 59
    assert row.prefix_exhausts_all_branches is True
    assert row.seed_analysis_eligible is False


def test_seed_with_prefix_exhaustion_marks_all_roles_ineligible():
    rows = residual_gap_rows(
        [
            CohortManifestRow(118, "complete", 118, 0, 100, 200, 4, True, ""),
            CohortManifestRow(118, "local_mod6_control", 124, 0, 100, 200, 4, True, ""),
        ],
        max_branch=100,
    )
    assert {row.seed_analysis_eligible for row in rows} == {False}


def test_pair_delta_excludes_ineligible_seed_and_summarizes_direction():
    rows = residual_gap_rows(
        [
            CohortManifestRow(3000, "complete", 3000, 0, 2500, 3500, 0, True, ""),
            CohortManifestRow(3000, "local_mod6_control", 3006, 0, 2500, 3500, 0, True, ""),
            CohortManifestRow(3000, "band_mod6_control", 3012, 0, 2500, 3500, 0, True, ""),
            CohortManifestRow(3000, "band_ordinary_control", 3013, 0, 2500, 3500, 1, True, ""),
        ],
        max_branch=100,
    )
    deltas = residual_gap_pair_delta_rows(rows)
    assert len(deltas) == 18
    summary = residual_gap_effect_summary_rows(deltas)
    assert len(summary) == 18
    for row in summary:
        assert (
            row.complete_smaller_count
            + row.complete_larger_count
            + row.tie_count
            == row.eligible_pair_count
        )


def test_pair_delta_uses_complete_minus_control_for_fixed_fixture():
    rows = residual_gap_rows(
        [
            CohortManifestRow(5000, "complete", 5000, 0, 4500, 5500, 2, True, ""),
            CohortManifestRow(5000, "local_mod6_control", 5006, 0, 4500, 5500, 2, True, ""),
        ],
        max_branch=100,
    )
    deltas = residual_gap_pair_delta_rows(rows)
    top_share = next(row for row in deltas if row.metric == "residual_top_gap_share")
    complete = next(row for row in rows if row.cohort_role == "complete")
    control = next(row for row in rows if row.cohort_role == "local_mod6_control")
    assert top_share.delta_complete_minus_control == pytest.approx(
        complete.residual_top_gap_share - control.residual_top_gap_share
    )


def test_residual_gap_cli_writes_fixed_header(tmp_path):
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(
        "\n".join(
            [
                "seed_n,cohort_role,n,bin_index,bin_start,bin_stop,n_mod_6,eligible,exclusion_reason",
                "118,complete,118,0,100,200,4,True,",
            ]
        ),
        encoding="utf-8",
    )
    summary = tmp_path / "summary.csv"
    summary.write_text(
        "\n".join(
            [
                "seed_n,cohort_role,n,bin_index,max_branch,full_uncovered_measure,exact_complete,k50,k90,k99,k50_censored,k90_censored,k99_censored,a_branch1,a_last,residual_last,cumulative_arc_width_last",
                "118,complete,118,0,100,0.0,True,1,1,1,False,False,False,0.0,0.0,0.0,1.0",
            ]
        ),
        encoding="utf-8",
    )
    output = tmp_path / "residual.csv"
    assert (
        main(
            [
                "covering-branch-fill-residual-gaps",
                "--manifest",
                str(manifest),
                "--summary",
                str(summary),
                "--max-branch",
                "100",
                "--out",
                str(output),
                "--skip-figures",
            ]
        )
        == 0
    )
    with output.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["seed_n"] == "118"
    assert rows[0]["residual_gap_count"] == "0"
    assert rows[0]["prefix_exhausts_all_branches"] == "True"


def test_residual_gap_pairs_cli_writes_outputs(tmp_path):
    residual = tmp_path / "residual.csv"
    residual.write_text(
        "\n".join(
            [
                "seed_n,cohort_role,n,bin_index,max_branch,max_possible_branch,prefix_exhausts_all_branches,seed_analysis_eligible,full_uncovered_measure,exact_complete,residual_uncovered_measure,residual_gap_count,residual_gap_max,residual_gap_p50,residual_gap_p90,residual_gap_p99,residual_gap_entropy,residual_top_gap_share,residual_gap_near_zero_count",
                "3000,complete,3000,0,100,1500,False,True,0.0,True,0.3,3,0.2,0.1,0.2,0.2,0.8,0.66,0",
                "3000,local_mod6_control,3006,0,100,1503,False,True,0.1,False,0.4,4,0.2,0.1,0.2,0.2,0.9,0.50,1",
                "3000,band_mod6_control,3012,0,100,1506,False,True,0.1,False,0.4,4,0.2,0.1,0.2,0.2,0.9,0.50,1",
                "3000,band_ordinary_control,3013,0,100,1506,False,True,0.1,False,0.4,4,0.2,0.1,0.2,0.2,0.9,0.50,1",
            ]
        ),
        encoding="utf-8",
    )
    delta_out = tmp_path / "deltas.csv"
    summary_out = tmp_path / "summary.csv"
    assert (
        main(
            [
                "covering-branch-fill-residual-gap-pairs",
                "--input",
                str(residual),
                "--delta-out",
                str(delta_out),
                "--summary-out",
                str(summary_out),
                "--skip-figures",
            ]
        )
        == 0
    )
    assert len(list(csv.DictReader(delta_out.open(encoding="utf-8")))) == 18
    summary_rows = list(csv.DictReader(summary_out.open(encoding="utf-8")))
    assert len(summary_rows) == 18
    assert summary_rows[0]["eligible_pair_count"] == "1"


def test_exact_sign_test_handles_ties_via_non_tie_count():
    assert exact_two_sided_sign_test_p(4, 5) == pytest.approx(0.375)
    assert exact_two_sided_sign_test_p(0, 0) == 1.0


def test_benjamini_hochberg_q_values_are_stable():
    assert benjamini_hochberg_q_values([0.03, 0.20, 0.01]) == pytest.approx(
        [0.045, 0.20, 0.03]
    )


def test_bootstrap_median_delta_ci_is_seeded():
    first = bootstrap_median_delta_ci([-3.0, -2.0, 1.0, 4.0], iterations=50, seed=1729)
    second = bootstrap_median_delta_ci([-3.0, -2.0, 1.0, 4.0], iterations=50, seed=1729)
    assert first == second


def test_gap_count_test_rows_and_secondary_rows():
    rows = residual_gap_rows(
        [
            CohortManifestRow(5000, "complete", 5000, 0, 4500, 5500, 2, True, ""),
            CohortManifestRow(5000, "local_mod6_control", 5006, 0, 4500, 5500, 2, True, ""),
            CohortManifestRow(5000, "band_mod6_control", 5012, 0, 4500, 5500, 2, True, ""),
            CohortManifestRow(5000, "band_ordinary_control", 5018, 0, 4500, 5500, 2, True, ""),
        ],
        max_branch=100,
    )
    deltas = residual_gap_pair_delta_rows(rows)
    test_rows = residual_gap_count_test_rows(
        deltas,
        bootstrap_iterations=25,
        bootstrap_seed=1729,
    )
    assert len(test_rows) == 3
    for row in test_rows:
        assert row.metric == "residual_gap_count"
        assert row.complete_smaller_count + row.complete_larger_count + row.tie_count == row.pair_count
        assert row.non_tie_pair_count == row.complete_smaller_count + row.complete_larger_count
        assert 0.0 <= row.sign_test_p_two_sided <= 1.0
        assert 0.0 <= row.bh_q_value <= 1.0
    secondary = residual_gap_secondary_direction_rows(deltas)
    assert len(secondary) == 18


def test_residual_gap_count_test_cli_writes_outputs(tmp_path):
    deltas = tmp_path / "deltas.csv"
    deltas.write_text(
        "\n".join(
            [
                "seed_n,control_role,metric,complete_n,control_n,complete_value,control_value,delta_complete_minus_control",
                "1,local_mod6_control,residual_gap_count,10,11,3,4,-1",
                "2,local_mod6_control,residual_gap_count,20,21,3,2,1",
                "3,local_mod6_control,residual_gap_count,30,31,3,3,0",
                "1,band_mod6_control,residual_gap_count,10,12,3,4,-1",
                "2,band_mod6_control,residual_gap_count,20,22,3,4,-1",
                "3,band_mod6_control,residual_gap_count,30,32,3,2,1",
                "1,band_ordinary_control,residual_gap_count,10,13,3,4,-1",
                "2,band_ordinary_control,residual_gap_count,20,23,3,4,-1",
                "3,band_ordinary_control,residual_gap_count,30,33,3,4,-1",
                "1,local_mod6_control,residual_gap_max,10,11,0.1,0.2,-0.1",
                "1,band_mod6_control,residual_gap_max,10,12,0.1,0.2,-0.1",
                "1,band_ordinary_control,residual_gap_max,10,13,0.1,0.2,-0.1",
            ]
        ),
        encoding="utf-8",
    )
    out = tmp_path / "tests.csv"
    secondary = tmp_path / "secondary.csv"
    assert (
        main(
            [
                "covering-branch-fill-residual-gap-count-test",
                "--input",
                str(deltas),
                "--out",
                str(out),
                "--secondary-out",
                str(secondary),
                "--bootstrap-iterations",
                "25",
                "--skip-figures",
            ]
        )
        == 0
    )
    test_rows = list(csv.DictReader(out.open(encoding="utf-8")))
    secondary_rows = list(csv.DictReader(secondary.open(encoding="utf-8")))
    assert len(test_rows) == 3
    assert len(secondary_rows) == 6
    assert test_rows[0]["metric"] == "residual_gap_count"
    assert test_rows[0]["non_tie_pair_count"] == "2"
