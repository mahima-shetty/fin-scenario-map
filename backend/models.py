from pydantic import BaseModel, EmailStr, field_validator
from pydantic import Field
from enum import Enum

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: str | None = None
    token_type: str = "bearer"
    role: str | None = None


class RiskType(str, Enum):
    credit = "Credit"
    market = "Market"
    liquidity = "Liquidity"
    operational = "Operational"
    fraud = "Fraud"


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str
    environment: str


def _coerce_risk_type(v: str | RiskType) -> RiskType:
    if isinstance(v, RiskType):
        return v
    s = (v or "").strip().replace(" ", "").lower()
    if not s:
        return RiskType.market
    for r in RiskType:
        if r.value.lower() == s or r.name.lower() == s:
            return r
    if "credit" in s:
        return RiskType.credit
    if "liquidity" in s:
        return RiskType.liquidity
    if "operational" in s:
        return RiskType.operational
    if "fraud" in s:
        return RiskType.fraud
    return RiskType.market


class ScenarioInputRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    riskType: RiskType

    @field_validator("riskType", mode="before")
    @classmethod
    def normalize_risk_type(cls, v: str | RiskType) -> RiskType:
        return _coerce_risk_type(v)


class ScenarioInputResponse(BaseModel):
    status: str = "received"
    data: dict


class ScenarioUploadResponse(BaseModel):
    filename: str
    content_type: str | None = None
    size_bytes: int
    scenario_ids: list[str] = []  # one per scenario created from parsed CSV/JSON
