import time

from runtime_evidence import runtime_evidence


def test_foundation_contract():
    evidence = runtime_evidence(
        request_id="foundation",
        stage="gateway",
        decision="FAIL",
        started=time.perf_counter(),
        error="test",
    )
    assert evidence["decision"] == "FAIL"
    assert evidence["error"] == "test"
