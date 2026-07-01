import math
from app.utils.helpers import round_to_two, safe_divide


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Calculates Equated Monthly Installment (EMI) using standard formula.
    EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    P = principal, r = monthly interest rate, n = tenure in months
    """
    if annual_rate == 0:
        return round_to_two(safe_divide(principal, tenure_months))

    monthly_rate = annual_rate / (12 * 100)
    power = math.pow(1 + monthly_rate, tenure_months)
    emi = principal * monthly_rate * power / (power - 1)
    return round_to_two(emi)


def calculate_monthly_surplus(income: float, expenses: float, emi: float) -> float:
    """
    Monthly surplus = income - expenses - EMI.
    Positive = borrower has money left. Negative = borrower is in deficit.
    """
    return round_to_two(income - expenses - emi)


def calculate_emi_ratio(emi: float, income: float) -> float:
    """
    EMI-to-income ratio = EMI / income * 100 (as percentage).
    Industry standard: above 40% is considered high risk.
    """
    return round_to_two(safe_divide(emi, income) * 100)


def calculate_debt_to_income_ratio(outstanding_balance: float, annual_income: float) -> float:
    """
    Debt-to-income ratio = outstanding balance / annual income * 100.
    Higher ratio = more debt relative to earnings.
    """
    return round_to_two(safe_divide(outstanding_balance, annual_income) * 100)


def calculate_expense_ratio(expenses: float, income: float) -> float:
    """
    Expense ratio = expenses / income * 100.
    Shows what percentage of income goes to living expenses alone.
    """
    return round_to_two(safe_divide(expenses, income) * 100)


def calculate_settlement_percentage(
    outstanding_balance: float,
    monthly_surplus: float,
    overdue_days: int
) -> float:
    """
    Estimates a realistic settlement offer percentage (what % of debt the lender might accept).
    Logic:
    - Base: 60% of outstanding balance
    - Lower surplus = lender may accept less (borrower has less capacity)
    - Higher overdue days = lender more willing to settle quickly
    Returns a percentage between 30% and 85%.
    """
    base_percentage = 60.0

    # Adjust for surplus: every 5000 surplus adds 2%
    surplus_adjustment = (monthly_surplus / 5000) * 2
    base_percentage += surplus_adjustment

    # Adjust for overdue: every 30 days overdue reduces by 3%
    overdue_adjustment = (overdue_days / 30) * 3
    base_percentage -= overdue_adjustment

    # Clamp between 30% and 85%
    return round_to_two(max(30.0, min(85.0, base_percentage)))