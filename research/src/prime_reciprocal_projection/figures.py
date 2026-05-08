"""Figure generation for PRP v0."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import csv
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

from .branches import branch_decomposition, limit_branch_mass
from .cluster_scan import ClusterScanRow, read_cluster_scan_csv, unique_certified_values
from .covering_branch_fill import BranchFillRow, read_branch_fill_csv
from .covering_metrics import covering_table
from .experiments import histogram_masses, limit_bin_masses
from .fourier import fourier_coefficient, limit_fourier_coefficient
from .projection import fractional_parts


def _require_matplotlib():
    cache_dir = Path(".matplotlib-cache").resolve()
    cache_dir.mkdir(exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cache_dir))
    os.environ.setdefault("MPLBACKEND", "Agg")
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as exc:
        raise RuntimeError("matplotlib is required for figure generation") from exc
    return plt


def _git_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None
    return result.stdout.strip()


def write_manifest(
    output_dir: Path,
    *,
    command: str,
    generated_files: list[str],
    name: str = "Prime Reciprocal Projection",
    filename: str = "manifest.json",
) -> None:
    """Write a reproducibility manifest for generated figures."""
    payload = {
        "name": name,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "git_sha": _git_sha(),
        "command": command,
        "generated_files": generated_files,
    }
    (output_dir / filename).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def distribution_figure(n: int, output_dir: Path, *, bins: int = 100) -> str:
    """Generate histogram-vs-limit distribution figure."""
    plt = _require_matplotlib()
    values = fractional_parts(n)
    edges, empirical = histogram_masses(values, bins=bins)
    _, limit = limit_bin_masses(bins=bins)
    centers = [(edges[index] + edges[index + 1]) / 2 for index in range(bins)]
    width = 1 / bins

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(centers, empirical, width=width, alpha=0.55, label="empirical bin mass")
    ax.plot(centers, limit, color="black", linewidth=1.6, label="limit rho bin mass")
    ax.set_title(f"PRP distribution, N={n}")
    ax.set_xlabel("x = {N/p}")
    ax.set_ylabel("bin mass")
    ax.legend()
    ax.grid(alpha=0.25)
    output_path = output_dir / f"distribution_N{n}_bins{bins}.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def branch_figure(n: int, output_dir: Path, *, max_k: int = 20) -> str:
    """Generate exact branch mass vs limiting branch mass figure."""
    plt = _require_matplotlib()
    branches = branch_decomposition(n, max_k=max_k)
    observed = {branch.k: branch.mass for branch in branches}
    ks = list(range(1, max_k + 1))
    observed_values = [observed.get(k, 0.0) for k in ks]
    limit_values = [limit_branch_mass(k) for k in ks]

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(ks, observed_values, marker="o", label="empirical branch mass")
    ax.plot(ks, limit_values, marker="x", label="limit 1/(k(k+1))")
    ax.set_title(f"PRP branch decomposition, N={n}")
    ax.set_xlabel("branch k = floor(N/p)")
    ax.set_ylabel("mass")
    ax.legend()
    ax.grid(alpha=0.25)
    output_path = output_dir / f"branches_N{n}_k{max_k}.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def fourier_figure(n: int, output_dir: Path, *, max_m: int = 20) -> str:
    """Generate Fourier residual figure."""
    plt = _require_matplotlib()
    modes = list(range(0, max_m + 1))
    residuals = [
        abs(fourier_coefficient(n, m) - limit_fourier_coefficient(m, samples=256, k_max=500))
        for m in modes
    ]

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(modes, residuals, marker="o")
    ax.set_title(f"PRP Fourier residuals, N={n}")
    ax.set_xlabel("mode m")
    ax.set_ylabel("|hat_mu_N(m) - hat_rho(m)|")
    ax.grid(alpha=0.25)
    output_path = output_dir / f"fourier_N{n}_m{max_m}.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def generate_v0_figures(output_dir: str | Path, *, n: int = 100000, bins: int = 100) -> list[str]:
    """Generate the v0 figure set and manifest."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    generated = [
        distribution_figure(n, output_path, bins=bins),
        branch_figure(n, output_path),
        fourier_figure(n, output_path),
    ]
    write_manifest(
        output_path,
        command=(
            "python -m prime_reciprocal_projection.cli "
            f"figures --out {output_path} --n {n} --bins {bins}"
        ),
        generated_files=generated,
    )
    return generated


def covering_trend_figure(ns: list[int], output_dir: Path) -> str:
    """Generate PRC uncovered-measure trend figure."""
    plt = _require_matplotlib()
    rows = covering_table(ns)
    x_values = [row.n for row in rows]
    uncovered = [row.uncovered_measure for row in rows]
    scaled = [row.uncovered_measure_times_log_n for row in rows]
    baseline = [row.random_arc_baseline for row in rows]

    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(9, 7.2), sharex=True)
    ax_top.plot(x_values, uncovered, marker="o", label="A(N)")
    ax_top.plot(x_values, baseline, marker="x", label="random arc baseline")
    ax_top.set_xscale("log")
    ax_top.set_ylabel("uncovered measure")
    ax_top.set_title("PRC uncovered measure")
    ax_top.legend()
    ax_top.grid(alpha=0.25)

    ax_bottom.plot(x_values, scaled, marker="o", color="black", label="A(N) log N")
    ax_bottom.set_xscale("log")
    ax_bottom.set_xlabel("N")
    ax_bottom.set_ylabel("A(N) log N")
    ax_bottom.legend()
    ax_bottom.grid(alpha=0.25)

    output_path = output_dir / f"prc_covering_trend_N{x_values[0]}_{x_values[-1]}.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def covering_gap_fill_figure(ns: list[int], output_dir: Path) -> str:
    """Generate PRC branch-1 gap fill-in figure."""
    plt = _require_matplotlib()
    rows = covering_table(ns)
    x_values = [row.n for row in rows]
    ratios = [row.gap_fill_ratio if row.gap_fill_ratio is not None else 0.0 for row in rows]
    drops = [row.gap_fill_drop for row in rows]
    components = [row.uncovered_component_count for row in rows]

    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(9, 7.2), sharex=True)
    ax_top.plot(x_values, ratios, marker="o", label="G(N)/G1(N)")
    ax_top.set_xscale("log")
    ax_top.set_ylabel("gap fill ratio")
    ax_top.set_title("PRC branch-1 gap fill-in")
    ax_top.legend()
    ax_top.grid(alpha=0.25)

    ax_bottom.plot(x_values, drops, marker="o", label="G1(N)-G(N)")
    ax_bottom_twin = ax_bottom.twinx()
    ax_bottom_twin.plot(
        x_values,
        components,
        marker="x",
        color="tab:orange",
        label="uncovered components",
    )
    ax_bottom.set_xscale("log")
    ax_bottom.set_xlabel("N")
    ax_bottom.set_ylabel("gap drop")
    ax_bottom_twin.set_ylabel("component count")
    lines, labels = ax_bottom.get_legend_handles_labels()
    twin_lines, twin_labels = ax_bottom_twin.get_legend_handles_labels()
    ax_bottom.legend(lines + twin_lines, labels + twin_labels, loc="best")
    ax_bottom.grid(alpha=0.25)

    output_path = output_dir / f"prc_gap_fill_N{x_values[0]}_{x_values[-1]}.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def covering_branch1_gap_figure(ns: list[int], output_dir: Path) -> str:
    """Generate branch-1 G1 versus transformed prime-gap estimate figure."""
    plt = _require_matplotlib()
    rows = covering_table(ns)
    estimates = [row.branch1_exposed_gap_estimate for row in rows]
    observed = [row.branch1_max_uncovered_gap for row in rows]
    colors = [row.n for row in rows]
    max_value = max([*estimates, *observed, 0.0])

    fig, ax = plt.subplots(figsize=(7.2, 6.4))
    scatter = ax.scatter(estimates, observed, c=colors, cmap="viridis", s=38)
    ax.plot([0, max_value], [0, max_value], color="black", linewidth=1.0, label="y=x")
    ax.set_xlabel("branch-1 exposed gap estimate")
    ax.set_ylabel("observed G1(N)")
    ax.set_title("PRC branch-1 gap check")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.colorbar(scatter, ax=ax, label="N")
    output_path = output_dir / f"prc_branch1_gap_N{rows[0].n}_{rows[-1].n}.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def generate_prc_v0_figures(
    output_dir: str | Path,
    *,
    ns: list[int] | None = None,
) -> list[str]:
    """Generate the PRC v0 figure set and manifest."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    grid = ns or [1000, 10000, 100000, 1000000]
    generated = [
        covering_trend_figure(grid, output_path),
        covering_gap_fill_figure(grid, output_path),
        covering_branch1_gap_figure(grid, output_path),
    ]
    write_manifest(
        output_path,
        command="python -m prime_reciprocal_projection.cli covering-figures",
        generated_files=generated,
        name="Prime Reciprocal Covering",
        filename="prc_manifest.json",
    )
    return generated


def generate_prc_window_figure(
    output_dir: str | Path,
    *,
    center: int,
    radius: int = 500,
) -> list[str]:
    """Generate a local PRC window figure around one center N."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    ns = list(range(max(2, center - radius), center + radius + 1))
    generated = [covering_local_window_figure(ns, output_path, center=center)]
    write_manifest(
        output_path,
        command=(
            "python -m prime_reciprocal_projection.cli "
            f"covering-window-figure --center {center} --radius {radius}"
        ),
        generated_files=generated,
        name="Prime Reciprocal Covering local window",
        filename=f"prc_window_N{ns[0]}_{ns[-1]}_manifest.json",
    )
    return generated


def generate_prc_branch_fill_figures(
    input_csv: str | Path,
    output_dir: str | Path,
) -> list[str]:
    """Generate PRC branch fill-in figures from a canonical branch-fill CSV."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    rows = read_branch_fill_csv(input_csv)
    if not rows:
        raise ValueError("branch fill CSV must contain at least one row")
    generated = [
        branch_fill_residual_figure(rows, output_path),
        branch_fill_fraction_figure(rows, output_path),
    ]
    write_manifest(
        output_path,
        command=(
            "python -m prime_reciprocal_projection.cli "
            f"covering-branch-fill-figures --input {input_csv} --out {output_path}"
        ),
        generated_files=generated,
        name="Prime Reciprocal Covering branch fill",
        filename="prc_branch_fill_manifest.json",
    )
    return generated


def branch_fill_residual_figure(rows: list[BranchFillRow], output_dir: Path) -> str:
    """Generate residual fraction by cumulative branch checkpoint."""
    plt = _require_matplotlib()
    grouped = _branch_fill_groups(rows)
    fig, ax = plt.subplots(figsize=(9, 5.8))
    for n, n_rows in grouped.items():
        checkpoints = _checkpoint_rows(n_rows)
        ax.plot(
            [row.branch for row in checkpoints],
            [row.residual_fraction if row.residual_fraction is not None else 0.0 for row in checkpoints],
            marker="o",
            linewidth=1.2,
            label=f"N={n}",
        )
    ax.set_xscale("log")
    ax.set_xlabel("cumulative branch K")
    ax.set_ylabel("R_K = residual fraction")
    ax.set_title("PRC branch fill-in residual")
    ax.set_ylim(-0.03, 1.03)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    output_path = output_dir / "prc_branch_fill_residual_v0_3.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def branch_fill_fraction_figure(rows: list[BranchFillRow], output_dir: Path) -> str:
    """Generate filled fraction by cumulative branch checkpoint."""
    plt = _require_matplotlib()
    grouped = _branch_fill_groups(rows)
    fig, ax = plt.subplots(figsize=(9, 5.8))
    for n, n_rows in grouped.items():
        checkpoints = _checkpoint_rows(n_rows)
        ax.plot(
            [row.branch for row in checkpoints],
            [row.fill_fraction if row.fill_fraction is not None else 0.0 for row in checkpoints],
            marker="o",
            linewidth=1.2,
            label=f"N={n}",
        )
    ax.set_xscale("log")
    ax.set_xlabel("cumulative branch K")
    ax.set_ylabel("F_K = filled fraction")
    ax.set_title("PRC branch fill-in progress")
    ax.set_ylim(-0.03, 1.03)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    output_path = output_dir / "prc_branch_fill_fraction_v0_3.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def _branch_fill_groups(rows: list[BranchFillRow]) -> dict[int, list[BranchFillRow]]:
    grouped: dict[int, list[BranchFillRow]] = {}
    for row in rows:
        grouped.setdefault(row.n, []).append(row)
    for n_rows in grouped.values():
        n_rows.sort(key=lambda row: row.branch)
    return dict(sorted(grouped.items()))


def _checkpoint_rows(rows: list[BranchFillRow]) -> list[BranchFillRow]:
    if not rows:
        return []
    checkpoints = {branch for branch in range(1, min(20, rows[-1].branch) + 1)}
    checkpoints.update({30, 50, 100, 200, 500, 1000})
    checkpoints.add(rows[-1].branch)
    by_branch = {row.branch: row for row in rows}
    return [by_branch[branch] for branch in sorted(checkpoints) if branch in by_branch]


def generate_prc_branch_fill_cohort_figures(
    summary_csv: str | Path,
    checkpoints_csv: str | Path,
    output_dir: str | Path,
) -> list[str]:
    """Generate PRC v0.4 cohort comparison figures."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    summary_rows = _read_csv_rows(summary_csv)
    checkpoint_rows = _read_csv_rows(checkpoints_csv)
    generated = [
        cohort_k_depth_figure(summary_rows, output_path),
        cohort_residual_figure(summary_rows, output_path),
        cohort_checkpoint_fill_figure(checkpoint_rows, output_path),
    ]
    write_manifest(
        output_path,
        command=(
            "python -m prime_reciprocal_projection.cli "
            f"covering-branch-fill-cohort-figures --summary {summary_csv} "
            f"--checkpoints {checkpoints_csv} --out {output_path}"
        ),
        generated_files=generated,
        name="Prime Reciprocal Covering branch fill cohort comparison",
        filename="prc_branch_fill_cohort_manifest.json",
    )
    return generated


def cohort_k_depth_figure(rows: list[dict[str, str]], output_dir: Path) -> str:
    """Generate median K-depth comparison by cohort role."""
    if not rows:
        raise ValueError("rows must not be empty")
    plt = _require_matplotlib()
    roles = _cohort_roles(rows)
    thresholds = ["k50", "k90", "k99"]
    x_base = list(range(len(roles)))
    width = 0.24

    fig, ax = plt.subplots(figsize=(10, 5.8))
    for offset, threshold in enumerate(thresholds):
        values = []
        for role in roles:
            role_values = [_optional_float(row[threshold]) for row in rows if row["cohort_role"] == role]
            numeric_values = [value for value in role_values if value is not None]
            values.append(median(numeric_values) if numeric_values else 0.0)
        xs = [x + (offset - 1) * width for x in x_base]
        ax.bar(xs, values, width=width, label=threshold.upper())
    ax.set_xticks(x_base, roles, rotation=18, ha="right")
    ax.set_ylabel("median uncensored K")
    ax.set_title("PRC branch fill-in depth by cohort")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    output_path = output_dir / "prc_branch_fill_cohort_k_depth_v0_4.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def cohort_residual_figure(rows: list[dict[str, str]], output_dir: Path) -> str:
    """Generate residual-at-last comparison by cohort role."""
    if not rows:
        raise ValueError("rows must not be empty")
    plt = _require_matplotlib()
    roles = _cohort_roles(rows)
    data = [
        [
            value
            for value in (_optional_float(row["residual_last"]) for row in rows if row["cohort_role"] == role)
            if value is not None
        ]
        for role in roles
    ]
    fig, ax = plt.subplots(figsize=(9, 5.6))
    ax.boxplot(data, tick_labels=roles, showmeans=True)
    ax.set_xticklabels(roles, rotation=18, ha="right")
    ax.set_ylabel("residual fraction at K=1000")
    ax.set_title("PRC residual after cumulative branches <=1000")
    ax.grid(axis="y", alpha=0.25)
    output_path = output_dir / "prc_branch_fill_cohort_residual_v0_4.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def cohort_checkpoint_fill_figure(rows: list[dict[str, str]], output_dir: Path) -> str:
    """Generate median fill curve at checkpoint branches by cohort role."""
    if not rows:
        raise ValueError("rows must not be empty")
    plt = _require_matplotlib()
    roles = _cohort_roles(rows)
    branches = sorted({int(row["branch"]) for row in rows})
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    for role in roles:
        medians = []
        for branch in branches:
            values = [
                value
                for value in (
                    _optional_float(row["fill_fraction"])
                    for row in rows
                    if row["cohort_role"] == role and int(row["branch"]) == branch
                )
                if value is not None
            ]
            medians.append(median(values) if values else 0.0)
        ax.plot(branches, medians, marker="o", linewidth=1.3, label=role)
    ax.set_xscale("log")
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlabel("cumulative branch K")
    ax.set_ylabel("median filled fraction")
    ax.set_title("PRC cohort median branch fill-in curve")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    output_path = output_dir / "prc_branch_fill_cohort_checkpoint_fill_v0_4.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def generate_prc_residual_gap_figures(
    input_csv: str | Path,
    output_dir: str | Path,
) -> list[str]:
    """Generate PRC v0.5 residual gap comparison figures."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    rows = _read_csv_rows(input_csv)
    generated = [
        residual_gap_count_figure(rows, output_path),
        residual_gap_shape_figure(rows, output_path),
    ]
    write_manifest(
        output_path,
        command=(
            "python -m prime_reciprocal_projection.cli "
            f"covering-branch-fill-residual-gaps --out {input_csv} --figures-out {output_path}"
        ),
        generated_files=generated,
        name="Prime Reciprocal Covering residual gap comparison",
        filename="prc_branch_fill_residual_gaps_manifest.json",
    )
    return generated


def residual_gap_count_figure(rows: list[dict[str, str]], output_dir: Path) -> str:
    """Generate residual gap count comparison by cohort role."""
    if not rows:
        raise ValueError("rows must not be empty")
    plt = _require_matplotlib()
    roles = _cohort_roles(rows)
    data = [
        [int(row["residual_gap_count"]) for row in rows if row["cohort_role"] == role]
        for role in roles
    ]
    fig, ax = plt.subplots(figsize=(9, 5.6))
    ax.boxplot(data, tick_labels=roles, showmeans=True)
    ax.set_xticklabels(roles, rotation=18, ha="right")
    ax.set_ylabel("residual gap count at K=1000")
    ax.set_title("PRC residual component count after branch prefix")
    ax.grid(axis="y", alpha=0.25)
    output_path = output_dir / "prc_branch_fill_residual_gap_count_v0_5.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def residual_gap_shape_figure(rows: list[dict[str, str]], output_dir: Path) -> str:
    """Generate residual gap shape comparison by cohort role."""
    if not rows:
        raise ValueError("rows must not be empty")
    plt = _require_matplotlib()
    roles = _cohort_roles(rows)
    entropy_data = [
        [
            value
            for value in (
                _optional_float(row["residual_gap_entropy"])
                for row in rows
                if row["cohort_role"] == role
            )
            if value is not None
        ]
        for role in roles
    ]
    share_data = [
        [
            value
            for value in (
                _optional_float(row["residual_top_gap_share"])
                for row in rows
                if row["cohort_role"] == role
            )
            if value is not None
        ]
        for role in roles
    ]
    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(9, 8.2), sharex=True)
    ax_top.boxplot(entropy_data, tick_labels=roles, showmeans=True)
    ax_top.set_xticks(range(1, len(roles) + 1), roles, rotation=18, ha="right")
    ax_top.set_ylabel("normalized gap entropy")
    ax_top.set_title("PRC residual gap shape after branch prefix")
    ax_top.grid(axis="y", alpha=0.25)

    ax_bottom.boxplot(share_data, tick_labels=roles, showmeans=True)
    ax_bottom.set_xticks(range(1, len(roles) + 1), roles, rotation=18, ha="right")
    ax_bottom.set_ylabel("top gap share")
    ax_bottom.grid(axis="y", alpha=0.25)
    output_path = output_dir / "prc_branch_fill_residual_gap_shape_v0_5.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def generate_prc_residual_gap_pair_figures(
    delta_csv: str | Path,
    summary_csv: str | Path,
    output_dir: str | Path,
) -> list[str]:
    """Generate PRC v0.6 residual gap paired comparison figures."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    delta_rows = _read_csv_rows(delta_csv)
    summary_rows = _read_csv_rows(summary_csv)
    generated = [
        residual_gap_pair_delta_figure(delta_rows, output_path),
        residual_gap_effect_summary_figure(summary_rows, output_path),
    ]
    write_manifest(
        output_path,
        command=(
            "python -m prime_reciprocal_projection.cli "
            f"covering-branch-fill-residual-gap-pairs --delta-out {delta_csv} "
            f"--summary-out {summary_csv} --figures-out {output_path}"
        ),
        generated_files=generated,
        name="Prime Reciprocal Covering residual gap paired diagnostics",
        filename="prc_residual_gap_pairs_manifest.json",
    )
    return generated


def residual_gap_pair_delta_figure(rows: list[dict[str, str]], output_dir: Path) -> str:
    """Generate paired delta distributions for the primary residual metrics."""
    if not rows:
        raise ValueError("rows must not be empty")
    plt = _require_matplotlib()
    metrics = ["residual_top_gap_share", "residual_gap_max", "residual_gap_p90"]
    control_roles = _control_roles(rows)
    fig, axes = plt.subplots(len(metrics), 1, figsize=(10, 9.4), sharex=True)
    for ax, metric in zip(axes, metrics):
        data = [
            [
                float(row["delta_complete_minus_control"])
                for row in rows
                if row["metric"] == metric and row["control_role"] == role
            ]
            for role in control_roles
        ]
        ax.boxplot(data, tick_labels=control_roles, showmeans=True)
        ax.axhline(0.0, color="black", linewidth=1.0, alpha=0.55)
        ax.set_ylabel(metric.replace("residual_", ""))
        ax.grid(axis="y", alpha=0.25)
    axes[-1].set_xticks(range(1, len(control_roles) + 1), control_roles, rotation=18, ha="right")
    axes[0].set_title("PRC paired delta: complete minus control")
    output_path = output_dir / "prc_residual_gap_pair_delta_v0_6.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def residual_gap_effect_summary_figure(rows: list[dict[str, str]], output_dir: Path) -> str:
    """Generate complete-smaller rate summary by metric and control role."""
    if not rows:
        raise ValueError("rows must not be empty")
    plt = _require_matplotlib()
    metrics = [
        "residual_top_gap_share",
        "residual_gap_max",
        "residual_gap_p90",
        "residual_gap_entropy",
        "residual_gap_count",
        "residual_uncovered_measure",
    ]
    control_roles = _control_roles(rows)
    fig, ax = plt.subplots(figsize=(10, 6.2))
    width = 0.25
    x_values = list(range(len(metrics)))
    for role_index, role in enumerate(control_roles):
        rates = [
            next(
                (
                    float(row["complete_smaller_rate"])
                    for row in rows
                    if row["metric"] == metric and row["control_role"] == role
                ),
                0.0,
            )
            for metric in metrics
        ]
        xs = [x + (role_index - 1) * width for x in x_values]
        ax.bar(xs, rates, width=width, label=role)
    ax.axhline(0.5, color="black", linewidth=1.0, alpha=0.55)
    ax.set_xticks(x_values, [metric.replace("residual_", "") for metric in metrics], rotation=25, ha="right")
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("complete smaller rate")
    ax.set_title("PRC residual gap paired direction")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    output_path = output_dir / "prc_residual_gap_effect_summary_v0_6.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _cohort_roles(rows: list[dict[str, str]]) -> list[str]:
    preferred = ["complete", "local_mod6_control", "band_mod6_control", "band_ordinary_control"]
    present = {row["cohort_role"] for row in rows}
    return [role for role in preferred if role in present] + sorted(present - set(preferred))


def _control_roles(rows: list[dict[str, str]]) -> list[str]:
    preferred = ["local_mod6_control", "band_mod6_control", "band_ordinary_control"]
    present = {row["control_role"] for row in rows}
    return [role for role in preferred if role in present] + sorted(present - set(preferred))


def _optional_float(value: str) -> float | None:
    return None if value == "" else float(value)


def generate_prc_cluster_figures(
    input_csv: str | Path,
    output_dir: str | Path,
) -> list[str]:
    """Generate PRC cluster-density figures from a cluster scan CSV."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    rows = read_cluster_scan_csv(input_csv)
    generated = [
        cluster_density_figure(rows, output_path),
        cluster_efficiency_figure(rows, output_path),
    ]
    write_manifest(
        output_path,
        command=(
            "python -m prime_reciprocal_projection.cli "
            f"covering-cluster-figures --input {input_csv} --out {output_path}"
        ),
        generated_files=generated,
        name="Prime Reciprocal Covering cluster scan",
        filename="prc_cluster_manifest.json",
    )
    return generated


def cluster_density_figure(rows: list[ClusterScanRow], output_dir: Path) -> str:
    """Generate a D_R cluster-density overview figure."""
    if not rows:
        raise ValueError("rows must not be empty")
    plt = _require_matplotlib()
    centers = [row.center for row in rows]
    counts = [row.exact_complete_count for row in rows]
    unique_count = len(unique_certified_values(rows))
    memberships = sum(counts)
    known_rows = [row for row in rows if row.seed_baseline_ratio is not None]
    missing_rows = [row for row in rows if row.seed_baseline_ratio is None]

    fig, ax = plt.subplots(figsize=(10, 5.8))
    scatter = None
    if known_rows:
        scatter = ax.scatter(
            [row.center for row in known_rows],
            [row.d_r for row in known_rows],
            c=[row.seed_baseline_ratio for row in known_rows],
            s=[40 + 10 * row.exact_complete_count for row in known_rows],
            cmap="magma_r",
            edgecolors="black",
            linewidths=0.4,
            alpha=0.88,
            label="coarse seed center",
        )
    if missing_rows:
        ax.scatter(
            [row.center for row in missing_rows],
            [row.d_r for row in missing_rows],
            s=[40 + 10 * row.exact_complete_count for row in missing_rows],
            color="lightgray",
            edgecolors="black",
            linewidths=0.4,
            marker="D",
            alpha=0.88,
            label="manual center",
        )
    ax.set_xscale("log")
    ax.set_xlabel("cluster center N")
    ax.set_ylabel("D_R")
    ax.set_title(
        "PRC local complete-covering density "
        f"(memberships={memberships}, unique={unique_count})"
    )
    ax.grid(alpha=0.25)
    if scatter is not None:
        fig.colorbar(scatter, ax=ax, label="seed A(N) / random baseline")
    if missing_rows:
        ax.legend()
    output_path = output_dir / f"prc_cluster_density_N{min(centers)}_{max(centers)}.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def cluster_efficiency_figure(rows: list[ClusterScanRow], output_dir: Path) -> str:
    """Generate a D_R versus local-window efficiency figure."""
    if not rows:
        raise ValueError("rows must not be empty")
    plt = _require_matplotlib()
    densities = [row.d_r for row in rows]
    median_ratios = [row.median_baseline_ratio for row in rows]
    max_measures = [row.max_uncovered_measure for row in rows]
    centers = [row.center for row in rows]
    counts = [row.exact_complete_count for row in rows]

    fig, ax = plt.subplots(figsize=(8.6, 6.2))
    scatter = ax.scatter(
        median_ratios,
        densities,
        c=max_measures,
        s=[45 + 10 * count for count in counts],
        cmap="viridis",
        edgecolors="black",
        linewidths=0.4,
        alpha=0.88,
    )
    for center, x_value, y_value in zip(centers, median_ratios, densities):
        if y_value >= max(densities) * 0.94:
            ax.annotate(str(center), (x_value, y_value), xytext=(5, 5), textcoords="offset points")
    ax.set_xlabel("median A(N) / random baseline in window")
    ax.set_ylabel("D_R")
    ax.set_title("PRC cluster density versus local uncovered mass")
    ax.grid(alpha=0.25)
    fig.colorbar(scatter, ax=ax, label="max A(N) in window")
    output_path = output_dir / f"prc_cluster_efficiency_N{min(centers)}_{max(centers)}.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name


def covering_local_window_figure(ns: list[int], output_dir: Path, *, center: int) -> str:
    """Generate a focused local-window PRC diagnostic figure."""
    plt = _require_matplotlib()
    rows = covering_table(ns)
    x_values = [row.n for row in rows]
    uncovered = [row.uncovered_measure for row in rows]
    baseline_ratio = [
        row.uncovered_measure / row.random_arc_baseline if row.random_arc_baseline > 0 else 0.0
        for row in rows
    ]
    gaps = [row.max_uncovered_gap for row in rows]
    ratios = [row.gap_fill_ratio if row.gap_fill_ratio is not None else 0.0 for row in rows]
    components = [row.uncovered_component_count for row in rows]

    fig, axes = plt.subplots(3, 1, figsize=(10, 9.2), sharex=True)
    axes[0].plot(x_values, uncovered, linewidth=1.2, label="A(N)")
    axes[0].axvline(center, color="black", linewidth=1.0, alpha=0.6)
    axes[0].set_ylabel("A(N)")
    axes[0].set_title(f"PRC local window around N={center}")
    axes[0].legend()
    axes[0].grid(alpha=0.25)

    axes[1].plot(x_values, baseline_ratio, linewidth=1.2, color="tab:green", label="A/baseline")
    axes[1].axhline(1.0, color="black", linewidth=1.0, alpha=0.45)
    axes[1].axvline(center, color="black", linewidth=1.0, alpha=0.6)
    axes[1].set_ylabel("A / baseline")
    axes[1].legend()
    axes[1].grid(alpha=0.25)

    axes[2].plot(x_values, gaps, linewidth=1.1, label="G(N)")
    axes_twin = axes[2].twinx()
    axes_twin.plot(
        x_values,
        ratios,
        linewidth=1.1,
        color="tab:orange",
        label="G/G1",
    )
    axes[2].scatter(
        x_values,
        [0.0 for _ in x_values],
        s=[4 + min(component, 2000) / 40 for component in components],
        color="tab:purple",
        alpha=0.25,
        label="component count scale",
    )
    axes[2].axvline(center, color="black", linewidth=1.0, alpha=0.6)
    axes[2].set_xlabel("N")
    axes[2].set_ylabel("G(N)")
    axes_twin.set_ylabel("G/G1")
    lines, labels = axes[2].get_legend_handles_labels()
    twin_lines, twin_labels = axes_twin.get_legend_handles_labels()
    axes[2].legend(lines + twin_lines, labels + twin_labels, loc="best")
    axes[2].grid(alpha=0.25)

    output_path = output_dir / f"prc_window_N{x_values[0]}_{x_values[-1]}.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path.name
