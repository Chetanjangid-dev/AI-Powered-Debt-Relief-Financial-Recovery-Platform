from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.services.gemini_service import call_gemini
from app.services.financial_engine import run_financial_analysis
from app.utils.exceptions import AIServiceError

router = APIRouter(prefix="/ai", tags=["AI"])


class NegotiationLetterRequest(BaseModel):
    """
    Request body for generating a negotiation letter.
    Scenario 2 from project README.
    Frontend sends borrower + loan data, gets back AI-generated letter.
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
    Generates a professional negotiation letter using Gemini AI.
    Scenario 2: Frontend sends borrower + loan data, gets back a letter.
    Automatically falls back to rule-based system if Gemini is unavailable.
    Returns: negotiation letter text + strategy + financial tips + source
    """
    # Step 1: Run financial analysis
    analysis = run_financial_analysis(
        loan_amount=request.loan_amount,
        outstanding_balance=request.outstanding_balance,
        interest_rate=request.interest_rate,
        tenure_months=request.tenure_months,
        monthly_income=request.monthly_income,
        monthly_expenses=request.monthly_expenses,
        emi_amount=request.emi_amount,
    )

    # Step 2: Call Gemini AI (falls back automatically if Gemini unavailable)
    result = call_gemini(
        debt_stress_level=analysis["debt_stress_level"],
        financial_health_score=analysis["financial_health_score"],
        emi_ratio=analysis["emi_ratio"],
        monthly_surplus=analysis["monthly_surplus"],
        outstanding_balance=request.outstanding_balance,
        recommended_settlement_amount=analysis["recommended_settlement_amount"],
        settlement_percentage=analysis["settlement_percentage"],
        lender_name=request.lender_name,
        borrower_name=request.borrower_name,
    )

    return {
        "success": True,
        "source": result["source"],
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
    """
    gemini_active = bool(settings.GEMINI_API_KEY)
    return {
        "gemini_active": gemini_active,
        "fallback_active": not gemini_active,
        "message": "Gemini AI active." if gemini_active else "Running on fallback.",
    }