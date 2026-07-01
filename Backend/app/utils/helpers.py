from datetime import date
from typing import Optional


def calculate_overdue_days(emi_due_date: Optional[date]) -> int:
    """Returns how many days overdue a loan is. 0 if not overdue or no date provided."""
    if not emi_due_date:
        return 0
    delta = (date.today() - emi_due_date).days
    return max(0, delta)


def round_to_two(value: float) -> float:
    """Rounds a float to 2 decimal places for clean financial output."""
    return round(value, 2)


def safe_divide(numerator: float, denominator: float, fallback: float = 0.0) -> float:
    """Divides two numbers safely, returning fallback if denominator is zero."""
    if denominator == 0:
        return fallback
    return numerator / denominator


def format_currency(amount: float) -> str:
    """Formats a number as Indian Rupee string. e.g. 150000 → '₹1,50,000.00'"""
    return f"₹{amount:,.2f}"