"""
schemas.py
----------
Pydantic models used to validate incoming data before it touches the database.
Backend developer will use these as request bodies in FastAPI endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoanCreate(BaseModel):
    user_id: int
    lender_name: str = Field(..., min_length=2, max_length=150)
    loan_type: str
    loan_amount: float = Field(..., gt=0)
    interest_rate: float = Field(..., ge=0, le=100)
    outstanding_balance: float = Field(..., ge=0)
    tenure_months: int = Field(..., gt=0)
    emi_due_date: Optional[date] = None
    start_date: date


class MonthlyFinancialCreate(BaseModel):
    user_id: int
    month: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$")  # YYYY-MM
    monthly_income: float = Field(..., ge=0)
    monthly_expenses: float = Field(..., ge=0)


class SettlementCreate(BaseModel):
    loan_id: int
    recommended_settlement_amount: float = Field(..., gt=0)
    settlement_percentage: float = Field(..., ge=0, le=100)
    negotiation_strategy: Optional[str] = None