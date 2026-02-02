from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
import re

# Support running as either:
# - `uvicorn backend.main:app --reload` (package import)
# - `uvicorn main:app --reload` from within the `backend/` directory (module import)
try:
    from .models import (
        LoginRequest,
        LoginResponse,
        HealthResponse,
        ScenarioInputRequest,
        ScenarioInputResponse,
        ScenarioUploadResponse,
    )
    from .users import verify_user
    from .settings import get_settings
except ImportError:  # pragma: no cover
    from models import (
        LoginRequest,
        LoginResponse,
        HealthResponse,
        ScenarioInputRequest,
        ScenarioInputResponse,
        ScenarioUploadResponse,
    )
    from users import verify_user
    from settings import get_settings

settings = get_settings()


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_origin_regex=settings.cors_allow_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return application


app = create_app()


def _normalize_text(value: str) -> str:
    # Trim, collapse internal whitespace, keep readable output.
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return value

@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    if verify_user(request.email, request.password):
        return LoginResponse(success=True, message="Login successful")
    else:
        return LoginResponse(success=False, message="Invalid email or password")


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(service=settings.app_name, environment=settings.environment)


@app.post("/api/scenarios/input", response_model=ScenarioInputResponse)
def create_scenario(payload: ScenarioInputRequest):
    normalized = {
        "name": _normalize_text(payload.name),
        "description": _normalize_text(payload.description) if payload.description else "",
        "riskType": payload.riskType.value,
    }
    return ScenarioInputResponse(data=normalized)




@app.post("/api/scenarios/upload", response_model=ScenarioUploadResponse)
async def upload_scenario(file: UploadFile = File(...)):
    if file.content_type and file.content_type not in settings.allowed_upload_content_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file.content_type}",
        )

    content = await file.read()
    size_bytes = len(content)
    if size_bytes > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large (max {settings.max_upload_size_bytes} bytes)",
        )

    return ScenarioUploadResponse(
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=size_bytes,
    )


@app.get("/api/scenarios/{scenario_id}/result")
def get_scenario_result(scenario_id: str):
    # Mock result payload (shape matches frontend `ScenarioResultResponse`)
    return {
        "scenarioName": f"Scenario {scenario_id}",
        "riskType": "Market Risk",
        "confidenceScore": 0.82,
        "createdAt": "2026-02-01",
        "recommendations": [
            "Increase capital buffer by 10%",
            "Reprice floating-rate products",
            "Hedge long-term exposure",
        ],
        "historicalCases": [
            {"id": "HC-001", "name": "2018 Rate Hike", "similarity": "87%"},
            {"id": "HC-002", "name": "2020 Inflation Spike", "similarity": "79%"},
        ],
    }