#!/usr/bin/env python3
"""Generate source-only PRC v2.4 transition taxonomy figures."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Iterable

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = str(
        Path(tempfile.gettempdir()) / "primeclock-matplotlib"
    )

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_FIGURE_DIR = EXPERIMENT_DIR / "figures" / "v2_4"
TAXONOMY_LABELS = ("miss", "trim", "split", "partial_close", "close")

if str(EXPERIMENT_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_DIR))

from v2_4_transition_pilot import (  # noqa: E402
    DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV,
    DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV,
    TRANSITION_CLOSE,
    TRANSITION_MISS,
    TRANSITION_PARTIAL_CLOSE,
    TRANSITION_SPLIT,
    TRANSITION_TRIM,
    TransitionProbeRow,
    canonical_transition_summary,
    classify_canonical_transition,
    component_transition_stats,
    read_b5_gap_close_transition_pilot_csv,
)
from v2_4_residual_genealogy import (  # noqa: E402
    BirthResidualGenealogyRow,
    read_birth_residual_genealogy_csv,
)
from v2_4_angle_aperture_diagnostics import (  # noqa: E402
    read_birth_potential_correlation_csv,
    read_birth_potential_score_csv,
    read_incremental_grid_phase_csv,
    read_k2_gap_width_bias_csv,
    read_lineage_measure_bias_csv,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate source-only PRC v2.4 transition figures.",
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_FIGURE_DIR,
        type=Path,
        help="output figure directory",
    )
    args = parser.parse_args()

    generated = generate_figures(args.out)
    for path in generated:
        print(path)
    return 0


def generate_figures(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    datasets = load_datasets()
    genealogy_rows = read_birth_residual_genealogy_csv()
    generated = [
        plot_taxonomy_counts(datasets, output_dir),
        plot_component_delta_counts(datasets, output_dir),
        plot_b5_to_b6_genealogy_flow(datasets, output_dir),
        plot_remainder_taxonomy_heatmaps(datasets, output_dir),
        plot_birth_residual_genealogy(genealogy_rows, output_dir),
        plot_origin_zero_diagnostics(genealogy_rows, output_dir),
        plot_k2_gap_width_bias(output_dir),
        plot_lineage_measure_bias(output_dir),
        plot_incremental_grid_phase_histograms(output_dir),
        plot_birth_potential_score(output_dir),
    ]
    manifest_path = write_manifest(output_dir, generated, datasets, genealogy_rows)
    return [*generated, manifest_path]


def load_datasets() -> dict[str, list[TransitionProbeRow]]:
    return {
        "B5 pilot": read_b5_gap_close_transition_pilot_csv(),
        "B5->B6 full": read_b5_gap_close_transition_pilot_csv(
            DEFAULT_B5_TO_B6_FULL_TRANSITION_CSV
        ),
        "B6->B7 full": read_b5_gap_close_transition_pilot_csv(
            DEFAULT_B6_TO_B7_FULL_TRANSITION_CSV
        ),
    }


def plot_taxonomy_counts(
    datasets: dict[str, list[TransitionProbeRow]],
    output_dir: Path,
) -> Path:
    path = output_dir / "prc_v2_4_transition_taxonomy_counts_v0_1.png"
    fig, ax = plt.subplots(figsize=(10, 5.6))
    x_positions = range(len(datasets))
    bottom = [0] * len(datasets)
    colors = taxonomy_colors()

    for label in TAXONOMY_LABELS:
        values = [
            canonical_transition_summary(rows)[label] for rows in datasets.values()
        ]
        bars = ax.bar(
            x_positions,
            values,
            bottom=bottom,
            label=label,
            color=colors[label],
            edgecolor="white",
            linewidth=0.8,
        )
        for bar, value in zip(bars, values):
            if value:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + bar.get_height() / 2,
                    str(value),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white" if value > 100 else "#222222",
                )
        bottom = [old + value for old, value in zip(bottom, values)]

    ax.set_title("PRC v2.4 transition taxonomy counts")
    ax.set_ylabel("rows")
    ax.set_xticks(list(x_positions), list(datasets.keys()), rotation=12, ha="right")
    ax.legend(ncols=5, loc="upper center", bbox_to_anchor=(0.5, -0.16))
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_component_delta_counts(
    datasets: dict[str, list[TransitionProbeRow]],
    output_dir: Path,
) -> Path:
    path = output_dir / "prc_v2_4_transition_component_delta_v0_1.png"
    columns = [
        (TRANSITION_MISS, 0),
        (TRANSITION_TRIM, 0),
        (TRANSITION_SPLIT, 1),
        (TRANSITION_PARTIAL_CLOSE, -1),
        (TRANSITION_CLOSE, -1),
    ]
    matrix = []
    for rows in datasets.values():
        counts = component_delta_summary(rows)
        matrix.append([counts[column] for column in columns])

    fig, ax = plt.subplots(figsize=(10, 4.8))
    image = ax.imshow([[value + 1 for value in row] for row in matrix], norm=LogNorm())
    ax.set_title("PRC v2.4 taxonomy by component delta (log count + 1)")
    ax.set_yticks(range(len(datasets)), list(datasets.keys()))
    ax.set_xticks(
        range(len(columns)),
        [f"{label}\ndelta {delta:+d}" for label, delta in columns],
        rotation=0,
    )
    annotate_matrix(ax, matrix)
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.03)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_b5_to_b6_genealogy_flow(
    datasets: dict[str, list[TransitionProbeRow]],
    output_dir: Path,
) -> Path:
    path = output_dir / "prc_v2_4_b5_to_b6_genealogy_flow_v0_1.png"
    b5_rows = {row.child_residue: row for row in datasets["B5 pilot"]}
    b5_to_b6_rows = datasets["B5->B6 full"]
    source_labels = [
        (TRANSITION_MISS, 0),
        (TRANSITION_TRIM, 0),
        (TRANSITION_SPLIT, 1),
        (TRANSITION_PARTIAL_CLOSE, -1),
    ]
    target_labels = [
        (TRANSITION_MISS, 0, False),
        (TRANSITION_TRIM, 0, False),
        (TRANSITION_SPLIT, 1, False),
        (TRANSITION_PARTIAL_CLOSE, -1, False),
        (TRANSITION_CLOSE, -1, True),
    ]
    source_index = {label: index for index, label in enumerate(source_labels)}
    target_index = {label: index for index, label in enumerate(target_labels)}
    matrix = [[0 for _ in target_labels] for _ in source_labels]

    for row in b5_to_b6_rows:
        parent = b5_rows[row.parent_residue]
        source = (
            classify_canonical_transition(parent),
            component_transition_stats(parent).component_delta,
        )
        target = (
            classify_canonical_transition(row),
            component_transition_stats(row).component_delta,
            row.is_b5_birth,
        )
        if source in source_index and target in target_index:
            matrix[source_index[source]][target_index[target]] += 1

    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    image = ax.imshow([[value + 1 for value in row] for row in matrix], norm=LogNorm())
    ax.set_title("B5 state -> B6 transition flow (log count + 1)")
    ax.set_ylabel("B5 parent transition state")
    ax.set_xlabel("B6 child transition state")
    ax.set_yticks(
        range(len(source_labels)),
        [f"{label}\ndelta {delta:+d}" for label, delta in source_labels],
    )
    ax.set_xticks(
        range(len(target_labels)),
        [
            f"{label}\ndelta {delta:+d}" + ("\nbirth" if is_birth else "")
            for label, delta, is_birth in target_labels
        ],
        rotation=18,
        ha="right",
    )
    annotate_matrix(ax, matrix)
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.03)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_remainder_taxonomy_heatmaps(
    datasets: dict[str, list[TransitionProbeRow]],
    output_dir: Path,
) -> Path:
    path = output_dir / "prc_v2_4_remainder_taxonomy_heatmaps_v0_1.png"
    fig, axes = plt.subplots(len(datasets), 1, figsize=(11, 8.5), constrained_layout=True)
    colors = taxonomy_colors()

    for ax, (dataset_name, rows) in zip(axes, datasets.items()):
        remainders = sorted({row.new_prime_remainder for row in rows})
        counts = remainder_taxonomy_counts(rows)
        bottom = [0] * len(remainders)
        for label in TAXONOMY_LABELS:
            values = [counts[(remainder, label)] for remainder in remainders]
            ax.bar(
                remainders,
                values,
                bottom=bottom,
                color=colors[label],
                edgecolor="white",
                linewidth=0.4,
                label=label,
            )
            bottom = [old + value for old, value in zip(bottom, values)]
        ax.set_title(dataset_name)
        ax.set_ylabel("rows")
        ax.set_xticks(remainders)
        ax.grid(axis="y", alpha=0.25)
    axes[-1].set_xlabel("new-prime remainder")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, ncols=5, loc="lower center")
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_birth_residual_genealogy(
    rows: list[BirthResidualGenealogyRow],
    output_dir: Path,
) -> Path:
    path = output_dir / "prc_v2_4_birth_residual_genealogy_layers_v0_1.png"
    labels = ("start", *TAXONOMY_LABELS)
    keys = sorted({(row.birth_k, row.layer_k) for row in rows})
    counts = Counter(
        (row.birth_k, row.layer_k, row.transition_label)
        for row in rows
    )
    fig, ax = plt.subplots(figsize=(13, 5.8))
    x_positions = range(len(keys))
    bottom = [0] * len(keys)
    colors = {"start": "#4d4d4d", **taxonomy_colors()}
    for label in labels:
        values = [counts[(birth_k, layer_k, label)] for birth_k, layer_k in keys]
        ax.bar(
            x_positions,
            values,
            bottom=bottom,
            color=colors[label],
            edgecolor="white",
            linewidth=0.4,
            label=label,
        )
        bottom = [old + value for old, value in zip(bottom, values)]
    ax.set_title("B5/B6/B7 birth residual genealogy by layer")
    ax.set_ylabel("lineage rows")
    ax.set_xticks(
        list(x_positions),
        [f"B{birth_k}\nk{layer_k}" for birth_k, layer_k in keys],
        rotation=0,
    )
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncols=6, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_origin_zero_diagnostics(
    rows: list[BirthResidualGenealogyRow],
    output_dir: Path,
) -> Path:
    path = output_dir / "prc_v2_4_birth_origin_zero_diagnostics_v0_1.png"
    keys = sorted({(row.birth_k, row.layer_k) for row in rows})
    totals = Counter((row.birth_k, row.layer_k) for row in rows)
    origin = Counter(
        (row.birth_k, row.layer_k) for row in rows if row.origin_component_present
    )
    zero_center = Counter(
        (row.birth_k, row.layer_k) for row in rows if row.zero_center_available
    )
    x_positions = list(range(len(keys)))
    fig, ax = plt.subplots(figsize=(13, 5.2))
    ax.plot(
        x_positions,
        [origin[key] / totals[key] for key in keys],
        marker="o",
        label="origin component present",
        color="#7b3294",
    )
    ax.plot(
        x_positions,
        [zero_center[key] / totals[key] for key in keys],
        marker="s",
        label="zero center available",
        color="#1b7837",
    )
    ax.set_ylim(-0.04, 1.04)
    ax.set_title("Origin-side and zero-center diagnostics by genealogy layer")
    ax.set_ylabel("share of lineage rows")
    ax.set_xticks(
        x_positions,
        [f"B{birth_k}\nk{layer_k}" for birth_k, layer_k in keys],
        rotation=0,
    )
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncols=2)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_k2_gap_width_bias(output_dir: Path) -> Path:
    path = output_dir / "prc_v2_4_k2_gap_width_bias_v0_1.png"
    rows = read_k2_gap_width_bias_csv()
    residues = [row.residue_mod_6 for row in rows]
    residual_degrees = [fraction_to_float(row.residual_width) * 360 for row in rows]
    birth_counts = [row.birth_lineage_count for row in rows]

    fig, ax_width = plt.subplots(figsize=(9, 5.2))
    bars = ax_width.bar(
        residues,
        residual_degrees,
        color="#8c8c8c",
        edgecolor="white",
        label="k=2 residual width (degrees)",
    )
    for bar, value in zip(bars, residual_degrees):
        ax_width.text(
            bar.get_x() + bar.get_width() / 2,
            value + 4,
            f"{value:.0f} deg",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    ax_count = ax_width.twinx()
    ax_count.plot(
        residues,
        birth_counts,
        color="#0f7f3a",
        marker="o",
        linewidth=2.5,
        label="B5/B6/B7 birth-lineage count",
    )
    for residue, value in zip(residues, birth_counts):
        ax_count.text(residue, value + 12, str(value), ha="center", fontsize=8)

    ax_width.set_title("k=2 gap width vs future birth-lineage enrichment")
    ax_width.set_xlabel("residue mod 6")
    ax_width.set_ylabel("residual width (degrees)")
    ax_count.set_ylabel("birth-lineage rows")
    ax_width.set_xticks(residues)
    ax_width.grid(axis="y", alpha=0.25)
    handles_1, labels_1 = ax_width.get_legend_handles_labels()
    handles_2, labels_2 = ax_count.get_legend_handles_labels()
    ax_width.legend(handles_1 + handles_2, labels_1 + labels_2, loc="upper center")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_lineage_measure_bias(output_dir: Path) -> Path:
    path = output_dir / "prc_v2_4_lineage_measure_bias_v0_1.png"
    rows = read_lineage_measure_bias_csv()
    populations = ("all_residues", "birth_lineage")
    colors = {"all_residues": "#666666", "birth_lineage": "#2b8cbe"}

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharex=True)
    for population in populations:
        population_rows = [row for row in rows if row.population == population]
        layer_values = [row.layer_k for row in population_rows]
        residual_values = [
            fraction_to_float(row.average_residual_measure)
            for row in population_rows
        ]
        target_values = [
            fraction_to_float(row.target_sector_share_of_residual)
            for row in population_rows
        ]
        axes[0].plot(
            layer_values,
            residual_values,
            marker="o",
            linewidth=2,
            color=colors[population],
            label=population,
        )
        axes[1].plot(
            layer_values,
            target_values,
            marker="o",
            linewidth=2,
            color=colors[population],
            label=population,
        )

    axes[0].set_title("Average residual measure")
    axes[0].set_ylabel("fraction of circle")
    axes[1].set_title("Target-sector share of residual")
    axes[1].set_ylabel("share")
    for ax in axes:
        ax.set_xlabel("layer k")
        ax.set_xticks([1, 2, 3, 4])
        ax.grid(alpha=0.25)
        ax.legend()
    fig.suptitle("All residues vs future birth lineages")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_incremental_grid_phase_histograms(output_dir: Path) -> Path:
    path = output_dir / "prc_v2_4_incremental_grid_phase_histograms_v0_1.png"
    rows = read_incremental_grid_phase_csv()
    layers = sorted({row.layer_k for row in rows})
    colors = taxonomy_colors() | {"start": "#444444"}
    labels = ("start", *TAXONOMY_LABELS)
    fig, axes = plt.subplots(len(layers), 1, figsize=(11, 12), constrained_layout=True)

    for ax, layer_k in zip(axes, layers):
        layer_rows = [row for row in rows if row.layer_k == layer_k]
        new_prime = layer_rows[0].new_prime
        remainders = list(range(new_prime))
        bottom = [0] * len(remainders)
        for label in labels:
            values = [
                sum(
                    row.row_count
                    for row in layer_rows
                    if row.new_prime_remainder == remainder
                    and row.transition_label == label
                )
                for remainder in remainders
            ]
            if any(values):
                ax.bar(
                    remainders,
                    values,
                    bottom=bottom,
                    color=colors.get(label, "#999999"),
                    edgecolor="white",
                    linewidth=0.5,
                    label=label,
                )
                bottom = [old + value for old, value in zip(bottom, values)]
        ax.set_title(f"k={layer_k}, new prime p={new_prime}")
        ax.set_ylabel("lineage rows")
        ax.set_xticks(remainders)
        ax.grid(axis="y", alpha=0.2)
        if layer_k == 2:
            ax.annotate(
                "p=3 center at 0 splits the k=1 origin-side gap",
                xy=(0, max(bottom) if bottom else 0),
                xytext=(0.2, max(bottom) * 0.75 if bottom else 1),
                arrowprops={"arrowstyle": "->", "color": "#222222"},
                fontsize=8,
            )
    axes[-1].set_xlabel("new-prime remainder")
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, ncols=6, loc="lower center")
    fig.suptitle("Incremental new-prime grid phases along checked birth lineages")
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def plot_birth_potential_score(output_dir: Path) -> Path:
    path = output_dir / "prc_v2_4_birth_potential_score_v0_1.png"
    score_rows = read_birth_potential_score_csv()
    correlation_rows = read_birth_potential_correlation_csv()
    models = ("uniform", "covered_width", "inverse_width", "residual_width")
    residues = sorted({row.residue for row in score_rows})
    observed = [
        next(
            row.observed_birth_lineage_count
            for row in score_rows
            if row.model == "uniform" and row.residue == residue
        )
        for residue in residues
    ]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)
    axes[0].bar(
        residues,
        observed,
        color="#444444",
        alpha=0.35,
        label="observed birth-lineage count",
    )
    model_colors = {
        "uniform": "#999999",
        "covered_width": "#4daf4a",
        "inverse_width": "#2b8cbe",
        "residual_width": "#e41a1c",
    }
    for model in models:
        expected = [
            fraction_to_float(
                next(
                    row.normalized_expected_count
                    for row in score_rows
                    if row.model == model and row.residue == residue
                )
            )
            for residue in residues
        ]
        axes[0].plot(
            residues,
            expected,
            marker="o",
            linewidth=2,
            color=model_colors[model],
            label=model,
        )
    axes[0].set_title("k=2 birth-potential score models")
    axes[0].set_xlabel("residue mod 6")
    axes[0].set_ylabel("lineage rows")
    axes[0].set_xticks(residues)
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].legend(fontsize=8)

    correlations = {row.model: row for row in correlation_rows}
    x_positions = range(len(models))
    axes[1].bar(
        x_positions,
        [float(correlations[model].pearson_correlation) for model in models],
        color=[model_colors[model] for model in models],
    )
    axes[1].set_title("Observed vs expected correlation")
    axes[1].set_ylabel("Pearson correlation")
    axes[1].set_xticks(x_positions, models, rotation=20, ha="right")
    axes[1].set_ylim(-1.05, 1.05)
    axes[1].grid(axis="y", alpha=0.25)
    fig.suptitle("Width-based birth-potential models are hypotheses, not exclusions")
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def component_delta_summary(
    rows: Iterable[TransitionProbeRow],
) -> Counter[tuple[str, int]]:
    return Counter(
        (
            classify_canonical_transition(row),
            component_transition_stats(row).component_delta,
        )
        for row in rows
    )


def remainder_taxonomy_counts(
    rows: Iterable[TransitionProbeRow],
) -> Counter[tuple[int, str]]:
    return Counter(
        (row.new_prime_remainder, classify_canonical_transition(row))
        for row in rows
    )


def annotate_matrix(ax, matrix: list[list[int]]) -> None:
    for row_index, row in enumerate(matrix):
        for column_index, value in enumerate(row):
            if value:
                ax.text(
                    column_index,
                    row_index,
                    str(value),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white" if value > 100 else "#222222",
                )


def fraction_to_float(value: str) -> float:
    return float(Fraction(value))


def taxonomy_colors() -> dict[str, str]:
    return {
        TRANSITION_MISS: "#767676",
        TRANSITION_TRIM: "#2b8cbe",
        TRANSITION_SPLIT: "#7b3294",
        TRANSITION_PARTIAL_CLOSE: "#e08214",
        TRANSITION_CLOSE: "#1b7837",
    }


def write_manifest(
    output_dir: Path,
    generated: list[Path],
    datasets: dict[str, list[TransitionProbeRow]],
    genealogy_rows: list[BirthResidualGenealogyRow],
) -> Path:
    path = output_dir / "prc_v2_4_transition_figures_manifest_v0_1.json"
    manifest = {
        "status": "source-only v2.4 Gate R diagnostic",
        "taxonomy": list(TAXONOMY_LABELS),
        "files": [figure.name for figure in generated],
        "datasets": {
            name: {
                "rows": len(rows),
                "taxonomy_counts": dict(canonical_transition_summary(rows)),
            }
            for name, rows in datasets.items()
        },
        "birth_residual_genealogy": {
            "rows": len(genealogy_rows),
            "transition_counts": dict(
                Counter(row.transition_label for row in genealogy_rows)
            ),
        },
    }
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    raise SystemExit(main())
