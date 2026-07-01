import sys
import os

# Make Database/ importable from anywhere in the backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "Database"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_database
from app.api import health, loan, financial, settlement, ai

# ── App Creation ──────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="AI Powered Debt Relief & Financial Recovery Platform - Backend API",
    docs_url="/docs",       # Swagger UI at http://127.0.0.1:8000/docs
    redoc_url="/redoc",     # ReDoc UI at http://127.0.0.1:8000/redoc
)

# ── CORS Middleware ───────────────────────────────────────────────────────────
# Allows Frontend (React/Vite on port 5173) to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup Event ─────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    """Runs once when the server starts. Creates DB tables if they don't exist."""
    init_database()
    print(f"✅ {settings.APP_NAME} started successfully.")
    print(f"📄 API Docs: http://127.0.0.1:8000/docs")

# ── Routers ───────────────────────────────────────────────────────────────────
# Each router handles a specific domain of the API
app.include_router(health.router,     prefix=settings.API_PREFIX)
app.include_router(loan.router,       prefix=settings.API_PREFIX)
app.include_router(financial.router,  prefix=settings.API_PREFIX)
app.include_router(settlement.router, prefix=settings.API_PREFIX)
app.include_router(ai.router,         prefix=settings.API_PREFIX)

# ── Root Endpoint ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "http://127.0.0.1:8000/docs",
        "health": "http://127.0.0.1:8000/api/v1/health/",
        "version": settings.API_VERSION,
    }