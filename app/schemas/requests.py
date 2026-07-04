from typing import Optional, List
from pydantic import BaseModel

# Create Request Payload
class CreateRequestPayload(BaseModel):
    title: str
    description: str
    deadline: str  # ISO date string, e.g. "2026-07-15"
    priority: str  # "High" / "Medium" / "Low"
    platform: Optional[List[str]] = []
    request_type: str  # "Poster" / "Reel" / "Story" / etc.
    thumbnail_source: str = "pending"  # "uploaded" / "choose_from_raw" / "pending"
    caption_requirements: Optional[str] = ""
    subtitle_requirements: Optional[str] = ""

# File Upload Resource
class FileUploadResponse(BaseModel):
    id: str
    name: str
    view_link: Optional[str] = None
    download_link: Optional[str] = None

# Request Changes By Creator Payload
class RequestChangesPayload(BaseModel):
    reason: str

# Update a Particular Request Payload
class UpdateRequestPayload(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[str] = None
    priority: Optional[str] = None
    platform: Optional[List[str]] = None
    thumbnail_source: Optional[str] = None
    caption_requirements: Optional[str] = None
    subtitle_requirements: Optional[str] = None

# Add Comment Payload
class AddCommentPayload(BaseModel):
    message: str
    comment_type: str = "general"  # "clarification" / "general" / "update_note"