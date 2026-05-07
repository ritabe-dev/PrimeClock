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
from .covering_runs import (
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
    write_length2_neighborhoods_csv,
    write_length2_pair_forensics_csv,
    write_prefilter_validation_windows_csv,
    write_run_transition_stats_csv,
)
from .covering import exact_is_completely_covered, exact_uncovered_measure
from .figures import (
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

    covering_window_figures = subparsers.add_parser(
        "covering-window-figure", help="generate a local PRC window figure"
    )
    covering_window_figures.add_argument("--center", type=int, required=True)
    covering_window_figures.add_argument("--radius", type=int, default=500)
    covering_window_figures.add_argument("--out", default="figures/v0", help="output directory")

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
        "--allow-unguaranteed-prefilter",
        action="store_true",
        help="allow exploratory prefilter scans outside the documented v0 guarantee range",
    )
    covering_run_prefilter_scan.add_argument(
        "--out", default="data/summaries/prc_prefilter_exact_runs.csv"
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
    if args.command == "covering-window-figure":
        generate_prc_window_figure(args.out, center=args.center, radius=args.radius)
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
