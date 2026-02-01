from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import LoginRequest, LoginResponse
from .users import verify_user

app = FastAPI(title="Login API")

# Allow requests from frontend
origins = [
    "http://localhost:5173",  # Vite dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
