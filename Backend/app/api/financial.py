from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.services.financial_engine import run_financial_analysis
from app.utils.exceptions import DatabaseError

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "Database"))
import crud
import schemas

router = APIRouter(prefix="/financial", tags=["Financial Analysis"])


class FinancialAnalysisRequest(BaseModel):
    """
    Request body for financial analysis endpoint.
    Frontend sends this when user submits the financial form.
    emi_amount and emi_due_date are optional — will be calculated if not provided.
    """
    loan_amount: float = Field(..., gt=0, description="Original loan amount")
    outstanding_balance: float = Field(..., gt=0, description="Remaining balance")
    interest_rate: float = Field(..., ge=0, le=100, description="Annual interest rate %")
    tenure_months: int = Field(..., gt=0, description="Loan tenure in months")
    monthly_income: float = Field(..., gt=0, description="Borrower monthly income")
    monthly_expenses: float = Field(..., gt=0, description="Borrower monthly expenses")
    emi_amount: Optional[float] = Field(None, gt=0, description="Known EMI (optional)")
    emi_due_date: Optional[date] = Field(None, description="EMI due date (optional)")


class MonthlyFinancialRequest(BaseModel):
    """Request body for saving monthly financials to database."""
    user_id: int
    month: str = Field(..., description="Format: YYYY-MM")
    monthly_income: float = Field(..., gt=0)
    monthly_expenses: float = Field(..., gt=0)


@router.post("/analyze")
def analyze_finances(request: FinancialAnalysisRequest):
    """
    Core financial analysis endpoint — no DB required.
    Frontend sends loan + income data, gets back full financial metrics.
    Returns: EMI, surplus, ratios, stress level, health score, settlement recommendation
    """
    result = run_financial_analysis(
        loan_amount=request.loan_amount,
        outstanding_balance=request.outstanding_balance,
        interest_rate=request.interest_rate,
        tenure_months=request.tenure_months,
        monthly_income=request.monthly_income,
        monthly_expenses=request.monthly_expenses,
        emi_amount=request.emi_amount,
        emi_due_date=request.emi_due_date,
    )
    return {"success": True, "analysis": result}


@router.post("/monthly")
def save_monthly_financial(request: MonthlyFinancialRequest, db: Session = Depends(get_db)):
    """
    Saves monthly income/expense record to database.
    Frontend calls this after user submits monthly financial form.
    Returns: saved record confirmation
    """
    try:
        financial = schemas.MonthlyFinancialCreate(
            user_id=request.user_id,
            month=request.month,
            monthly_income=request.monthly_income,
            monthly_expenses=request.monthly_expenses,
        )
        record = crud.create_monthly_financial(db=db, financial=financial)
        return {"success": True, "record_id": record.id, "message": "Monthly financial data saved"}
    except Exception as e:
        raise DatabaseError(f"Failed to save monthly financial data: {str(e)}")


@router.get("/monthly/{user_id}")
def get_monthly_financials(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all monthly financial records for a user.
    Frontend uses this to populate financial history on dashboard.
    Returns: list of monthly financial records
    """
    records = crud.get_financials_by_user(db=db, user_id=user_id)
    return {"user_id": user_id, "records": records, "total": len(records)}


@router.post("/predict-settlement/{user_id}")
def predict_settlement_from_db(
    user_id: int,
    monthly_income: float,
    monthly_expenses: float,
    db: Session = Depends(get_db)
):
    """
    Predicts settlement using Khushi's settlement_prediction.py engine.
    Uses actual loan data from database for this user.
    Returns: full prediction with per-loan settlement amounts.
    """
    from settlement_prediction import generate_settlement_prediction, PredictionError

    try:
        result = generate_settlement_prediction(
            db=db,
            user_id=user_id,
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
        )
        return {"success": True, "prediction": result}
    except PredictionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise DatabaseError(f"Prediction failed: {str(e)}")