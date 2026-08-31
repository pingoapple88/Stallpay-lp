from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlsplit


class ConfigurationError(RuntimeError):
    """Raised when the adapter is not safely configured."""


@dataclass(frozen=True)
class Settings:
    api_base_url: str
    company: str
    token: str
    tester_access_key: str
    manager_access_key: str
    credential_encryption_key: str
    audit_hash_salt: str
    database_url: str
    tenant_id: str
    allowed_origins: tuple[str, ...]
    connect_timeout_seconds: float
    read_timeout_seconds: float

    @property
    def credentials_configured(self) -> bool:
        return bool(
            self.company
            and self.token
            and self.tester_access_key
            and self.manager_access_key
            and self.credential_encryption_key
            and self.audit_hash_salt
            and self.database_url
            and self.tenant_id
        )

    @property
    def upstream_host(self) -> str:
        return urlsplit(self.api_base_url).hostname or ""

    @classmethod
    def from_env(cls) -> "Settings":
        base_url = os.getenv("TIANLAI_API_BASE_URL", "").strip().rstrip("/")
        company = os.getenv("TIANLAI_COMPANY", "").strip()
        token = os.getenv("TIANLAI_TOKEN", "").strip()
        tester_access_key = os.getenv("T7_TESTER_ACCESS_KEY", "").strip()
        manager_access_key = os.getenv("T7_MANAGER_ACCESS_KEY", "").strip()
        encryption_key = os.getenv("CREDENTIAL_ENCRYPTION_KEY", "").strip()
        audit_hash_salt = os.getenv("AUDIT_HASH_SALT", "").strip()
        database_url = os.getenv("DATABASE_URL", "").strip()
        tenant_id = os.getenv("T7_TENANT_ID", "").strip()
        origins = tuple(
            origin.strip().rstrip("/")
            for origin in os.getenv("T7_ALLOWED_ORIGINS", "").split(",")
            if origin.strip()
        )
        connect_timeout = float(os.getenv("TIANLAI_CONNECT_TIMEOUT_SECONDS", "5"))
        read_timeout = float(os.getenv("TIANLAI_READ_TIMEOUT_SECONDS", "15"))

        if base_url:
            parts = urlsplit(base_url)
            if parts.scheme != "https" or not parts.hostname or parts.path not in ("", "/"):
                raise ConfigurationError("TIANLAI_API_BASE_URL must be an HTTPS origin without a path")
        if connect_timeout <= 0 or read_timeout <= 0:
            raise ConfigurationError("timeouts must be positive")

        return cls(
            api_base_url=base_url,
            company=company,
            token=token,
            tester_access_key=tester_access_key,
            manager_access_key=manager_access_key,
            credential_encryption_key=encryption_key,
            audit_hash_salt=audit_hash_salt,
            database_url=database_url,
            tenant_id=tenant_id,
            allowed_origins=origins,
            connect_timeout_seconds=connect_timeout,
            read_timeout_seconds=read_timeout,
        )
