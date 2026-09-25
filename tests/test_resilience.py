import pytest
from resilience import BoundedExecutor,CircuitBreaker,CircuitOpenError,RetryPolicy,TokenBucket,call_with_retry
def test_retry_uses_bounded_attempts():
    calls=[]
    def fn():
        calls.append(1)
        if len(calls)<3: raise TimeoutError("dependency timeout")
        return "ok"
    assert call_with_retry(fn,policy=RetryPolicy(attempts=3,base_delay=0),retryable=lambda e:isinstance(e,TimeoutError))=="ok"
    assert len(calls)==3
def test_retry_does_not_retry_non_retryable_error():
    calls=[]
    def fn(): calls.append(1); raise ValueError("bad input")
    with pytest.raises(ValueError): call_with_retry(fn,policy=RetryPolicy(attempts=3,base_delay=0),retryable=lambda e:False)
    assert len(calls)==1
def test_bounded_concurrency_fails_fast():
    ex=BoundedExecutor(1); ex._sem.acquire()
    try:
        with pytest.raises(RuntimeError,match="concurrency limit exceeded"): ex.run(lambda:"x")
    finally: ex._sem.release()
def test_token_bucket_enforces_rate():
    b=TokenBucket(rate=1,capacity=1); assert b.allow(); assert not b.allow()
def test_circuit_breaker_opens_after_failures():
    b=CircuitBreaker(failure_threshold=3,reset_timeout=60)
    for _ in range(3): b.record_failure()
    assert b.open
    with pytest.raises(CircuitOpenError): call_with_retry(lambda:"x",policy=RetryPolicy(attempts=1),retryable=lambda e:True,breaker=b)
