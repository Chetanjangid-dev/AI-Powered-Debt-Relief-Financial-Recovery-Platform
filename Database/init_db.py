"""
init_db.py
----------
Run this file once to create all tables in the SQLite database.
This confirms database.py + models.py are wired correctly.

Usage:
    python init_db.py

After running, a file named debt_relief.db will appear in this folder
with all 6 tables created (users, loans, monthly_financials,
settlement_recommendations, negotiation_letters, financial_metrics).
"""

from database import engine, Base
import models  # noqa: F401  (import needed so models register with Base)

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done. Check for debt_relief.db in this folder.")
#verified