from pathlib import Path

from prime_reciprocal_projection.metrics import convergence_row, write_convergence_csv


def test_convergence_row_has_expected_fields():
    row = convergence_row(1000, bins=20, max_branch_k=10, max_fourier_m=3)
    assert row.n == 1000
    assert row.prime_count == 168
    assert row.hist_l1 >= 0
    assert row.ks_distance >= 0
    assert row.fourier_max_mode_m1_20 in {1, 2, 3}


def test_write_convergence_csv(tmp_path: Path):
    row = convergence_row(1000, bins=20, max_branch_k=10, max_fourier_m=3)
    output = tmp_path / "summary.csv"
    write_convergence_csv([row], output)
    text = output.read_text(encoding="utf-8")
    assert "prime_count" in text
    assert "1000" in text

