from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.exceptions import AppException
from app.middleware.error_handler import app_exception_handler, unhandled_exception_handler
from app.routers import auth, requests, weekly
from app.services import drive_client
from app.config import settings
from app.services import requests_sheets_client

app = FastAPI(title="Creative Request System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://graphics-ui-frontend.vercel.app",
        "http://graphics.acmemigration.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(auth.router)
app.include_router(requests.router)
app.include_router(weekly.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def health_check():
    return {"status": "ok"}

@app.head("/")
async def root_head() -> Response:
    return Response(status_code=200)


@app.get("/test-drive")
async def test_drive():
    folder = drive_client.create_folder("Test Request Folder", settings.google_test_folder_id)
    return {"created_folder": folder}


@app.get("/test-requests-sheet")
async def test_requests_sheet():
    result = await requests_sheets_client.list_requests()
    return {"requests": result}