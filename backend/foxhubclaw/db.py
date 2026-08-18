from __future__ import annotations

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from foxhubclaw.config import settings
from foxhubclaw.models import Base, User, UserSetting


def _engine_url() -> str:
    url = settings.database_url
    if url.startswith("sqlite:///./"):
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{(settings.data_dir / 'foxhubclaw.sqlite3').resolve().as_posix()}"
    return url


engine = create_engine(_engine_url(), future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)
    if settings.mode == "desktop":
        with SessionLocal() as session:
            user = session.scalar(select(User).where(User.username == "desktop"))
            if user is None:
                user = User(username="desktop", email=None, is_admin=True, is_active=True)
                session.add(user)
                session.flush()
                session.add(UserSetting(user_id=user.id))
                session.commit()


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def desktop_user(session: Session) -> User:
    user = session.scalar(select(User).where(User.username == "desktop"))
    if user is None:
        raise RuntimeError("desktop user missing")
    return user
