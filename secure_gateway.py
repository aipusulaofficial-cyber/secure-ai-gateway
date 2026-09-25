"""Secure AI gateway policy core: authentication, quotas and content controls."""
from dataclasses import dataclass
import re,sys,time
class GatewayDenied(Exception):pass
@dataclass(frozen=True)
class Request: principal:str; text:str; request_id:str
class Policy:
 def __init__(self,blocked=None,max_chars=4000): self.blocked=blocked or ["ignore previous instructions","exfiltrate"],self.max_chars=max_chars
 def check(self,r):
  if not r.principal: raise GatewayDenied("unauthenticated")
  if len(r.text)>self.max_chars: raise GatewayDenied("payload too large")
  if any(x in r.text.lower() for x in self.blocked): raise GatewayDenied("policy blocked")
  return True
class RateLimiter:
 def __init__(self,limit=10,window=60): self.limit,self.window,self.hits=limit,window,{}
 def allow(self,key,now=None):
  now=time.monotonic() if now is None else now; q=[t for t in self.hits.get(key,[]) if now-t<self.window]
  if len(q)>=self.limit:return False
  q.append(now);self.hits[key]=q;return True
class Gateway:
 def __init__(self,policy=None,limiter=None):self.policy=policy or Policy();self.limiter=limiter or RateLimiter()
 def authorize(self,r,now=None):
  self.policy.check(r)
  if not self.limiter.allow(r.principal,now):raise GatewayDenied("rate limit exceeded")
  return {"request_id":r.request_id,"decision":"allow"}
if __name__=="__main__": print(Gateway().authorize(Request("demo","hello","r1")))
