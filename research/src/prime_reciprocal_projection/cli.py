"""Command line entrypoint for PRP research helpers."""

from __future__ import annotations

import argparse
import math

from .cluster_scan import (
    ClusterSeedRow,
    cluster_sensitivity_table,
    discover_seed_rows,
    scan_cluster_table,
    unique_certified_values,
    write_cluster_scan_csv,
    write_cluster_sensitivity_csv,
)
from .covering_metrics import covering_table, write_covering_csv
from .covering_prime_prefix import (
    prime_prefix_profile_rows,
    write_prime_prefix_profile_csv,
)
from .covering_prime_prefix_certificates import (
    prime_prefix_certificate_rows_from_runs_csv,
    prime_prefix_certificate_summary_rows,
    prime_prefix_uncertified_mod210_audit_rows,
    prime_prefix_uncertified_mod210_class_boundary_summary_rows,
    prime_prefix_uncertified_mod210_class_detail_rows,
    prime_prefix_uncertified_mod210_class_review_rows,
    prime_prefix_uncertified_mod210_class_source_summary_rows,
    prime_prefix_uncertified_mod210_summary_rows,
    prime_prefix_uncertified_matched_pair_delta_rows,
    prime_prefix_uncertified_matched_profile_rows_from_csv,
    prime_prefix_uncertified_matched_summary_rows,
    prime_prefix_uncertified_overall_summary_rows,
    prime_prefix_uncertified_residue_rows,
    prime_prefix_uncertified_source_depth_summary_rows,
    read_prime_prefix_certificate_csv,
    read_prime_prefix_uncertified_mod210_audit_csv,
    read_prime_prefix_uncertified_mod210_class_detail_csv,
    read_prime_prefix_uncertified_mod210_class_review_csv,
    read_prime_prefix_uncertified_matched_profile_csv,
    write_prime_prefix_certificate_csv,
    write_prime_prefix_certificate_summary_csv,
    write_prime_prefix_uncertified_mod210_audit_csv,
    write_prime_prefix_uncertified_mod210_class_boundary_summary_csv,
    write_prime_prefix_uncertified_mod210_class_detail_csv,
    write_prime_prefix_uncertified_mod210_class_review_csv,
    write_prime_prefix_uncertified_mod210_class_source_summary_csv,
    write_prime_prefix_uncertified_mod210_summary_csv,
    write_prime_prefix_uncertified_matched_pair_delta_csv,
    write_prime_prefix_uncertified_matched_profile_csv,
    write_prime_prefix_uncertified_matched_summary_csv,
    write_prime_prefix_uncertified_overall_summary_csv,
    write_prime_prefix_uncertified_residue_csv,
    write_prime_prefix_uncertified_source_depth_summary_csv,
)
from .covering_prime_prefix_filtration import (
    prime_prefix_residue_filtration_tables,
    write_prime_prefix_residue_birth_samples_csv,
    write_prime_prefix_residue_filtration_csv,
)
from .covering_branch_fill import (
    branch_fill_summary_table,
    branch_fill_summary_rows,
    branch_fill_table,
    read_branch_fill_csv,
    write_branch_fill_csv,
    write_branch_fill_summary_csv,
)
from .covering_branch_fill_cohorts import (
    build_cohort_manifest_from_runs_csv,
    cohort_branch_fill_tables,
    read_cohort_manifest_csv,
    write_cohort_branch_fill_checkpoints_csv,
    write_cohort_branch_fill_summary_csv,
    write_cohort_manifest_csv,
)
from .covering_null_model import (
    branch_uniform_null_rows,
    branch_uniform_null_summary_rows,
    write_branch_uniform_null_csv,
    write_branch_uniform_null_summary_csv,
)
from .covering_residual_gaps import (
    cluster_level_gap_count_direction_rows,
    control_reuse_detail_rows,
    read_residual_gap_pair_delta_csv,
    read_residual_gap_csv,
    residual_gap_count_test_rows,
    residual_gap_effect_summary_rows,
    residual_gap_pair_delta_rows,
    residual_gap_rows_from_manifest_csv,
    residual_gap_secondary_direction_rows,
    seed_cluster_audit_rows,
    write_cluster_level_gap_count_direction_csv,
    write_control_reuse_detail_csv,
    write_residual_gap_count_test_csv,
    write_residual_gap_effect_summary_csv,
    write_residual_gap_csv,
    write_residual_gap_pair_delta_csv,
    write_residual_gap_secondary_direction_csv,
    write_seed_cluster_audit_csv,
)
from .covering_runs import (
    benchmark_prefilter_windows,
    block_scan_prefilter_runs,
    c0_autocorrelation_rows,
    complete_covering_runs_from_cluster_csv,
    exact_complete_runs_in_range,
    prefiltered_exact_complete_values_in_range,
    consecutive_runs,
    default_prefilter_validation_windows,
    length2_neighborhood_rows,
    length2_pair_forensics,
    prefilter_validation_windows,
    read_complete_covering_runs_csv,
    summarize_runs,
    transition_stats_from_runs,
    write_complete_covering_runs_csv,
    write_c0_autocorrelation_csv,
    write_fast_scan_benchmark_csv,
    write_length2_neighborhoods_csv,
    write_length2_pair_forensics_csv,
    write_prefilter_validation_windows_csv,
    write_run_transition_stats_csv,
)
from .covering import exact_is_completely_covered, exact_uncovered_measure
from .figures import (
    generate_prc_branch_fill_cohort_figures,
    generate_prc_branch_fill_figures,
    generate_prc_branch_uniform_null_figures,
    generate_prc_cluster_audit_figures,
    generate_prc_residual_gap_count_test_figures,
    generate_prc_residual_gap_pair_figures,
    generate_prc_residual_gap_figures,
    generate_prc_cluster_figures,
    generate_prc_v0_figures,
    generate_prc_window_figure,
    generate_v0_figures,
)
from .metrics import convergence_table, write_convergence_csv


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prp")
    subparsers = parser.add_subparsers(dest="command", required=True)

    figures = subparsers.add_parser("figures", help="generate v0 figures")
    figures.add_argument("--out", default="figures/v0", help="output directory")
    figures.add_argument("--n", type=int, default=100000, help="N value for generated figures")
    figures.add_argument("--bins", type=int, default=100, help="histogram bins")

    metrics = subparsers.add_parser("metrics", help="generate convergence metrics")
    metrics.add_argument(
        "--n",
        type=int,
        nargs="+",
        default=[1000, 10000, 100000, 1000000],
        help="N values",
    )
    metrics.add_argument("--out", default="data/summaries/prp_v0_summary.csv")

    covering_metrics = subparsers.add_parser(
        "covering-metrics", help="generate Prime Reciprocal Covering metrics"
    )
    covering_metrics.add_argument(
        "--n",
        type=int,
        nargs="+",
        default=None,
        help="N values",
    )
    covering_metrics.add_argument(
        "--log-grid",
        type=int,
        nargs=3,
        metavar=("START", "STOP", "COUNT"),
        help="add COUNT log-spaced integer N values from START to STOP",
    )
    covering_metrics.add_argument(
        "--window",
        type=int,
        nargs=2,
        action="append",
        metavar=("CENTER", "RADIUS"),
        help="add all integer N in [CENTER-RADIUS, CENTER+RADIUS]",
    )
    covering_metrics.add_argument("--out", default="data/summaries/prc_v0_covering.csv")

    covering_figures = subparsers.add_parser(
        "covering-figures", help="generate Prime Reciprocal Covering figures"
    )
    covering_figures.add_argument("--out", default="figures/v0", help="output directory")
    covering_figures.add_argument(
        "--n",
        type=int,
        nargs="+",
        default=[1000, 10000, 100000, 1000000],
        help="N values",
    )
    covering_figures.add_argument(
        "--log-grid",
        type=int,
        nargs=3,
        metavar=("START", "STOP", "COUNT"),
        help="add COUNT log-spaced integer N values from START to STOP",
    )

    covering_prime_prefix_profile = subparsers.add_parser(
        "covering-prime-prefix-profile",
        help="generate PRC prime-prefix residual profile diagnostics",
    )
    covering_prime_prefix_profile.add_argument(
        "--n",
        type=int,
        nargs="+",
        default=[1000, 10000, 100000, 1000000, 39069, 372759],
        help="N values",
    )
    covering_prime_prefix_profile.add_argument(
        "--out", default="data/summaries/prc_prime_prefix_profile_v0_1.csv"
    )

    covering_prime_prefix_filtration = subparsers.add_parser(
        "covering-prime-prefix-filtration",
        help="generate exact PRC prime-prefix residue-covering filtration tables",
    )
    covering_prime_prefix_filtration.add_argument("--max-k", type=int, default=7)
    covering_prime_prefix_filtration.add_argument("--birth-sample-limit", type=int, default=200)
    covering_prime_prefix_filtration.add_argument(
        "--allow-large-k",
        action="store_true",
        help="allow exploratory primorial-scale scans beyond the v0.1 max-k=7 guardrail",
    )
    covering_prime_prefix_filtration.add_argument(
        "--summary-out",
        default="data/summaries/prc_prime_prefix_residue_covering_filtration_v0_1.csv",
    )
    covering_prime_prefix_filtration.add_argument(
        "--birth-samples-out",
        default="data/summaries/prc_prime_prefix_residue_covering_birth_samples_v0_1.csv",
    )

    covering_prime_prefix_certificates = subparsers.add_parser(
        "covering-prime-prefix-certificates",
        help="connect exact C_k residue filtrations to complete-covering values",
    )
    covering_prime_prefix_certificates.add_argument(
        "--complete-source",
        default="data/summaries/prc_combined_runs_2_1000000.csv",
        help="complete-covering runs CSV",
    )
    covering_prime_prefix_certificates.add_argument("--max-k", type=int, default=7)
    covering_prime_prefix_certificates.add_argument(
        "--allow-large-k",
        action="store_true",
        help="allow exploratory primorial-scale scans beyond the v0.2 max-k=7 guardrail",
    )
    covering_prime_prefix_certificates.add_argument(
        "--out",
        default="data/summaries/prc_prime_prefix_certificate_depth_v0_2.csv",
    )
    covering_prime_prefix_certificates.add_argument(
        "--summary-out",
        default="data/summaries/prc_prime_prefix_certificate_depth_summary_v0_2.csv",
    )

    covering_prime_prefix_uncertified = subparsers.add_parser(
        "covering-prime-prefix-uncertified-residues",
        help="profile no-prefix-certificate values against the checked C_k set",
    )
    covering_prime_prefix_uncertified.add_argument(
        "--certificates",
        default="data/summaries/prc_prime_prefix_certificate_depth_k8_v0_3.csv",
        help="certificate-depth detail CSV",
    )
    covering_prime_prefix_uncertified.add_argument("--max-k", type=int, default=8)
    covering_prime_prefix_uncertified.add_argument(
        "--allow-large-k",
        action="store_true",
        help="allow exploratory primorial-scale scans beyond the v0.2 max-k=7 guardrail",
    )
    covering_prime_prefix_uncertified.add_argument(
        "--out",
        default="data/summaries/prc_prime_prefix_uncertified_residue_profile_v0_4.csv",
    )
    covering_prime_prefix_uncertified.add_argument(
        "--summary-out",
        default="data/summaries/prc_prime_prefix_uncertified_residue_summary_v0_4.csv",
    )
    covering_prime_prefix_uncertified.add_argument(
        "--mod210-out",
        default="data/summaries/prc_prime_prefix_uncertified_mod210_summary_v0_4.csv",
    )

    covering_prime_prefix_uncertified_controls = subparsers.add_parser(
        "covering-prime-prefix-uncertified-controls",
        help="compare uncertified complete rows to local non-complete controls",
    )
    covering_prime_prefix_uncertified_controls.add_argument(
        "--uncertified-profile",
        default="data/summaries/prc_prime_prefix_uncertified_residue_profile_v0_4.csv",
    )
    covering_prime_prefix_uncertified_controls.add_argument(
        "--complete-source",
        default="data/summaries/prc_combined_runs_2_1000000.csv",
    )
    covering_prime_prefix_uncertified_controls.add_argument("--start", type=int, default=2)
    covering_prime_prefix_uncertified_controls.add_argument("--stop", type=int, default=1000000)
    covering_prime_prefix_uncertified_controls.add_argument(
        "--local-radius", type=int, default=250
    )
    covering_prime_prefix_uncertified_controls.add_argument("--max-k", type=int, default=8)
    covering_prime_prefix_uncertified_controls.add_argument(
        "--allow-large-k",
        action="store_true",
        help="allow exploratory primorial-scale scans beyond the v0.2 max-k=7 guardrail",
    )
    covering_prime_prefix_uncertified_controls.add_argument(
        "--out",
        default="data/summaries/prc_prime_prefix_uncertified_control_profile_v0_5.csv",
    )
    covering_prime_prefix_uncertified_controls.add_argument(
        "--summary-out",
        default="data/summaries/prc_prime_prefix_uncertified_control_summary_v0_5.csv",
    )
    covering_prime_prefix_uncertified_controls.add_argument(
        "--pair-deltas-out",
        default="data/summaries/prc_prime_prefix_uncertified_control_pair_deltas_v0_5.csv",
    )

    covering_prime_prefix_uncertified_control_audit = subparsers.add_parser(
        "covering-prime-prefix-uncertified-control-audit",
        help="audit v0.5 uncertified complete/control profiles by mod210 and C_k source depth",
    )
    covering_prime_prefix_uncertified_control_audit.add_argument(
        "--profile",
        default="data/summaries/prc_prime_prefix_uncertified_control_profile_v0_5.csv",
        help="matched complete/control residue profile CSV",
    )
    covering_prime_prefix_uncertified_control_audit.add_argument(
        "--mod210-out",
        default="data/summaries/prc_prime_prefix_uncertified_control_mod210_audit_v0_6.csv",
    )
    covering_prime_prefix_uncertified_control_audit.add_argument(
        "--source-depth-out",
        default="data/summaries/prc_prime_prefix_uncertified_source_depth_summary_v0_6.csv",
    )

    covering_prime_prefix_uncertified_class_review = subparsers.add_parser(
        "covering-prime-prefix-uncertified-class-review",
        help="rank modulo-210 classes from the v0.6 uncertified control audit",
    )
    covering_prime_prefix_uncertified_class_review.add_argument(
        "--audit",
        default="data/summaries/prc_prime_prefix_uncertified_control_mod210_audit_v0_6.csv",
        help="modulo-210 complete/control audit CSV",
    )
    covering_prime_prefix_uncertified_class_review.add_argument(
        "--out",
        default="data/summaries/prc_prime_prefix_uncertified_mod210_class_review_v0_7.csv",
    )

    covering_prime_prefix_uncertified_class_detail = subparsers.add_parser(
        "covering-prime-prefix-uncertified-class-detail",
        help="expand selected modulo-210 classes to seed/control profile rows",
    )
    covering_prime_prefix_uncertified_class_detail.add_argument(
        "--profile",
        default="data/summaries/prc_prime_prefix_uncertified_control_profile_v0_5.csv",
        help="matched complete/control residue profile CSV",
    )
    covering_prime_prefix_uncertified_class_detail.add_argument(
        "--class-review",
        default="data/summaries/prc_prime_prefix_uncertified_mod210_class_review_v0_7.csv",
        help="ranked modulo-210 class review CSV",
    )
    covering_prime_prefix_uncertified_class_detail.add_argument(
        "--class-limit",
        type=int,
        default=8,
        help="number of top-ranked classes to expand when --mod210 is omitted",
    )
    covering_prime_prefix_uncertified_class_detail.add_argument(
        "--mod210",
        type=int,
        action="append",
        default=[],
        help="explicit modulo-210 class to expand; may be repeated",
    )
    covering_prime_prefix_uncertified_class_detail.add_argument(
        "--out",
        default="data/summaries/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.csv",
    )

    covering_prime_prefix_uncertified_class_source_summary = subparsers.add_parser(
        "covering-prime-prefix-uncertified-class-source-summary",
        help="summarize selected modulo-210 class detail rows by nearest C_k source depth",
    )
    covering_prime_prefix_uncertified_class_source_summary.add_argument(
        "--detail",
        default="data/summaries/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.csv",
        help="selected modulo-210 class detail CSV",
    )
    covering_prime_prefix_uncertified_class_source_summary.add_argument(
        "--out",
        default=(
            "data/summaries/"
            "prc_prime_prefix_uncertified_mod210_class_source_summary_v0_9.csv"
        ),
    )

    covering_prime_prefix_uncertified_class_boundary_summary = subparsers.add_parser(
        "covering-prime-prefix-uncertified-class-boundary-summary",
        help="summarize selected modulo-210 class detail rows by nearest covered mod210 anchor",
    )
    covering_prime_prefix_uncertified_class_boundary_summary.add_argument(
        "--detail",
        default="data/summaries/prc_prime_prefix_uncertified_mod210_class_detail_v0_8.csv",
        help="selected modulo-210 class detail CSV",
    )
    covering_prime_prefix_uncertified_class_boundary_summary.add_argument(
        "--out",
        default=(
            "data/summaries/"
            "prc_prime_prefix_uncertified_mod210_class_boundary_summary_v0_10.csv"
        ),
    )

    covering_window_figures = subparsers.add_parser(
        "covering-window-figure", help="generate a local PRC window figure"
    )
    covering_window_figures.add_argument("--center", type=int, required=True)
    covering_window_figures.add_argument("--radius", type=int, default=500)
    covering_window_figures.add_argument("--out", default="figures/v0", help="output directory")

    covering_branch_fill = subparsers.add_parser(
        "covering-branch-fill",
        help="generate cumulative PRC branch fill-in diagnostics",
    )
    covering_branch_fill.add_argument(
        "--n",
        type=int,
        nargs="+",
        default=[1000, 10000, 100000, 1000000],
        help="N values",
    )
    covering_branch_fill.add_argument("--max-branch", type=int, default=1000)
    covering_branch_fill.add_argument(
        "--out", default="data/summaries/prc_branch_fill_v0_3.csv"
    )

    covering_branch_fill_summary = subparsers.add_parser(
        "covering-branch-fill-summary",
        help="generate PRC branch fill-in threshold summaries",
    )
    covering_branch_fill_summary.add_argument(
        "--n",
        type=int,
        nargs="+",
        default=[1000, 10000, 100000, 1000000],
        help="N values",
    )
    covering_branch_fill_summary.add_argument(
        "--input",
        help="optional long branch-fill CSV to summarize instead of recomputing",
    )
    covering_branch_fill_summary.add_argument("--max-branch", type=int, default=1000)
    covering_branch_fill_summary.add_argument(
        "--out", default="data/summaries/prc_branch_fill_summary_v0_3.csv"
    )

    covering_branch_fill_figures = subparsers.add_parser(
        "covering-branch-fill-figures",
        help="generate PRC branch fill-in figures from a CSV",
    )
    covering_branch_fill_figures.add_argument(
        "--input", default="data/summaries/prc_branch_fill_v0_3.csv"
    )
    covering_branch_fill_figures.add_argument("--out", default="figures/v0")

    covering_branch_fill_cohorts = subparsers.add_parser(
        "covering-branch-fill-cohorts",
        help="generate deterministic PRC branch fill-in comparison cohorts",
    )
    covering_branch_fill_cohorts.add_argument(
        "--complete-source", default="data/summaries/prc_combined_runs_2_1000000.csv"
    )
    covering_branch_fill_cohorts.add_argument("--start", type=int, default=1000)
    covering_branch_fill_cohorts.add_argument("--stop", type=int, default=1000000)
    covering_branch_fill_cohorts.add_argument("--bin-count", type=int, default=12)
    covering_branch_fill_cohorts.add_argument("--max-per-bin", type=int, default=3)
    covering_branch_fill_cohorts.add_argument("--local-radius", type=int, default=250)
    covering_branch_fill_cohorts.add_argument(
        "--out", default="data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv"
    )

    covering_branch_fill_cohort_summary = subparsers.add_parser(
        "covering-branch-fill-cohort-summary",
        help="generate branch fill-in summary/checkpoint rows for comparison cohorts",
    )
    covering_branch_fill_cohort_summary.add_argument(
        "--manifest", default="data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv"
    )
    covering_branch_fill_cohort_summary.add_argument("--max-branch", type=int, default=1000)
    covering_branch_fill_cohort_summary.add_argument(
        "--summary-out", default="data/summaries/prc_branch_fill_cohort_summary_v0_4.csv"
    )
    covering_branch_fill_cohort_summary.add_argument(
        "--checkpoint-out",
        default="data/summaries/prc_branch_fill_cohort_checkpoints_v0_4.csv",
    )

    covering_branch_fill_cohort_figures = subparsers.add_parser(
        "covering-branch-fill-cohort-figures",
        help="generate PRC branch fill-in cohort comparison figures",
    )
    covering_branch_fill_cohort_figures.add_argument(
        "--summary", default="data/summaries/prc_branch_fill_cohort_summary_v0_4.csv"
    )
    covering_branch_fill_cohort_figures.add_argument(
        "--checkpoints",
        default="data/summaries/prc_branch_fill_cohort_checkpoints_v0_4.csv",
    )
    covering_branch_fill_cohort_figures.add_argument("--out", default="figures/v0")

    covering_branch_fill_residual_gaps = subparsers.add_parser(
        "covering-branch-fill-residual-gaps",
        help="generate residual gap metrics after a fixed PRC branch prefix",
    )
    covering_branch_fill_residual_gaps.add_argument(
        "--manifest", default="data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv"
    )
    covering_branch_fill_residual_gaps.add_argument(
        "--summary", default="data/summaries/prc_branch_fill_cohort_summary_v0_4.csv"
    )
    covering_branch_fill_residual_gaps.add_argument("--max-branch", type=int, default=1000)
    covering_branch_fill_residual_gaps.add_argument(
        "--near-zero-threshold", type=float, default=1e-6
    )
    covering_branch_fill_residual_gaps.add_argument(
        "--out", default="data/summaries/prc_branch_fill_residual_gaps_v0_5.csv"
    )
    covering_branch_fill_residual_gaps.add_argument("--figures-out", default="figures/v0")
    covering_branch_fill_residual_gaps.add_argument(
        "--skip-figures",
        action="store_true",
        help="write only the residual gap CSV",
    )

    covering_branch_fill_residual_gap_pairs = subparsers.add_parser(
        "covering-branch-fill-residual-gap-pairs",
        help="generate paired complete-control residual gap dominance diagnostics",
    )
    covering_branch_fill_residual_gap_pairs.add_argument(
        "--input", default="data/summaries/prc_branch_fill_residual_gaps_v0_5.csv"
    )
    covering_branch_fill_residual_gap_pairs.add_argument(
        "--delta-out", default="data/summaries/prc_residual_gap_pair_deltas_v0_6.csv"
    )
    covering_branch_fill_residual_gap_pairs.add_argument(
        "--summary-out", default="data/summaries/prc_residual_gap_effect_summary_v0_6.csv"
    )
    covering_branch_fill_residual_gap_pairs.add_argument("--figures-out", default="figures/v0")
    covering_branch_fill_residual_gap_pairs.add_argument(
        "--skip-figures",
        action="store_true",
        help="write only the v0.6 paired CSVs",
    )

    covering_branch_fill_residual_gap_count_test = subparsers.add_parser(
        "covering-branch-fill-residual-gap-count-test",
        help="generate v0.7 residual gap count sign-test diagnostics",
    )
    covering_branch_fill_residual_gap_count_test.add_argument(
        "--input", default="data/summaries/prc_residual_gap_pair_deltas_v0_6.csv"
    )
    covering_branch_fill_residual_gap_count_test.add_argument(
        "--out", default="data/summaries/prc_residual_gap_count_tests_v0_7.csv"
    )
    covering_branch_fill_residual_gap_count_test.add_argument(
        "--secondary-out",
        default="data/summaries/prc_residual_gap_secondary_direction_v0_7.csv",
    )
    covering_branch_fill_residual_gap_count_test.add_argument(
        "--bootstrap-iterations", type=int, default=10000
    )
    covering_branch_fill_residual_gap_count_test.add_argument(
        "--bootstrap-seed", type=int, default=1729
    )
    covering_branch_fill_residual_gap_count_test.add_argument("--figures-out", default="figures/v0")
    covering_branch_fill_residual_gap_count_test.add_argument(
        "--skip-figures",
        action="store_true",
        help="write only the v0.7 CSVs",
    )

    covering_branch_fill_cluster_audit = subparsers.add_parser(
        "covering-branch-fill-cluster-audit",
        help="generate v0.8 cluster-robust residual gap count audit",
    )
    covering_branch_fill_cluster_audit.add_argument(
        "--manifest", default="data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv"
    )
    covering_branch_fill_cluster_audit.add_argument(
        "--deltas", default="data/summaries/prc_residual_gap_pair_deltas_v0_6.csv"
    )
    covering_branch_fill_cluster_audit.add_argument("--metric", default="residual_gap_count")
    covering_branch_fill_cluster_audit.add_argument("--cluster-radius", type=int, default=250)
    covering_branch_fill_cluster_audit.add_argument(
        "--cluster-out", default="data/summaries/prc_seed_cluster_audit_v0_8.csv"
    )
    covering_branch_fill_cluster_audit.add_argument(
        "--direction-out",
        default="data/summaries/prc_cluster_level_gap_count_direction_v0_8.csv",
    )
    covering_branch_fill_cluster_audit.add_argument(
        "--reuse-out", default="data/summaries/prc_control_reuse_detail_v0_8.csv"
    )
    covering_branch_fill_cluster_audit.add_argument("--figures-out", default="figures/v0")
    covering_branch_fill_cluster_audit.add_argument(
        "--skip-figures",
        action="store_true",
        help="write only the v0.8 CSVs",
    )

    covering_branch_fill_null_model = subparsers.add_parser(
        "covering-branch-fill-null-model",
        help="generate v0.9 branch-prefix null model comparison diagnostics",
    )
    covering_branch_fill_null_model.add_argument(
        "--manifest", default="data/summaries/prc_branch_fill_cohort_manifest_v0_4.csv"
    )
    covering_branch_fill_null_model.add_argument(
        "--observed", default="data/summaries/prc_branch_fill_residual_gaps_v0_5.csv"
    )
    covering_branch_fill_null_model.add_argument(
        "--model", choices=["branch_uniform"], default="branch_uniform"
    )
    covering_branch_fill_null_model.add_argument("--max-branch", type=int, default=1000)
    covering_branch_fill_null_model.add_argument("--iterations", type=int, default=1000)
    covering_branch_fill_null_model.add_argument("--seed", type=int, default=1729)
    covering_branch_fill_null_model.add_argument(
        "--out", default="data/summaries/prc_branch_uniform_null_v0_9.csv"
    )
    covering_branch_fill_null_model.add_argument(
        "--summary-out",
        default="data/summaries/prc_branch_uniform_null_summary_v0_9.csv",
    )
    covering_branch_fill_null_model.add_argument("--figures-out", default="figures/v0")
    covering_branch_fill_null_model.add_argument(
        "--skip-figures",
        action="store_true",
        help="write only the v0.9 CSVs",
    )

    covering_certify = subparsers.add_parser(
        "covering-certify", help="check exact rational PRC coverage"
    )
    covering_certify.add_argument("--n", type=int, nargs="+", required=True, help="N values")

    covering_cluster_scan = subparsers.add_parser(
        "covering-cluster-scan",
        help="run a two-stage PRC cluster scan and write D_R summaries",
    )
    covering_cluster_scan.add_argument("--start", type=int, default=1000)
    covering_cluster_scan.add_argument("--stop", type=int, default=1000000)
    covering_cluster_scan.add_argument("--count", type=int, default=500)
    covering_cluster_scan.add_argument("--ratio-threshold", type=float, default=0.05)
    covering_cluster_scan.add_argument("--radius", type=int, default=250)
    covering_cluster_scan.add_argument(
        "--center",
        type=int,
        action="append",
        default=[],
        help="manually add a local window center; may be repeated",
    )
    covering_cluster_scan.add_argument(
        "--out", default="data/summaries/prc_cluster_scan_v0.csv"
    )

    covering_cluster_figures = subparsers.add_parser(
        "covering-cluster-figures",
        help="generate D_R figures from a PRC cluster scan CSV",
    )
    covering_cluster_figures.add_argument(
        "--input", default="data/summaries/prc_cluster_scan_v0.csv"
    )
    covering_cluster_figures.add_argument("--out", default="figures/v0")

    covering_cluster_sensitivity = subparsers.add_parser(
        "covering-cluster-sensitivity",
        help="compare D_R across coarse seed thresholds and radii",
    )
    covering_cluster_sensitivity.add_argument("--start", type=int, default=1000)
    covering_cluster_sensitivity.add_argument("--stop", type=int, default=1000000)
    covering_cluster_sensitivity.add_argument("--count", type=int, default=500)
    covering_cluster_sensitivity.add_argument(
        "--ratio-threshold",
        type=float,
        nargs="+",
        default=[0.0, 0.02, 0.05],
    )
    covering_cluster_sensitivity.add_argument(
        "--radius",
        type=int,
        nargs="+",
        default=[100, 250, 500],
    )
    covering_cluster_sensitivity.add_argument(
        "--out", default="data/summaries/prc_cluster_sensitivity_v0.csv"
    )

    covering_runs = subparsers.add_parser(
        "covering-runs",
        help="summarize consecutive exact complete-covering runs from a cluster scan CSV",
    )
    covering_runs.add_argument("--input", default="data/summaries/prc_cluster_scan_v0.csv")
    covering_runs.add_argument("--out", default="data/summaries/prc_complete_runs_v0.csv")

    covering_run_scan = subparsers.add_parser(
        "covering-run-scan",
        help="exact-check a contiguous N range and write consecutive complete-covering runs",
    )
    covering_run_scan.add_argument("--start", type=int, required=True)
    covering_run_scan.add_argument("--stop", type=int, required=True)
    covering_run_scan.add_argument("--out", default="data/summaries/prc_exact_runs.csv")

    covering_run_prefilter_scan = subparsers.add_parser(
        "covering-run-prefilter-scan",
        help=(
            "numeric-prefilter a contiguous N range, exact-check candidates, "
            "and write consecutive complete-covering runs"
        ),
    )
    covering_run_prefilter_scan.add_argument("--start", type=int, required=True)
    covering_run_prefilter_scan.add_argument("--stop", type=int, required=True)
    covering_run_prefilter_scan.add_argument("--tolerance", type=float, default=1e-12)
    covering_run_prefilter_scan.add_argument("--workers", type=int, default=1)
    covering_run_prefilter_scan.add_argument("--chunk-size", type=int, default=100000)
    covering_run_prefilter_scan.add_argument(
        "--engine", choices=["python", "numpy"], default="python"
    )
    covering_run_prefilter_scan.add_argument(
        "--allow-unguaranteed-prefilter",
        action="store_true",
        help="allow exploratory prefilter scans outside the documented v0 guarantee range",
    )
    covering_run_prefilter_scan.add_argument(
        "--out", default="data/summaries/prc_prefilter_exact_runs.csv"
    )

    covering_run_block_scan = subparsers.add_parser(
        "covering-run-block-scan",
        help="run a resumable block PRC complete-covering scan",
    )
    covering_run_block_scan.add_argument("--start", type=int, required=True)
    covering_run_block_scan.add_argument("--stop", type=int, required=True)
    covering_run_block_scan.add_argument("--block-size", type=int, required=True)
    covering_run_block_scan.add_argument("--tolerance", type=float, default=1e-12)
    covering_run_block_scan.add_argument("--workers", type=int, default=1)
    covering_run_block_scan.add_argument("--chunk-size", type=int, default=100000)
    covering_run_block_scan.add_argument("--engine", choices=["python", "numpy"], default="numpy")
    covering_run_block_scan.add_argument("--out-dir", required=True)
    covering_run_block_scan.add_argument("--combined-out", required=True)
    covering_run_block_scan.add_argument("--summary-out", required=True)
    covering_run_block_scan.add_argument("--resume", action="store_true")
    covering_run_block_scan.add_argument(
        "--allow-unguaranteed-prefilter",
        action="store_true",
        help="allow exploratory block scans outside the documented guarantee range",
    )

    covering_run_benchmark = subparsers.add_parser(
        "covering-run-benchmark",
        help="benchmark PRC prefilter engines on one or more windows",
    )
    covering_run_benchmark.add_argument(
        "--window",
        nargs=3,
        action="append",
        metavar=("START", "STOP", "LABEL"),
        required=True,
        help="benchmark one inclusive window; may be repeated",
    )
    covering_run_benchmark.add_argument(
        "--engine",
        choices=["python", "numpy"],
        nargs="+",
        default=["python", "numpy"],
    )
    covering_run_benchmark.add_argument("--tolerance", type=float, default=1e-12)
    covering_run_benchmark.add_argument("--chunk-size", type=int, default=100000)
    covering_run_benchmark.add_argument("--out", required=True)
    covering_run_benchmark.add_argument(
        "--append",
        action="store_true",
        help="append rows to an existing benchmark CSV without writing a duplicate header",
    )
    covering_run_benchmark.add_argument(
        "--allow-unguaranteed-prefilter",
        action="store_true",
        help="allow exploratory benchmark windows outside the documented guarantee range",
    )

    covering_run_forensics = subparsers.add_parser(
        "covering-run-forensics",
        help="generate PRC consecutive-run forensic CSVs from combined run rows",
    )
    covering_run_forensics.add_argument(
        "--input", default="data/summaries/prc_combined_runs_2_1000000.csv"
    )
    covering_run_forensics.add_argument("--start", type=int, default=2)
    covering_run_forensics.add_argument("--stop", type=int, default=1000000)
    covering_run_forensics.add_argument(
        "--transition-out", default="data/summaries/prc_run_transition_stats_2_1000000.csv"
    )
    covering_run_forensics.add_argument(
        "--pair-out", default="data/summaries/prc_length2_pair_forensics_2_1000000.csv"
    )
    covering_run_forensics.add_argument(
        "--neighborhood-out",
        default="data/summaries/prc_length2_neighborhoods_2_1000000.csv",
    )
    covering_run_forensics.add_argument(
        "--validation-out",
        default="data/summaries/prc_prefilter_validation_windows.csv",
    )

    covering_run_autocorrelation = subparsers.add_parser(
        "covering-run-autocorrelation",
        help="generate lagged exact C0 autocorrelation diagnostics from run rows",
    )
    covering_run_autocorrelation.add_argument(
        "--input", default="data/summaries/prc_combined_runs_2_1000000.csv"
    )
    covering_run_autocorrelation.add_argument("--start", type=int, default=2)
    covering_run_autocorrelation.add_argument("--stop", type=int, default=1000000)
    covering_run_autocorrelation.add_argument("--max-lag", type=int, default=210)
    covering_run_autocorrelation.add_argument(
        "--out", default="data/summaries/prc_c0_autocorrelation_2_1000000.csv"
    )

    args = parser.parse_args(argv)
    if args.command == "figures":
        generate_v0_figures(args.out, n=args.n, bins=args.bins)
        return 0
    if args.command == "metrics":
        rows = convergence_table(args.n)
        write_convergence_csv(rows, args.out)
        return 0
    if args.command == "covering-metrics":
        ns = _combined_ns(
            args.n,
            args.log_grid,
            args.window,
            default_ns=[1000, 10000, 100000, 1000000],
        )
        rows = covering_table(ns)
        write_covering_csv(rows, args.out)
        return 0
    if args.command == "covering-figures":
        ns = sorted({*args.n, *_log_grid(*args.log_grid)}) if args.log_grid else sorted(set(args.n))
        generate_prc_v0_figures(args.out, ns=ns)
        return 0
    if args.command == "covering-prime-prefix-profile":
        rows = prime_prefix_profile_rows(args.n)
        write_prime_prefix_profile_csv(rows, args.out)
        print(
            "covering-prime-prefix-profile: "
            f"n_values={len(set(args.n))}, rows={len(rows)}, out={args.out}"
        )
        return 0
    if args.command == "covering-prime-prefix-filtration":
        summary_rows, birth_rows = prime_prefix_residue_filtration_tables(
            max_k=args.max_k,
            birth_sample_limit=args.birth_sample_limit,
            allow_large_k=args.allow_large_k,
        )
        write_prime_prefix_residue_filtration_csv(summary_rows, args.summary_out)
        write_prime_prefix_residue_birth_samples_csv(birth_rows, args.birth_samples_out)
        print(
            "covering-prime-prefix-filtration: "
            f"summary_rows={len(summary_rows)}, birth_sample_rows={len(birth_rows)}, "
            f"summary_out={args.summary_out}, birth_samples_out={args.birth_samples_out}"
        )
        return 0
    if args.command == "covering-prime-prefix-certificates":
        rows = prime_prefix_certificate_rows_from_runs_csv(
            args.complete_source,
            max_k=args.max_k,
            allow_large_k=args.allow_large_k,
        )
        summary_rows = prime_prefix_certificate_summary_rows(rows)
        write_prime_prefix_certificate_csv(rows, args.out)
        write_prime_prefix_certificate_summary_csv(summary_rows, args.summary_out)
        print(
            "covering-prime-prefix-certificates: "
            f"rows={len(rows)}, summary_rows={len(summary_rows)}, "
            f"out={args.out}, summary_out={args.summary_out}"
        )
        return 0
    if args.command == "covering-prime-prefix-uncertified-residues":
        certificate_rows = read_prime_prefix_certificate_csv(args.certificates)
        rows = prime_prefix_uncertified_residue_rows(
            certificate_rows,
            max_k=args.max_k,
            allow_large_k=args.allow_large_k,
        )
        overall_rows = prime_prefix_uncertified_overall_summary_rows(rows)
        mod210_rows = prime_prefix_uncertified_mod210_summary_rows(rows)
        write_prime_prefix_uncertified_residue_csv(rows, args.out)
        write_prime_prefix_uncertified_overall_summary_csv(overall_rows, args.summary_out)
        write_prime_prefix_uncertified_mod210_summary_csv(mod210_rows, args.mod210_out)
        print(
            "covering-prime-prefix-uncertified-residues: "
            f"rows={len(rows)}, mod210_rows={len(mod210_rows)}, "
            f"out={args.out}, summary_out={args.summary_out}, mod210_out={args.mod210_out}"
        )
        return 0
    if args.command == "covering-prime-prefix-uncertified-controls":
        rows = prime_prefix_uncertified_matched_profile_rows_from_csv(
            args.uncertified_profile,
            args.complete_source,
            start=args.start,
            stop=args.stop,
            local_radius=args.local_radius,
            max_k=args.max_k,
            allow_large_k=args.allow_large_k,
        )
        summary_rows = prime_prefix_uncertified_matched_summary_rows(rows)
        delta_rows = prime_prefix_uncertified_matched_pair_delta_rows(rows)
        write_prime_prefix_uncertified_matched_profile_csv(rows, args.out)
        write_prime_prefix_uncertified_matched_summary_csv(summary_rows, args.summary_out)
        write_prime_prefix_uncertified_matched_pair_delta_csv(
            delta_rows, args.pair_deltas_out
        )
        print(
            "covering-prime-prefix-uncertified-controls: "
            f"rows={len(rows)}, summary_rows={len(summary_rows)}, "
            f"pair_delta_rows={len(delta_rows)}, out={args.out}, "
            f"summary_out={args.summary_out}, pair_deltas_out={args.pair_deltas_out}"
        )
        return 0
    if args.command == "covering-prime-prefix-uncertified-control-audit":
        rows = read_prime_prefix_uncertified_matched_profile_csv(args.profile)
        mod210_rows = prime_prefix_uncertified_mod210_audit_rows(rows)
        source_depth_rows = prime_prefix_uncertified_source_depth_summary_rows(rows)
        write_prime_prefix_uncertified_mod210_audit_csv(mod210_rows, args.mod210_out)
        write_prime_prefix_uncertified_source_depth_summary_csv(
            source_depth_rows,
            args.source_depth_out,
        )
        print(
            "covering-prime-prefix-uncertified-control-audit: "
            f"profile_rows={len(rows)}, mod210_rows={len(mod210_rows)}, "
            f"source_depth_rows={len(source_depth_rows)}, "
            f"mod210_out={args.mod210_out}, source_depth_out={args.source_depth_out}"
        )
        return 0
    if args.command == "covering-prime-prefix-uncertified-class-review":
        rows = prime_prefix_uncertified_mod210_class_review_rows(
            read_prime_prefix_uncertified_mod210_audit_csv(args.audit)
        )
        write_prime_prefix_uncertified_mod210_class_review_csv(rows, args.out)
        print(
            "covering-prime-prefix-uncertified-class-review: "
            f"rows={len(rows)}, out={args.out}"
        )
        return 0
    if args.command == "covering-prime-prefix-uncertified-class-detail":
        rows = prime_prefix_uncertified_mod210_class_detail_rows(
            read_prime_prefix_uncertified_matched_profile_csv(args.profile),
            read_prime_prefix_uncertified_mod210_class_review_csv(args.class_review),
            class_limit=args.class_limit,
            selected_mod210=args.mod210 or None,
        )
        write_prime_prefix_uncertified_mod210_class_detail_csv(rows, args.out)
        print(
            "covering-prime-prefix-uncertified-class-detail: "
            f"rows={len(rows)}, out={args.out}"
        )
        return 0
    if args.command == "covering-prime-prefix-uncertified-class-source-summary":
        rows = prime_prefix_uncertified_mod210_class_source_summary_rows(
            read_prime_prefix_uncertified_mod210_class_detail_csv(args.detail)
        )
        write_prime_prefix_uncertified_mod210_class_source_summary_csv(rows, args.out)
        print(
            "covering-prime-prefix-uncertified-class-source-summary: "
            f"rows={len(rows)}, out={args.out}"
        )
        return 0
    if args.command == "covering-prime-prefix-uncertified-class-boundary-summary":
        rows = prime_prefix_uncertified_mod210_class_boundary_summary_rows(
            read_prime_prefix_uncertified_mod210_class_detail_csv(args.detail)
        )
        write_prime_prefix_uncertified_mod210_class_boundary_summary_csv(rows, args.out)
        print(
            "covering-prime-prefix-uncertified-class-boundary-summary: "
            f"rows={len(rows)}, out={args.out}"
        )
        return 0
    if args.command == "covering-window-figure":
        generate_prc_window_figure(args.out, center=args.center, radius=args.radius)
        return 0
    if args.command == "covering-branch-fill":
        rows = branch_fill_table(sorted(set(args.n)), max_branch=args.max_branch)
        write_branch_fill_csv(rows, args.out)
        return 0
    if args.command == "covering-branch-fill-summary":
        rows = (
            branch_fill_summary_table(read_branch_fill_csv(args.input))
            if args.input
            else branch_fill_summary_rows(sorted(set(args.n)), max_branch=args.max_branch)
        )
        write_branch_fill_summary_csv(rows, args.out)
        return 0
    if args.command == "covering-branch-fill-figures":
        generate_prc_branch_fill_figures(args.input, args.out)
        return 0
    if args.command == "covering-branch-fill-cohorts":
        rows = build_cohort_manifest_from_runs_csv(
            args.complete_source,
            start=args.start,
            stop=args.stop,
            bin_count=args.bin_count,
            max_per_bin=args.max_per_bin,
            local_radius=args.local_radius,
        )
        write_cohort_manifest_csv(rows, args.out)
        eligible_seeds = len({row.seed_n for row in rows if row.eligible})
        excluded_seeds = len({row.seed_n for row in rows if not row.eligible})
        print(
            "covering-branch-fill-cohorts: "
            f"rows={len(rows)}, eligible_seeds={eligible_seeds}, "
            f"excluded_seeds={excluded_seeds}"
        )
        return 0
    if args.command == "covering-branch-fill-cohort-summary":
        summary_rows, checkpoint_rows = cohort_branch_fill_tables(
            read_cohort_manifest_csv(args.manifest),
            max_branch=args.max_branch,
        )
        write_cohort_branch_fill_summary_csv(summary_rows, args.summary_out)
        write_cohort_branch_fill_checkpoints_csv(checkpoint_rows, args.checkpoint_out)
        print(
            "covering-branch-fill-cohort-summary: "
            f"summary_rows={len(summary_rows)}, checkpoint_rows={len(checkpoint_rows)}"
        )
        return 0
    if args.command == "covering-branch-fill-cohort-figures":
        generated = generate_prc_branch_fill_cohort_figures(
            args.summary,
            args.checkpoints,
            args.out,
        )
        print(f"covering-branch-fill-cohort-figures: files={len(generated)}")
        return 0
    if args.command == "covering-branch-fill-residual-gaps":
        rows = residual_gap_rows_from_manifest_csv(
            args.manifest,
            summary_csv=args.summary,
            max_branch=args.max_branch,
            near_zero_threshold=args.near_zero_threshold,
        )
        write_residual_gap_csv(rows, args.out)
        generated = [] if args.skip_figures else generate_prc_residual_gap_figures(args.out, args.figures_out)
        print(
            "covering-branch-fill-residual-gaps: "
            f"rows={len(rows)}, figures={len(generated)}, out={args.out}"
        )
        return 0
    if args.command == "covering-branch-fill-residual-gap-pairs":
        delta_rows = residual_gap_pair_delta_rows(read_residual_gap_csv(args.input))
        summary_rows = residual_gap_effect_summary_rows(delta_rows)
        write_residual_gap_pair_delta_csv(delta_rows, args.delta_out)
        write_residual_gap_effect_summary_csv(summary_rows, args.summary_out)
        generated = (
            []
            if args.skip_figures
            else generate_prc_residual_gap_pair_figures(
                args.delta_out,
                args.summary_out,
                args.figures_out,
            )
        )
        print(
            "covering-branch-fill-residual-gap-pairs: "
            f"delta_rows={len(delta_rows)}, summary_rows={len(summary_rows)}, "
            f"figures={len(generated)}"
        )
        return 0
    if args.command == "covering-branch-fill-residual-gap-count-test":
        delta_rows = read_residual_gap_pair_delta_csv(args.input)
        test_rows = residual_gap_count_test_rows(
            delta_rows,
            bootstrap_iterations=args.bootstrap_iterations,
            bootstrap_seed=args.bootstrap_seed,
        )
        secondary_rows = residual_gap_secondary_direction_rows(delta_rows)
        write_residual_gap_count_test_csv(test_rows, args.out)
        write_residual_gap_secondary_direction_csv(secondary_rows, args.secondary_out)
        generated = (
            []
            if args.skip_figures
            else generate_prc_residual_gap_count_test_figures(
                args.out,
                args.figures_out,
            )
        )
        print(
            "covering-branch-fill-residual-gap-count-test: "
            f"test_rows={len(test_rows)}, secondary_rows={len(secondary_rows)}, "
            f"figures={len(generated)}"
        )
        return 0
    if args.command == "covering-branch-fill-cluster-audit":
        delta_rows = read_residual_gap_pair_delta_csv(args.deltas)
        cluster_rows = seed_cluster_audit_rows(
            read_cohort_manifest_csv(args.manifest),
            delta_rows,
            metric=args.metric,
            cluster_radius=args.cluster_radius,
        )
        direction_rows = cluster_level_gap_count_direction_rows(cluster_rows, metric=args.metric)
        reuse_rows = control_reuse_detail_rows(delta_rows, cluster_rows, metric=args.metric)
        write_seed_cluster_audit_csv(cluster_rows, args.cluster_out)
        write_cluster_level_gap_count_direction_csv(direction_rows, args.direction_out)
        write_control_reuse_detail_csv(reuse_rows, args.reuse_out)
        generated = (
            []
            if args.skip_figures
            else generate_prc_cluster_audit_figures(
                args.direction_out,
                args.reuse_out,
                args.figures_out,
            )
        )
        print(
            "covering-branch-fill-cluster-audit: "
            f"cluster_rows={len(cluster_rows)}, direction_rows={len(direction_rows)}, "
            f"reuse_rows={len(reuse_rows)}, figures={len(generated)}"
        )
        return 0
    if args.command == "covering-branch-fill-null-model":
        rows = branch_uniform_null_rows(
            read_cohort_manifest_csv(args.manifest),
            read_residual_gap_csv(args.observed),
            model=args.model,
            max_branch=args.max_branch,
            iterations=args.iterations,
            seed=args.seed,
        )
        summary_rows = branch_uniform_null_summary_rows(rows)
        write_branch_uniform_null_csv(rows, args.out)
        write_branch_uniform_null_summary_csv(summary_rows, args.summary_out)
        generated = (
            []
            if args.skip_figures
            else generate_prc_branch_uniform_null_figures(
                args.out,
                args.summary_out,
                args.figures_out,
            )
        )
        print(
            "covering-branch-fill-null-model: "
            f"rows={len(rows)}, summary_rows={len(summary_rows)}, figures={len(generated)}"
        )
        return 0
    if args.command == "covering-certify":
        for n in args.n:
            measure = exact_uncovered_measure(n)
            covered = exact_is_completely_covered(n)
            print(f"N={n}, exact_complete={covered}, exact_uncovered_measure={measure}")
        return 0
    if args.command == "covering-cluster-scan":
        seeds = discover_seed_rows(
            start=args.start,
            stop=args.stop,
            count=args.count,
            ratio_threshold=args.ratio_threshold,
        )
        centers_by_n: dict[int, ClusterSeedRow | int] = {seed.n: seed for seed in seeds}
        for center in args.center:
            centers_by_n.setdefault(center, center)
        centers = [centers_by_n[n] for n in sorted(centers_by_n)]
        rows = scan_cluster_table(centers, radius=args.radius)
        write_cluster_scan_csv(rows, args.out)
        exact_memberships = sum(row.exact_complete_count for row in rows)
        exact_unique = len(unique_certified_values(rows))
        print(
            "covering-cluster-scan: "
            f"seeds={len(seeds)}, centers={len(centers)}, "
            f"exact_complete_memberships={exact_memberships}, "
            f"unique_exact_complete={exact_unique}"
        )
        return 0
    if args.command == "covering-cluster-figures":
        generate_prc_cluster_figures(args.input, args.out)
        return 0
    if args.command == "covering-cluster-sensitivity":
        rows = cluster_sensitivity_table(
            start=args.start,
            stop=args.stop,
            count=args.count,
            ratio_thresholds=args.ratio_threshold,
            radii=args.radius,
        )
        write_cluster_sensitivity_csv(rows, args.out)
        print(
            "covering-cluster-sensitivity: "
            f"rows={len(rows)}, thresholds={len(set(args.ratio_threshold))}, "
            f"radii={len(set(args.radius))}"
        )
        return 0
    if args.command == "covering-runs":
        runs = complete_covering_runs_from_cluster_csv(args.input)
        write_complete_covering_runs_csv(runs, args.out)
        summary = summarize_runs(runs)
        print(
            "covering-runs: "
            f"values={summary.value_count}, runs={summary.run_count}, "
            f"longest={summary.longest_run_length}"
        )
        return 0
    if args.command == "covering-run-scan":
        runs = exact_complete_runs_in_range(args.start, args.stop)
        write_complete_covering_runs_csv(runs, args.out)
        summary = summarize_runs(runs)
        print(
            "covering-run-scan: "
            f"values={summary.value_count}, runs={summary.run_count}, "
            f"longest={summary.longest_run_length}"
        )
        return 0
    if args.command == "covering-run-prefilter-scan":
        result = prefiltered_exact_complete_values_in_range(
            args.start,
            args.stop,
            tolerance=args.tolerance,
            workers=args.workers,
            chunk_size=args.chunk_size,
            require_guarantee=not args.allow_unguaranteed_prefilter,
            engine=args.engine,
        )
        runs = consecutive_runs(result.values)
        write_complete_covering_runs_csv(runs, args.out)
        summary = summarize_runs(runs)
        print(
            "covering-run-prefilter-scan: "
            f"checked={result.checked_count}, "
            f"numeric_candidates={result.numeric_candidate_count}, "
            f"exact_values={result.exact_complete_count}, "
            f"runs={summary.run_count}, longest={summary.longest_run_length}"
        )
        return 0
    if args.command == "covering-run-block-scan":
        result = block_scan_prefilter_runs(
            args.start,
            args.stop,
            block_size=args.block_size,
            out_dir=args.out_dir,
            combined_out=args.combined_out,
            summary_out=args.summary_out,
            tolerance=args.tolerance,
            workers=args.workers,
            chunk_size=args.chunk_size,
            require_guarantee=not args.allow_unguaranteed_prefilter,
            engine=args.engine,
            resume=args.resume,
        )
        print(
            "covering-run-block-scan: "
            f"blocks={result.block_count}, computed={result.computed_block_count}, "
            f"resumed={result.resumed_block_count}, checked={result.checked_count}, "
            f"exact_values={result.exact_complete_count}, runs={result.run_count}, "
            f"longest={result.longest_run_length}"
        )
        return 0
    if args.command == "covering-run-benchmark":
        windows = [(int(start), int(stop), label) for start, stop, label in args.window]
        rows = benchmark_prefilter_windows(
            windows,
            engines=args.engine,
            tolerance=args.tolerance,
            chunk_size=args.chunk_size,
            require_guarantee=not args.allow_unguaranteed_prefilter,
        )
        write_fast_scan_benchmark_csv(rows, args.out, append=args.append)
        print(f"covering-run-benchmark: rows={len(rows)}, out={args.out}")
        return 0
    if args.command == "covering-run-forensics":
        runs = read_complete_covering_runs_csv(args.input)
        transition = transition_stats_from_runs(runs, start=args.start, stop=args.stop)
        pair_rows = length2_pair_forensics(runs)
        neighborhood_rows = length2_neighborhood_rows(runs)
        validation_rows = prefilter_validation_windows(
            default_prefilter_validation_windows(runs, start=args.start, stop=args.stop)
        )
        write_run_transition_stats_csv(transition, args.transition_out)
        write_length2_pair_forensics_csv(pair_rows, args.pair_out)
        write_length2_neighborhoods_csv(neighborhood_rows, args.neighborhood_out)
        write_prefilter_validation_windows_csv(validation_rows, args.validation_out)
        print(
            "covering-run-forensics: "
            f"complete={transition.complete_count}, "
            f"length2={transition.length2_run_count}, "
            f"length3={transition.length3_start_count}, "
            f"validation_windows={len(validation_rows)}"
        )
        return 0
    if args.command == "covering-run-autocorrelation":
        runs = read_complete_covering_runs_csv(args.input)
        rows = c0_autocorrelation_rows(
            runs,
            start=args.start,
            stop=args.stop,
            max_lag=args.max_lag,
        )
        write_c0_autocorrelation_csv(rows, args.out)
        print(
            "covering-run-autocorrelation: "
            f"rows={len(rows)}, max_lag={args.max_lag}, out={args.out}"
        )
        return 0
    parser.error(f"unknown command: {args.command}")
    return 2


def _log_grid(start: int, stop: int, count: int) -> list[int]:
    if start < 2:
        raise ValueError("START must be >= 2")
    if stop < start:
        raise ValueError("STOP must be >= START")
    if count < 2:
        raise ValueError("COUNT must be >= 2")
    log_start = math.log(start)
    log_stop = math.log(stop)
    values = {
        int(round(math.exp(log_start + (log_stop - log_start) * index / (count - 1))))
        for index in range(count)
    }
    return sorted(values)


def _window_grid(center: int, radius: int) -> list[int]:
    if center < 2:
        raise ValueError("CENTER must be >= 2")
    if radius < 0:
        raise ValueError("RADIUS must be >= 0")
    return list(range(max(2, center - radius), center + radius + 1))


def _combined_ns(
    ns: list[int] | None,
    log_grid: list[int] | None,
    windows: list[list[int]] | None,
    *,
    default_ns: list[int] | None = None,
) -> list[int]:
    if ns is None:
        values = set(default_ns or []) if not log_grid and not windows else set()
    else:
        values = set(ns)
    if log_grid:
        values.update(_log_grid(*log_grid))
    for center, radius in windows or []:
        values.update(_window_grid(center, radius))
    return sorted(values)


if __name__ == "__main__":
    raise SystemExit(main())
