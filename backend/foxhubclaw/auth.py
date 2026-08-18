from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from foxhubclaw.config import settings
from foxhubclaw.db import desktop_user, get_db
from foxhubclaw.models import User

bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.token_hours),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def user_from_access_token(token: str, session: Session) -> User:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="登录已过期") from exc
    user = session.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=403, detail="账号不可用")
    return user


def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: Session = Depends(get_db),
) -> User:
    if settings.mode == "desktop":
        return desktop_user(session)
    if creds is None:
        raise HTTPException(status_code=401, detail="请先登录")
    return user_from_access_token(creds.credentials, session)


def current_file_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    token: str | None = Query(default=None),
    session: Session = Depends(get_db),
) -> User:
    """Report files are opened as normal browser navigations, so they cannot send Authorization."""
    if settings.mode == "desktop":
        return desktop_user(session)
    raw = creds.credentials if creds else token
    if not raw:
        raise HTTPException(status_code=401, detail="请先登录")
    return user_from_access_token(raw, session)


def require_admin(user: User = Depends(current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


def find_user(session: Session, login: str) -> User | None:
    return session.scalar(select(User).where((User.username == login) | (User.email == login)))
