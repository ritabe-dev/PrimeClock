"""Figure generation for PRP v0."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .branches import branch_decomposition, limit_branch_mass
from .experiments import histogram_masses, limit_bin_masses
from .fourier import fourier_coefficient, limit_fourier_coefficient
from .projection import fractional_parts


def _require_matplotlib():
    try:
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


def write_manifest(output_dir: Path, *, command: str, generated_files: list[str]) -> None:
    """Write a reproducibility manifest for generated figures."""
    payload = {
        "name": "Prime Reciprocal Projection",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "git_sha": _git_sha(),
        "command": command,
        "generated_files": generated_files,
    }
    (output_dir / "manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


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
        abs(fourier_coefficient(n, m) - limit_fourier_coefficient(m, samples=1024, k_max=2000))
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
        command=f"python -m prime_reciprocal_projection.cli figures --out {output_path}",
        generated_files=generated,
    )
    return generated

