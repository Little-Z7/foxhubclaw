from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from foxhubclaw.auth import (
    create_token,
    current_user,
    find_user,
    hash_password,
    require_admin,
    verify_password,
)
from foxhubclaw.capabilities import list_platforms
from foxhubclaw.config import settings
from foxhubclaw.crypto import mask_key
from foxhubclaw.db import get_db, init_db
from foxhubclaw.models import JobRun, QueryJob, Report, User
from foxhubclaw.scheduler import start_scheduler
from foxhubclaw.services import (
    dump_list,
    execute_query,
    file_belongs,
    get_or_create_setting,
    load_api_key,
    load_list,
    next_run_time,
    save_api_key,
)

app = FastAPI(title="FoxHubClaw", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterIn(BaseModel):
    username: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=6, max_length=80)
    email: str | None = None


class LoginIn(BaseModel):
    login: str
    password: str


class SettingsIn(BaseModel):
    api_key: str | None = None
    limit_per_platform: int | None = Field(default=None, ge=1, le=100)
    comment_depth: int | None = Field(default=None, ge=1, le=10)


class QueryIn(BaseModel):
    keyword: str = Field(min_length=1, max_length=200)
    platforms: list[str]
    kinds: list[str] = ["post"]


class TaskIn(BaseModel):
    name: str = ""
    keyword: str
    platforms: list[str]
    kinds: list[str] = ["post"]
    cadence: str = "daily"


class AdminFlagIn(BaseModel):
    is_active: bool


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    start_scheduler()


@app.get("/api/meta")
def meta():
    return {
        "name": "FoxHubClaw",
        "mode": settings.mode,
        "auth_required": settings.auth_required,
        "platforms": list_platforms(),
    }


@app.post("/api/auth/register")
def register(body: RegisterIn, session: Session = Depends(get_db)):
    if settings.mode == "desktop":
        raise HTTPException(status_code=400, detail="桌面版无需注册")
    if find_user(session, body.username) or (body.email and find_user(session, body.email)):
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
    count = session.scalar(select(func.count()).select_from(User)) or 0
    user = User(
        username=body.username.strip(),
        email=body.email.strip() if body.email else None,
        password_hash=hash_password(body.password),
        is_admin=count == 0,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"token": create_token(user), "username": user.username, "is_admin": user.is_admin}


@app.post("/api/auth/login")
def login(body: LoginIn, session: Session = Depends(get_db)):
    user = find_user(session, body.login.strip())
    if user is None or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=400, detail="账号或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已停用")
    return {"token": create_token(user), "username": user.username, "is_admin": user.is_admin}


@app.get("/api/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "username": user.username, "email": user.email, "is_admin": user.is_admin}


@app.get("/api/settings")
def read_settings(user: User = Depends(current_user), session: Session = Depends(get_db)):
    setting = get_or_create_setting(session, user)
    key = load_api_key(session, user)
    return {
        "api_key_masked": mask_key(key),
        "has_key": bool(key),
        "limit_per_platform": setting.limit_per_platform,
        "comment_depth": setting.comment_depth,
    }


@app.put("/api/settings")
def update_settings(body: SettingsIn, user: User = Depends(current_user), session: Session = Depends(get_db)):
    setting = get_or_create_setting(session, user)
    masked = None
    if body.api_key is not None:
        masked = save_api_key(session, user, body.api_key.strip())
    if body.limit_per_platform is not None:
        setting.limit_per_platform = body.limit_per_platform
    if body.comment_depth is not None:
        setting.comment_depth = body.comment_depth
    session.commit()
    key = load_api_key(session, user)
    return {
        "api_key_masked": masked if masked is not None else mask_key(key),
        "has_key": bool(key),
        "limit_per_platform": setting.limit_per_platform,
        "comment_depth": setting.comment_depth,
    }


@app.post("/api/search")
def search(body: QueryIn, user: User = Depends(current_user), session: Session = Depends(get_db)):
    try:
        return execute_query(session, user, body.keyword.strip(), body.platforms, body.kinds)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/tasks")
def list_tasks(user: User = Depends(current_user), session: Session = Depends(get_db)):
    jobs = session.scalars(select(QueryJob).where(QueryJob.user_id == user.id).order_by(QueryJob.id.desc())).all()
    return [
        {
            "id": job.id,
            "name": job.name,
            "keyword": job.keyword,
            "platforms": load_list(job.platforms),
            "kinds": load_list(job.kinds),
            "cadence": job.cadence,
            "next_run_at": job.next_run_at.isoformat() if job.next_run_at else None,
            "enabled": job.enabled,
        }
        for job in jobs
    ]


@app.post("/api/tasks")
def create_task(body: TaskIn, user: User = Depends(current_user), session: Session = Depends(get_db)):
    if body.cadence not in {"daily", "weekly"}:
        raise HTTPException(status_code=400, detail="周期只能是 daily 或 weekly")
    job = QueryJob(
        user_id=user.id,
        name=body.name or body.keyword,
        keyword=body.keyword.strip(),
        platforms=dump_list(body.platforms),
        kinds=dump_list(body.kinds),
        cadence=body.cadence,
        next_run_at=next_run_time(body.cadence),
        enabled=True,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return {"id": job.id}


@app.post("/api/tasks/{task_id}/toggle")
def toggle_task(task_id: int, user: User = Depends(current_user), session: Session = Depends(get_db)):
    job = session.get(QueryJob, task_id)
    if job is None or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="任务不存在")
    job.enabled = not job.enabled
    session.commit()
    return {"enabled": job.enabled}


@app.get("/api/runs")
def list_runs(user: User = Depends(current_user), session: Session = Depends(get_db)):
    runs = session.scalars(select(JobRun).where(JobRun.user_id == user.id).order_by(JobRun.id.desc()).limit(50)).all()
    return [
        {
            "id": run.id,
            "keyword": run.keyword,
            "status": run.status,
            "item_count": run.item_count,
            "message": run.message,
            "started_at": run.started_at.isoformat(),
        }
        for run in runs
    ]


@app.get("/api/reports")
def list_reports(user: User = Depends(current_user), session: Session = Depends(get_db)):
    rows = session.scalars(select(Report).where(Report.user_id == user.id).order_by(Report.id.desc())).all()
    return [
        {
            "id": report.id,
            "keyword": report.keyword,
            "created_at": report.created_at.isoformat(),
            "has_xlsx": bool(report.xlsx_path),
            "has_html": bool(report.html_path),
            "has_pdf": bool(report.pdf_path),
        }
        for report in rows
    ]


@app.get("/api/reports/{report_id}/file/{kind}")
def download_report(report_id: int, kind: str, user: User = Depends(current_user), session: Session = Depends(get_db)):
    report = session.get(Report, report_id)
    if report is None or report.user_id != user.id:
        raise HTTPException(status_code=404, detail="报告不存在")
    path = {"xlsx": report.xlsx_path, "html": report.html_path, "pdf": report.pdf_path}.get(kind)
    if not path or not Path(path).exists() or not file_belongs(path, user.id):
        raise HTTPException(status_code=404, detail="文件不存在")
    media = {
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "html": "text/html",
        "pdf": "application/pdf",
    }[kind]
    return FileResponse(path, media_type=media, filename=Path(path).name)


@app.get("/api/admin/users")
def admin_users(_: User = Depends(require_admin), session: Session = Depends(get_db)):
    users = session.scalars(select(User).order_by(User.id.asc())).all()
    return [
        {
            "id": item.id,
            "username": item.username,
            "email": item.email,
            "is_admin": item.is_admin,
            "is_active": item.is_active,
            "created_at": item.created_at.isoformat(),
        }
        for item in users
    ]


@app.patch("/api/admin/users/{user_id}")
def admin_toggle(user_id: int, body: AdminFlagIn, admin: User = Depends(require_admin), session: Session = Depends(get_db)):
    target = session.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if target.id == admin.id and body.is_active is False:
        raise HTTPException(status_code=400, detail="不能停用自己")
    target.is_active = body.is_active
    session.commit()
    return {"id": target.id, "is_active": target.is_active}


def frontend_dist() -> Path | None:
    import sys

    candidates = [
        Path(__file__).resolve().parents[2] / "frontend" / "dist",
        Path(getattr(sys, "_MEIPASS", ".")) / "frontend" / "dist",
        Path.cwd() / "frontend" / "dist",
    ]
    for path in candidates:
        if path.is_dir():
            return path
    return None


def mount_frontend(application: FastAPI) -> None:
    dist = frontend_dist()
    if dist is not None:
        application.mount("/", StaticFiles(directory=dist, html=True), name="ui")
