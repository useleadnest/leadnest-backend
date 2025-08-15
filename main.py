# main.py
import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

# Try to load Stripe if it's installed; run without it if not
try:
    import stripe as stripe_sdk  # pip install stripe
except Exception:
    stripe_sdk = None

APP_NAME = "LeadNest Backend"

app = FastAPI(title=APP_NAME, version="0.1.0", openapi_url="/openapi.json")

# --- CORS ---
# Allow both apex and www domains (and localhost for dev).
default_origins = [
    "https://useleadnest.com",
    "https://www.useleadnest.com",
    "http://localhost:3000",
]
# Optional: add more origins via env (comma-separated)
extra_origins = os.getenv("CORS_ORIGINS")
if extra_origins:
    default_origins.extend([o.strip() for o in extra_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=default_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Basic routes ---
@app.get("/")
def root():
    return {"ok": True, "service": "leadnest-backend"}

@app.get("/health")
def health():
    return {"status": "ok"}

# --- Auth: Register (stub) ---
class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

@app.post("/api/auth/register")
async def register_user(payload: RegisterIn):
    """
    TODO: Replace this stub with real logic:
      - check if user exists
      - hash password
      - save to DB
      - (optional) create Stripe customer / start trial
    """
    return {"email": payload.email, "created": True}

# --- Stripe webhook (safe/no-op if Stripe isn't configured) ---
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
if stripe_sdk and os.getenv("STRIPE_SECRET_KEY"_


