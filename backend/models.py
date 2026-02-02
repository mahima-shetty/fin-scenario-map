from pydantic import BaseModel, EmailStr
from pydantic import Field
from enum import Enum

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str


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


class ScenarioInputRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    riskType: RiskType


class ScenarioInputResponse(BaseModel):
    status: str = "received"
    data: dict


class ScenarioUploadResponse(BaseModel):
    filename: str
    content_type: str | None = None
    size_bytes: int
