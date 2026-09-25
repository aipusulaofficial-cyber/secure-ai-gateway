from fastapi.testclient import TestClient
from hypothesis import given, strategies as st

from service import app


client = TestClient(app)


def test_contract():
    assert client.get("/health/live").status_code == 200


@given(st.text(min_size=1, max_size=32))
def test_property(value: str):
    response = client.post(
        "/v1/gateway",
        json={
            "key": value,
            "payload": {"token": "Bearer inference", "scope": "inference"},
        },
    )
    assert response.status_code == 200, response.text
