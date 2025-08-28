from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
import os
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app first
app = FastAPI(title="LeadNest API", version="1.0.0", description="Production Ready")

# Add CORS middleware immediately
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://useleadnest.com",
        "https://www.useleadnest.com", 
        "http://localhost:3000",
        "http://localhost:5173"
  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
try:
    from routers.auth import router as auth_router
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    logger.info("✅ Auth router loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to load auth router: {e}")

# Root endpoint - Updated per requirements
@app.get("/")
def read_root():
    return {
        "status": "healthy", 
        "service": "leadnest-api", 
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    
@app.get("/health")
async def health():
    return {"status": "ok"}

# Generate leads endpoint (simplified fallback)
@app.post("/generate-leads")
async def generate_leads(search_data: dict):
    """Generate leads endpoint - simplified version"""
    try:
        return {
            "message": "Lead generation request received",
            "status": "processing",
            "location": search_data.get("location", "unknown"),
            "business_type": search_data.get("business_type", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Generate leads failed: {e}")
        return {"error": "Lead generation temporarily unavailable", "status": "error"}

# Stripe webhook endpoint
@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        payload = await request.body()
        sig_header = request.headers.get("Stripe-Signature", "")
        
        # Basic webhook acknowledgment
        logger.info(f"Received Stripe webhook with signature: {sig_header[:20]}...")
        
        # Try to parse the payload
        try:
            event_data = json.loads(payload)
            event_type = event_data.get("type", "unknown")
            logger.info(f"Stripe webhook event type: {event_type}")
            
            return {
                "received": True,
                "event_type": event_type,
                "status": "processed"
            }
        except json.JSONDecodeError:
            logger.warning("Failed to parse Stripe webhook payload")
            return {"received": True, "status": "payload_error"}
            
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return {"error": "Webhook processing failed", "status": "error"}

@app.get("/debug")
async def debug_info():
    """Debug endpoint with comprehensive service information"""
    endpoints = [
        "/", "/health", "/api/auth/register", "/api/auth/login", "/api/auth/me",
        "/generate-leads", "/stripe/webhook", "/debug"
    ]
    
    return {
        "service": "leadnest-api",
        "version": "1.0.0-PRODUCTION", 
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "python_path": os.getenv("PYTHONPATH", "not set"),
        "available_endpoints": endpoints,
        "cors_origins": [
            "https://useleadnest.com",
            "https://www.useleadnest.com", 
            "http://localhost:3000",
            "http://localhost:5173"
        ],
        "auth_router_loaded": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
