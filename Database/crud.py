"""
crud.py
-------
All Create / Read / Update / Delete functions in one place.
Backend developer imports these functions inside FastAPI route handlers.
They never need to write raw SQLAlchemy queries themselves.
"""

from sqlalchemy.orm import Session
import models
import schemas


# ---------- USER ----------

def create_user(db: Session, user: schemas.UserCreate, password_hash: str):
    db_user = models.User(name=user.name, email=user.email, password_hash=password_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


# ---------- LOAN ----------

def create_loan(db: Session, loan: schemas.LoanCreate):
    db_loan = models.Loan(**loan.dict())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan


def get_loans_by_user(db: Session, user_id: int):
    return db.query(models.Loan).filter(models.Loan.user_id == user_id).all()


def update_loan_status(db: Session, loan_id: int, status: str):
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if db_loan:
        db_loan.status = status
        db.commit()
        db.refresh(db_loan)
    return db_loan


def delete_loan(db: Session, loan_id: int):
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if db_loan:
        db.delete(db_loan)
        db.commit()
    return db_loan


# ---------- MONTHLY FINANCIALS ----------

def create_monthly_financial(db: Session, data: schemas.MonthlyFinancialCreate):
    db_record = models.MonthlyFinancial(**data.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_financials_by_user(db: Session, user_id: int):
    return db.query(models.MonthlyFinancial).filter(models.MonthlyFinancial.user_id == user_id).all()


# ---------- SETTLEMENT ----------

def create_settlement(db: Session, settlement: schemas.SettlementCreate):
    db_settlement = models.SettlementRecommendation(**settlement.dict())
    db.add(db_settlement)
    db.commit()
    db.refresh(db_settlement)
    return db_settlement


def get_settlements_by_loan(db: Session, loan_id: int):
    return db.query(models.SettlementRecommendation).filter(
        models.SettlementRecommendation.loan_id == loan_id
    ).all()


def update_settlement_status(db: Session, settlement_id: int, status: str):
    db_settlement = db.query(models.SettlementRecommendation).filter(
        models.SettlementRecommendation.id == settlement_id
    ).first()
    if db_settlement:
        db_settlement.status = status
        db.commit()
        db.refresh(db_settlement)
    return db_settlement


# ---------- NEGOTIATION LETTER ----------

def save_negotiation_letter(db: Session, settlement_id: int, letter_content: str):
    db_letter = models.NegotiationLetter(settlement_id=settlement_id, letter_content=letter_content)
    db.add(db_letter)
    db.commit()
    db.refresh(db_letter)
    return db_letter


# ---------- FINANCIAL METRICS ----------

def save_financial_metric(db: Session, user_id: int, dti_ratio: float, health_score: float):
    db_metric = models.FinancialMetric(
        user_id=user_id,
        debt_to_income_ratio=dti_ratio,
        financial_health_score=health_score,
    )
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric