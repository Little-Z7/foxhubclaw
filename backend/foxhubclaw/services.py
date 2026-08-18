from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from foxhubclaw.config import settings
from foxhubclaw.crypto import decrypt_secret, encrypt_secret, mask_key
from foxhubclaw.models import JobRun, QueryJob, Report, User, UserSetting
from foxhubclaw.query_runner import QueryRunner
from foxhubclaw.reports import write_report_files


def get_or_create_setting(session: Session, user: User) -> UserSetting:
    setting = session.scalar(select(UserSetting).where(UserSetting.user_id == user.id))
    if setting is None:
        setting = UserSetting(user_id=user.id)
        session.add(setting)
        session.commit()
        session.refresh(setting)
    return setting


def save_api_key(session: Session, user: User, api_key: str) -> str:
    setting = get_or_create_setting(session, user)
    setting.api_key_encrypted = encrypt_secret(api_key, settings.secret_key) if api_key else ""
    session.commit()
    return mask_key(api_key)


def load_api_key(session: Session, user: User) -> str:
    setting = get_or_create_setting(session, user)
    if not setting.api_key_encrypted:
        return ""
    return decrypt_secret(setting.api_key_encrypted, settings.secret_key)


def execute_query(
    session: Session,
    user: User,
    keyword: str,
    platforms: list[str],
    kinds: list[str],
    job_id: int | None = None,
) -> dict:
    setting = get_or_create_setting(session, user)
    api_key = load_api_key(session, user)
    if not api_key:
        raise ValueError("请先在设置里填写 RedFox Key")

    run = JobRun(user_id=user.id, job_id=job_id, keyword=keyword, status="running")
    session.add(run)
    session.commit()
    session.refresh(run)

    try:
        items, failures = QueryRunner(api_key).run(
            keyword=keyword,
            platforms=platforms,
            kinds=kinds,
            limit_per_platform=setting.limit_per_platform,
            comment_depth=setting.comment_depth,
        )
        paths = write_report_files(
            output_dir=settings.reports_dir / str(user.id),
            keyword=keyword,
            items=items,
            failures=failures,
        )
        report = Report(
            user_id=user.id,
            run_id=run.id,
            keyword=keyword,
            xlsx_path=paths["xlsx"],
            html_path=paths["html"],
            pdf_path=paths["pdf"],
        )
        session.add(report)
        run.status = "partial" if failures and items else ("failed" if failures and not items else "success")
        run.item_count = len(items)
        run.message = "; ".join(f"{f['platform']}/{f['kind']}: {f['message']}" for f in failures)
        run.finished_at = datetime.utcnow()
        session.commit()
        session.refresh(report)
        return {
            "run_id": run.id,
            "report_id": report.id,
            "status": run.status,
            "items": items,
            "failures": failures,
        }
    except Exception as exc:
        run.status = "failed"
        run.message = str(exc)
        run.finished_at = datetime.utcnow()
        session.commit()
        raise


def next_run_time(cadence: str) -> datetime | None:
    now = datetime.utcnow()
    if cadence == "daily":
        return now + timedelta(days=1)
    if cadence == "weekly":
        return now + timedelta(weeks=1)
    return None


def dump_list(values: list[str]) -> str:
    return json.dumps(values, ensure_ascii=False)


def load_list(raw: str) -> list[str]:
    try:
        data = json.loads(raw)
        return [str(item) for item in data]
    except Exception:  # noqa: BLE001
        return [part.strip() for part in raw.split(",") if part.strip()]


def due_jobs(session: Session) -> list[QueryJob]:
    now = datetime.utcnow()
    return list(
        session.scalars(
            select(QueryJob).where(
                QueryJob.enabled.is_(True),
                QueryJob.cadence.in_(["daily", "weekly"]),
                QueryJob.next_run_at.is_not(None),
                QueryJob.next_run_at <= now,
            )
        )
    )


def file_belongs(path: str, user_id: int) -> bool:
    resolved = Path(path).resolve()
    root = (settings.reports_dir / str(user_id)).resolve()
    return str(resolved).startswith(str(root))
