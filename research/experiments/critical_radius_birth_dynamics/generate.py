"""Generate critical-radius and birth-dynamics sandbox artifacts."""

from __future__ import annotations

from pathlib import Path

from tools import (
    birth_threshold_crossing_rows,
    birth_dynamics_rows,
    birth_dynamics_summary_rows,
    critical_radius_rows,
    critical_radius_near_miss_rows,
    critical_radius_summary_rows,
    near_miss_birth_parent_rows,
    write_birth_threshold_crossing_csv,
    write_birth_dynamics_csv,
    write_birth_dynamics_summary_csv,
    write_critical_radius_csv,
    write_critical_radius_near_miss_csv,
    write_critical_radius_summary_csv,
    write_near_miss_birth_parent_csv,
)


EXPERIMENT_DIR = Path(__file__).resolve().parent
DATA_DIR = EXPERIMENT_DIR / "data"


def main() -> int:
    radius_rows = critical_radius_rows(min_k=4, max_k=5)
    radius_summary_rows = critical_radius_summary_rows(radius_rows)
    near_miss_rows = critical_radius_near_miss_rows(radius_rows, limit_per_k=20)
    near_miss_parent_rows = near_miss_birth_parent_rows(near_miss_rows)
    birth_rows = birth_dynamics_rows(min_k=5, max_k=7)
    summary_rows = birth_dynamics_summary_rows(birth_rows)
    crossing_rows = birth_threshold_crossing_rows(min_k=5, max_k=7)
    b5_crossing_rows = [row for row in crossing_rows if row.k == 5]

    write_critical_radius_csv(
        radius_rows,
        DATA_DIR / "prc_prime_prefix_critical_radius_k4_k5_v0_1.csv",
    )
    write_critical_radius_summary_csv(
        radius_summary_rows,
        DATA_DIR / "prc_prime_prefix_critical_radius_summary_v0_1.csv",
    )
    write_critical_radius_near_miss_csv(
        near_miss_rows,
        DATA_DIR / "prc_prime_prefix_critical_radius_near_misses_k4_k5_v0_1.csv",
    )
    write_near_miss_birth_parent_csv(
        near_miss_parent_rows,
        DATA_DIR / "prc_prime_prefix_near_miss_birth_parent_overlap_k4_k6_v0_1.csv",
    )
    write_birth_threshold_crossing_csv(
        b5_crossing_rows,
        DATA_DIR / "prc_prime_prefix_birth_threshold_crossing_k5_v0_1.csv",
    )
    write_birth_threshold_crossing_csv(
        crossing_rows,
        DATA_DIR / "prc_prime_prefix_birth_threshold_crossing_k5_k7_v0_1.csv",
    )
    write_birth_dynamics_csv(
        birth_rows,
        DATA_DIR / "prc_prime_prefix_birth_dynamics_k5_k7_v0_1.csv",
    )
    write_birth_dynamics_summary_csv(
        summary_rows,
        DATA_DIR / "prc_prime_prefix_birth_dynamics_summary_v0_1.csv",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
