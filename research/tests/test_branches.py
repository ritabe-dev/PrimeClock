from prime_reciprocal_projection import branch_decomposition, primes_up_to


def test_branch_counts_sum_to_pi_n():
    n = 100
    branches = branch_decomposition(n)
    assert sum(branch.count for branch in branches) == len(primes_up_to(n))


def test_branch_one_for_n_10():
    branches = {branch.k: branch.count for branch in branch_decomposition(10)}
    assert branches[1] == 1  # p=7
    assert branches[2] == 1  # p=5
    assert branches[3] == 1  # p=3
    assert branches[5] == 1  # p=2

