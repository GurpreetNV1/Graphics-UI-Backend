from fastapi import FastAPI, Request
from app.utils.api_responses import (APIError)
from fastapi.exceptions import RequestValidationError, HTTPException
from .config import (ALLOWED_ORIGINS)
from fastapi.middleware.cors import CORSMiddleware

allowed_origins=ALLOWED_ORIGINS
app = FastAPI(
    title="Graphics Team Storage",
)

@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    print(f"API Error: {exc.message} | Status: {exc.status_code}")
    return exc.to_response()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    validation_errors = exc.errors()
    print(f"Validation Errors: {validation_errors}") 
    
    custom_error = APIError(
        status_code=422,
        message="Validation failed",
        errors=validation_errors
    )
    return custom_error.to_response()

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    print(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    custom_error = APIError(
        status_code=exc.status_code,
        message=str(exc.detail),
        errors=[]
    )
    return custom_error.to_response()

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    print(f" Unhandled Exception: {str(exc)}")
    
    custom_error = APIError(
        status_code=500,
        message="Internal Server Error",
        errors=[str(exc)]
    )
    return custom_error.to_response()



@app.middleware("http")
async def log_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    print(f"Request received from Origin: {origin}")
    response = await call_next(request)
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def root():
    return{
        "message":"Sys Active"
    }
