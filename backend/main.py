from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
import re
import uuid

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
    from .run_log import init_run_log
    from .workflow.runner import run_scenario_workflow
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
    from run_log import init_run_log
    from workflow.runner import run_scenario_workflow

settings = get_settings()

# In-memory store for scenario results (keyed by scenario_id)
_scenario_results: dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: one log file per run; remove any previous run's log
    init_run_log()
    # Preload historical matcher dataset so first scenario submit doesn't timeout
    try:
        from .historical_matcher import preload_dataset
        preload_dataset()
    except Exception:
        try:
            from historical_matcher import preload_dataset
            preload_dataset()
        except Exception:
            pass
    yield
    # Shutdown: nothing to do for run log (file stays for inspection until next run)
    pass


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name, lifespan=lifespan)

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
    scenario_id = f"scn-{uuid.uuid4().hex[:8]}"
    result = run_scenario_workflow(scenario_id, normalized)
    _scenario_results[scenario_id] = result
    normalized["scenario_id"] = scenario_id
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
    stored = _scenario_results.get(scenario_id)
    if stored:
        return {
            "scenarioName": stored.get("scenarioName", scenario_id),
            "riskType": stored.get("riskType", "Market Risk"),
            "confidenceScore": stored.get("confidenceScore", 0.82),
            "createdAt": stored.get("createdAt", ""),
            "recommendations": stored.get("recommendations", []),
            "historicalCases": stored.get("historicalCases", []),
            "step_log": stored.get("step_log", []),
        }
    # Fallback mock when no stored result (e.g. old ID or direct URL)
    return {
        "scenarioName": f"Scenario {scenario_id}",
        "riskType": "Market Risk",
        "confidenceScore": 0.82,
        "createdAt": "",
        "recommendations": [
            "Increase capital buffer by 10%",
            "Reprice floating-rate products",
            "Hedge long-term exposure",
        ],
        "historicalCases": [
            {"id": "HC-001", "name": "2018 Rate Hike", "similarity": "87%"},
            {"id": "HC-002", "name": "2020 Inflation Spike", "similarity": "79%"},
        ],
        "step_log": [],
    }