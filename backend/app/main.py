from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel

from app.core.config import get_settings


class GovernanceStatus(BaseModel):
    service: str
    environment: str
    formal_service_connected: bool
    external_integrations: str
    timestamp_utc: datetime


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/healthz", tags=["system"])
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.get("/api/v1/governance/status", response_model=GovernanceStatus, tags=["governance"])
def governance_status() -> GovernanceStatus:
    return GovernanceStatus(
        service=settings.app_name,
        environment=settings.environment,
        formal_service_connected=settings.formal_service_connected,
        external_integrations=(
            "blocked: owner approval and provider contracts required"
            if not settings.formal_service_connected
            else "configured through provider adapters"
        ),
        timestamp_utc=datetime.now(timezone.utc),
    )
