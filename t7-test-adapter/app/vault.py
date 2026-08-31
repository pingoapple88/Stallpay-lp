from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import timezone

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .database import AuditLog, CredentialVersion


class CredentialVaultError(RuntimeError):
    pass


@dataclass(frozen=True)
class CredentialMaterial:
    version_id: str
    company: str
    token: str
    source: str


class CredentialVault:
    def __init__(self, encryption_key: str, audit_hash_salt: str, tenant_id: str) -> None:
        if not encryption_key or not audit_hash_salt or not tenant_id:
            raise CredentialVaultError("encryption, audit, and tenant configuration are required")
        try:
            self._fernet = Fernet(encryption_key.encode("ascii"))
        except (ValueError, TypeError) as exc:
            raise CredentialVaultError("invalid CREDENTIAL_ENCRYPTION_KEY") from exc
        self._audit_hash_salt = audit_hash_salt.encode("utf-8")
        self._tenant_id = tenant_id

    def _encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode("utf-8")).decode("ascii")

    def _decrypt(self, value: str) -> str:
        try:
            return self._fernet.decrypt(value.encode("ascii")).decode("utf-8")
        except (InvalidToken, ValueError, TypeError) as exc:
            raise CredentialVaultError("credential decryption failed") from exc

    def _fingerprint(self, value: str) -> str:
        return hmac.new(self._audit_hash_salt, value.encode("utf-8"), hashlib.sha256).hexdigest()

    def _active_record(self, session: Session) -> CredentialVersion | None:
        statement = (
            select(CredentialVersion)
            .where(
                CredentialVersion.tenant_id == self._tenant_id,
                CredentialVersion.is_active.is_(True),
            )
            .order_by(CredentialVersion.created_at_utc.desc())
            .limit(1)
        )
        return session.scalar(statement)

    def bootstrap_if_empty(self, session: Session, company: str, token: str) -> CredentialVersion | None:
        if self._active_record(session) is not None:
            return None
        if not company or not token:
            return None
        actor_hash = self._fingerprint("ENV_BOOTSTRAP")
        return self._create_version(session, company, token, actor_hash, "ENV_BOOTSTRAP")

    def active_material(self, session: Session) -> CredentialMaterial:
        record = self._active_record(session)
        if record is None:
            raise CredentialVaultError("ACTIVE_CREDENTIAL_NOT_CONFIGURED")
        return CredentialMaterial(
            version_id=record.id,
            company=self._decrypt(record.company_ciphertext),
            token=self._decrypt(record.token_ciphertext),
            source=record.source,
        )

    def status(self, session: Session) -> dict[str, object]:
        record = self._active_record(session)
        if record is None:
            return {
                "configured": False,
                "active_version_id": None,
                "company_masked": None,
                "token_configured": False,
                "company_fingerprint_prefix": None,
                "token_fingerprint_prefix": None,
                "source": None,
                "updated_at_utc": None,
            }
        company = self._decrypt(record.company_ciphertext)
        company_masked = company if len(company) <= 4 else f"{company[:2]}***{company[-2:]}"
        created = record.created_at_utc
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return {
            "configured": True,
            "active_version_id": record.id,
            "company_masked": company_masked,
            "token_configured": True,
            "company_fingerprint_prefix": record.company_fingerprint[:12],
            "token_fingerprint_prefix": record.token_fingerprint[:12],
            "source": record.source,
            "updated_at_utc": created.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

    def replace(self, session: Session, company: str, token: str, actor_hash: str, reason: str) -> CredentialVersion:
        company = company.strip()
        token = token.strip()
        if not company or len(company) > 128:
            raise CredentialVaultError("company is required and must be at most 128 characters")
        if len(token) < 8 or len(token) > 512:
            raise CredentialVaultError("token length is invalid")
        return self._create_version(session, company, token, actor_hash, "MANAGER_UPDATE", reason=reason)

    def rollback(self, session: Session, target_version_id: str, actor_hash: str, reason: str) -> CredentialVersion:
        target = session.get(CredentialVersion, target_version_id)
        if target is None or target.tenant_id != self._tenant_id:
            raise CredentialVaultError("TARGET_VERSION_NOT_FOUND")
        company = self._decrypt(target.company_ciphertext)
        token = self._decrypt(target.token_ciphertext)
        return self._create_version(
            session,
            company,
            token,
            actor_hash,
            "MANAGER_ROLLBACK",
            source_version_id=target.id,
            reason=reason,
        )

    def _create_version(
        self,
        session: Session,
        company: str,
        token: str,
        actor_hash: str,
        source: str,
        source_version_id: str | None = None,
        reason: str = "bootstrap",
    ) -> CredentialVersion:
        previous = self._active_record(session)
        session.execute(
            update(CredentialVersion)
            .where(
                CredentialVersion.tenant_id == self._tenant_id,
                CredentialVersion.is_active.is_(True),
            )
            .values(is_active=False)
        )
        record = CredentialVersion(
            tenant_id=self._tenant_id,
            company_ciphertext=self._encrypt(company),
            token_ciphertext=self._encrypt(token),
            company_fingerprint=self._fingerprint(company),
            token_fingerprint=self._fingerprint(token),
            is_active=True,
            source=source,
            created_by_hash=actor_hash,
            previous_version_id=previous.id if previous else source_version_id,
        )
        session.add(record)
        session.flush()
        details = {
            "company_fingerprint_prefix": record.company_fingerprint[:12],
            "token_fingerprint_prefix": record.token_fingerprint[:12],
            "source_version_id": source_version_id,
            "reason_fingerprint": self._fingerprint(reason),
        }
        session.add(
            AuditLog(
                tenant_id=self._tenant_id,
                actor_hash=actor_hash,
                action="CREDENTIAL_ROLLBACK" if source == "MANAGER_ROLLBACK" else "CREDENTIAL_UPDATE",
                status="SUCCESS",
                credential_version_id=record.id,
                previous_version_id=previous.id if previous else None,
                details_json=json.dumps(details, separators=(",", ":"), sort_keys=True),
            )
        )
        session.commit()
        session.refresh(record)
        return record
