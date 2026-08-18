from uuid import uuid4

from fastapi.testclient import TestClient

from foxhubclaw.api_app import app
from foxhubclaw.config import settings
from foxhubclaw.db import SessionLocal, init_db
from foxhubclaw.models import JobRun, Report, User


def _seed_report() -> tuple[TestClient, str, int]:
    settings.mode = "web"
    init_db()
    client = TestClient(app)
    username = f"rep_{uuid4().hex[:8]}"
    registered = client.post(
        "/api/auth/register",
        json={"username": username, "password": "secret12"},
    )
    assert registered.status_code == 200, registered.text
    token = registered.json()["token"]

    with SessionLocal() as session:
        user = session.query(User).filter(User.username == username).one()
        run = JobRun(user_id=user.id, keyword="人工智能", status="success", item_count=1)
        session.add(run)
        session.flush()
        folder = settings.reports_dir / str(user.id)
        folder.mkdir(parents=True, exist_ok=True)
        html = folder / "sample.html"
        html.write_text("<html><body>report-ok</body></html>", encoding="utf-8")
        report = Report(
            user_id=user.id,
            run_id=run.id,
            keyword="人工智能",
            html_path=str(html.resolve()),
        )
        session.add(report)
        session.commit()
        session.refresh(report)
        report_id = report.id
    return client, token, report_id


def test_report_file_without_login_says_please_login():
    client, _token, report_id = _seed_report()
    response = client.get(f"/api/reports/{report_id}/file/html")
    assert response.status_code == 401
    assert response.json()["detail"] == "请先登录"


def test_report_file_opens_with_bearer_token():
    client, token, report_id = _seed_report()
    response = client.get(
        f"/api/reports/{report_id}/file/html",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "report-ok" in response.text
    assert "FoxHubClaw-" in (response.headers.get("content-disposition") or "")


def test_report_file_opens_with_query_token():
    client, token, report_id = _seed_report()
    response = client.get(f"/api/reports/{report_id}/file/html?token={token}")
    assert response.status_code == 200
    assert "report-ok" in response.text
