from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import List

from app.schemas.response import SuccessResponse
from app.core.dependencies import require_role, get_current_user
from app.services import weekly_service

router = APIRouter(prefix="/weekly", tags=["weekly"])


@router.post("/upload", response_model=SuccessResponse)
async def upload_weekly_post(
    title: str = Form(...),
    caption: str = Form(...),
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(require_role("designer")),
):
    result = await weekly_service.upload_weekly_post(title, caption, files, current_user)
    return SuccessResponse(message="Weekly post uploaded", data=result)


@router.get("/weeks", response_model=SuccessResponse)
async def list_weeks(current_user: dict = Depends(get_current_user)):
    result = await weekly_service.list_weeks()
    return SuccessResponse(message="Weeks fetched", data=result)