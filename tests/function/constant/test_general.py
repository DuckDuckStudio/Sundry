from function.constant.general import RETRY_INTERVAL


def test_RETRY_INTERVAL_is_int():
    assert isinstance(RETRY_INTERVAL, int)
