from failure_injection import admission, bounded_retry, run_failure_matrix


def test_timeout_is_bounded():
    assert bounded_retry(0, 2) == "RETRY"
    assert bounded_retry(2, 2) == "FAIL"


def test_unhealthy_backend_fails_closed():
    assert admission(False, True, True) == "DENY"


def test_unauthorized_request_is_denied():
    assert admission(True, False, True) == "DENY"


def test_quota_exhaustion_is_denied():
    assert admission(True, True, False) == "DENY"


def test_matrix_is_deterministic():
    assert run_failure_matrix() == {
        "timeout": "RETRY",
        "backend_unavailable": "DENY",
        "unauthorized": "DENY",
        "quota_exhausted": "DENY",
    }
