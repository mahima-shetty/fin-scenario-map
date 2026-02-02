from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File

# Support running as either:
# - `uvicorn backend.main:app --reload` (package import)
# - `uvicorn main:app --reload` from within the `backend/` directory (module import)
try:
    from .models import LoginRequest, LoginResponse
    from .users import verify_user
except ImportError:  # pragma: no cover
    from models import LoginRequest, LoginResponse
    from users import verify_user

app = FastAPI(title="Login API")

# Allow requests from frontend
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",  # Vite dev server (alternate)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],  # allow POST, OPTIONS etc.
    allow_headers=["*"],
)

@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    if verify_user(request.email, request.password):
        return LoginResponse(success=True, message="Login successful")
    else:
        return LoginResponse(success=False, message="Invalid email or password")


@app.post("/api/scenarios/input")
def create_scenario(payload: dict):
    return {"status": "received", "data": payload}




@app.post("/api/scenarios/upload")
async def upload_scenario(file: UploadFile = File(...)):
    return {"filename": file.filename}


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