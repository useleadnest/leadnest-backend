import os
import stripe
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LeadNest Backend")

# CORS
allowed = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allowed == ["*"] else [o.strip() for o in allowed if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"service": "leadnest-backend", "status": "ok"}

@app.get("/health")
def health():
    return {"ok": True}

# Stripe webhook (basic placeholder)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    # In test mode, allow empty secret to skip verification
    if not STRIPE_WEBHOOK_SECRET:
        return {"received": True, "verified": False}

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # TODO: handle event types your app needs
    # e.g., checkout.session.completed, customer.subscription.created
    return {"received": True, "type": getattr(event, "type", None)}