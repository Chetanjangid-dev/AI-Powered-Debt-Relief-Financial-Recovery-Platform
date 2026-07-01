"""
db_optimization.py
------------------
Performance Optimization for AI Powered Debt Relief Platform.
Adds database indexes on frequently queried columns to speed up:
  - User lookup by email (login)
  - Loan lookup by user_id and status
  - Settlement lookup by loan_id and status
  - Financial metrics lookup by user_id
  - Negotiation letters lookup by settlement_id

Run this file once after init_db.py to apply all indexes.

Usage:
    python db_optimization.py

Depends on: database.py, models.py
"""

from sqlalchemy import Index, text
from database import engine, SessionLocal
import models


def create_indexes():
    """Creates all performance indexes on the database."""

    indexes = [
        # Users table
        Index("ix_users_email", models.User.email),

        # Loans table
        Index("ix_loans_user_id", models.Loan.user_id),
        Index("ix_loans_status", models.Loan.status),
        Index("ix_loans_user_status", models.Loan.user_id, models.Loan.status),

        # Monthly financials table
        Index("ix_monthly_financials_user_id", models.MonthlyFinancial.user_id),
        Index("ix_monthly_financials_month", models.MonthlyFinancial.month),

        # Settlement recommendations table
        Index("ix_settlements_loan_id", models.SettlementRecommendation.loan_id),
        Index("ix_settlements_status", models.SettlementRecommendation.status),

        # Negotiation letters table
        Index("ix_letters_settlement_id", models.NegotiationLetter.settlement_id),

        # Financial metrics table
        Index("ix_metrics_user_id", models.FinancialMetric.user_id),
    ]

    print("Applying performance indexes...")
    for index in indexes:
        try:
            index.create(bind=engine, checkfirst=True)
            print(f"  ✓ Index created: {index.name}")
        except Exception as e:
            print(f"  ! Skipped {index.name}: {e}")

    print("\nRunning ANALYZE to update query planner statistics...")
    with engine.connect() as conn:
        conn.execute(text("ANALYZE"))
        conn.commit()

    print("\nPerformance optimization complete.")
    print("All indexes applied and query planner updated.")


if __name__ == "__main__":
    create_indexes()