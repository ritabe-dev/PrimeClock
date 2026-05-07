import pytest


def test_matplotlib_is_optional_for_core_tests():
    try:
        import matplotlib  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("matplotlib is not installed in this environment")

