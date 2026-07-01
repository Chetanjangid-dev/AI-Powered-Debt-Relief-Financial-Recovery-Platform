from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from app.core.database import get_db
from app.services.financial_engine import run_financial_analysis
from app.services.fallback_service import generate_fallback_recommendation
from app.utils.exceptions import NotFoundError, DatabaseError

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "Database"))
import crud
import schemas

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


class SettlementActionRequest(BaseModel):
    """Request body for accepting or rejecting a settlement."""
    settlement_id: int
    action: str = Field(..., description="Must be 'accept' or 'reject'")


@router.post("/recommend")
def get_settlement_recommendation(request: SettlementRequest, db: Session = Depends(get_db)):
    """
    Generates a settlement recommendation using the Financial Engine + Fallback Service.
    This is the Scenario 1 endpoint from the project README.
    Flow: Frontend → this endpoint → Financial Engine → Fallback Service → DB save → Frontend
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

    # Step 2: Generate recommendation via fallback (Gemini replaces this in Task 7)
    recommendation = generate_fallback_recommendation(
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
            user_id=request.user_id,
            loan_id=request.loan_id,
            recommended_amount=analysis["recommended_settlement_amount"],
            settlement_percentage=analysis["settlement_percentage"],
            ai_recommendation=recommendation["negotiation_strategy"],
            status="pending",
        )
        saved = crud.create_settlement(db=db, settlement=settlement_data)
        recommendation["settlement_id"] = saved.id
    except Exception as e:
        # Don't fail the whole request if DB save fails — still return recommendation
        recommendation["settlement_id"] = None
        recommendation["db_warning"] = f"Recommendation generated but not saved: {str(e)}"

    recommendation["analysis"] = analysis
    return {"success": True, "recommendation": recommendation}


@router.get("/{settlement_id}")
def get_settlement(settlement_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single settlement record by ID.
    Frontend uses this to show settlement detail view.
    """
    settlement = crud.get_settlement(db=db, settlement_id=settlement_id)
    if not settlement:
        raise NotFoundError("Settlement", settlement_id)
    return settlement


@router.get("/user/{user_id}")
def get_user_settlements(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all settlement records for a user.
    Frontend uses this to populate settlement history on dashboard.
    """
    settlements = crud.get_settlements_by_user(db=db, user_id=user_id)
    return {"user_id": user_id, "settlements": settlements, "total": len(settlements)}