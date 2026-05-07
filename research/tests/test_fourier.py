from prime_reciprocal_projection import fourier_coefficient, limit_fourier_coefficient


def test_fourier_zero_mode_is_one():
    assert abs(fourier_coefficient(100, 0) - 1) < 1e-12
    assert limit_fourier_coefficient(0) == 1 + 0j

