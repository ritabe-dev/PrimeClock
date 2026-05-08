import pytest


def test_matplotlib_is_optional_for_core_tests():
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
    except ModuleNotFoundError:
        pytest.skip("matplotlib is not installed in this environment")


def test_prc_covering_figures_smoke(tmp_path):
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
    except ModuleNotFoundError:
        pytest.skip("matplotlib is not installed in this environment")

    from prime_reciprocal_projection.figures import generate_prc_v0_figures

    generated = generate_prc_v0_figures(tmp_path, ns=[1000, 10000])
    assert len(generated) == 3
    for filename in generated:
        assert (tmp_path / filename).exists()
    assert (tmp_path / "prc_manifest.json").exists()


def test_prc_cluster_figures_smoke(tmp_path):
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
    except ModuleNotFoundError:
        pytest.skip("matplotlib is not installed in this environment")

    from prime_reciprocal_projection.cluster_scan import ClusterScanRow, write_cluster_scan_csv
    from prime_reciprocal_projection.figures import generate_prc_cluster_figures

    csv_path = tmp_path / "cluster.csv"
    write_cluster_scan_csv(
        [
            ClusterScanRow(
                center=1000,
                seed_uncovered_measure=0.0,
                seed_baseline_ratio=0.0,
                radius=1,
                window_start=999,
                window_stop=1001,
                window_size=3,
                float_zero_count=1,
                exact_complete_count=1,
                float_positive_exact_count=0,
                d_r=1 / 3,
                min_uncovered_measure=0.0,
                median_uncovered_measure=0.1,
                median_baseline_ratio=0.5,
                max_uncovered_measure=0.2,
                certified_values="1000",
            ),
            ClusterScanRow(
                center=1200,
                seed_uncovered_measure=None,
                seed_baseline_ratio=None,
                radius=1,
                window_start=1199,
                window_stop=1201,
                window_size=3,
                float_zero_count=0,
                exact_complete_count=1,
                float_positive_exact_count=1,
                d_r=1 / 3,
                min_uncovered_measure=0.0,
                median_uncovered_measure=0.1,
                median_baseline_ratio=0.5,
                max_uncovered_measure=0.2,
                certified_values="1200",
            )
        ],
        csv_path,
    )
    generated = generate_prc_cluster_figures(csv_path, tmp_path)
    assert len(generated) == 2
    for filename in generated:
        assert (tmp_path / filename).exists()
    assert (tmp_path / "prc_cluster_manifest.json").exists()


def test_prc_branch_fill_figures_smoke(tmp_path):
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
    except ModuleNotFoundError:
        pytest.skip("matplotlib is not installed in this environment")

    from prime_reciprocal_projection.covering_branch_fill import branch_fill_rows, write_branch_fill_csv
    from prime_reciprocal_projection.figures import generate_prc_branch_fill_figures

    csv_path = tmp_path / "branch-fill.csv"
    write_branch_fill_csv(branch_fill_rows(1000, max_branch=5), csv_path)
    generated = generate_prc_branch_fill_figures(csv_path, tmp_path)
    assert generated == [
        "prc_branch_fill_residual_v0_3.png",
        "prc_branch_fill_fraction_v0_3.png",
    ]
    for filename in generated:
        assert (tmp_path / filename).exists()
    assert (tmp_path / "prc_branch_fill_manifest.json").exists()


def test_prc_branch_fill_cohort_figures_smoke(tmp_path):
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
    except ModuleNotFoundError:
        pytest.skip("matplotlib is not installed in this environment")

    from prime_reciprocal_projection.figures import generate_prc_branch_fill_cohort_figures

    summary_csv = tmp_path / "summary.csv"
    summary_csv.write_text(
        "\n".join(
            [
                "seed_n,cohort_role,n,bin_index,max_branch,full_uncovered_measure,exact_complete,k50,k90,k99,k50_censored,k90_censored,k99_censored,a_branch1,a_last,residual_last,cumulative_arc_width_last",
                "118,complete,118,0,5,0.0,True,2,,,False,True,True,0.5,0.1,0.2,1.0",
                "118,local_mod6_control,112,0,5,0.1,False,3,,,False,True,True,0.6,0.2,0.4,1.0",
            ]
        ),
        encoding="utf-8",
    )
    checkpoints_csv = tmp_path / "checkpoints.csv"
    checkpoints_csv.write_text(
        "\n".join(
            [
                "seed_n,cohort_role,n,bin_index,max_branch,branch,cumulative_uncovered_measure,full_uncovered_measure,fill_fraction,residual_fraction,cumulative_max_gap,cumulative_component_count,exact_complete",
                "118,complete,118,0,5,1,0.5,0.0,0.0,1.0,0.2,4,True",
                "118,complete,118,0,5,5,0.1,0.0,0.8,0.2,0.1,2,True",
                "118,local_mod6_control,112,0,5,1,0.6,0.1,0.0,1.0,0.3,5,False",
                "118,local_mod6_control,112,0,5,5,0.2,0.1,0.6,0.4,0.1,2,False",
            ]
        ),
        encoding="utf-8",
    )
    generated = generate_prc_branch_fill_cohort_figures(summary_csv, checkpoints_csv, tmp_path)
    assert set(generated) == {
        "prc_branch_fill_cohort_k_depth_v0_4.png",
        "prc_branch_fill_cohort_residual_v0_4.png",
        "prc_branch_fill_cohort_checkpoint_fill_v0_4.png",
    }
    for filename in generated:
        assert (tmp_path / filename).exists()
    assert (tmp_path / "prc_branch_fill_cohort_manifest.json").exists()


def test_prc_residual_gap_figures_smoke(tmp_path):
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
    except ModuleNotFoundError:
        pytest.skip("matplotlib is not installed in this environment")

    from prime_reciprocal_projection.figures import generate_prc_residual_gap_figures

    csv_path = tmp_path / "residual.csv"
    csv_path.write_text(
        "\n".join(
            [
                "seed_n,cohort_role,n,bin_index,max_branch,full_uncovered_measure,exact_complete,residual_uncovered_measure,residual_gap_count,residual_gap_max,residual_gap_p50,residual_gap_p90,residual_gap_p99,residual_gap_entropy,residual_top_gap_share,residual_gap_near_zero_count",
                "118,complete,118,0,1000,0.0,True,0.3,3,0.2,0.1,0.2,0.2,0.8,0.66,0",
                "118,local_mod6_control,112,0,1000,0.1,False,0.4,4,0.2,0.1,0.2,0.2,0.9,0.50,1",
            ]
        ),
        encoding="utf-8",
    )
    generated = generate_prc_residual_gap_figures(csv_path, tmp_path)
    assert set(generated) == {
        "prc_branch_fill_residual_gap_count_v0_5.png",
        "prc_branch_fill_residual_gap_shape_v0_5.png",
    }
    for filename in generated:
        assert (tmp_path / filename).exists()
    assert (tmp_path / "prc_branch_fill_residual_gaps_manifest.json").exists()


def test_prc_residual_gap_pair_figures_smoke(tmp_path):
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
    except ModuleNotFoundError:
        pytest.skip("matplotlib is not installed in this environment")

    from prime_reciprocal_projection.figures import generate_prc_residual_gap_pair_figures

    delta_csv = tmp_path / "deltas.csv"
    delta_csv.write_text(
        "\n".join(
            [
                "seed_n,control_role,metric,complete_n,control_n,complete_value,control_value,delta_complete_minus_control",
                "3000,local_mod6_control,residual_top_gap_share,3000,3006,0.4,0.5,-0.1",
                "3000,local_mod6_control,residual_gap_max,3000,3006,0.1,0.2,-0.1",
                "3000,local_mod6_control,residual_gap_p90,3000,3006,0.1,0.2,-0.1",
                "3000,band_mod6_control,residual_top_gap_share,3000,3012,0.4,0.5,-0.1",
                "3000,band_mod6_control,residual_gap_max,3000,3012,0.1,0.2,-0.1",
                "3000,band_mod6_control,residual_gap_p90,3000,3012,0.1,0.2,-0.1",
                "3000,band_ordinary_control,residual_top_gap_share,3000,3013,0.4,0.5,-0.1",
                "3000,band_ordinary_control,residual_gap_max,3000,3013,0.1,0.2,-0.1",
                "3000,band_ordinary_control,residual_gap_p90,3000,3013,0.1,0.2,-0.1",
            ]
        ),
        encoding="utf-8",
    )
    summary_csv = tmp_path / "summary.csv"
    summary_csv.write_text(
        "\n".join(
            [
                "control_role,metric,eligible_pair_count,median_delta,complete_smaller_count,complete_larger_count,tie_count,complete_smaller_rate",
                "local_mod6_control,residual_top_gap_share,1,-0.1,1,0,0,1.0",
                "local_mod6_control,residual_gap_max,1,-0.1,1,0,0,1.0",
                "local_mod6_control,residual_gap_p90,1,-0.1,1,0,0,1.0",
                "local_mod6_control,residual_gap_entropy,1,0.1,0,1,0,0.0",
                "local_mod6_control,residual_gap_count,1,1,0,1,0,0.0",
                "local_mod6_control,residual_uncovered_measure,1,0.1,0,1,0,0.0",
                "band_mod6_control,residual_top_gap_share,1,-0.1,1,0,0,1.0",
                "band_mod6_control,residual_gap_max,1,-0.1,1,0,0,1.0",
                "band_mod6_control,residual_gap_p90,1,-0.1,1,0,0,1.0",
                "band_mod6_control,residual_gap_entropy,1,0.1,0,1,0,0.0",
                "band_mod6_control,residual_gap_count,1,1,0,1,0,0.0",
                "band_mod6_control,residual_uncovered_measure,1,0.1,0,1,0,0.0",
                "band_ordinary_control,residual_top_gap_share,1,-0.1,1,0,0,1.0",
                "band_ordinary_control,residual_gap_max,1,-0.1,1,0,0,1.0",
                "band_ordinary_control,residual_gap_p90,1,-0.1,1,0,0,1.0",
                "band_ordinary_control,residual_gap_entropy,1,0.1,0,1,0,0.0",
                "band_ordinary_control,residual_gap_count,1,1,0,1,0,0.0",
                "band_ordinary_control,residual_uncovered_measure,1,0.1,0,1,0,0.0",
            ]
        ),
        encoding="utf-8",
    )
    generated = generate_prc_residual_gap_pair_figures(delta_csv, summary_csv, tmp_path)
    assert set(generated) == {
        "prc_residual_gap_pair_delta_v0_6.png",
        "prc_residual_gap_effect_summary_v0_6.png",
    }
    for filename in generated:
        assert (tmp_path / filename).exists()
    assert (tmp_path / "prc_residual_gap_pairs_manifest.json").exists()


def test_prc_residual_gap_count_test_figures_smoke(tmp_path):
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
    except ModuleNotFoundError:
        pytest.skip("matplotlib is not installed in this environment")

    from prime_reciprocal_projection.figures import generate_prc_residual_gap_count_test_figures

    test_csv = tmp_path / "count_tests.csv"
    test_csv.write_text(
        "\n".join(
            [
                "control_role,metric,pair_count,non_tie_pair_count,complete_smaller_count,complete_larger_count,tie_count,complete_smaller_rate_all_pairs,complete_smaller_rate_non_tie,median_delta,mean_delta,sign_test_p_two_sided,bh_q_value,bootstrap_median_delta_ci_low,bootstrap_median_delta_ci_high,bootstrap_iterations,bootstrap_seed",
                "local_mod6_control,residual_gap_count,33,33,22,11,0,0.6666666667,0.6666666667,-11,-8.1,0.080,0.120,-30,2,10000,1729",
                "band_mod6_control,residual_gap_count,33,31,19,12,2,0.5757575758,0.6129032258,-9,-6.0,0.281,0.281,-20,4,10000,1729",
                "band_ordinary_control,residual_gap_count,33,33,26,7,0,0.7878787879,0.7878787879,-37,-26.4,0.0018,0.0054,-50,-4,10000,1729",
            ]
        ),
        encoding="utf-8",
    )
    generated = generate_prc_residual_gap_count_test_figures(test_csv, tmp_path)
    assert set(generated) == {
        "prc_residual_gap_count_test_v0_7.png",
        "prc_residual_gap_count_ci_v0_7.png",
    }
    for filename in generated:
        assert (tmp_path / filename).exists()
    assert (tmp_path / "prc_residual_gap_count_tests_manifest.json").exists()
