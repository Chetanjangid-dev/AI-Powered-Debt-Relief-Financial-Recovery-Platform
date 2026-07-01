from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from app.core.database import get_db
from app.services.fallback_service import generate_fallback_recommendation
from app.services.financial_engine import run_financial_analysis
from app.utils.exceptions import AIServiceError

router = APIRouter(prefix="/ai", tags=["AI"])


class NegotiationLetterRequest(BaseModel):
    """
    Request body for generating a negotiation letter.
    This is Scenario 2 from the project README.
    Gemini AI will replace fallback in Task 7.
    """
    loan_amount: float = Field(..., gt=0)
    outstanding_balance: float = Field(..., gt=0)
    interest_rate: float = Field(..., ge=0, le=100)
    tenure_months: int = Field(..., gt=0)
    monthly_income: float = Field(..., gt=0)
    monthly_expenses: float = Field(..., gt=0)
    emi_amount: Optional[float] = None
    lender_name: Optional[str] = "the Lender"
    borrower_name: Optional[str] = "[Borrower Name]"


@router.post("/negotiation-letter")
def generate_negotiation_letter(request: NegotiationLetterRequest):
    """
    Generates a professional negotiation letter.
    Scenario 2: Frontend sends borrower + loan data, gets back a letter.
    Currently uses fallback service. Gemini AI plugs in here during Task 7.
    Team Lead's Gemini integration will replace the fallback call below.
    Returns: negotiation letter text + strategy + financial tips
    """
    # Step 1: Run financial analysis to get metrics
    analysis = run_financial_analysis(
        loan_amount=request.loan_amount,
        outstanding_balance=request.outstanding_balance,
        interest_rate=request.interest_rate,
        tenure_months=request.tenure_months,
        monthly_income=request.monthly_income,
        monthly_expenses=request.monthly_expenses,
        emi_amount=request.emi_amount,
    )

    # Step 2: Generate letter via fallback (Gemini replaces this in Task 7)
    # INTEGRATION POINT FOR TEAM LEAD: replace the line below with gemini_service call
    result = generate_fallback_recommendation(
        debt_stress_level=analysis["debt_stress_level"],
        financial_health_score=analysis["financial_health_score"],
        emi_ratio=analysis["emi_ratio"],
        monthly_surplus=analysis["monthly_surplus"],
        outstanding_balance=request.outstanding_balance,
        recommended_settlement_amount=analysis["recommended_settlement_amount"],
        settlement_percentage=analysis["settlement_percentage"],
    )

    return {
        "success": True,
        "lender_name": request.lender_name,
        "borrower_name": request.borrower_name,
        "negotiation_letter": result["negotiation_letter"],
        "negotiation_strategy": result["negotiation_strategy"],
        "financial_tips": result["financial_tips"],
        "analysis_summary": {
            "health_score": analysis["financial_health_score"],
            "stress_level": analysis["debt_stress_level"],
            "settlement_offer": analysis["recommended_settlement_amount"],
        },
    }


@router.get("/status")
def ai_status():
    """
    Returns current AI service status.
    Frontend uses this to show whether Gemini AI is active or fallback is running.
    Team Lead updates GEMINI_ACTIVE to True once Gemini is integrated in Task 7.
    """
    return {
        "gemini_active": False,
        "fallback_active": True,
        "message": "Running on rule-based fallback. Gemini AI integration pending.",
    }