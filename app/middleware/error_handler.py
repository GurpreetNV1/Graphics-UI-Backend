from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException
from app.schemas.response import ErrorResponse

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(message=exc.message, error_code=exc.error_code).model_dump(),
    )

async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(message="Internal server error", error_code="INTERNAL_ERROR").model_dump(),
    )