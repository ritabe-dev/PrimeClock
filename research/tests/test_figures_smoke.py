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
