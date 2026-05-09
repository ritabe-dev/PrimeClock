"""Generate critical-radius and birth-dynamics sandbox artifacts."""

from __future__ import annotations

from pathlib import Path

from tools import (
    birth_dynamics_rows,
    birth_dynamics_summary_rows,
    critical_radius_rows,
    write_birth_dynamics_csv,
    write_birth_dynamics_summary_csv,
    write_critical_radius_csv,
)


EXPERIMENT_DIR = Path(__file__).resolve().parent
DATA_DIR = EXPERIMENT_DIR / "data"


def main() -> int:
    radius_rows = critical_radius_rows(min_k=4, max_k=5)
    birth_rows = birth_dynamics_rows(min_k=5, max_k=7)
    summary_rows = birth_dynamics_summary_rows(birth_rows)

    write_critical_radius_csv(
        radius_rows,
        DATA_DIR / "prc_prime_prefix_critical_radius_k4_k5_v0_1.csv",
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
