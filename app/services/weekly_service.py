import uuid
from datetime import datetime, timedelta, timezone

from app.config import settings
from app.services import drive_client, weekly_sheets_client
from app.core.exceptions import FeedbackRequiredError, WeeklyPostNotFoundError


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_current_week_label() -> str:
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return f"{monday.strftime('%Y-%m-%d')}_to_{sunday.strftime('%Y-%m-%d')}"


async def upload_weekly_post(title: str, caption: str, files: list, current_user: dict) -> dict:
    week_label = get_current_week_label()
    week_folder = drive_client.get_or_create_week_folder(week_label, settings.google_weekly_folder_id)
    post_folder = drive_client.create_folder(title, week_folder["id"])

    uploaded_files = []
    for file in files:
        content = await file.read()
        result = drive_client.upload_file(
            file_bytes=content,
            filename=file.filename,
            mime_type=file.content_type or "application/octet-stream",
            parent_id=post_folder["id"],
        )
        drive_client.set_domain_permission(result["id"], settings.google_workspace_domain, allow_download=True)
        uploaded_files.append({
            "id": result["id"],
            "name": file.filename,
            "view_link": result.get("view_link"),
            "download_link": result.get("download_link"),
        })

    caption_file = drive_client.upload_text_file(caption, "caption.txt", post_folder["id"])
    drive_client.set_domain_permission(caption_file["id"], settings.google_workspace_domain, allow_download=True)

    # NEW — write a tracking row into the WeeklyPosts sheet
    post_id = f"wp_{uuid.uuid4().hex[:8]}"
    today_date = datetime.now().strftime("%Y-%m-%d")

    await weekly_sheets_client.create_weekly_post({
        "post_id": post_id,
        "week": week_label,
        "title": title,
        "date": today_date,
        "file_link": uploaded_files[0]["download_link"] if uploaded_files else "",
        "caption_link": caption_file.get("download_link"),
        "created_by": current_user["user_id"],
        "created_at": _now_iso(),
        "is_posted": False,
        "posted_feedback": "",
        "posted_at": "",
    })

    return {
        "post_id": post_id,
        "week": week_label,
        "post_title": title,
        "post_folder_link": post_folder["link"],
        "files": uploaded_files,
        "caption_file": {
            "id": caption_file["id"],
            "view_link": caption_file.get("view_link"),
            "download_link": caption_file.get("download_link"),
        },
    }


async def list_weeks() -> list[dict]:
    results = drive_client.list_files_in_folder(settings.google_weekly_folder_id)
    return [
        {"name": f["name"], "link": f.get("webViewLink")}
        for f in results
        if f.get("mimeType") == "application/vnd.google-apps.folder"
    ]


# ===== NEW — sheet-tracking functions =====

async def list_posts() -> list[dict]:
    return await weekly_sheets_client.list_weekly_posts()


async def mark_post_done(post_id: str, feedback: str) -> dict:
    if not feedback or not feedback.strip():
        raise FeedbackRequiredError()

    result = await weekly_sheets_client.mark_weekly_post_done(post_id, feedback)
    if not result.get("success"):
        raise WeeklyPostNotFoundError()
    return result


async def add_review(post_id: str, note: str) -> dict:
    if not note or not note.strip():
        raise FeedbackRequiredError()  # same rule — a review shouldn't be empty either

    result = await weekly_sheets_client.add_weekly_post_review(post_id, note)
    if not result.get("success"):
        raise WeeklyPostNotFoundError()
    return result


async def delete_post(post_id: str) -> dict:
    result = await weekly_sheets_client.delete_weekly_post(post_id)
    if not result.get("success"):
        raise WeeklyPostNotFoundError()
    return result