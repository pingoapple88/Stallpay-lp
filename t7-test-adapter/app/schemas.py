from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PreflightRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1, max_length=96, pattern=r"^[A-Za-z0-9._:-]+$")
    client_time_utc: datetime
    device_role: Literal["cargo_lane_machine", "pickup_machine"]
    device_id: str = Field(min_length=1, max_length=128)
    site_label: str = Field(min_length=1, max_length=128)


class CredentialUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company: str = Field(min_length=1, max_length=128)
    token: str = Field(min_length=8, max_length=512)
    reason: str = Field(min_length=3, max_length=256)


class CredentialRollbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_version_id: str = Field(min_length=36, max_length=36)
    reason: str = Field(min_length=3, max_length=256)
