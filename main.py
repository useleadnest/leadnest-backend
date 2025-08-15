# main.py
import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

try:
    import stripe as stripe_sdk
except Exception:
    stripe_sdk = None

app = FastAPI(title="LeadNest Backend", version="0.1.0", openapi_url="/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://useleadnest.com",
        "https://www.useleadnest.com",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"ok": True, "service": "leadnest-backend"}

@app.get("/health")
def health():
    return {"status": "ok"}

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

@app.post("/api/auth/register")
async def register_user(payload: RegisterIn):
    return {"email": payload.email, "created": True}

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
if stripe_sdk and os.getenv("STRIPE_SECRET_KEY"):
    stripe_sdk.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    if not stripe_sdk or not STRIPE_WEBHOOK_SECRET:
        return {"received": True, "verified": False, "type": None}
    try:
        event = stripe_sdk.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"received": True, "verified": True, "type": event.get("type")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))


