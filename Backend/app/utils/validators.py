from app.utils.exceptions import ValidationError


def validate_positive(value: float, field_name: str) -> float:
    """Ensures a numeric value is greater than zero."""
    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than zero.")
    return value


def validate_percentage(value: float, field_name: str) -> float:
    """Ensures a percentage value is between 0 and 100."""
    if not (0 <= value <= 100):
        raise ValidationError(f"{field_name} must be between 0 and 100.")
    return value


def validate_income_vs_expenses(income: float, expenses: float) -> None:
    """Ensures income is greater than expenses for meaningful financial analysis."""
    if expenses >= income:
        raise ValidationError(
            "Monthly expenses cannot be equal to or greater than monthly income. "
            "Please review your financial inputs."
        )


def validate_loan_amount_vs_balance(loan_amount: float, outstanding_balance: float) -> None:
    """Ensures outstanding balance does not exceed original loan amount."""
    if outstanding_balance > loan_amount:
        raise ValidationError(
            "Outstanding balance cannot exceed the original loan amount."
        )