from prime_reciprocal_projection import rho, rho_bin_mass
from prime_reciprocal_projection.density import rho_integral_midpoint


def test_rho_positive():
    assert rho(0.0, k_max=100) > rho(0.9, k_max=100) > 0


def test_rho_integrates_near_one():
    assert abs(rho_integral_midpoint(samples=500, k_max=5000) - 1.0) < 0.01


def test_bin_masses_sum_near_one():
    masses = [rho_bin_mass(index / 20, (index + 1) / 20, k_max=5000) for index in range(20)]
    assert abs(sum(masses) - 1.0) < 0.01

