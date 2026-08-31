from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class CredentialVersion(Base):
    __tablename__ = "t7_tianlai_credential_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    company_ciphertext: Mapped[str] = mapped_column(Text, nullable=False)
    token_ciphertext: Mapped[str] = mapped_column(Text, nullable=False)
    company_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    token_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    created_by_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    previous_version_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t7_tianlai_credential_versions.id"), nullable=True
    )


class AuditLog(Base):
    __tablename__ = "t7_tianlai_audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    occurred_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    actor_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    credential_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    previous_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class Database:
    def __init__(self, database_url: str) -> None:
        if not database_url:
            raise ValueError("DATABASE_URL is required")
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        self.engine = create_engine(database_url, pool_pre_ping=True, connect_args=connect_args)
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)

    def session(self) -> Iterator[Session]:
        with self.session_factory() as session:
            yield session
