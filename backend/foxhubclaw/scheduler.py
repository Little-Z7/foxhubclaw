from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from foxhubclaw.db import SessionLocal
from foxhubclaw.models import QueryJob, User
from foxhubclaw.services import due_jobs, execute_query, load_list, next_run_time

_scheduler: BackgroundScheduler | None = None


def process_due_jobs() -> int:
    count = 0
    with SessionLocal() as session:
        for job in due_jobs(session):
            user = session.get(User, job.user_id)
            if user is None or not user.is_active:
                continue
            try:
                execute_query(
                    session,
                    user,
                    job.keyword,
                    load_list(job.platforms),
                    load_list(job.kinds),
                    job_id=job.id,
                )
            except Exception:
                session.rollback()
            job.next_run_at = next_run_time(job.cadence)
            session.commit()
            count += 1
    return count


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = BackgroundScheduler()
    _scheduler.add_job(process_due_jobs, "interval", minutes=1, id="foxhubclaw-due")
    _scheduler.start()
