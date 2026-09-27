from platform.admission_policy import decide

def test_admission_fails_closed():
    context={k:True for k in ("authenticated","authorized","rate_limited","ai_policy","cost_policy","data_policy")}
    assert decide(context) == "ALLOW"
    context["data_policy"]=False
    assert decide(context) == "DENY"
