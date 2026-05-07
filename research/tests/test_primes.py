from prime_reciprocal_projection import is_prime, primes_up_to


def test_primes_up_to_30():
    assert primes_up_to(30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]


def test_is_prime_boundaries():
    assert not is_prime(1)
    assert is_prime(2)
    assert not is_prime(9)
    assert is_prime(97)

