from runtime_evidence import runtime_evidence
import time

def test_foundation_contract():
    e=runtime_evidence(request_id="foundation",stage="gateway",decision="FAIL",started=time.perf_counter(),error="test")
    assert e["decision"] == "FAIL"
    assert e["error"] == "test"
