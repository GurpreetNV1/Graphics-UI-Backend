from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import List

from app.schemas.response import SuccessResponse
from app.schemas.requests import WeeklyFeedbackPayload
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


@router.get("/posts", response_model=SuccessResponse)
async def list_posts(current_user: dict = Depends(get_current_user)):
    result = await weekly_service.list_posts()
    return SuccessResponse(message="Posts fetched", data=result)


@router.post("/posts/{post_id}/mark-done", response_model=SuccessResponse)
async def mark_post_done(
    post_id: str,
    payload: WeeklyFeedbackPayload,
    current_user: dict = Depends(get_current_user),
):
    result = await weekly_service.mark_post_done(post_id, payload.feedback)
    return SuccessResponse(message="Marked as posted", data=result)


@router.post("/posts/{post_id}/review", response_model=SuccessResponse)
async def add_review(
    post_id: str,
    payload: WeeklyFeedbackPayload,
    current_user: dict = Depends(get_current_user),
):
    result = await weekly_service.add_review(post_id, payload.feedback)
    return SuccessResponse(message="Review added", data=result)


@router.delete("/posts/{post_id}", response_model=SuccessResponse)
async def delete_post(
    post_id: str,
    current_user: dict = Depends(require_role("designer")),
):
    result = await weekly_service.delete_post(post_id)
    return SuccessResponse(message="Post deleted", data=result)