# LeadNest Backend Starter

Minimal FastAPI service ready for Render.

## Environment variables
- OPENAI_API_KEY (optional for now)
- STRIPE_PUBLIC_KEY
- STRIPE_SECRET_KEY
- STRIPE_WEBHOOK_SECRET (fill after creating the Stripe webhook)
- ALLOWED_ORIGINS (e.g., https://app.leadnest.ai,https://localhost:3000)

## Health
- `/` root
- `/health` health check
- `/stripe/webhook` placeholder endpoint