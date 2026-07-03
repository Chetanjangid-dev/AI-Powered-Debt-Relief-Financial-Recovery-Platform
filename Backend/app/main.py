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
    allow_origins=[
    "http://localhost:5173",
    "http://localhost:3000",
    "https://ai-powered-debt-relief-financial-re.vercel.app",
    "https://ai-powered-debt-relief-financial-recovery-platform-2dmrzx7qg.vercel.app",
  ],
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
    Returns list with both 'points' array AND 'description' — both formats work.
    """
    return {
        "rights": [
            {
                "title": "Fair Debt Collection Practices Act (FDCPA)",
                "icon": "🛡️",
                "summary": "Protects you from abusive, unfair, or deceptive debt collection practices.",
                "description": "Protects you from abusive, unfair, or deceptive debt collection practices.",
                "points": [
                    "Collectors cannot call before 8 AM or after 9 PM",
                    "You can request written validation of the debt within 30 days",
                    "Collectors must stop contact if you send a cease-and-desist letter",
                    "Harassment, threats, and false statements are prohibited",
                ]
            },
            {
                "title": "Right to Debt Validation",
                "icon": "📄",
                "summary": "You have the right to request proof that you owe the debt.",
                "description": "You have the right to request proof that you owe the debt.",
                "points": [
                    "Send a validation request within 30 days of first contact",
                    "Collector must provide amount owed, creditor name, and verification",
                    "Collection must pause until validation is provided",
                    "Dispute inaccurate information in writing",
                ]
            },
            {
                "title": "Statute of Limitations",
                "icon": "⏳",
                "summary": "Debts have a time limit after which they cannot be legally enforced.",
                "description": "Debts have a time limit after which they cannot be legally enforced.",
                "points": [
                    "Varies by state (typically 3-6 years for credit card debt)",
                    "Making a payment may restart the clock in some states",
                    "Expired debts can still appear on credit reports for 7 years",
                    "You can still be contacted, but not sued after expiration",
                ]
            },
            {
                "title": "Credit Reporting Rights",
                "icon": "📊",
                "summary": "You have rights regarding how debts appear on your credit report.",
                "description": "You have rights regarding how debts appear on your credit report.",
                "points": [
                    "Request free credit reports from AnnualCreditReport.com",
                    "Dispute inaccurate items with credit bureaus",
                    "Settled debts should be reported as Paid or Settled",
                    "Negative items must be removed after 7 years",
                ]
            },
            {
                "title": "Settlement Agreement Protections",
                "icon": "🤝",
                "summary": "Always get settlement terms in writing before paying.",
                "description": "Always get settlement terms in writing before paying.",
                "points": [
                    "Require written confirmation of payment in full status",
                    "Specify how the account will be reported to credit bureaus",
                    "Keep copies of all correspondence and payment records",
                    "Never give collectors access to your bank account",
                ]
            },
            {
                "title": "Right to Negotiate Settlement",
                "icon": "⚖️",
                "summary": "You have the right to negotiate a settlement for less than the full amount owed.",
                "description": "You have the right to negotiate a settlement for less than the full amount owed.",
                "points": [
                    "Lenders often prefer settlement over non-payment",
                    "Start negotiations at 40-50% of outstanding balance",
                    "Always get the agreed settlement in writing first",
                    "Consult a financial advisor for complex situations",
                ]
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
