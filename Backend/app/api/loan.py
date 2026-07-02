from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.exceptions import NotFoundError, DatabaseError

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "Database"))
import crud
import schemas
import models

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.post("/", response_model=dict)
def create_loan(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    """
    Creates a new loan record for a user.
    Frontend sends: user_id, loan_amount, interest_rate, outstanding_balance,
                   loan_type, lender_name, tenure_months, start_date
    Returns: created loan object with generated ID
    """
    try:
        new_loan = crud.create_loan(db=db, loan=loan)
        return {"success": True, "loan_id": new_loan.id, "message": "Loan created successfully"}
    except Exception as e:
        raise DatabaseError(f"Failed to create loan: {str(e)}")


@router.get("/user/{user_id}")
def get_loans_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all loans belonging to a specific user.
    Frontend uses this to populate the loan list on dashboard.
    Returns: list of loan objects
    """
    loans = crud.get_loans_by_user(db=db, user_id=user_id)
    return {"user_id": user_id, "loans": loans, "total": len(loans)}


@router.get("/{loan_id}")
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single loan by ID.
    Uses direct DB query since crud.get_loan doesn't exist in teammate's crud.py
    Returns: full loan object or 404 if not found
    """
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise NotFoundError("Loan", loan_id)
    return loan


@router.delete("/{loan_id}")
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    """
    Deletes a loan record by ID.
    Returns: success confirmation
    """
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise NotFoundError("Loan", loan_id)
    try:
        crud.delete_loan(db=db, loan_id=loan_id)
        return {"success": True, "message": f"Loan {loan_id} deleted successfully"}
    except Exception as e:
        raise DatabaseError(f"Failed to delete loan: {str(e)}")