from prime_reciprocal_projection import fractional_parts, phi


def test_phi_uses_fractional_part():
    assert phi(10, 3) == 1 / 3
    assert phi(10, 5) == 0


def test_fractional_parts_are_in_unit_interval():
    values = fractional_parts(100)
    assert values
    assert all(0 <= value < 1 for value in values)

