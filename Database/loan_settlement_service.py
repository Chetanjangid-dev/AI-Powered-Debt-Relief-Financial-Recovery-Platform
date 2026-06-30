"""
loan_settlement_service.py
---------------------------
Business logic layer for Loan & Settlement Processing.
Sits on top of models.py — handles the rules around how a loan moves
through its lifecycle (active -> settled/defaulted) and how
settlement offers are created, accepted, or rejected.

Depends on: database.py, models.py
Used by: backend developer's FastAPI routes, e.g.
         POST /loans/{id}/payment
         POST /settlements/{id}/accept
         POST /settlements/{id}/reject
"""

from sqlalchemy.orm import Session
import models


class LoanProcessingError(Exception):
    """Raised when a loan/settlement action violates a business rule."""
    pass


# ---------- LOAN LIFECYCLE ----------

def record_payment(db: Session, loan_id: int, payment_amount: float):
    """
    Reduces a loan's outstanding balance by payment_amount.
    Automatically marks the loan as 'settled' once balance hits zero.
    """
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise LoanProcessingError("Loan not found")
    if loan.status == "settled":
        raise LoanProcessingError("Cannot record payment on an already settled loan")
    if payment_amount <= 0:
        raise LoanProcessingError("Payment amount must be positive")
    if payment_amount > loan.outstanding_balance:
        raise LoanProcessingError("Payment exceeds outstanding balance")

    loan.outstanding_balance -= payment_amount
    if loan.outstanding_balance <= 0:
        loan.outstanding_balance = 0
        loan.status = "settled"

    db.commit()
    db.refresh(loan)
    return loan


def mark_loan_defaulted(db: Session, loan_id: int):
    """Manually flags a loan as defaulted (e.g. missed payments)."""
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise LoanProcessingError("Loan not found")
    loan.status = "defaulted"
    db.commit()
    db.refresh(loan)
    return loan


# ---------- SETTLEMENT LIFECYCLE ----------

def validate_settlement_amount(loan: models.Loan, recommended_amount: float):
    """
    Business rule: a settlement offer cannot exceed the loan's
    current outstanding balance, and must be greater than zero.
    """
    if recommended_amount <= 0:
        raise LoanProcessingError("Settlement amount must be positive")
    if recommended_amount > loan.outstanding_balance:
        raise LoanProcessingError("Settlement amount cannot exceed outstanding balance")


def create_settlement_offer(db: Session, loan_id: int, recommended_amount: float, strategy_text: str = None):
    """
    Creates a new settlement offer for a loan after validating it
    against the loan's current outstanding balance. Percentage is
    auto-calculated relative to the outstanding balance.
    """
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise LoanProcessingError("Loan not found")

    validate_settlement_amount(loan, recommended_amount)
    percentage = round((recommended_amount / loan.outstanding_balance) * 100, 2)

    settlement = models.SettlementRecommendation(
        loan_id=loan_id,
        recommended_settlement_amount=recommended_amount,
        settlement_percentage=percentage,
        negotiation_strategy=strategy_text,
        status="pending",
    )
    db.add(settlement)
    db.commit()
    db.refresh(settlement)
    return settlement


def accept_settlement(db: Session, settlement_id: int):
    """
    Accepts a settlement offer:
    - marks the settlement as 'accepted'
    - zeroes out the loan's outstanding balance
    - marks the loan as 'settled'
    """
    settlement = db.query(models.SettlementRecommendation).filter(
        models.SettlementRecommendation.id == settlement_id
    ).first()
    if not settlement:
        raise LoanProcessingError("Settlement not found")
    if settlement.status != "pending":
        raise LoanProcessingError(f"Settlement is already {settlement.status}")

    loan = db.query(models.Loan).filter(models.Loan.id == settlement.loan_id).first()
    if not loan:
        raise LoanProcessingError("Associated loan not found")

    settlement.status = "accepted"
    loan.outstanding_balance = 0
    loan.status = "settled"

    db.commit()
    db.refresh(settlement)
    db.refresh(loan)
    return settlement


def reject_settlement(db: Session, settlement_id: int):
    """Marks a settlement offer as rejected (loan stays active)."""
    settlement = db.query(models.SettlementRecommendation).filter(
        models.SettlementRecommendation.id == settlement_id
    ).first()
    if not settlement:
        raise LoanProcessingError("Settlement not found")
    settlement.status = "rejected"
    db.commit()
    db.refresh(settlement)
    return settlement


# ---------- SUMMARY / DASHBOARD HELPER ----------

def get_loan_with_settlements(db: Session, loan_id: int):
    """
    Returns a loan along with its full settlement offer history,
    most recent first. Useful for the dashboard view.
    """
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise LoanProcessingError("Loan not found")
    settlements = db.query(models.SettlementRecommendation).filter(
        models.SettlementRecommendation.loan_id == loan_id
    ).order_by(models.SettlementRecommendation.created_at.desc()).all()
    return {"loan": loan, "settlements": settlements}