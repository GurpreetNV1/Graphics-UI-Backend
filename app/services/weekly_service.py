from datetime import datetime, timedelta

from app.config import settings
from app.services import drive_client


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

    return {
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