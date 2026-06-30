"""
models.py
---------
SQLAlchemy ORM models. Each class = one database table.
Backend developer will use these models inside FastAPI routes via crud.py functions.
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    loans = relationship("Loan", back_populates="user", cascade="all, delete-orphan")
    financials = relationship("MonthlyFinancial", back_populates="user", cascade="all, delete-orphan")
    metrics = relationship("FinancialMetric", back_populates="user", cascade="all, delete-orphan")


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lender_name = Column(String(150), nullable=False)
    loan_type = Column(String(50), nullable=False)          # e.g. personal, credit_card, auto
    loan_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    outstanding_balance = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    tenure_months = Column(Integer, nullable=False)
    emi_due_date = Column(Date, nullable=True)
    status = Column(String(30), default="active")           # active, settled, defaulted
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="loans")
    settlements = relationship("SettlementRecommendation", back_populates="loan", cascade="all, delete-orphan")


class MonthlyFinancial(Base):
    __tablename__ = "monthly_financials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month = Column(String(7), nullable=False)                # format: YYYY-MM
    monthly_income = Column(Float, nullable=False)
    monthly_expenses = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="financials")


class SettlementRecommendation(Base):
    __tablename__ = "settlement_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    recommended_settlement_amount = Column(Float, nullable=False)
    settlement_percentage = Column(Float, nullable=False)    # % of outstanding balance
    negotiation_strategy = Column(Text)                      # short AI-generated summary
    status = Column(String(30), default="pending")           # pending, accepted, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    loan = relationship("Loan", back_populates="settlements")
    letter = relationship(
        "NegotiationLetter", back_populates="settlement",
        uselist=False, cascade="all, delete-orphan"
    )


class NegotiationLetter(Base):
    __tablename__ = "negotiation_letters"

    id = Column(Integer, primary_key=True, index=True)
    settlement_id = Column(Integer, ForeignKey("settlement_recommendations.id"), nullable=False, unique=True)
    letter_content = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    settlement = relationship("SettlementRecommendation", back_populates="letter")


class FinancialMetric(Base):
    __tablename__ = "financial_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    debt_to_income_ratio = Column(Float, nullable=False)
    financial_health_score = Column(Float, nullable=False)   # 0-100 scale
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="metrics")