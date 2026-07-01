import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "Database"))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_database
from app.api import health, loan, financial, settlement, ai, user
from app.services.financial_engine import run_financial_analysis
from app.services.gemini_service import call_gemini

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


# ── URL Aliases for Frontend compatibility ─────────────────────────────────────
# These endpoints match exactly what Chetali's api.js calls
# Backend handles ALL field name differences — frontend needs zero changes


@app.post("/api/auth/register")
async def alias_register(request: Request):
    """Alias: /api/auth/register → /api/v1/auth/register"""
    body = await request.json()
    from app.api.user import register, RegisterRequest
    from app.core.database import get_db
    db = next(get_db())
    return register(RegisterRequest(**body), db)


@app.post("/api/auth/login")
async def alias_login(request: Request):
    """Alias: /api/auth/login → /api/v1/auth/login"""
    body = await request.json()
    from app.api.user import login, LoginRequest
    from app.core.database import get_db
    db = next(get_db())
    return login(LoginRequest(**body), db)


@app.get("/api/dashboard")
async def alias_dashboard():
    """
    Dashboard overview endpoint.
    Frontend calls this on load to show financial summary.
    Returns zero values until user submits loan details.
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
    """
    Settlement prediction endpoint.
    Accepts Chetali's frontend field names AND standard names — both work.
    Returns response in exact format Chetali's SettlementPredictor.jsx expects.
    Chetali reads: result.recommended_settlement, result.settlement_percentage,
                   result.savings, result.strategy, result.confidence,
                   result.monthly_payment_plan
    """
    body = await request.json()

    # Accept both Chetali's field names and standard names
    loan_amount = float(body.get("loan_amount") or body.get("original_balance") or 1)
    outstanding_balance = float(body.get("outstanding_balance") or body.get("current_balance") or 1)
    interest_rate = float(body.get("interest_rate") or 12.0)
    tenure_months = int(body.get("tenure_months") or body.get("months_delinquent") or 12)
    monthly_income = float(body.get("monthly_income") or body.get("monthly_payment_capacity") or 1)
    # If monthly_expenses not provided, estimate as 60% of income
    monthly_expenses = float(body.get("monthly_expenses") or monthly_income * 0.6)

    # Safety check — expenses can't exceed income
    if monthly_expenses >= monthly_income:
        monthly_expenses = monthly_income * 0.6

    analysis = run_financial_analysis(
        loan_amount=loan_amount,
        outstanding_balance=outstanding_balance,
        interest_rate=interest_rate,
        tenure_months=tenure_months,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
    )

    recommendation = call_gemini(
        debt_stress_level=analysis["debt_stress_level"],
        financial_health_score=analysis["financial_health_score"],
        emi_ratio=analysis["emi_ratio"],
        monthly_surplus=analysis["monthly_surplus"],
        outstanding_balance=outstanding_balance,
        recommended_settlement_amount=analysis["recommended_settlement_amount"],
        settlement_percentage=analysis["settlement_percentage"],
    )

    # Return in Chetali's exact expected format
    return {
        "success": True,
        "recommended_settlement": str(round(analysis["recommended_settlement_amount"], 2)),
        "settlement_percentage": f"{analysis['settlement_percentage']}%",
        "monthly_payment_plan": str(round(analysis["recommended_settlement_amount"] / 12, 2)),
        "confidence": (
            "High" if analysis["financial_health_score"] >= 70
            else "Medium" if analysis["financial_health_score"] >= 40
            else "Low"
        ),
        "strategy": recommendation["negotiation_strategy"],
        "savings": str(round(outstanding_balance - analysis["recommended_settlement_amount"], 2)),
        "analysis": analysis,
    }


@app.post("/api/negotiation/generate")
async def alias_negotiation(request: Request):
    """
    Negotiation letter generation endpoint.
    Accepts Chetali's frontend field names AND standard names — both work.
    Returns response in exact format Chetali's NegotiationEmail.jsx expects.
    Chetali reads: data.letter || data.content
    We return all three keys so any version of her code works.
    """
    body = await request.json()

    # Accept both Chetali's field names and standard names
    outstanding_balance = float(
        body.get("current_balance") or body.get("outstanding_balance") or 1
    )
    offer_amount = float(body.get("offer_amount") or outstanding_balance * 0.5)
    monthly_income = float(
        body.get("monthly_payment_capacity") or body.get("monthly_income") or offer_amount * 3
    )
    monthly_expenses = float(body.get("monthly_expenses") or monthly_income * 0.6)
    loan_amount = float(body.get("loan_amount") or outstanding_balance * 1.2)

    # Safety check
    if monthly_expenses >= monthly_income:
        monthly_expenses = monthly_income * 0.6

    analysis = run_financial_analysis(
        loan_amount=loan_amount,
        outstanding_balance=outstanding_balance,
        interest_rate=float(body.get("interest_rate") or 12.0),
        tenure_months=int(body.get("tenure_months") or 24),
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
    )

    result = call_gemini(
        debt_stress_level=analysis["debt_stress_level"],
        financial_health_score=analysis["financial_health_score"],
        emi_ratio=analysis["emi_ratio"],
        monthly_surplus=analysis["monthly_surplus"],
        outstanding_balance=outstanding_balance,
        recommended_settlement_amount=offer_amount,
        settlement_percentage=analysis["settlement_percentage"],
        lender_name=body.get("creditor_name") or body.get("lender_name") or "the Lender",
        borrower_name=body.get("borrower_name") or "[Borrower Name]",
    )

    # Return ALL possible key names Chetali might check
    # data.letter || data.content || data.negotiation_letter — all work
    return {
        "success": True,
        "letter": result["negotiation_letter"],
        "content": result["negotiation_letter"],
        "negotiation_letter": result["negotiation_letter"],
        "negotiation_strategy": result["negotiation_strategy"],
        "financial_tips": result["financial_tips"],
    }


@app.get("/api/rights")
async def alias_rights():
    """
    Borrower rights endpoint.
    Frontend KnowYourRights.jsx calls this on load.
    Returns list of legal rights borrowers have.
    """
    return {
        "rights": [
            {
                "title": "Right to Fair Debt Collection",
                "description": "Under the Fair Debt Collection Practices Act, debt collectors cannot harass, oppress, or abuse you in any way."
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
    """
    History endpoint.
    Frontend History.jsx calls this on load.
    Returns empty list — will connect to real data once user auth is fully integrated.
    """
    return {
        "history": [],
        "items": [],
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