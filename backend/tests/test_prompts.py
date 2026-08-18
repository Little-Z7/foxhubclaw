from uuid import uuid4

from fastapi.testclient import TestClient

from foxhubclaw.api_app import app
from foxhubclaw.config import settings
from foxhubclaw.db import init_db
from foxhubclaw.prompts import DEFAULT_PROMPTS


def _user_client() -> TestClient:
    settings.mode = "web"
    init_db()
    client = TestClient(app)
    username = f"prompt_{uuid4().hex[:8]}"
    response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "secret12"},
    )
    assert response.status_code == 200, response.text
    client.headers.update({"Authorization": f"Bearer {response.json()['token']}"})
    return client


def test_settings_return_builtin_prompts_by_default():
    client = _user_client()
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert response.json()["prompts"] == DEFAULT_PROMPTS


def test_custom_prompts_roundtrip():
    client = _user_client()
    response = client.put("/api/settings", json={"prompts": ["国货美妆", "  国货美妆  ", "新品种草"]})
    assert response.status_code == 200
    assert response.json()["prompts"] == ["国货美妆", "新品种草"]
    assert client.get("/api/settings").json()["prompts"] == ["国货美妆", "新品种草"]
