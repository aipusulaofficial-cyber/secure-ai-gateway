from gateway_domain import *
def test_policy_and_rate_limit():
 assert authorize("Bearer inference","inference").allowed
 r=RateLimiter(1);assert r.allow("k",0);assert not r.allow("k",1)