from fastapi import APIRouter, Header, HTTPException

from app.integration_readiness import ExternalIntegrationRegistration, can_enable_production

router = APIRouter(prefix="/api/v1/mock/integrations", tags=["mock-integrations"])


def require_demo(x_demo_mode: str | None) -> None:
    if x_demo_mode != "true":
        raise HTTPException(status_code=403, detail="integration readiness mock requires X-Demo-Mode: true")


@router.post("/readiness", response_model=dict[str, bool])
def integration_readiness(registration: ExternalIntegrationRegistration, x_demo_mode: str | None = Header(default=None)) -> dict[str, bool]:
    require_demo(x_demo_mode)
    return {"can_enable_sandbox": registration.environment.value == "sandbox", "can_enable_production": can_enable_production(registration)}
