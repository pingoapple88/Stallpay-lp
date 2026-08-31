from __future__ import annotations

import hashlib
import json
from contextlib import asynccontextmanager
from datetime import timezone
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .auth import EnvHeaderAuthorizationProvider
from .config import ConfigurationError, Settings
from .database import AuditLog, Database
from .provider import TianlaiReadOnlyProvider
from .schemas import CredentialRollbackRequest, CredentialUpdateRequest, PreflightRequest
from .signing import AsciiSortedSha256SignatureProvider
from .vault import CredentialVault, CredentialVaultError


settings = Settings.from_env()
database: Database | None = None
vault: CredentialVault | None = None
configuration_error: str | None = None

try:
    if settings.database_url:
        database = Database(settings.database_url)
    if settings.credential_encryption_key and settings.audit_hash_salt:
        vault = CredentialVault(
            settings.credential_encryption_key,
            settings.audit_hash_salt,
            settings.tenant_id,
        )
except (ValueError, ConfigurationError, CredentialVaultError):
    configuration_error = "ADAPTER_CONFIGURATION_INVALID"

authorization = EnvHeaderAuthorizationProvider(settings)


def _require_database() -> Database:
    if database is None or vault is None or configuration_error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ADAPTER_NOT_CONFIGURED",
        )
    return database


def get_session(db: Annotated[Database, Depends(_require_database)]) -> Any:
    yield from db.session()


def _safe_details(**values: object) -> str:
    return json.dumps(values, separators=(",", ":"), sort_keys=True, ensure_ascii=True)


def _identifier_hash(value: str) -> str:
    salt = settings.audit_hash_salt.encode("utf-8") if settings.audit_hash_salt else b"not-configured"
    return hashlib.sha256(salt + b":" + value.encode("utf-8")).hexdigest()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if database is not None and vault is not None and not configuration_error:
        with database.session_factory() as session:
            vault.bootstrap_if_empty(session, settings.company, settings.token)
    yield


app = FastAPI(
    title="StallPay T7 Read-only Network Preflight Adapter",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

if settings.allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "OPTIONS"],
        allow_headers=["Content-Type", "X-T7-Test-Key", "X-T7-Manager-Key"],
        max_age=600,
    )


@app.middleware("http")
async def no_store_and_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, __: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": "INVALID_REQUEST"})


@app.get("/healthz")
def healthz() -> dict[str, object]:
    infrastructure_ready = bool(database is not None and vault is not None and not configuration_error)
    credentials_configured = False
    if infrastructure_ready and database is not None and vault is not None:
        with database.session_factory() as session:
            credentials_configured = bool(vault.status(session)["configured"])
    return {
        "status": "ok" if infrastructure_ready else "blocked",
        "service": "t7-readonly-preflight-adapter",
        "credentials_configured": credentials_configured,
        "database_configured": bool(settings.database_url),
        "manager_access_configured": bool(settings.manager_access_key),
        "tester_access_configured": bool(settings.tester_access_key),
        "mode": "READ_ONLY_TEST_ADAPTER",
        "formal_device_control": False,
        "completion_signal": False,
        "gate_06": "BLOCKED",
    }


@app.post("/api/v1/t7/network/preflight")
async def network_preflight(
    payload: PreflightRequest,
    session: Annotated[Session, Depends(get_session)],
    test_key: Annotated[str | None, Header(alias="X-T7-Test-Key")] = None,
) -> dict[str, object]:
    principal = authorization.authenticate_tester(test_key)
    assert vault is not None
    try:
        credentials = vault.active_material(session)
    except CredentialVaultError as exc:
        raise HTTPException(status_code=503, detail="ACTIVE_CREDENTIAL_NOT_CONFIGURED") from exc

    provider = TianlaiReadOnlyProvider(
        api_base_url=settings.api_base_url,
        signer_factory=AsciiSortedSha256SignatureProvider,
        connect_timeout_seconds=settings.connect_timeout_seconds,
        read_timeout_seconds=settings.read_timeout_seconds,
    )
    result = await provider.preflight(credentials, payload.client_time_utc.astimezone(timezone.utc).isoformat())
    session.add(
        AuditLog(
            tenant_id=settings.tenant_id,
            actor_hash=principal.actor_hash,
            action="READ_ONLY_NETWORK_PREFLIGHT",
            status=str(result["status"]),
            credential_version_id=credentials.version_id,
            details_json=_safe_details(
                run_id_hash=_identifier_hash(payload.run_id),
                device_id_hash=_identifier_hash(payload.device_id),
                device_role=payload.device_role,
                site_label_hash=_identifier_hash(payload.site_label),
                formal_device_control=False,
            ),
        )
    )
    session.commit()
    return {
        "schema_version": "T7-NETWORK-PREFLIGHT-01",
        "run_id": payload.run_id,
        "device_role": payload.device_role,
        "status": result["status"],
        "network": result,
        "mode": "READ_ONLY_TEST_ADAPTER",
        "evidence_level": "SANDBOX_CONNECTIVITY",
        "completion_signal": False,
        "gate_06": "BLOCKED",
        "test_device_verified": False,
    }


@app.get("/api/v1/t7/settings/status")
def credential_status(
    session: Annotated[Session, Depends(get_session)],
    manager_key: Annotated[str | None, Header(alias="X-T7-Manager-Key")] = None,
) -> dict[str, object]:
    authorization.authenticate_manager(manager_key)
    assert vault is not None
    return {
        "schema_version": "T7-CREDENTIAL-STATUS-01",
        "credential": vault.status(session),
        "token_returned": False,
    }


@app.put("/api/v1/t7/settings")
def replace_credentials(
    payload: CredentialUpdateRequest,
    session: Annotated[Session, Depends(get_session)],
    manager_key: Annotated[str | None, Header(alias="X-T7-Manager-Key")] = None,
) -> dict[str, object]:
    principal = authorization.authenticate_manager(manager_key)
    assert vault is not None
    try:
        record = vault.replace(session, payload.company, payload.token, principal.actor_hash, payload.reason)
    except CredentialVaultError as exc:
        raise HTTPException(status_code=422, detail="INVALID_CREDENTIAL_CONFIGURATION") from exc
    return {
        "status": "UPDATED",
        "active_version_id": record.id,
        "credential": vault.status(session),
        "token_returned": False,
        "reason_recorded": bool(payload.reason),
    }


@app.post("/api/v1/t7/settings/rollback")
def rollback_credentials(
    payload: CredentialRollbackRequest,
    session: Annotated[Session, Depends(get_session)],
    manager_key: Annotated[str | None, Header(alias="X-T7-Manager-Key")] = None,
) -> dict[str, object]:
    principal = authorization.authenticate_manager(manager_key)
    assert vault is not None
    try:
        record = vault.rollback(session, payload.target_version_id, principal.actor_hash, payload.reason)
    except CredentialVaultError as exc:
        raise HTTPException(status_code=404, detail="TARGET_VERSION_NOT_FOUND") from exc
    return {
        "status": "ROLLED_BACK",
        "active_version_id": record.id,
        "credential": vault.status(session),
        "token_returned": False,
        "reason_recorded": bool(payload.reason),
    }
