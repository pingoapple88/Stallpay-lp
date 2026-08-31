from __future__ import annotations

import hashlib
import hmac
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum

from fastapi import HTTPException, status

from .config import Settings


class Role(IntEnum):
    TESTER = 20
    SUPER_ADMIN = 100


@dataclass(frozen=True)
class SessionPrincipal:
    actor_hash: str
    role: Role


class IAuthorizationProvider(ABC):
    @abstractmethod
    def authenticate_tester(self, supplied_key: str | None) -> SessionPrincipal:
        """Authenticate a field tester."""

    @abstractmethod
    def authenticate_manager(self, supplied_key: str | None) -> SessionPrincipal:
        """Authenticate a high-level manager."""


class EnvHeaderAuthorizationProvider(IAuthorizationProvider):
    def __init__(self, settings: Settings) -> None:
        self._tester_key = settings.tester_access_key
        self._manager_key = settings.manager_access_key
        self._audit_salt = settings.audit_hash_salt

    def _authenticate(self, supplied_key: str | None, expected_key: str, role: Role) -> SessionPrincipal:
        if not expected_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ACCESS_CONTROL_NOT_CONFIGURED",
            )
        if not supplied_key or not hmac.compare_digest(supplied_key, expected_key):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
        digest = hashlib.sha256(f"{self._audit_salt}:{role.name}:{supplied_key}".encode("utf-8")).hexdigest()
        return SessionPrincipal(actor_hash=digest, role=role)

    def authenticate_tester(self, supplied_key: str | None) -> SessionPrincipal:
        if self._manager_key and supplied_key and hmac.compare_digest(supplied_key, self._manager_key):
            return self._authenticate(supplied_key, self._manager_key, Role.SUPER_ADMIN)
        return self._authenticate(supplied_key, self._tester_key, Role.TESTER)

    def authenticate_manager(self, supplied_key: str | None) -> SessionPrincipal:
        return self._authenticate(supplied_key, self._manager_key, Role.SUPER_ADMIN)
