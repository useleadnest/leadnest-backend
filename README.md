ALLOWED_ORIGINS=https://useleadnest.com,https://www.useleadnest.com,http://localhost:3000

STRIPE_SECRET_KEY=sk_live_xxx_or_sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx       # from Stripe webhook “Signing secret”
STRIPE_PUBLISHABLE_KEY=pk_live_xxx_or_pk_test_xxx  # (not required on server, optional)

JWT_SECRET=generate-a-long-random-string
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require
ENV=production
