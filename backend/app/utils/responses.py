from typing import Any
from fastapi.responses import JSONResponse


def success_response(
    data: Any = None, message: str = "Success", status_code: int = 200
) -> JSONResponse:
    """Create standard JSON response structure for successful requests."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data,
        },
    )


def error_response(
    message: str = "An error occurred",
    details: Any = None,
    status_code: int = 400,
) -> JSONResponse:
    """Create standard JSON response structure for failed requests."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "details": details,
        },
    )
