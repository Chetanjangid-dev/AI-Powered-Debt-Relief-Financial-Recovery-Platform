import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "Database"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_database
from app.api import health, loan, financial, settlement, ai, user

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="AI Powered Debt Relief & Financial Recovery Platform - Backend API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    init_database()
    print(f"✅ {settings.APP_NAME} started successfully.")
    print(f"📄 API Docs: http://127.0.0.1:8000/docs")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router,      prefix=settings.API_PREFIX)
app.include_router(user.router,        prefix=settings.API_PREFIX)
app.include_router(loan.router,        prefix=settings.API_PREFIX)
app.include_router(financial.router,   prefix=settings.API_PREFIX)
app.include_router(settlement.router,  prefix=settings.API_PREFIX)
app.include_router(ai.router,          prefix=settings.API_PREFIX)

# ── URL Aliases for Frontend compatibility ────────────────────────────────────
# Chetali's api.js calls these URLs — we map them to our existing endpoints

from fastapi import Request
from fastapi.responses import JSONResponse
from app.services.financial_engine import run_financial_analysis
from app.services.gemini_service import call_gemini

@app.post("/api/auth/register")
async def alias_register(request: Request):
    """Alias: maps frontend /api/auth/register → /api/v1/auth/register"""
    body = await request.json()
    from app.api.user import register, RegisterRequest
    from app.core.database import get_db
    db = next(get_db())
    return register(RegisterRequest(**body), db)


@app.post("/api/auth/login")
async def alias_login(request: Request):
    """Alias: maps frontend /api/auth/login → /api/v1/auth/login"""
    body = await request.json()
    from app.api.user import login, LoginRequest
    from app.core.database import get_db
    db = next(get_db())
    return login(LoginRequest(**body), db)


@app.get("/api/dashboard")
async def alias_dashboard():
    """
    Dashboard overview endpoint.
    Frontend calls this to get summary data.
    Returns placeholder structure — connects to real data once user_id is passed.
    """
    return {
        "totalDebt": 0,
        "monthlyIncome": 0,
        "monthlyExpenses": 0,
        "disposableIncome": 0,
        "debtToIncomeRatio": "0%",
        "financialHealthScore": 0,
        "loans": [],
        "message": "Submit your loan details to see your financial overview."
    }


@app.post("/api/settlement/predict")
async def alias_settlement(request: Request):
    """Alias: maps frontend /api/settlement/predict → our financial engine"""
    body = await request.json()
    analysis = run_financial_analysis(
        loan_amount=body.get("loan_amount", 0),
        outstanding_balance=body.get("outstanding_balance", 0),
        interest_rate=body.get("interest_rate", 0),
        tenure_months=body.get("tenure_months", 12),
        monthly_income=body.get("monthly_income", 0),
        monthly_expenses=body.get("monthly_expenses", 0),
    )
    recommendation = call_gemini(
        debt_stress_level=analysis["debt_stress_level"],
        financial_health_score=analysis["financial_health_score"],
        emi_ratio=analysis["emi_ratio"],
        monthly_surplus=analysis["monthly_surplus"],
        outstanding_balance=body.get("outstanding_balance", 0),
        recommended_settlement_amount=analysis["recommended_settlement_amount"],
        settlement_percentage=analysis["settlement_percentage"],
    )
    return {"success": True, "analysis": analysis, "recommendation": recommendation}


@app.post("/api/negotiation/generate")
async def alias_negotiation(request: Request):
    """Alias: maps frontend /api/negotiation/generate → our AI endpoint"""
    body = await request.json()
    analysis = run_financial_analysis(
        loan_amount=body.get("loan_amount", 0),
        outstanding_balance=body.get("outstanding_balance", 0),
        interest_rate=body.get("interest_rate", 0),
        tenure_months=body.get("tenure_months", 12),
        monthly_income=body.get("monthly_income", 0),
        monthly_expenses=body.get("monthly_expenses", 0),
    )
    result = call_gemini(
        debt_stress_level=analysis["debt_stress_level"],
        financial_health_score=analysis["financial_health_score"],
        emi_ratio=analysis["emi_ratio"],
        monthly_surplus=analysis["monthly_surplus"],
        outstanding_balance=body.get("outstanding_balance", 0),
        recommended_settlement_amount=analysis["recommended_settlement_amount"],
        settlement_percentage=analysis["settlement_percentage"],
        lender_name=body.get("lender_name", "the Lender"),
        borrower_name=body.get("borrower_name", "[Borrower Name]"),
    )
    return {
        "success": True,
        "negotiation_letter": result["negotiation_letter"],
        "negotiation_strategy": result["negotiation_strategy"],
        "financial_tips": result["financial_tips"],
    }


@app.get("/api/rights")
async def alias_rights():
    """Returns borrower rights information for the Know Your Rights page."""
    return {
        "rights": [
            {
                "title": "Right to Fair Debt Collection",
                "description": "Under the Fair Debt Collection Practices Act (FDCPA), debt collectors cannot harass, oppress, or abuse you."
            },
            {
                "title": "Right to Dispute a Debt",
                "description": "You have the right to dispute a debt within 30 days of first contact. The collector must stop collection until they verify the debt."
            },
            {
                "title": "Right to Request Debt Validation",
                "description": "You can request written verification of the debt including the amount owed and the name of the original creditor."
            },
            {
                "title": "Right to Stop Contact",
                "description": "You can request in writing that a debt collector stop contacting you. They must comply except to confirm no further contact or notify of legal action."
            },
            {
                "title": "Right to Sue for Violations",
                "description": "If a debt collector violates the FDCPA, you have the right to sue them in state or federal court within one year of the violation."
            },
            {
                "title": "Right to Negotiate Settlement",
                "description": "You have the right to negotiate a settlement for less than the full amount owed. Lenders often prefer settlement over non-payment."
            }
        ]
    }


@app.get("/api/history")
async def alias_history():
    """Returns settlement and negotiation history. Placeholder until auth is connected."""
    return {
        "history": [],
        "message": "Login to view your settlement and negotiation history."
    }


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "http://127.0.0.1:8000/docs",
        "health": "http://127.0.0.1:8000/api/v1/health/",
        "version": settings.API_VERSION,
    }