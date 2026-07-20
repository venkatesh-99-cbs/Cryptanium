from typing import Any
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.utils.responses import error_response


class BaseAppException(Exception):
    """Base custom application exception."""

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Any = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class UnauthorizedException(BaseAppException):
    def __init__(self, message: str = "Authentication credentials were invalid or missing."):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(BaseAppException):
    def __init__(self, message: str = "You do not have permission to access this resource."):
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundException(BaseAppException):
    def __init__(self, message: str = "The requested resource was not found."):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)


class ValidationException(BaseAppException):
    def __init__(self, message: str = "Input validation failed.", details: Any = None):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST, details=details)


async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    return error_response(message=exc.message, details=exc.details, status_code=exc.status_code)
