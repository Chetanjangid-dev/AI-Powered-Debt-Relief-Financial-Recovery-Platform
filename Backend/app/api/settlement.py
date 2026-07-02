from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from app.core.database import get_db
from app.services.financial_engine import run_financial_analysis
from app.services.gemini_service import call_gemini
from app.utils.exceptions import NotFoundError, DatabaseError

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "Database"))
import crud
import schemas
import models

router = APIRouter(prefix="/settlement", tags=["Settlement"])


class SettlementRequest(BaseModel):
    """
    Request body for generating a settlement recommendation.
    Frontend sends this when user clicks 'Get Settlement Recommendation'.
    """
    user_id: int
    loan_id: int
    loan_amount: float = Field(..., gt=0)
    outstanding_balance: float = Field(..., gt=0)
    interest_rate: float = Field(..., ge=0, le=100)
    tenure_months: int = Field(..., gt=0)
    monthly_income: float = Field(..., gt=0)
    monthly_expenses: float = Field(..., gt=0)
    emi_amount: Optional[float] = None
    notes: Optional[str] = None


@router.post("/recommend")
def get_settlement_recommendation(request: SettlementRequest, db: Session = Depends(get_db)):
    """
    Generates a settlement recommendation using Financial Engine + Gemini AI.
    Scenario 1 from project README.
    Flow: Frontend → Financial Engine → Gemini AI → DB save → Frontend
    Returns: full recommendation with strategy, letter, tips, and settlement offer
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

    # Step 2: Generate recommendation via Gemini AI
    recommendation = call_gemini(
        debt_stress_level=analysis["debt_stress_level"],
        financial_health_score=analysis["financial_health_score"],
        emi_ratio=analysis["emi_ratio"],
        monthly_surplus=analysis["monthly_surplus"],
        outstanding_balance=request.outstanding_balance,
        recommended_settlement_amount=analysis["recommended_settlement_amount"],
        settlement_percentage=analysis["settlement_percentage"],
    )

    # Step 3: Save settlement recommendation to database
    try:
        settlement_data = schemas.SettlementCreate(
            loan_id=request.loan_id,
            recommended_settlement_amount=analysis["recommended_settlement_amount"],
            settlement_percentage=analysis["settlement_percentage"],
            negotiation_strategy=recommendation["negotiation_strategy"],
        )
        saved = crud.create_settlement(db=db, settlement=settlement_data)
        recommendation["settlement_id"] = saved.id
    except Exception as e:
        # Don't fail the whole request if DB save fails — still return recommendation
        recommendation["settlement_id"] = None
        recommendation["db_warning"] = f"Recommendation generated but not saved: {str(e)}"

    recommendation["analysis"] = analysis
    return {"success": True, "recommendation": recommendation}


@router.get("/user/{user_id}")
def get_user_settlements(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all settlement records for a user via their loans.
    Frontend uses this to populate settlement history on dashboard.
    """
    # Get all loans for this user first
    loans = crud.get_loans_by_user(db=db, user_id=user_id)
    all_settlements = []
    for loan in loans:
        settlements = crud.get_settlements_by_loan(db=db, loan_id=loan.id)
        all_settlements.extend(settlements)
    return {"user_id": user_id, "settlements": all_settlements, "total": len(all_settlements)}


@router.get("/{settlement_id}")
def get_settlement(settlement_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single settlement record by ID.
    Uses direct DB query since crud.get_settlement doesn't exist in teammate's crud.py
    Frontend uses this to show settlement detail view.
    """
    settlement = db.query(models.SettlementRecommendation).filter(
        models.SettlementRecommendation.id == settlement_id
    ).first()
    if not settlement:
        raise NotFoundError("Settlement", settlement_id)
    return settlement