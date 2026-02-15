from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
import csv
import io
import json
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


@app.get("/api/status")
def get_status():
    """Return vector store status so you can verify ChromaDB is used (vector_store should be 'chromadb')."""
    try:
        from .historical_matcher import get_vector_store_status
        return get_vector_store_status()
    except Exception:
        try:
            from historical_matcher import get_vector_store_status
            return get_vector_store_status()
        except Exception:
            return {"vector_store": "unknown", "embedding_backend": ""}


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
        db.save_scenario_case(
            scenario_id,
            source="input",
            name=normalized["name"],
            description=normalized["description"],
            risk_type=normalized["riskType"],
            file_name=None,
        )
    except Exception:
        pass  # log already in db layer if needed; do not fail the request
    normalized["scenario_id"] = scenario_id
    return ScenarioInputResponse(data=normalized)




def _parse_upload_content(content: bytes, content_type: str | None, filename: str) -> list[dict]:
    """Parse JSON or CSV upload into list of {name, description, riskType/risk_type}. Returns [] on failure."""
    cases = []
    try:
        text = content.decode("utf-8", errors="replace").strip()
        if not text:
            return []
        if content_type and "json" in content_type:
            data = json.loads(text)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        cases.append({
                            "name": item.get("name") or item.get("title") or "",
                            "description": item.get("description") or "",
                            "riskType": item.get("riskType") or item.get("risk_type") or "Market",
                        })
            elif isinstance(data, dict):
                cases.append({
                    "name": data.get("name") or data.get("title") or "",
                    "description": data.get("description") or "",
                    "riskType": data.get("riskType") or data.get("risk_type") or "Market",
                })
        else:
            # CSV (or treat as CSV for .csv / text)
            reader = csv.DictReader(io.StringIO(text))
            for row in reader:
                name = (row.get("name") or row.get("title") or row.get("Name") or "").strip()
                description = (row.get("description") or row.get("Description") or "").strip()
                risk = (row.get("risk_type") or row.get("riskType") or row.get("Risk Type") or "Market").strip()
                cases.append({"name": name, "description": description, "riskType": risk or "Market"})
    except Exception:
        pass
    return cases


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

    cases = _parse_upload_content(content, file.content_type, file.filename or "")
    if cases:
        try:
            db.save_scenario_cases_from_upload(cases, file.filename or "upload")
        except Exception:
            pass

    return ScenarioUploadResponse(
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=size_bytes,
    )


@app.get("/api/scenarios/recent")
def list_recent_scenarios(limit: int = 20):
    """Return most recent scenario submissions for the dashboard."""
    try:
        scenarios = db.get_recent_scenarios(limit=limit)
    except Exception as e:
        try:
            from .run_log import get_run_logger
            get_run_logger().warning("scenarios/recent get_recent_scenarios failed: %s", e)
        except ImportError:
            from run_log import get_run_logger
            get_run_logger().warning("scenarios/recent get_recent_scenarios failed: %s", e)
        scenarios = []
    return {"scenarios": scenarios}


@app.get("/api/scenarios/{scenario_id}/result")
def get_scenario_result(scenario_id: str):
    try:
        stored = db.get_scenario_by_id(scenario_id)
    except Exception:
        stored = None
    if stored:
        # stored already uses input fallback for name/risk in db.get_scenario_by_id
        scenario_name = (stored.get("scenarioName") or "").strip() or (stored.get("inputName") or "").strip() or "—"
        risk_type = (stored.get("riskType") or "").strip() or (stored.get("inputRiskType") or "").strip() or "—"
        description = (stored.get("inputDescription") or "").strip()
        created_at = (stored.get("createdAt") or "").strip() or "—"
        # Derive confidence from historical case similarities when not stored
        confidence = stored.get("confidenceScore")
        if confidence is None:
            hist = stored.get("historicalCases") or []
            if hist:
                total, n = 0.0, 0
                for h in hist:
                    sim = (h or {}).get("similarity") or ""
                    if isinstance(sim, str) and sim.endswith("%"):
                        try:
                            total += float(sim[:-1].strip()) / 100.0
                            n += 1
                        except ValueError:
                            pass
                if n:
                    confidence = round(total / n, 2)
        return {
            "scenarioName": scenario_name,
            "riskType": risk_type,
            "description": description,
            "confidenceScore": confidence,
            "createdAt": created_at,
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