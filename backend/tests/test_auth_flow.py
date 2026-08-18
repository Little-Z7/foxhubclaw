from uuid import uuid4

from fastapi.testclient import TestClient

from foxhubclaw.api_app import app
from foxhubclaw.config import settings
from foxhubclaw.db import init_db


def test_register_and_login_returns_current_user():
    settings.mode = "web"
    init_db()
    client = TestClient(app)
    username = f"user_{uuid4().hex[:8]}"
    response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "secret12", "email": f"{username}@example.com"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["token"]
    me = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == username
