from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    """Raised when a requested resource does not exist in the database."""
    def __init__(self, resource: str, resource_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with ID {resource_id} not found."
        )


class ValidationError(HTTPException):
    """Raised when input data fails business logic validation."""
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message
        )


class DatabaseError(HTTPException):
    """Raised when a database operation fails unexpectedly."""
    def __init__(self, message: str = "A database error occurred."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )


class AIServiceError(HTTPException):
    """Raised when Gemini AI call fails and no fallback is available."""
    def __init__(self, message: str = "AI service is temporarily unavailable."):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=message
        )


class InsufficientDataError(HTTPException):
    """Raised when financial calculations cannot proceed due to missing data."""
    def __init__(self, message: str = "Insufficient financial data to process request."):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )