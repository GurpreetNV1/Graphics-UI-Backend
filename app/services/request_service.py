import uuid
from datetime import datetime, timezone

from app.services import requests_sheets_client, drive_client
from app.config import settings
from app.core.exceptions import RequestNotFoundError, InvalidStatusTransitionError


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _generate_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:8]}"

# Creation of a Request
async def create_request(current_user: dict, payload) -> dict:
    request_id = _generate_request_id()

    # Create the request's folder structure in Drive
    parent_folder = drive_client.create_folder(payload.title, settings.google_test_folder_id)
    raw_folder = drive_client.create_folder("Raw Files", parent_folder["id"])
    deliverables_folder = drive_client.create_folder("Deliverables", parent_folder["id"])

    fields = {
        "request_id": request_id,
        "title": payload.title,
        "description": payload.description,
        "deadline": payload.deadline,
        "priority": payload.priority,
        "status": "Pending",
        "created_by": current_user["user_id"],
        "assigned_designer": "",
        "raw_folder_id": raw_folder["id"],
        "raw_folder_link": raw_folder["link"],
        "deliverables_folder_id": deliverables_folder["id"],
        "deliverables_folder_link": deliverables_folder["link"],
        "thumbnail_source": payload.thumbnail_source,
        "caption_requirements": payload.caption_requirements or "",
        "subtitle_requirements": payload.subtitle_requirements or "",
        "platform": ",".join(payload.platform) if payload.platform else "",
        "request_type": payload.request_type,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }

    await requests_sheets_client.create_request(fields)

    return fields

# uploading Raw Files for a particular request
async def upload_raw_files(request_id: str, files: list) -> list[dict]:
    request = await requests_sheets_client.get_request_by_id(request_id)
    if not request:
        raise RequestNotFoundError()

    uploaded = []
    for file in files:
        content = await file.read()
        result = drive_client.upload_file(
            file_bytes=content,
            filename=file.filename,
            mime_type=file.content_type or "application/octet-stream",
            parent_id=request["raw_folder_id"],
        )
        drive_client.set_domain_permission(result["id"], settings.google_workspace_domain, allow_download=True)
        uploaded.append({
            "id": result["id"],
            "name": file.filename,
            "view_link": result.get("view_link"),
            "download_link": result.get("download_link"),
        })

    return uploaded

# List all the requests
async def list_requests(current_user: dict) -> list[dict]:
    all_requests = await requests_sheets_client.list_requests()

    role = current_user["role"]
    user_id = current_user["user_id"]

    if role == "designer":
        # Designers see: unclaimed (Pending) requests + anything assigned to them
        return [
            r for r in all_requests
            if r.get("status") == "Pending" or r.get("assigned_designer") == user_id
        ]

    if role == "employer":
        # Employers see only requests they created
        return [r for r in all_requests if r.get("created_by") == user_id]

    # Admin sees everything
    return all_requests


# Get a single request by ID
async def get_request(request_id: str) -> dict:
    request = await requests_sheets_client.get_request_by_id(request_id)
    if not request:
        raise RequestNotFoundError()
    return request

# Accepting a particular Request
async def accept_request(request_id: str, current_user: dict) -> dict:
    request = await requests_sheets_client.get_request_by_id(request_id)
    if not request:
        raise RequestNotFoundError()

    if request.get("status") != "Pending":
        raise InvalidStatusTransitionError("This request is no longer available to accept")

    fields = {
        "status": "In Progress",
        "assigned_designer": current_user["user_id"],
        "updated_at": _now_iso(),
    }
    await requests_sheets_client.update_request(request_id, fields)

    return {**request, **fields}

# upload deliverables inside the Deliverables folder
async def upload_deliverables(request_id: str, files: list, current_user: dict) -> list[dict]:
    request = await requests_sheets_client.get_request_by_id(request_id)
    if not request:
        raise RequestNotFoundError()

    if request.get("status") not in ("In Progress", "Changes Requested"):
        raise InvalidStatusTransitionError("Deliverables can only be uploaded while a request is in progress or has changes requested")

    uploaded = []
    for file in files:
        content = await file.read()
        result = drive_client.upload_file(
            file_bytes=content,
            filename=file.filename,
            mime_type=file.content_type or "application/octet-stream",
            parent_id=request["deliverables_folder_id"],
        )
        drive_client.set_domain_permission(result["id"], settings.google_workspace_domain, allow_download=False)
        uploaded.append({
            "id": result["id"],
            "name": file.filename,
            "view_link": result.get("view_link"),
            "download_link": result.get("download_link"),
        })

    return uploaded

# Submit the deliverable for Review
async def submit_for_review(request_id: str, current_user: dict) -> dict:
    request = await requests_sheets_client.get_request_by_id(request_id)
    if not request:
        raise RequestNotFoundError()

    if request.get("status") != "In Progress":
        raise InvalidStatusTransitionError("Only requests currently in progress can be submitted for review")

    fields = {
        "status": "Review",
        "updated_at": _now_iso(),
    }
    await requests_sheets_client.update_request(request_id, fields)

    return {**request, **fields}

# Request Approved by Request Creator
async def approve_request(request_id: str, current_user: dict) -> dict:
    request = await requests_sheets_client.get_request_by_id(request_id)
    if not request:
        raise RequestNotFoundError()

    if request.get("created_by") != current_user["user_id"]:
        raise InvalidStatusTransitionError("Only the request's creator can approve it")

    if request.get("status") != "Review":
        raise InvalidStatusTransitionError("Only requests currently in review can be approved")

    fields = {
        "status": "Completed",
        "updated_at": _now_iso(),
    }
    await requests_sheets_client.update_request(request_id, fields)
    
    deliverable_files = drive_client.list_files_in_folder(request["deliverables_folder_id"])
    for f in deliverable_files:
        drive_client.set_domain_permission(f["id"], settings.google_workspace_domain, allow_download=True)


    return {**request, **fields}

# Changes Requested from the deliverables right
async def request_changes(request_id: str, reason: str, current_user: dict) -> dict:
    request = await requests_sheets_client.get_request_by_id(request_id)
    if not request:
        raise RequestNotFoundError()

    if request.get("created_by") != current_user["user_id"]:
        raise InvalidStatusTransitionError("Only the request's creator can request changes")

    if request.get("status") != "Review":
        raise InvalidStatusTransitionError("Only requests currently in review can have changes requested")

    fields = {
        "status": "Changes Requested",
        "updated_at": _now_iso(),
    }
    await requests_sheets_client.update_request(request_id, fields)

    comment_id = f"cmt_{uuid.uuid4().hex[:8]}"
    await requests_sheets_client.add_comment({
        "comment_id": comment_id,
        "request_id": request_id,
        "author_id": current_user["user_id"],
        "message": reason,
        "comment_type": "rejection_reason",
        "created_at": _now_iso(),
    })

    return {**request, **fields}

# Update a particular request by the creator
async def update_request(request_id: str, payload, current_user: dict) -> dict:
    request = await requests_sheets_client.get_request_by_id(request_id)
    if not request:
        raise RequestNotFoundError()

    if request.get("created_by") != current_user["user_id"]:
        raise InvalidStatusTransitionError("Only the request's creator can update it")

    if request.get("status") in ("Completed", "Cancelled"):
        raise InvalidStatusTransitionError("Completed or cancelled requests cannot be updated")

    # Only include fields the caller actually provided
    fields = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not fields:
        raise InvalidStatusTransitionError("No fields provided to update")

    if "platform" in fields:
        fields["platform"] = ",".join(fields["platform"])

    fields["updated_at"] = _now_iso()

    await requests_sheets_client.update_request(request_id, fields)

    return {**request, **fields}

# Cancel a particular request by the creator
async def cancel_request(request_id: str, current_user: dict) -> dict:
    request = await requests_sheets_client.get_request_by_id(request_id)
    if not request:
        raise RequestNotFoundError()

    if request.get("created_by") != current_user["user_id"]:
        raise InvalidStatusTransitionError("Only the request's creator can cancel it")

    if request.get("status") in ("Completed", "Cancelled"):
        raise InvalidStatusTransitionError("This request is already completed or cancelled")

    fields = {
        "status": "Cancelled",
        "updated_at": _now_iso(),
    }
    await requests_sheets_client.update_request(request_id, fields)

    return {**request, **fields}

# Add Comment or Ask Clarification
async def add_comment(request_id: str, message: str, comment_type: str, current_user: dict) -> dict:
    request = await requests_sheets_client.get_request_by_id(request_id)
    if not request:
        raise RequestNotFoundError()

    comment_id = f"cmt_{uuid.uuid4().hex[:8]}"
    comment = {
        "comment_id": comment_id,
        "request_id": request_id,
        "author_id": current_user["user_id"],
        "message": message,
        "comment_type": comment_type,
        "created_at": _now_iso(),
    }
    await requests_sheets_client.add_comment(comment)

    return comment

# Get List of all comments right
async def get_comments(request_id: str) -> list[dict]:
    request = await requests_sheets_client.get_request_by_id(request_id)
    if not request:
        raise RequestNotFoundError()

    return await requests_sheets_client.get_comments_by_request_id(request_id)

# List all files of a Request
async def list_files(request_id: str, current_user: dict) -> dict:
    request = await requests_sheets_client.get_request_by_id(request_id)
    if not request:
        raise RequestNotFoundError()

    raw_files = drive_client.list_files_in_folder(request["raw_folder_id"])
    deliverable_files = drive_client.list_files_in_folder(request["deliverables_folder_id"])

    # Enforce: employer only gets download links for deliverables once Completed
    if current_user["role"] == "employer" and request.get("status") != "Completed":
        deliverable_files = [
            {**f, "webContentLink": None}  # strip download link, keep view link
            for f in deliverable_files
        ]

    return {
        "raw_files": raw_files,
        "deliverable_files": deliverable_files,
    }