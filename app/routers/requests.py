from fastapi import APIRouter, Depends, UploadFile, File
from app.schemas.requests import CreateRequestPayload
from app.schemas.response import SuccessResponse
from app.core.dependencies import require_role, get_current_user
from app.services import request_service
from app.schemas.requests import CreateRequestPayload, RequestChangesPayload, UpdateRequestPayload, AddCommentPayload
from typing import List

router = APIRouter(prefix="/requests", tags=["requests"])

@router.post("", response_model=SuccessResponse)
async def create_request(payload: CreateRequestPayload, current_user: dict = Depends(require_role("employer", "admin")),):
    result = await request_service.create_request(current_user, payload)
    return SuccessResponse(message="Request created successfully", data=result)

@router.post("/{request_id}/raw-files", response_model=SuccessResponse)
async def upload_raw_files(request_id: str, files: List[UploadFile] = File(...), current_user: dict = Depends(require_role("employer", "admin")),):
    result = await request_service.upload_raw_files(request_id, files)
    return SuccessResponse(message="Files uploaded successfully", data=result)

@router.get("", response_model=SuccessResponse)
async def list_requests(current_user: dict = Depends(get_current_user)):
    result = await request_service.list_requests(current_user)
    return SuccessResponse(message="Requests fetched", data=result)

@router.get("/{request_id}", response_model=SuccessResponse)
async def get_request(request_id: str, current_user: dict = Depends(get_current_user)):
    result = await request_service.get_request(request_id)
    return SuccessResponse(message="Request fetched", data=result)

@router.post("/{request_id}/accept", response_model=SuccessResponse)
async def accept_request(request_id: str, current_user: dict = Depends(require_role("designer", "admin"))):
    result = await request_service.accept_request(request_id, current_user)
    return SuccessResponse(message="Request accepted", data=result)

@router.post("/{request_id}/deliverables", response_model=SuccessResponse)
async def upload_deliverables(request_id: str, files: List[UploadFile] = File(...), current_user: dict = Depends(require_role("designer", "admin"))):
    result = await request_service.upload_deliverables(request_id, files, current_user)
    return SuccessResponse(message="Deliverables uploaded successfully", data=result)

@router.post("/{request_id}/submit-review", response_model=SuccessResponse)
async def submit_for_review(request_id: str, current_user: dict = Depends(require_role("designer", "admin"))):
    result = await request_service.submit_for_review(request_id, current_user)
    return SuccessResponse(message="Submitted for review", data=result)

@router.post("/{request_id}/approve", response_model=SuccessResponse)
async def approve_request(request_id: str, current_user: dict = Depends(require_role("employer", "admin"))):
    result = await request_service.approve_request(request_id, current_user)
    return SuccessResponse(message="Request approved", data=result)

@router.post("/{request_id}/request-changes", response_model=SuccessResponse)
async def request_changes(request_id: str, payload: RequestChangesPayload, current_user: dict = Depends(require_role("employer", "admin"))):
    result = await request_service.request_changes(request_id, payload.reason, current_user)
    return SuccessResponse(message="Changes requested", data=result)

@router.patch("/{request_id}", response_model=SuccessResponse)
async def update_request(request_id: str, payload: UpdateRequestPayload, current_user: dict = Depends(require_role("employer", "admin"))):
    result = await request_service.update_request(request_id, payload, current_user)
    return SuccessResponse(message="Request updated", data=result)

@router.post("/{request_id}/cancel", response_model=SuccessResponse)
async def cancel_request(request_id: str, current_user: dict = Depends(require_role("employer", "admin")),):
    result = await request_service.cancel_request(request_id, current_user)
    return SuccessResponse(message="Request cancelled", data=result)

@router.post("/{request_id}/comments", response_model=SuccessResponse)
async def add_comment(request_id: str, payload: AddCommentPayload, current_user: dict = Depends(get_current_user)):
    result = await request_service.add_comment(request_id, payload.message, payload.comment_type, current_user)
    return SuccessResponse(message="Comment added", data=result)

@router.get("/{request_id}/comments", response_model=SuccessResponse)
async def get_comments(request_id: str, current_user: dict = Depends(get_current_user),):
    result = await request_service.get_comments(request_id)
    return SuccessResponse(message="Comments fetched", data=result)

@router.get("/{request_id}/files", response_model=SuccessResponse)
async def list_files(request_id: str, current_user: dict = Depends(get_current_user),):
    result = await request_service.list_files(request_id, current_user)
    return SuccessResponse(message="Files fetched", data=result)