from typing import Optional
from datetime import date

from app.services.calculator import (
    calculate_emi,
    calculate_monthly_surplus,
    calculate_emi_ratio,
    calculate_debt_to_income_ratio,
    calculate_expense_ratio,
    calculate_settlement_percentage,
)
from app.utils.helpers import calculate_overdue_days, round_to_two
from app.utils.validators import (
    validate_positive,
    validate_percentage,
    validate_income_vs_expenses,
    validate_loan_amount_vs_balance,
)


def determine_debt_stress_level(emi_ratio: float, monthly_surplus: float) -> str:
    """
    Classifies debt stress into 4 levels based on EMI ratio and monthly surplus.
    LOW     → EMI ratio < 30% and surplus > 0
    MEDIUM  → EMI ratio 30–40% or surplus slightly negative
    HIGH    → EMI ratio 40–60% or surplus clearly negative
    CRITICAL→ EMI ratio > 60% or deep deficit
    """
    if emi_ratio > 60 or monthly_surplus < -10000:
        return "CRITICAL"
    elif emi_ratio > 40 or monthly_surplus < 0:
        return "HIGH"
    elif emi_ratio > 30 or monthly_surplus < 5000:
        return "MEDIUM"
    else:
        return "LOW"


def calculate_financial_health_score(
    emi_ratio: float,
    expense_ratio: float,
    monthly_surplus: float,
    overdue_days: int
) -> float:
    """
    Produces a financial health score out of 100.
    Higher = healthier financial position.
    Scoring breakdown:
    - EMI ratio (40 points): lower is better
    - Expense ratio (30 points): lower is better
    - Monthly surplus (20 points): higher is better
    - Overdue days (10 points): fewer is better
    """
    # EMI ratio score (40 pts): 0% ratio = 40pts, 100% ratio = 0pts
    emi_score = max(0, 40 - (emi_ratio * 0.4))

    # Expense ratio score (30 pts): 0% = 30pts, 100% = 0pts
    expense_score = max(0, 30 - (expense_ratio * 0.3))

    # Surplus score (20 pts): 20000+ surplus = 20pts, 0 = 10pts, negative = 0pts
    if monthly_surplus >= 20000:
        surplus_score = 20
    elif monthly_surplus >= 0:
        surplus_score = 10 + (monthly_surplus / 20000) * 10
    else:
        surplus_score = max(0, 10 + (monthly_surplus / 10000))

    # Overdue score (10 pts): 0 days = 10pts, 365+ days = 0pts
    overdue_score = max(0, 10 - (overdue_days / 365) * 10)

    total = emi_score + expense_score + surplus_score + overdue_score
    return round_to_two(min(100.0, total))


def run_financial_analysis(
    loan_amount: float,
    outstanding_balance: float,
    interest_rate: float,
    tenure_months: int,
    monthly_income: float,
    monthly_expenses: float,
    emi_amount: Optional[float] = None,
    emi_due_date: Optional[date] = None,
) -> dict:
    """
    Main entry point for the Financial Engine.
    Accepts loan and income data, returns complete financial analysis.

    Parameters:
    - loan_amount: original loan amount
    - outstanding_balance: remaining balance
    - interest_rate: annual interest rate (%)
    - tenure_months: loan duration in months
    - monthly_income: borrower's monthly income
    - monthly_expenses: borrower's monthly living expenses
    - emi_amount: optional override (if provided, skips EMI calculation)
    - emi_due_date: optional due date to compute overdue days

    Returns: dict with all computed financial metrics
    """
    # Validate inputs
    validate_positive(loan_amount, "Loan amount")
    validate_positive(outstanding_balance, "Outstanding balance")
    validate_positive(monthly_income, "Monthly income")
    validate_positive(monthly_expenses, "Monthly expenses")
    validate_positive(tenure_months, "Tenure months")
    validate_percentage(interest_rate, "Interest rate")
    validate_loan_amount_vs_balance(loan_amount, outstanding_balance)
    validate_income_vs_expenses(monthly_income, monthly_expenses)

    # Step 1: Calculate EMI
    emi = emi_amount if emi_amount else calculate_emi(
        outstanding_balance, interest_rate, tenure_months
    )

    # Step 2: Calculate overdue days
    overdue_days = calculate_overdue_days(emi_due_date)

    # Step 3: Core financial metrics
    monthly_surplus = calculate_monthly_surplus(monthly_income, monthly_expenses, emi)
    emi_ratio = calculate_emi_ratio(emi, monthly_income)
    annual_income = monthly_income * 12
    debt_to_income = calculate_debt_to_income_ratio(outstanding_balance, annual_income)
    expense_ratio = calculate_expense_ratio(monthly_expenses, monthly_income)

    # Step 4: Derived insights
    debt_stress = determine_debt_stress_level(emi_ratio, monthly_surplus)
    health_score = calculate_financial_health_score(
        emi_ratio, expense_ratio, monthly_surplus, overdue_days
    )
    settlement_pct = calculate_settlement_percentage(
        outstanding_balance, monthly_surplus, overdue_days
    )
    settlement_amount = round_to_two(outstanding_balance * settlement_pct / 100)

    return {
        "emi_amount": emi,
        "monthly_surplus": monthly_surplus,
        "emi_ratio": emi_ratio,
        "debt_to_income_ratio": debt_to_income,
        "expense_ratio": expense_ratio,
        "overdue_days": overdue_days,
        "debt_stress_level": debt_stress,
        "financial_health_score": health_score,
        "settlement_percentage": settlement_pct,
        "recommended_settlement_amount": settlement_amount,
    }