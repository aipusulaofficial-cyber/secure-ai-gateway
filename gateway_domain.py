from dataclasses import dataclass
import time

@dataclass(frozen=True)
class Decision:
    allowed:bool; reason:str

class RateLimiter:
    def __init__(self,limit:int,window_s:float=60): self.limit,self.window_s,self._hits=limit,window_s,{}
    def allow(self,key:str,now:float|None=None)->bool:
        now=time.monotonic() if now is None else now
        hits=[t for t in self._hits.get(key,[]) if now-t<self.window_s]
        if len(hits)>=self.limit:self._hits[key]=hits;return False
        hits.append(now);self._hits[key]=hits;return True

def authorize(token:str, required_scope:str)->Decision:
    if not token:return Decision(False,"missing_credentials")
    scopes=set(token.removeprefix("Bearer ").split(","))
    return Decision(required_scope in scopes,"ok" if required_scope in scopes else "insufficient_scope")
