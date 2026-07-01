"""
settlement_prediction.py
-------------------------
Settlement Prediction System for AI Powered Debt Relief Platform.
Calculates:
  1. Debt-to-Income Ratio (DTI)
  2. Financial Health Score (0-100)
  3. Recommended Settlement Percentage based on financial health
  4. Saves results to financial_metrics table

Depends on: database.py, models.py
Used by: backend developer's FastAPI routes, e.g.
         POST /users/{id}/predict-settlement
"""

from sqlalchemy.orm import Session
import models


class PredictionError(Exception):
    """Raised when prediction inputs are invalid."""
    pass


# ---------- CORE CALCULATIONS ----------

def calculate_dti_ratio(monthly_income: float, total_monthly_debt_payments: float) -> float:
    """
    Debt-to-Income Ratio = (Total Monthly Debt Payments / Monthly Income) * 100
    Lower is better. Above 50% is considered high risk.
    """
    if monthly_income <= 0:
        raise PredictionError("Monthly income must be greater than zero")
    dti = (total_monthly_debt_payments / monthly_income) * 100
    return round(dti, 2)


def calculate_financial_health_score(
    monthly_income: float,
    monthly_expenses: float,
    total_outstanding_debt: float,
    dti_ratio: float
) -> float:
    """
    Financial Health Score (0-100). Higher is better.

    Scoring breakdown:
    - Income vs Expenses ratio   : 40 points
    - DTI ratio                  : 40 points
    - Debt load vs income        : 20 points
    """
    score = 0.0

    # 1. Income vs Expenses (40 points)
    if monthly_income > 0:
        savings_ratio = (monthly_income - monthly_expenses) / monthly_income
        if savings_ratio >= 0.3:
            score += 40
        elif savings_ratio >= 0.2:
            score += 30
        elif savings_ratio >= 0.1:
            score += 20
        elif savings_ratio >= 0:
            score += 10
        else:
            score += 0  # expenses exceed income

    # 2. DTI Ratio (40 points)
    if dti_ratio <= 20:
        score += 40
    elif dti_ratio <= 30:
        score += 30
    elif dti_ratio <= 40:
        score += 20
    elif dti_ratio <= 50:
        score += 10
    else:
        score += 0  # very high DTI

    # 3. Debt load vs Annual Income (20 points)
    annual_income = monthly_income * 12
    if annual_income > 0:
        debt_to_annual_income = total_outstanding_debt / annual_income
        if debt_to_annual_income <= 0.5:
            score += 20
        elif debt_to_annual_income <= 1.0:
            score += 15
        elif debt_to_annual_income <= 2.0:
            score += 10
        elif debt_to_annual_income <= 3.0:
            score += 5
        else:
            score += 0

    return round(min(score, 100.0), 2)


def predict_settlement_percentage(health_score: float) -> float:
    """
    Recommends what % of outstanding balance the borrower should offer
    as settlement, based on their financial health score.

    Lower health score = borrower is in more distress = lender may accept less.
    Higher health score = borrower can afford more = higher settlement offer needed.
    """
    if health_score >= 80:
        return 80.0   # healthy finances — offer 80% of outstanding
    elif health_score >= 60:
        return 65.0
    elif health_score >= 40:
        return 50.0
    elif health_score >= 20:
        return 35.0
    else:
        return 20.0   # severe distress — lender may accept 20%


# ---------- MAIN PREDICTION FUNCTION ----------

def generate_settlement_prediction(
    db: Session,
    user_id: int,
    monthly_income: float,
    monthly_expenses: float,
) -> dict:
    """
    Full prediction pipeline:
    1. Fetches all active loans for the user
    2. Calculates DTI ratio
    3. Calculates financial health score
    4. Predicts recommended settlement percentage
    5. Saves metrics to financial_metrics table
    6. Returns full prediction result

    Returns a dict with all calculated values + per-loan settlement amounts.
    """
    if monthly_income <= 0:
        raise PredictionError("Monthly income must be greater than zero")
    if monthly_expenses < 0:
        raise PredictionError("Monthly expenses cannot be negative")

    # Fetch active loans
    loans = db.query(models.Loan).filter(
        models.Loan.user_id == user_id,
        models.Loan.status == "active"
    ).all()

    if not loans:
        raise PredictionError("No active loans found for this user")

    # Calculate totals
    total_outstanding = sum(loan.outstanding_balance for loan in loans)
    # Estimate monthly debt payment as outstanding / tenure for each loan
    total_monthly_debt = sum(
        loan.outstanding_balance / loan.tenure_months
        for loan in loans if loan.tenure_months > 0
    )

    # Core calculations
    dti = calculate_dti_ratio(monthly_income, total_monthly_debt)
    health_score = calculate_financial_health_score(
        monthly_income, monthly_expenses, total_outstanding, dti
    )
    settlement_pct = predict_settlement_percentage(health_score)

    # Save to financial_metrics table
    metric = models.FinancialMetric(
        user_id=user_id,
        debt_to_income_ratio=dti,
        financial_health_score=health_score,
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)

    # Per-loan settlement amounts
    loan_predictions = []
    for loan in loans:
        recommended_amount = round(loan.outstanding_balance * (settlement_pct / 100), 2)
        loan_predictions.append({
            "loan_id": loan.id,
            "lender_name": loan.lender_name,
            "outstanding_balance": loan.outstanding_balance,
            "recommended_settlement_amount": recommended_amount,
            "settlement_percentage": settlement_pct,
        })

    return {
        "user_id": user_id,
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "total_outstanding_debt": total_outstanding,
        "debt_to_income_ratio": dti,
        "financial_health_score": health_score,
        "recommended_settlement_percentage": settlement_pct,
        "loan_predictions": loan_predictions,
        "metric_id": metric.id,
    }