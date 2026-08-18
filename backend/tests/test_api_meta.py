from fastapi.testclient import TestClient

from foxhubclaw.api_app import app
from foxhubclaw.db import init_db


def test_meta_exposes_product_name():
    init_db()
    client = TestClient(app)
    response = client.get("/api/meta")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "FoxHubClaw"
    assert "platforms" in body
    assert body["default_prompts"]
