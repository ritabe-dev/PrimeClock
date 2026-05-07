"""Prime Reciprocal Projection research helpers."""

from .branches import branch_decomposition, limit_branch_mass
from .cluster_scan import (
    cluster_sensitivity_table,
    discover_seed_rows,
    discover_seed_values,
    read_cluster_scan_csv,
    scan_cluster_table,
    scan_cluster_window,
    unique_certified_values,
    write_cluster_sensitivity_csv,
)
from .covering import (
    covering_summary,
    exact_is_completely_covered,
    exact_uncovered_measure,
    max_uncovered_gap,
    uncovered_measure,
)
from .covering_metrics import covering_row, covering_table
from .covering_runs import (
    DEFAULT_PREFILTER_TOLERANCE,
    PREFILTER_GUARANTEE_MAX_N,
    consecutive_runs,
    factorization,
    length2_pair_forensics,
    prefilter_validation_windows,
    exact_complete_runs_in_range,
    exact_complete_values_in_range,
    prefiltered_exact_complete_values_in_range,
    required_prefilter_tolerance,
    summarize_runs,
    transition_stats_from_runs,
    validate_prefilter_tolerance,
)
from .density import rho, rho_bin_mass, rho_n_pnt
from .fourier import fourier_coefficient, limit_fourier_coefficient
from .metrics import convergence_row, convergence_table
from .primes import is_prime, primes_up_to
from .projection import fractional_parts, phi

__all__ = [
    "branch_decomposition",
    "covering_row",
    "covering_summary",
    "covering_table",
    "consecutive_runs",
    "convergence_row",
    "convergence_table",
    "cluster_sensitivity_table",
    "DEFAULT_PREFILTER_TOLERANCE",
    "discover_seed_rows",
    "discover_seed_values",
    "exact_is_completely_covered",
    "exact_complete_runs_in_range",
    "exact_complete_values_in_range",
    "exact_uncovered_measure",
    "factorization",
    "fractional_parts",
    "fourier_coefficient",
    "is_prime",
    "limit_branch_mass",
    "limit_fourier_coefficient",
    "length2_pair_forensics",
    "max_uncovered_gap",
    "phi",
    "prefiltered_exact_complete_values_in_range",
    "prefilter_validation_windows",
    "PREFILTER_GUARANTEE_MAX_N",
    "primes_up_to",
    "required_prefilter_tolerance",
    "rho",
    "rho_bin_mass",
    "rho_n_pnt",
    "read_cluster_scan_csv",
    "scan_cluster_table",
    "scan_cluster_window",
    "summarize_runs",
    "transition_stats_from_runs",
    "unique_certified_values",
    "uncovered_measure",
    "validate_prefilter_tolerance",
    "write_cluster_sensitivity_csv",
]
