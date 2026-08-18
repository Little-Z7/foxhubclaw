from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(160), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(200), default="")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    setting: Mapped["UserSetting | None"] = relationship(back_populates="user", uselist=False)


class UserSetting(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    api_key_encrypted: Mapped[str] = mapped_column(Text, default="")
    limit_per_platform: Mapped[int] = mapped_column(Integer, default=20)
    comment_depth: Mapped[int] = mapped_column(Integer, default=3)

    user: Mapped[User] = relationship(back_populates="setting")


class QueryJob(Base):
    __tablename__ = "query_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(160), default="")
    keyword: Mapped[str] = mapped_column(String(200))
    platforms: Mapped[str] = mapped_column(Text)
    kinds: Mapped[str] = mapped_column(String(80), default="post")
    cadence: Mapped[str] = mapped_column(String(20), default="once")
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class JobRun(Base):
    __tablename__ = "job_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("query_jobs.id"), nullable=True)
    keyword: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="running")
    item_count: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(Text, default="")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("job_runs.id"))
    keyword: Mapped[str] = mapped_column(String(200))
    xlsx_path: Mapped[str] = mapped_column(Text, default="")
    html_path: Mapped[str] = mapped_column(Text, default="")
    pdf_path: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
