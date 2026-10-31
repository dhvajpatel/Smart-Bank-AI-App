"""
SmartBank AI - FastAPI backend entrypoint.

Run:
    cd backend
    python load_data.py        # one-time: load CSVs into the DB
    uvicorn main:app --reload  # start the API server

Then open http://127.0.0.1:8000/docs for interactive Swagger docs.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import customers, analytics, loans, recommendations, admin

app = FastAPI(
    title="SmartBank AI",
    description="AI-Powered Banking Intelligence Platform - Finance Analytics, "
                "Loan Risk Prediction, Spend Analysis & Personalized Recommendations.",
    version="0.1.0",
)

# CORS_ORIGINS env var: comma-separated list of allowed origins.
# Defaults to "*" for local development.
# In production set it to your Vercel URL, e.g.:
#   CORS_ORIGINS=https://smart-bank-ai.vercel.app
_raw_origins = os.getenv("CORS_ORIGINS", "*")
if _raw_origins == "*":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=_raw_origins != "*",
)

app.include_router(customers.router)
app.include_router(analytics.router)
app.include_router(loans.router)
app.include_router(recommendations.router)
app.include_router(admin.router)


@app.on_event("startup")
async def warmup_models():
    """
    Eagerly load the ML models at startup so the first /loans/predict
    request isn't hit with a 10-20 s cold-load on Render free tier.
    """
    try:
        from services import loan_service
        loan_service._load()
        print("✓ ML models loaded and ready.")
    except Exception as exc:
        print(f"⚠ Model warm-up failed (will retry on first request): {exc}")


@app.get("/")
def root():
    return {
        "message": "SmartBank AI backend is running.",
        "docs": "/docs",
        "modules": ["customers", "analytics", "loans", "recommendations", "admin"],
    }
