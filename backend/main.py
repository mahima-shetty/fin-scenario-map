from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
import re
import uuid

# Load .env from project root so DATABASE_URL is set (backend/.env or project .env)
try:
    from dotenv import load_dotenv
    _env_dir = Path(__file__).resolve().parent.parent
    load_dotenv(_env_dir / ".env")
except ImportError:
    pass

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
    from . import db
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
    import db

settings = get_settings()

# NA-style response when scenario not found (no hardcoded mock data)
def _na_result(scenario_id: str) -> dict:
    return {
        "scenarioName": "NA",
        "riskType": "NA",
        "description": "",
        "confidenceScore": None,
        "createdAt": "NA",
        "recommendations": [],
        "historicalCases": [],
        "step_log": [],
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: one log file per run; init DB; preload historical matcher
    init_run_log()
    try:
        db.init_db()
    except Exception:
        pass
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
    # Shutdown: nothing to do
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
    try:
        db.save_scenario(
            scenario_id,
            normalized["name"],
            normalized["description"],
            normalized["riskType"],
            result,
        )
    except Exception:
        pass  # log already in db layer if needed; do not fail the request
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
    try:
        stored = db.get_scenario_by_id(scenario_id)
    except Exception:
        stored = None
    if stored:
        # Use submitted input as fallback so "what you sent" always reflects on the page
        scenario_name = stored.get("scenarioName") or stored.get("inputName") or "NA"
        risk_type = stored.get("riskType") or stored.get("inputRiskType") or "NA"
        return {
            "scenarioName": scenario_name,
            "riskType": risk_type,
            "description": stored.get("inputDescription") or "",
            "confidenceScore": stored.get("confidenceScore"),
            "createdAt": stored.get("createdAt") or "NA",
            "recommendations": stored.get("recommendations") or [],
            "historicalCases": stored.get("historicalCases") or [],
            "step_log": stored.get("step_log") or [],
        }
    return _na_result(scenario_id)


@app.get("/api/historical-cases")
def list_historical_cases():
    """Return the 50 preloaded reference cases for the Historical Cases UI tab. Seeds table if empty or missing."""
    try:
        cases = db.get_reference_cases_list()
    except Exception as e:
        cases = []
        try:
            from .run_log import get_run_logger
            get_run_logger().warning("historical-cases get_reference_cases_list failed: %s", e)
        except ImportError:
            from run_log import get_run_logger
            get_run_logger().warning("historical-cases get_reference_cases_list failed: %s", e)
    if not cases:
        try:
            db.init_db()
            db.seed_reference_cases()
            cases = db.get_reference_cases_list()
        except Exception as e:
            try:
                from .run_log import get_run_logger
                get_run_logger().warning("historical-cases seed failed: %s", e)
            except ImportError:
                from run_log import get_run_logger
                get_run_logger().warning("historical-cases seed failed: %s", e)
    return {"cases": cases or []}